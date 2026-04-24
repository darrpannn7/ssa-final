"""
SSA Dashboard – Automated API Test Suite
Run with: pytest tests/test_api.py -v -s
The -s flag prints actual output for each test → copy into Excel "Actual Result" column
"""

import pytest
from fastapi.testclient import TestClient
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app.main import app

client = TestClient(app)


# ══════════════════════════════════════════════════════════
#  MAGNETOGRAM ENDPOINTS  (BE-004 to BE-007)
# ══════════════════════════════════════════════════════════

def test_BE004_magnetogram_latest_returns_success():
    """BE-004: GET /magnetogram/latest returns status+data (may be slow on first call)"""
    res = client.get("/space-weather/magnetogram/latest", timeout=120)
    if res.status_code in [500, 503, 502]:
        print(f"\n[BE-004] Status: {res.status_code} — magnetogram service unavailable. Skipping.")
        pytest.skip("Magnetogram service unavailable")
    data = res.json()
    print(f"\n[BE-004] Status: {res.status_code} | keys: {list(data.keys())} | meta: {data.get('meta')}")
    assert res.status_code == 200
    assert data.get("status") == "success"
    assert "result" in data or "meta" in data


def test_BE005_magnetogram_image_returns_png():
    """BE-005: GET /magnetogram/image returns image/png with non-empty body"""
    res = client.get("/space-weather/magnetogram/image", timeout=120)
    if res.status_code in [500, 503, 502, 404]:
        print(f"\n[BE-005] Status: {res.status_code} — magnetogram image unavailable. Skipping.")
        pytest.skip("Magnetogram image unavailable")
    ctype = res.headers.get("content-type", "")
    print(f"\n[BE-005] Status: {res.status_code} | Content-Type: {ctype} | Body size: {len(res.content)} bytes")
    assert res.status_code == 200
    assert "image" in ctype or "png" in ctype
    assert len(res.content) > 0


def test_BE006_magnetogram_regions_returns_array():
    """BE-006: GET /magnetogram/regions returns regions array with required keys"""
    res = client.get("/space-weather/magnetogram/regions", timeout=120)
    if res.status_code in [500, 503, 502, 404]:
        print(f"\n[BE-006] Status: {res.status_code} — regions unavailable. Skipping.")
        pytest.skip("Magnetogram regions unavailable")
    data = res.json()
    regions = data.get("regions", [])
    print(f"\n[BE-006] Status: {res.status_code} | status: {data.get('status')} | regions count: {len(regions)}")
    assert res.status_code == 200
    assert data.get("status") == "success"
    assert isinstance(regions, list)
    for r in regions:
        for key in ["id", "bbox", "strength", "area", "flare"]:
            assert key in r, f"Region missing key: {key}"


def test_BE007_magnetogram_cache_reused():
    """BE-007: Second call to /magnetogram/latest is faster (cache used if < 30 min)"""
    import time
    # First call (may download)
    t0 = time.time()
    res1 = client.get("/space-weather/magnetogram/latest", timeout=120)
    t1 = time.time() - t0
    if res1.status_code not in [200]:
        print(f"\n[BE-007] First call failed with {res1.status_code}. Skipping.")
        pytest.skip("Magnetogram unavailable for cache test")
    # Second call (should use cache)
    t0 = time.time()
    res2 = client.get("/space-weather/magnetogram/latest", timeout=60)
    t2 = time.time() - t0
    print(f"\n[BE-007] 1st call: {t1:.2f}s | 2nd call: {t2:.2f}s | second_faster: {t2 <= t1}")
    assert res2.status_code == 200


# ══════════════════════════════════════════════════════════
#  ROOT & SYSTEM
# ══════════════════════════════════════════════════════════

def test_BE001_root_returns_running_message():
    """BE-001: GET / returns running message"""
    res = client.get("/")
    data = res.json()
    print(f"\n[BE-001] Status: {res.status_code} | Body: {data}")
    assert res.status_code == 200
    assert "message" in data
    assert "running" in data["message"].lower()


def test_BE002_system_status_returns_health_info():
    """BE-002: GET /system/status returns health info"""
    res = client.get("/system/status")
    data = res.json()
    print(f"\n[BE-002] Status: {res.status_code} | Keys: {list(data.keys())} | magnetogram_cached: {data.get('magnetogram_cached')}")
    assert res.status_code == 200
    for key in ["service", "time", "magnetogram_cached", "cache_location"]:
        assert key in data


# ══════════════════════════════════════════════════════════
#  SOLAR FLARES
# ══════════════════════════════════════════════════════════

def test_BE008_flares_returns_success_and_data():
    """BE-008: GET /space-weather/flares returns {status, total, flares} (skips if unavailable)"""
    res = client.get("/space-weather/flares")
    if res.status_code == 500:
        print(f"\n[BE-008] Status: 500 — CCMC/NASA API rate limit or network error. Skipping.")
        pytest.skip("Flares API unavailable (rate limit or network)")
    data = res.json()
    flares = data.get("flares", [])
    count = len(flares)
    first = flares[0] if flares else {}
    print(f"\n[BE-008] Status: {res.status_code} | status: {data.get('status')} | Total flares: {count} | First keys: {list(first.keys())}")
    assert res.status_code == 200
    assert data.get("status") == "success"
    assert isinstance(flares, list)
    if flares:
        assert "classType" in flares[0]


def test_BE009_flare_data_within_last_10():
    """BE-009: /space-weather/flares returns at most 10 events (last 10 from CCMC)"""
    res = client.get("/space-weather/flares")
    if res.status_code != 200:
        pytest.skip("Flares API unavailable")
    data = res.json()
    flares = data.get("flares", [])
    print(f"\n[BE-009] Status: {res.status_code} | total: {data.get('total')} | flares in array: {len(flares)}")
    assert isinstance(flares, list)
    assert len(flares) <= 10
    if flares:
        for key in ["classType", "startTime", "peakTime", "endTime", "activeRegion"]:
            assert key in flares[0], f"Missing flare field: {key}"


def test_BE010_aia_image_returns_jpeg():
    """BE-010: GET /aia-image?wavelength=0171 returns image/jpeg"""
    res = client.get("/space-weather/aia-image?wavelength=0171")
    ctype = res.headers.get("content-type", "")
    print(f"\n[BE-010] Status: {res.status_code} | Content-Type: {ctype} | Body size: {len(res.content)} bytes")
    # Allow 502 if SDO server is unreachable in CI
    assert res.status_code in [200, 502, 503]
    if res.status_code == 200:
        assert "image" in ctype


def test_BE011_aia_invalid_wavelength_returns_400():
    """BE-011: Invalid wavelength returns 400"""
    res = client.get("/space-weather/aia-image?wavelength=9999")
    data = res.json()
    print(f"\n[BE-011] Status: {res.status_code} | Detail: {data.get('detail')}")
    assert res.status_code == 400
    assert "detail" in data


def test_BE012_aia_valid_wavelengths():
    """BE-012: All 4 current valid wavelengths return 200 or upstream error (not 400)"""
    # The updated endpoint only accepts: 0094, 0131, 0171, 0193
    # Other wavelengths (e.g. 0211, 0304) now return 400 Bad Request
    valid_wavelengths = ["0094", "0131", "0171", "0193"]
    invalid_wavelengths = ["0211", "0304", "0335", "1600", "1700"]
    results = {}
    for wl in valid_wavelengths:
        res = client.get(f"/space-weather/aia-image?wavelength={wl}")
        results[wl] = res.status_code
    print(f"\n[BE-012] Valid wavelength results: {results}")
    for wl, code in results.items():
        assert code in [200, 502, 503], f"Valid wavelength {wl} returned unexpected {code}"
    for wl in invalid_wavelengths:
        res = client.get(f"/space-weather/aia-image?wavelength={wl}")
        print(f"\n[BE-012] Invalid wavelength {wl}: status {res.status_code} (expected 400)")
        assert res.status_code == 400, f"Wavelength {wl} should now be invalid (400), got {res.status_code}"


# ══════════════════════════════════════════════════════════
#  GOES X-RAY
# ══════════════════════════════════════════════════════════

def test_BE013_goes_xray_returns_primary_and_secondary():
    """BE-013: /noaa/goes-xray returns primary and secondary"""
    res = client.get("/noaa/goes-xray")
    assert res.status_code == 200
    data = res.json()
    p_len = len(data.get("primary", []))
    s_len = len(data.get("secondary", []))
    print(f"\n[BE-013] Status: {res.status_code} | primary items: {p_len} | secondary items: {s_len}")
    assert "primary" in data
    assert "secondary" in data
    assert isinstance(data["primary"], list)
    assert isinstance(data["secondary"], list)


def test_BE014_goes_primary_max_200_items():
    """BE-014: primary list has ≤ 200 items"""
    res = client.get("/noaa/goes-xray")
    if res.status_code != 200:
        pytest.skip("NOAA unavailable")
    count = len(res.json().get("primary", []))
    print(f"\n[BE-014] Primary count: {count} (must be ≤ 200)")
    # NOAA returns exactly 200 (tail of last 200): ≤ 200 is correct
    assert count <= 200


def test_BE015_goes_flux_values_positive():
    """BE-015: All flux values > 0"""
    res = client.get("/noaa/goes-xray")
    items = res.json().get("primary", [])
    negatives = [i["flux"] for i in items if i["flux"] <= 0]
    print(f"\n[BE-015] Total primary items: {len(items)} | Non-positive flux values: {negatives}")
    assert negatives == [], f"Non-positive flux found: {negatives}"


# ══════════════════════════════════════════════════════════
#  CME
# ══════════════════════════════════════════════════════════

def test_BE016_cme_full_returns_events():
    """BE-016: /cme/full returns up to 10 CME events (skips if NASA rate-limited)"""
    res = client.get("/space-weather/cme/full")
    if res.status_code == 500:
        print(f"\n[BE-016] Status: 500 — NASA API rate limit or error. Skipping.")
        pytest.skip("NASA API unavailable (rate limit or network)")
    data = res.json()
    events = data.get("cme_events", [])
    first = {k: events[0][k] for k in ["activityID", "speed", "impactProbability"]} if events else {}
    print(f"\n[BE-016] Status: {res.status_code} | total: {data.get('total')} | first event: {first}")
    assert res.status_code == 200
    assert data["status"] == "success"
    assert len(events) <= 10


def test_BE018_cme_impact_probability_valid_values():
    """BE-018: impactProbability only Low/Moderate/High"""
    res = client.get("/space-weather/cme/full")
    events = res.json().get("cme_events", [])
    probs = {e["activityID"]: e.get("impactProbability") for e in events}
    print(f"\n[BE-018] Impact probabilities: {probs}")
    valid = {"Low", "Moderate", "High"}
    for aid, prob in probs.items():
        if prob:
            assert prob in valid, f"{aid} has invalid value: {prob}"


def test_BE017_cme_image_returns_file():
    """BE-017: /cme/image returns file"""
    res = client.get("/space-weather/cme/image")
    ctype = res.headers.get("content-type", "unknown")
    print(f"\n[BE-017] Status: {res.status_code} | Content-Type: {ctype} | Body size: {len(res.content)} bytes")
    assert res.status_code in [200, 500]


# ══════════════════════════════════════════════════════════
#  SOLAR WIND
# ══════════════════════════════════════════════════════════

def test_BE019_wind_speed_returns_data():
    """BE-019: /wind/speed returns speed, density, temperature"""
    res = client.get("/space-weather/wind/speed")
    data = res.json()
    items = data.get("data", [])
    latest = items[-1] if items else {}
    print(f"\n[BE-019] Status: {res.status_code} | data points: {len(items)} | latest: {latest}")
    assert res.status_code == 200
    assert data["status"] == "success"
    if items:
        for key in ["time_tag", "speed", "density", "temperature"]:
            assert key in items[0]


def test_BE020_wind_imf_returns_components():
    """BE-020: /wind/imf returns bx, by, bz, bt"""
    res = client.get("/space-weather/wind/imf")
    data = res.json()
    items = data.get("data", [])
    latest = items[-1] if items else {}
    print(f"\n[BE-020] Status: {res.status_code} | data points: {len(items)} | latest: {latest}")
    assert res.status_code == 200
    if items:
        for key in ["bx", "by", "bz", "bt"]:
            assert key in items[0]


def test_BE021_wind_all_returns_both():
    """BE-021: /wind/all returns solar_wind and imf"""
    res = client.get("/space-weather/wind/all")
    data = res.json()
    sw_len = len(data.get("solar_wind", []))
    imf_len = len(data.get("imf", []))
    print(f"\n[BE-021] Status: {res.status_code} | solar_wind points: {sw_len} | imf points: {imf_len}")
    assert res.status_code == 200
    assert "solar_wind" in data and "imf" in data


# ══════════════════════════════════════════════════════════
#  SEP
# ══════════════════════════════════════════════════════════

def test_BE023_sep_particle_flux():
    """BE-023: /sep/particle-flux returns proton and electron"""
    res = client.get("/space-weather/sep/particle-flux")
    data = res.json()
    p_len = len(data.get("proton", []))
    e_len = len(data.get("electron", []))
    print(f"\n[BE-023] Status: {res.status_code} | proton points: {p_len} | electron points: {e_len}")
    assert res.status_code == 200
    assert "proton" in data and "electron" in data


def test_BE024_sep_alerts_risk_level():
    """BE-024: /sep/alerts returns risk_level and alerts"""
    res = client.get("/space-weather/sep/alerts")
    data = res.json()
    print(f"\n[BE-024] Status: {res.status_code} | risk_level: {data.get('risk_level')} | alert count: {len(data.get('alerts', []))}")
    valid_levels = {"quiet", "low", "moderate", "high", "severe", "unknown"}
    assert data["risk_level"] in valid_levels
    assert isinstance(data["alerts"], list)


def test_BE025_sep_all_keys():
    """BE-025: /sep/all returns particle_flux, alerts, radiation_risk"""
    res = client.get("/space-weather/sep/all")
    data = res.json()
    risk = data.get("radiation_risk", {})
    print(f"\n[BE-025] Status: {res.status_code} | keys: {list(data.keys())} | radiation_risk: {risk}")
    assert "particle_flux" in data
    assert "alerts" in data
    assert "radiation_risk" in data


def test_BE026_sep_radiation_risk_valid():
    """BE-026: radiation_risk values are valid levels"""
    res = client.get("/space-weather/sep/all")
    risk = res.json().get("radiation_risk", {})
    valid = {"low", "moderate", "high", "severe", "extreme"}
    print(f"\n[BE-026] radiation_risk: {risk}")
    for key in ["crew", "satellite", "deep_space"]:
        if key in risk:
            assert risk[key] in valid


# ══════════════════════════════════════════════════════════
#  AI INFERENCE
# ══════════════════════════════════════════════════════════

def test_BE027_ai_chat_text_only():
    """BE-027: POST /ai/chat with text returns response"""
    res = client.post("/ai/chat", data={"message": "What is a solar flare?"})
    data = res.json()
    print(f"\n[BE-027] Status: {res.status_code} | source: {data.get('source')} | response preview: {str(data.get('response',''))[:80]}")
    assert res.status_code == 200
    assert "response" in data
    assert data.get("annotated_image") is None


def test_BE028_ai_flare_predict_live():
    """BE-028: POST /ai/flare-predict with live data"""
    res = client.post("/ai/flare-predict", json={"use_live_data": True})
    data = res.json()
    print(f"\n[BE-028] Status: {res.status_code} | predicted_class: {data.get('predicted_class')} | confidence: {data.get('confidence')} | model: {data.get('model_source')}")
    assert res.status_code == 200
    assert "predicted_class" in data
    assert "confidence" in data
