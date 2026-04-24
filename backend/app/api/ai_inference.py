import logging
import numpy as np
from fastapi import APIRouter, Form, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image
import io
from pydantic import BaseModel
from typing import Optional
from app.services.flare_llm_service import predict_flare

from app.services.ai_service import AIService
from app.services.detection_service import detect_and_annotate

logger     = logging.getLogger(__name__)
router     = APIRouter()
ai_service = AIService()

EXPECTED_CHANNELS = 13


def _fake_multichannel(h: int = 512, w: int = 512) -> np.ndarray:
    rng  = np.random.default_rng(seed=42)
    base = rng.standard_normal((h, w)).astype(np.float32)
    channels = [
        base + rng.standard_normal((h, w)).astype(np.float32) * 0.1
        for _ in range(EXPECTED_CHANNELS)
    ]
    return np.stack(channels, axis=0)


def _image_to_stack(raw: bytes) -> np.ndarray:
    pil = Image.open(io.BytesIO(raw)).convert("L")
    arr = np.array(pil, dtype=np.float32) / 255.0
    return np.stack([arr] * EXPECTED_CHANNELS, axis=0)


@router.post("/chat")
async def chat(
    message: str               = Form(...),
    image:   UploadFile | None = File(default=None),
):
    raw_bytes        = None
    image_stack      = _fake_multichannel()
    detection_result = None

    if image is not None:
        try:
            raw_bytes   = await image.read()
            image_stack = _image_to_stack(raw_bytes)

            # ── Run detection + annotation ──────────────────────
            detection_result = detect_and_annotate(raw_bytes)

        except Exception:
            logger.exception("Failed to process uploaded image")
            raise HTTPException(
                status_code=422,
                detail="Could not read the uploaded image."
            )

    try:
        result = ai_service.chat(
            message=message,
            image_stack=image_stack,
            image_bytes=raw_bytes,
        )
    except Exception:
        logger.exception("ai_service.chat raised unexpectedly")
        raise HTTPException(status_code=500, detail="Inference error.")

    return JSONResponse({
        "response":        result["text"],
        "surya_data":      result["surya_data"],
        "source":          result["source"],
        # ── New fields ──────────────────────────────────────────
        "annotated_image": detection_result["annotated_image"] if detection_result else None,
        "regions":         detection_result["regions"]         if detection_result else [],
    })

"""
ADDITION to: backend/app/api/ai_inference.py
--------------------------------------------
Add these imports and the new endpoint BELOW the existing /chat route.
Do NOT modify the existing /chat route at all.

Step 1: Add these imports at the top of ai_inference.py (after existing imports):
    from pydantic import BaseModel
    from typing import Optional
    from app.services.flare_llm_service import predict_flare
    from app.services.noaa_service import NOAAFetcher        # already exists as noaa_fetcher
    from app.services.surya_service import analyze_multichannel

Step 2: Paste the Pydantic models + endpoint below.
"""

from pydantic import BaseModel
from typing import Optional
import asyncio
import numpy as np
from datetime import datetime


# ── Request / Response models ──────────────────────────────────────

class FlareRequest(BaseModel):
    use_live_data:       bool            = True
    flux_window:         Optional[list[float]] = None   # manual override
    sunspot_count:       Optional[int]   = None
    wind_speed:          Optional[float] = None
    bz:                  Optional[float] = None
    include_explanation: bool            = True


class FlareResponse(BaseModel):
    predicted_class:       str
    confidence:            str
    onset_window_minutes:  int
    reasoning:             str
    surya_flare_risk:      str
    surya_magnetic_complexity: float
    goes_peak_flux:        float
    model_source:          str
    timestamp:             str


# ── Helpers ────────────────────────────────────────────────────────

async def _fetch_live_goes_flux() -> list[float]:
    """
    Fetches live GOES X-ray flux and returns last 12 points (60 min window).
    Reuses the existing NOAAFetcher pattern.
    """
    try:
        import httpx
        import pandas as pd
        GOES_URL = "https://services.swpc.noaa.gov/json/goes/primary/xrays-6-hour.json"
        async with httpx.AsyncClient() as client:
            r = await client.get(GOES_URL, timeout=8.0)
            r.raise_for_status()
            data = r.json()
        df = pd.DataFrame(data)
        df = df[(df["energy"] == "0.1-0.8nm") & (df["observed_flux"] > 0)]
        flux_vals = df["observed_flux"].tail(12).tolist()
        return flux_vals if len(flux_vals) >= 2 else [1e-7] * 12
    except Exception:
        logger.exception("Failed to fetch live GOES flux for prediction")
        return [1e-7] * 12


async def _fetch_live_solar_wind() -> dict:
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            r1 = await client.get(
                "https://services.swpc.noaa.gov/products/solar-wind/plasma-7-day.json",
                timeout=8.0
            )
            r2 = await client.get(
                "https://services.swpc.noaa.gov/products/solar-wind/mag-7-day.json",
                timeout=8.0
            )
        plasma = r1.json()
        mag    = r2.json()
        speed = float(plasma[-1][2]) if len(plasma) > 1 and plasma[-1][2] not in (None, "") else 400.0
        bz    = float(mag[-1][3])    if len(mag) > 1    and mag[-1][3]    not in (None, "") else 0.0
        return {"speed": speed, "bz": bz}
    except Exception:
        return {"speed": 400.0, "bz": 0.0}


async def _fetch_sunspots() -> int:
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            r = await client.get(
                "https://services.swpc.noaa.gov/json/sunspot_report.json",
                timeout=8.0
            )
            data = r.json()
            return int(data[0].get("SunspotNumber", 20)) if data else 20
    except Exception:
        return 20


def _run_surya_on_flux(flux_window: list[float]) -> dict:
    """
    Approximates Surya metrics from flux values when no real image is available.
    This is the same mock used in dataset building — consistent features.
    """
    arr     = np.array(flux_window, dtype=np.float32)
    log_arr = np.log10(np.clip(arr, 1e-9, None))
    intensity   = float(np.mean(np.abs(log_arr)) / 10.0)
    complexity  = float(np.var(log_arr) / 5.0)
    intensity   = round(min(max(intensity, 0.0), 1.0), 4)
    complexity  = round(min(max(complexity, 0.0), 1.0), 4)

    if intensity > 0.7:
        risk = "High — X-class likely"
    elif intensity > 0.45:
        risk = "Moderate — M-class possible"
    else:
        risk = "Low — C-class or below"

    return {"flare_risk": risk, "magnetic_complexity": complexity}


# ── Endpoint ───────────────────────────────────────────────────────

@router.post("/flare-predict", response_model=FlareResponse)
async def flare_predict(req: FlareRequest):
    """
    Predicts solar flare class using the fine-tuned LLaMA model
    (falls back to Groq if local model not available).

    - use_live_data=true: auto-fetches GOES flux + solar wind + sunspots
    - use_live_data=false: uses manually provided flux_window etc.
    """
    # ── 1. Gather inputs ───────────────────────────────────────────
    if req.use_live_data:
        flux_task  = _fetch_live_goes_flux()
        wind_task  = _fetch_live_solar_wind()
        ss_task    = _fetch_sunspots()
        flux_window, wind_data, sunspots = await asyncio.gather(
            flux_task, wind_task, ss_task
        )
        wind_speed = wind_data["speed"]
        bz         = wind_data["bz"]
    else:
        flux_window = req.flux_window or [1e-7] * 12
        wind_speed  = req.wind_speed  or 400.0
        bz          = req.bz          or 0.0
        sunspots    = req.sunspot_count or 20

    # ── 2. Surya metrics (from flux if no image available) ─────────
    surya = _run_surya_on_flux(flux_window)

    # ── 3. Run prediction ──────────────────────────────────────────
    try:
        from app.services.flare_llm_service import predict_flare
        result = predict_flare(
            flux_window=flux_window,
            sunspot_count=sunspots,
            wind_speed=wind_speed,
            bz=bz,
            surya_flare_risk=surya["flare_risk"],
            surya_magnetic_complexity=surya["magnetic_complexity"],
        )
    except Exception:
        logger.exception("flare_llm_service.predict_flare failed")
        raise HTTPException(status_code=500, detail="Flare prediction inference error.")

    return FlareResponse(
        predicted_class=result.predicted_class,
        confidence=result.confidence,
        onset_window_minutes=result.onset_window_minutes,
        reasoning=result.reasoning if req.include_explanation else "",
        surya_flare_risk=surya["flare_risk"],
        surya_magnetic_complexity=surya["magnetic_complexity"],
        goes_peak_flux=max(flux_window),
        model_source=result.model_source,
        timestamp=datetime.utcnow().isoformat() + "Z",
    )
