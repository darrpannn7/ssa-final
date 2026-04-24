"""
build_flare_dataset.py
----------------------
Fetches historical GOES X-ray flux + NASA DONKI flare events,
aligns them into 60-minute sliding windows, labels each window,
and saves to data/flare_dataset.jsonl

Usage:
    python build_flare_dataset.py --days 90 --output data/flare_dataset.jsonl
"""

import asyncio
import httpx
import json
import os
import argparse
import pandas as pd
import numpy as np
from collections import Counter
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ── Constants ──────────────────────────────────────────────────────
NASA_API_KEY      = os.getenv("NASA_API_KEY", "DEMO_KEY")
GOES_URL          = "https://services.swpc.noaa.gov/json/goes/secondary/xrays-6-hour.json"
DONKI_URL         = "https://api.nasa.gov/DONKI/FLR"
WIND_PLASMA_URL   = "https://services.swpc.noaa.gov/products/solar-wind/plasma-7-day.json"
WIND_MAG_URL      = "https://services.swpc.noaa.gov/products/solar-wind/mag-7-day.json"
SUNSPOT_URL       = "https://services.swpc.noaa.gov/json/sunspot_report.json"

POINTS_PER_WINDOW = 12   # 12 x 5-min = 60 min window

THRESHOLDS = {"X": 1e-4, "M": 1e-5, "C": 1e-6, "B": 1e-7}

SYSTEM_PROMPT = (
    "You are a solar flare prediction model. Analyze GOES X-ray flux "
    "time series and space weather indicators to predict solar flare "
    "class. Classes: no_flare, A, B, C, M, X."
)


# ── Pure helpers (no I/O) ──────────────────────────────────────────

def flux_to_class(flux: float) -> str:
    flux = float(flux)
    if flux >= THRESHOLDS["X"]: return "X"
    if flux >= THRESHOLDS["M"]: return "M"
    if flux >= THRESHOLDS["C"]: return "C"
    if flux >= THRESHOLDS["B"]: return "B"
    if flux >  0:               return "A"
    return "no_flare"


def get_trend(window: list) -> str:
    if len(window) < 2:
        return "stable"
    first = float(window[0])
    last  = float(window[-1])
    if first == 0:
        return "stable"
    diff = last - first
    if diff > first * 0.3:  return "rising"
    if diff < -first * 0.3: return "falling"
    return "stable"


def mock_surya(window: list) -> dict:
    arr     = np.array([float(v) for v in window], dtype=np.float32)
    log_arr = np.log10(np.clip(arr, 1e-9, None))
    intensity  = float(np.clip(np.mean(np.abs(log_arr)) / 10.0, 0, 1))
    complexity = float(np.clip(np.var(log_arr) / 5.0, 0, 1))

    if intensity > 0.7:    risk = "High — X-class likely"
    elif intensity > 0.45: risk = "Moderate — M-class possible"
    else:                  risk = "Low — C-class or below"

    return {"flare_risk": risk, "magnetic_complexity": round(complexity, 4)}


def build_user_prompt(window, peak_flux, sunspots, speed, bz, surya) -> str:
    flux_str = ", ".join(f"{float(v):.3e}" for v in window)
    return (
        f"GOES X-ray flux (last 60 min, W/m²): [{flux_str}]\n"
        f"Peak flux: {float(peak_flux):.3e}\n"
        f"Trend: {get_trend(window)}\n"
        f"Sunspot count: {sunspots}\n"
        f"Solar wind speed: {speed:.0f} km/s\n"
        f"Bz component: {bz:.1f} nT\n"
        f"Surya flare_risk: {surya['flare_risk']}\n"
        f"Surya magnetic_complexity: {surya['magnetic_complexity']:.4f}\n"
        f"Predict flare class and estimated onset window."
    )


def build_assistant_response(label: str, peak_flux: float, trend_str: str) -> str:
    if label == "no_flare":
        return (
            "Flare class: no_flare | Confidence: high | Onset: N/A | "
            "Reasoning: Flux below A-class threshold with stable trend."
        )
    confidence = "high" if label in ("M", "X") else "medium"
    onset      = "5-15 min" if label in ("M", "X") else "30-60 min"
    return (
        f"Flare class: {label} | Confidence: {confidence} | "
        f"Onset: {onset} | "
        f"Reasoning: {trend_str.capitalize()} flux trend reaching "
        f"{label}-class threshold ({float(peak_flux):.2e} W/m²)."
    )


# ── Async fetchers ─────────────────────────────────────────────────

async def fetch_goes() -> tuple:
    """Returns (flux_list, time_list) as plain Python lists."""
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(GOES_URL, timeout=30.0)
            r.raise_for_status()
            raw = r.json()
        except Exception as e:
            print(f"GOES fetch failed: {e}")
            return [], []

    flux_list, time_list = [], []
    for row in raw:
        if row.get("energy") != "0.1-0.8nm":
            continue
        val = row.get("flux")          # use corrected 'flux' column
        if val is None or float(val) <= 0:
            continue
        flux_list.append(float(val))
        time_list.append(row.get("time_tag", ""))

    return flux_list, time_list


async def fetch_donki(start: str, end: str) -> dict:
    """Returns {pd.Timestamp: class_letter} dict."""
    url = f"{DONKI_URL}?startDate={start}&endDate={end}&api_key={NASA_API_KEY}"
    async with httpx.AsyncClient() as client:
        try:
            r    = await client.get(url, timeout=30.0)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            print(f"DONKI fetch failed: {e}")
            return {}

    events = {}
    for f in data:
        peak = f.get("peakTime") or f.get("beginTime")
        cls  = f.get("classType", "")
        if peak and cls:
            try:
                events[pd.to_datetime(peak, utc=True)] = cls[0].upper()
            except Exception:
                pass
    return events


async def fetch_wind() -> dict:
    async with httpx.AsyncClient() as client:
        try:
            r1 = await client.get(WIND_PLASMA_URL, timeout=30.0)
            r2 = await client.get(WIND_MAG_URL,    timeout=30.0)
            plasma = r1.json()
            mag    = r2.json()
            speed = float(plasma[-1][2]) if plasma[-1][2] not in (None, "") else 400.0
            bz    = float(mag[-1][3])    if mag[-1][3]    not in (None, "") else 0.0
            return {"speed": speed, "bz": bz}
        except Exception:
            return {"speed": 400.0, "bz": 0.0}


async def fetch_sunspots() -> int:
    async with httpx.AsyncClient() as client:
        try:
            r    = await client.get(SUNSPOT_URL, timeout=30.0)
            data = r.json()
            return int(data[0].get("SunspotNumber", 20)) if data else 20
        except Exception:
            return 20


# ── Main builder ───────────────────────────────────────────────────

async def build_dataset(days: int, output_path: str):
    print(f"Building dataset: {days} days → {output_path}")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    wind, sunspots = await asyncio.gather(fetch_wind(), fetch_sunspots())
    print(f"Solar wind: {wind['speed']:.0f} km/s  Bz: {wind['bz']:.1f} nT")
    print(f"Sunspot count: {sunspots}")

    print("Fetching GOES X-ray flux...")
    flux_list, time_list = await fetch_goes()
    if not flux_list:
        print("ERROR: Could not fetch GOES data.")
        return
    print(f"Got {len(flux_list)} GOES data points")

    now        = datetime.now(timezone.utc)
    start_date = now - timedelta(days=days)
    print(f"Fetching DONKI flare events {start_date.date()} → {now.date()}...")
    flare_events = await fetch_donki(
        start_date.strftime("%Y-%m-%d"),
        now.strftime("%Y-%m-%d"),
    )
    print(f"Got {len(flare_events)} labeled flare events")

    # Parse timestamps to tz-aware
    parsed_times = []
    for t in time_list:
        try:
            parsed_times.append(pd.to_datetime(t, utc=True))
        except Exception:
            parsed_times.append(None)

    # Build sliding windows
    records = []
    for i in range(POINTS_PER_WINDOW, len(flux_list)):
        window    = flux_list[i - POINTS_PER_WINDOW : i]
        t_end     = parsed_times[i]
        peak_flux = float(max(window))
        label     = flux_to_class(peak_flux)

        # Override with real DONKI label if within ±30 min
        if t_end is not None:
            for ft, fc in flare_events.items():
                try:
                    if abs((ft - t_end).total_seconds()) / 60 <= 30:
                        label = fc
                        break
                except Exception:
                    pass

        surya     = mock_surya(window)
        trend_str = get_trend(window)

        records.append({
            "messages": [
                {"role": "system",    "content": SYSTEM_PROMPT},
                {"role": "user",      "content": build_user_prompt(
                    window, peak_flux, sunspots, wind["speed"], wind["bz"], surya
                )},
                {"role": "assistant", "content": build_assistant_response(
                    label, peak_flux, trend_str
                )},
            ],
            "metadata": {
                "timestamp":    str(t_end),
                "actual_class": label,
                "peak_flux":    peak_flux,
                "source":       "NOAA_GOES_secondary",
            },
        })

    dist = Counter(r["metadata"]["actual_class"] for r in records)
    print(f"\nClass distribution: {dict(dist)}")
    print(f"Total samples: {len(records)}")

    with open(output_path, "w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")

    print(f"✅ Saved {len(records)} samples to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--days",   type=int, default=30)
    parser.add_argument("--output", type=str, default="data/flare_dataset.jsonl")
    args = parser.parse_args()
    asyncio.run(build_dataset(args.days, args.output))
