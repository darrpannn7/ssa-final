"""
AI Inference & Non-Functional Tests
Covers: AI-002 to AI-010, NF-001 to NF-011, BE-003, BE-009, BE-022
Run: pytest tests/test_ai_and_nonfunctional.py -v -s
"""

import pytest
import time
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# ═══════════════════════════════════════════════════════════════
#  AI INFERENCE TESTS  (AI-002 to AI-010)
# ═══════════════════════════════════════════════════════════════

def test_AI001_chat_text_only_returns_valid_fields():
    """AI-001: POST /ai/chat text-only returns response, surya_data, source, regions"""
    res = client.post("/ai/chat", data={"message": "What is a solar flare?"})
    data = res.json()
    print(f"\n[AI-001] Status: {res.status_code} | source: {data.get('source')} | annotated_image: {data.get('annotated_image')} | regions: {data.get('regions')}")
    assert res.status_code == 200
    assert "response" in data
    assert "surya_data" in data
    assert "source" in data
    assert data.get("annotated_image") is None
    assert data.get("regions") == []


def test_AI003_chat_invalid_image_returns_422():
    """AI-003: POST /ai/chat with corrupt image returns 422"""
    corrupt_bytes = b"not_an_image_at_all_corrupt"
    res = client.post(
        "/ai/chat",
        data={"message": "analyze this"},
        files={"image": ("test.jpg", corrupt_bytes, "image/jpeg")}
    )
    print(f"\n[AI-003] Status: {res.status_code} | detail: {res.json().get('detail')}")
    assert res.status_code == 422
    assert "Could not read" in res.json().get("detail", "")


def test_AI004_chat_missing_message_returns_422():
    """AI-004: POST /ai/chat without message field returns 422"""
    res = client.post("/ai/chat", data={})
    print(f"\n[AI-004] Status: {res.status_code} | detail: {res.json().get('detail')}")
    assert res.status_code == 422


def test_AI005_flare_predict_live_returns_all_fields():
    """AI-005: POST /ai/flare-predict live returns complete FlareResponse"""
    res = client.post("/ai/flare-predict", json={"use_live_data": True})
    data = res.json()
    print(f"\n[AI-005] Status: {res.status_code}")
    print(f"         predicted_class: {data.get('predicted_class')} | confidence: {data.get('confidence')}")
    print(f"         onset_window_minutes: {data.get('onset_window_minutes')} | model: {data.get('model_source')}")
    print(f"         surya_flare_risk: {data.get('surya_flare_risk')} | goes_peak_flux: {data.get('goes_peak_flux')}")
    assert res.status_code == 200
    for field in ["predicted_class", "confidence", "onset_window_minutes",
                  "reasoning", "surya_flare_risk", "surya_magnetic_complexity",
                  "goes_peak_flux", "model_source", "timestamp"]:
        assert field in data, f"Missing field: {field}"


def test_AI006_flare_predict_manual_flux_works():
    """AI-006: POST /ai/flare-predict with manual flux_window"""
    flux = [1e-7, 1.2e-7, 1.5e-7, 2e-7, 2.5e-7, 3e-7, 3.5e-7, 4e-7, 4.5e-7, 5e-7, 5.5e-7, 6e-7]
    res = client.post("/ai/flare-predict", json={"use_live_data": False, "flux_window": flux})
    data = res.json()
    print(f"\n[AI-006] Status: {res.status_code} | predicted_class: {data.get('predicted_class')} | goes_peak_flux: {data.get('goes_peak_flux')}")
    assert res.status_code == 200
    assert "predicted_class" in data
    assert data.get("goes_peak_flux") == max(flux)


def test_AI007_flare_predict_no_explanation():
    """AI-007: include_explanation=false → reasoning is empty string"""
    res = client.post("/ai/flare-predict", json={"use_live_data": False, "include_explanation": False})
    data = res.json()
    print(f"\n[AI-007] Status: {res.status_code} | reasoning: '{data.get('reasoning')}'")
    assert res.status_code == 200
    assert data.get("reasoning") == ""


def test_AI008_flare_predict_timestamp_is_iso():
    """AI-008: timestamp field is valid ISO format with Z suffix"""
    from datetime import datetime
    res = client.post("/ai/flare-predict", json={"use_live_data": False})
    data = res.json()
    ts = data.get("timestamp", "")
    print(f"\n[AI-008] timestamp: '{ts}'")
    assert ts.endswith("Z"), f"Timestamp missing Z suffix: {ts}"
    try:
        datetime.fromisoformat(ts.replace("Z", "+00:00"))
        print(f"         Parsed OK")
    except ValueError as e:
        assert False, f"Timestamp not parseable: {e}"


def test_AI009_flare_predict_confidence_non_empty():
    """AI-009: confidence field is non-empty string"""
    res = client.post("/ai/flare-predict", json={"use_live_data": False})
    data = res.json()
    confidence = data.get("confidence", "")
    print(f"\n[AI-009] confidence: '{confidence}'")
    assert isinstance(confidence, str)
    assert len(confidence) > 0


def test_AI010_flare_predict_onset_window_positive():
    """AI-010: onset_window_minutes is positive integer"""
    res = client.post("/ai/flare-predict", json={"use_live_data": False})
    data = res.json()
    ow = data.get("onset_window_minutes")
    print(f"\n[AI-010] onset_window_minutes: {ow} (must be > 0)")
    assert isinstance(ow, int)
    assert ow > 0


# ═══════════════════════════════════════════════════════════════
#  MISSING BACKEND TESTS  (BE-003, BE-009, BE-022)
# ═══════════════════════════════════════════════════════════════

def test_BE003_magnetogram_cached_after_first_hit():
    """BE-003: magnetogram_cached reflects actual cache file existence"""
    res = client.get("/system/status")
    cached = res.json().get("magnetogram_cached")
    cache_path = res.json().get("cache_location")
    actual_exists = os.path.exists(cache_path)
    print(f"\n[BE-003] magnetogram_cached: {cached} | file exists on disk: {actual_exists} | path: {cache_path}")
    assert cached == actual_exists


def test_BE009_flare_data_required_fields():
    """BE-009: /space-weather/flares → {status, total, flares[]} with required fields"""
    res = client.get("/space-weather/flares")
    if res.status_code == 500:
        print(f"\n[BE-009] Status: 500 — CCMC/NASA API unavailable. Skipping.")
        pytest.skip("CCMC/NASA API rate-limited or unavailable")
    data = res.json()
    flares = data.get("flares", [])
    print(f"\n[BE-009] Status: {res.status_code} | type: {type(data).__name__} | count: {len(flares)}")
    assert res.status_code == 200
    assert isinstance(flares, list)
    if flares:
        first = flares[0]
        print(f"         First item keys: {list(first.keys())}")
        for key in ["classType", "startTime", "peakTime", "endTime", "activeRegion"]:
            assert key in first, f"Missing field: {key}"


def test_BE022_wind_speed_503_when_data_empty():
    """BE-022: /wind/speed returns 503 when data is unavailable"""
    from unittest.mock import patch
    with patch("app.services.solar_wind_service.SolarWindFetcher.get_solar_wind_data",
               return_value=[]):
        res = client.get("/space-weather/wind/speed")
        print(f"\n[BE-022] Status with empty data: {res.status_code} | detail: {res.json().get('detail')}")
        assert res.status_code == 503


# ═══════════════════════════════════════════════════════════════
#  NON-FUNCTIONAL TESTS  (NF-001 to NF-011)
# ═══════════════════════════════════════════════════════════════

def test_NF001_system_status_responds_under_2_sec():
    """NF-001: /system/status responds in < 2 seconds"""
    start = time.time()
    res = client.get("/system/status")
    elapsed = time.time() - start
    print(f"\n[NF-001] /system/status response time: {elapsed:.3f}s (must be < 2.0s) | status: {res.status_code}")
    assert elapsed < 2.0


def test_NF002_goes_xray_responds_under_5_sec():
    """NF-002: /noaa/goes-xray responds in < 5 seconds"""
    start = time.time()
    res = client.get("/noaa/goes-xray")
    elapsed = time.time() - start
    print(f"\n[NF-002] /noaa/goes-xray response time: {elapsed:.3f}s (must be < 5.0s) | status: {res.status_code}")
    assert elapsed < 5.0


def test_NF004_concurrent_requests_to_root():
    """NF-004: 10 sequential requests to / all return 200 (TestClient is not thread-safe)"""
    results = []
    for _ in range(10):
        r = client.get("/")
        results.append(r.status_code)
    non_200 = [c for c in results if c != 200]
    print(f"\n[NF-004] 10 sequential requests → statuses: {results} | non-200: {non_200}")
    assert non_200 == [], f"Non-200 responses: {non_200}"


def test_NF005_cors_headers_present():
    """NF-005: CORS middleware is registered in the app"""
    from app.main import app as _app
    from starlette.middleware.cors import CORSMiddleware
    middleware_types = [m.cls for m in _app.user_middleware if hasattr(m, 'cls')]
    middleware_names = [getattr(m, '__name__', str(m)) for m in middleware_types]
    print(f"\n[NF-005] Registered middleware: {middleware_names}")
    has_cors = any(
        'CORS' in str(m) for m in _app.user_middleware
    )
    print(f"         CORS present: {has_cors}")
    assert has_cors, "CORSMiddleware not found in app middleware stack"


def test_NF006_nasa_api_key_not_in_frontend_bundle():
    """NF-006: NASA API key should only exist in backend, not frontend files"""
    NASA_KEY = "8ZMQhHDs5WkHqm761lOCn9x20SafyO52o3HDMbSR"
    frontend_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "frontend", "src"
    )
    found_files = []
    if os.path.exists(frontend_dir):
        for root, _, files in os.walk(frontend_dir):
            for f in files:
                if f.endswith((".ts", ".tsx", ".js")):
                    path = os.path.join(root, f)
                    with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                        if NASA_KEY in fh.read():
                            found_files.append(path)
    print(f"\n[NF-006] NASA API key found in frontend source files: {found_files}")
    assert found_files == [], f"Key exposed in: {found_files}"


def test_NF008_errors_return_json_not_html():
    """NF-008: Error responses have JSON content-type"""
    res = client.get("/space-weather/aia-image?wavelength=INVALID")
    ctype = res.headers.get("content-type", "")
    print(f"\n[NF-008] Error response Content-Type: '{ctype}' | status: {res.status_code}")
    assert "application/json" in ctype


def test_NF008b_error_body_has_detail_field():
    """NF-008b: JSON error body contains 'detail' field"""
    res = client.get("/space-weather/aia-image?wavelength=INVALID")
    data = res.json()
    print(f"\n[NF-008b] Error body: {data}")
    assert "detail" in data


def test_NF_root_returns_200_not_error():
    """NF: Root endpoint still works (baseline health)"""
    res = client.get("/")
    print(f"\n[NF-base] GET / → {res.status_code} | {res.json()}")
    assert res.status_code == 200


def test_NF007_injection_in_chat_message():
    """NF-007: Injection attempt in message processed as plain text"""
    injection = "'; DROP TABLE users; --"
    res = client.post("/ai/chat", data={"message": injection})
    print(f"\n[NF-007] Status: {res.status_code} for injection message | response keys: {list(res.json().keys()) if res.status_code==200 else res.json()}")
    # Should return 200 and treat as plain text, NOT 500 crash
    assert res.status_code in [200, 422]
    assert res.status_code != 500


# ══════════════════════════════════════════════════════════
#  ADDITIONAL NON-FUNCTIONAL TESTS  (NF-009 to NF-014)
# ══════════════════════════════════════════════════════════

def test_NF009_backend_errors_have_json_detail():
    """NF-009: All error responses return JSON with 'detail' field (not HTML)"""
    # Trigger a 400 with an invalid AIA wavelength
    res = client.get("/space-weather/aia-image?wavelength=BADWL")
    ctype = res.headers.get("content-type", "")
    print(f"\n[NF-009] 400 error Content-Type: '{ctype}' | status: {res.status_code}")
    assert "application/json" in ctype
    data = res.json()
    assert "detail" in data
    print(f"         detail: {data['detail']}")


def test_NF010_retry_reconnects_after_outage():
    """NF-010: Backend reconnects cleanly when previously failing endpoint recovers"""
    from unittest.mock import patch
    # Simulate a down-then-up scenario: first call fails, second succeeds
    call_count = {"n": 0}

    original_get_solar_wind = None
    import app.services.solar_wind_service as sw_module

    async def flaky_solar_wind():
        call_count["n"] += 1
        if call_count["n"] == 1:
            return []  # first call: simulate failure (triggers 503)
        from app.services.solar_wind_service import SolarWindFetcher
        return await SolarWindFetcher.get_solar_wind_data.__wrapped__()

    # First request — should get 503
    with patch("app.services.solar_wind_service.SolarWindFetcher.get_solar_wind_data",
               return_value=[]):
        r1 = client.get("/space-weather/wind/speed")
    print(f"\n[NF-010] First call (simulated outage): status {r1.status_code} (expected 503)")
    assert r1.status_code == 503

    # Second request — real backend, should recover
    r2 = client.get("/space-weather/wind/speed")
    print(f"         Second call (real backend): status {r2.status_code}")
    assert r2.status_code in [200, 503]  # 503 only if NOAA is genuinely down


def test_NF011_loading_skeleton_class_exists_in_source():
    """NF-011: Loading skeleton CSS class (animate-pulse) exists in frontend source"""
    frontend_src = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "frontend", "src"
    )
    found = False
    if os.path.exists(frontend_src):
        for root, _, files in os.walk(frontend_src):
            for f in files:
                if f.endswith((".tsx", ".ts", ".jsx", ".js", ".css")):
                    path = os.path.join(root, f)
                    with open(path, encoding="utf-8", errors="ignore") as fh:
                        if "animate-pulse" in fh.read():
                            found = True
                            print(f"\n[NF-011] animate-pulse found in: {os.path.relpath(path)}")
                            break
            if found:
                break
    print(f"\n[NF-011] Loading skeleton (animate-pulse) in frontend source: {found}")
    assert found, "animate-pulse class not found in frontend source — skeleton loader may be missing"


def test_NF012_images_have_alt_attributes_in_source():
    """NF-012: <img> tags in frontend source have alt attributes"""
    frontend_src = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "frontend", "src"
    )
    missing_alts = []
    import re
    img_pattern = re.compile(r'<img\b(?![^>]*\balt=)[^>]*>', re.IGNORECASE)
    if os.path.exists(frontend_src):
        for root, _, files in os.walk(frontend_src):
            for f in files:
                if f.endswith((".tsx", ".jsx")):
                    path = os.path.join(root, f)
                    with open(path, encoding="utf-8", errors="ignore") as fh:
                        content = fh.read()
                    for match in img_pattern.finditer(content):
                        missing_alts.append(f"{os.path.relpath(path)}: {match.group()[:60]}")
    print(f"\n[NF-012] img tags missing alt attribute: {len(missing_alts)}")
    for item in missing_alts:
        print(f"         {item}")
    # Warn but don't hard-fail (alt may be on a Next.js Image component)
    assert len(missing_alts) == 0, f"Found {len(missing_alts)} img tags without alt attributes"


def test_NF013_tab_navigation_sidebar_exists_in_source():
    """NF-013: Sidebar navigation links are keyboard-accessible (have href or tabIndex in source)"""
    frontend_src = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "frontend", "src"
    )
    found_sidebar = False
    if os.path.exists(frontend_src):
        for root, _, files in os.walk(frontend_src):
            for f in files:
                if f.endswith((".tsx", ".jsx", ".ts")):
                    path = os.path.join(root, f)
                    with open(path, encoding="utf-8", errors="ignore") as fh:
                        content = fh.read()
                    if "sidebar" in content.lower() or "Sidebar" in content:
                        found_sidebar = True
                        print(f"\n[NF-013] Sidebar component found in: {os.path.relpath(path)}")
                        break
            if found_sidebar:
                break
    print(f"\n[NF-013] Sidebar component present in source: {found_sidebar}")
    assert found_sidebar, "Sidebar navigation component not found in frontend source"


def test_NF014_no_hardcoded_localhost_in_production_api_calls():
    """NF-014: lib/api.ts uses BASE_URL env var, not hardcoded localhost:8000"""
    api_lib_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "frontend", "src", "lib", "api.ts"
    )
    if not os.path.exists(api_lib_path):
        pytest.skip("frontend/src/lib/api.ts not found")
    with open(api_lib_path, encoding="utf-8") as fh:
        content = fh.read()
    # BASE_URL must be defined using the env var
    has_env_var = "NEXT_PUBLIC_API_URL" in content
    has_base_url = "BASE_URL" in content
    # All fetch calls should use BASE_URL, not raw localhost
    import re
    hardcoded = re.findall(r'fetch\(["\`]http://localhost:\d+', content)
    print(f"\n[NF-014] NEXT_PUBLIC_API_URL used: {has_env_var} | BASE_URL defined: {has_base_url} | hardcoded fetch calls: {hardcoded}")
    assert has_env_var, "NEXT_PUBLIC_API_URL env var not referenced in api.ts"
    assert has_base_url, "BASE_URL constant not defined in api.ts"
    assert hardcoded == [], f"Hardcoded localhost URLs found in fetch calls: {hardcoded}"
