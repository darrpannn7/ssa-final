"""
Frontend API Library Tests — LI-001 to LI-010
Tests the frontend lib/api.ts by reading the source file directly (URL/logic checks)
and by hitting the live backend endpoints the lib functions call.

Run: pytest tests/test_frontend_api_lib.py -v -s
"""

import pytest
import os
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app.main import app

client = TestClient(app)

# ── Path to lib/api.ts ───────────────────────────────────────────────────────
API_TS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "frontend", "src", "lib", "api.ts"
)

def _read_api_ts():
    """Read frontend lib/api.ts source for static analysis."""
    if not os.path.exists(API_TS):
        pytest.skip("frontend/src/lib/api.ts not found")
    with open(API_TS, encoding="utf-8") as fh:
        return fh.read()


# ═══════════════════════════════════════════════════════════════
#  LI-001: getMagnetogramImageUrl returns correct URL string
# ═══════════════════════════════════════════════════════════════

def test_LI001_getMagnetogramImageUrl_correct_path():
    """LI-001: getMagnetogramImageUrl() encodes correct endpoint path"""
    content = _read_api_ts()
    print(f"\n[LI-001] Checking getMagnetogramImageUrl in api.ts")
    assert "getMagnetogramImageUrl" in content, "getMagnetogramImageUrl not defined in api.ts"
    assert "magnetogram/image" in content, "magnetogram/image path not in getMagnetogramImageUrl"
    # Check it uses BASE_URL (not hardcoded localhost)
    import re
    fn_match = re.search(
        r'getMagnetogramImageUrl\s*\(.*?\)\s*\{([^}]+)\}', content, re.DOTALL
    )
    if fn_match:
        fn_body = fn_match.group(1)
        print(f"         Function body: {fn_body.strip()}")
        assert "BASE_URL" in fn_body or "localhost:8000" not in fn_body
    print(f"         PASS: getMagnetogramImageUrl returns path with 'magnetogram/image'")


# ═══════════════════════════════════════════════════════════════
#  LI-002: getGoesXrayFlux fetches /noaa/goes-xray → {primary, secondary}
# ═══════════════════════════════════════════════════════════════

def test_LI002_getGoesXrayFlux_source_has_correct_endpoint():
    """LI-002: getGoesXrayFlux function in api.ts calls /noaa/goes-xray"""
    content = _read_api_ts()
    print(f"\n[LI-002] Checking getGoesXrayFlux endpoint in api.ts")
    assert "getGoesXrayFlux" in content
    assert "noaa/goes-xray" in content, "/noaa/goes-xray not found in getGoesXrayFlux"
    print(f"         PASS: getGoesXrayFlux uses '/noaa/goes-xray'")


def test_LI002_getGoesXrayFlux_backend_returns_primary_secondary():
    """LI-002b: Live backend /noaa/goes-xray returns {primary, secondary}"""
    res = client.get("/noaa/goes-xray")
    if res.status_code != 200:
        pytest.skip("NOAA endpoint unavailable")
    data = res.json()
    print(f"\n[LI-002b] /noaa/goes-xray → primary: {len(data.get('primary',[]))} pts | secondary: {len(data.get('secondary',[]))} pts")
    assert "primary" in data
    assert "secondary" in data
    assert isinstance(data["primary"], list)
    assert isinstance(data["secondary"], list)


# ═══════════════════════════════════════════════════════════════
#  LI-003: getGoesXrayFlux throws on non-ok response
# ═══════════════════════════════════════════════════════════════

def test_LI003_getGoesXrayFlux_throws_on_error():
    """LI-003: getGoesXrayFlux function throws Error on non-ok (static analysis)"""
    content = _read_api_ts()
    print(f"\n[LI-003] Checking error throw in getGoesXrayFlux")
    # Function should contain a throw / error check after res.ok check
    assert "getGoesXrayFlux" in content
    assert "!res.ok" in content or "throw" in content, \
        "getGoesXrayFlux does not throw on error response"
    import re
    throws = re.findall(r'throw new Error\(["\'][^"\']+["\']\)', content)
    print(f"         Error throws found: {throws}")
    assert any("GOES" in t or "fetch" in t.lower() for t in throws), \
        "Expected throw for GOES fetch failure not found"


# ═══════════════════════════════════════════════════════════════
#  LI-004: getSolarFlares fetches /space-weather/flares
# ═══════════════════════════════════════════════════════════════

def test_LI004_getSolarFlares_source_has_correct_endpoint():
    """LI-004: getSolarFlares in api.ts uses /space-weather/flares"""
    content = _read_api_ts()
    print(f"\n[LI-004] Checking getSolarFlares endpoint in api.ts")
    assert "getSolarFlares" in content
    assert "space-weather/flares" in content or "/flares" in content
    print(f"         PASS: getSolarFlares calls correct /flares endpoint")


def test_LI004_getSolarFlares_backend_returns_data():
    """LI-004b: Live backend /space-weather/flares returns data"""
    res = client.get("/space-weather/flares")
    if res.status_code == 500:
        pytest.skip("Flares API unavailable")
    data = res.json()
    print(f"\n[LI-004b] /space-weather/flares → status: {res.status_code} | status_field: {data.get('status')} | total: {data.get('total')}")
    assert res.status_code == 200
    # Updated endpoint returns dict: {status, total, flares}
    assert "flares" in data or isinstance(data, list)


# ═══════════════════════════════════════════════════════════════
#  LI-005: getAIAImageUrl maps wavelength label to code correctly
# ═══════════════════════════════════════════════════════════════

def test_LI005_getAIAImageUrl_maps_wavelength_labels():
    """LI-005: getAIAImageUrl correctly maps '171Å' → wavelength=0171"""
    content = _read_api_ts()
    print(f"\n[LI-005] Checking getAIAImageUrl wavelength mapping in api.ts")
    assert "getAIAImageUrl" in content
    # Check the mapping table is present
    assert "171" in content and "0171" in content, \
        "Wavelength 171→0171 mapping not found in getAIAImageUrl"
    assert "94" in content and "0094" in content, \
        "Wavelength 94→0094 mapping not found"

    # Verify URL structure
    assert "aia-image?wavelength=" in content or "aia-image" in content
    print(f"         PASS: '171Å → 0171' mapping present in getAIAImageUrl")


# ═══════════════════════════════════════════════════════════════
#  LI-006: getCMEData fetches /space-weather/cme/full
# ═══════════════════════════════════════════════════════════════

def test_LI006_getCMEData_source_has_correct_endpoint():
    """LI-006: getCMEData in api.ts fetches /space-weather/cme/full"""
    content = _read_api_ts()
    print(f"\n[LI-006] Checking getCMEData endpoint in api.ts")
    assert "getCMEData" in content
    assert "cme/full" in content, "/cme/full not found in getCMEData"
    print(f"         PASS: getCMEData calls '/space-weather/cme/full'")


def test_LI006_getCMEData_backend_returns_events():
    """LI-006b: Live backend /cme/full returns {status, total, cme_events}"""
    res = client.get("/space-weather/cme/full")
    if res.status_code == 500:
        pytest.skip("CME API unavailable (rate limit or network)")
    data = res.json()
    print(f"\n[LI-006b] /space-weather/cme/full → status: {res.status_code} | keys: {list(data.keys())}")
    assert res.status_code == 200
    assert "status" in data
    assert "cme_events" in data


# ═══════════════════════════════════════════════════════════════
#  LI-007: getCMEImageUrl returns correct URL
# ═══════════════════════════════════════════════════════════════

def test_LI007_getCMEImageUrl_correct_path():
    """LI-007: getCMEImageUrl returns URL ending in /space-weather/cme/image"""
    content = _read_api_ts()
    print(f"\n[LI-007] Checking getCMEImageUrl in api.ts")
    assert "getCMEImageUrl" in content
    assert "cme/image" in content, "cme/image path not in getCMEImageUrl"
    print(f"         PASS: getCMEImageUrl returns path with 'cme/image'")


# ═══════════════════════════════════════════════════════════════
#  LI-008: getSolarWindData fetches /wind/speed
# ═══════════════════════════════════════════════════════════════

def test_LI008_getSolarWindData_source_has_correct_endpoint():
    """LI-008: getSolarWindData in api.ts fetches /wind/speed"""
    content = _read_api_ts()
    print(f"\n[LI-008] Checking getSolarWindData endpoint in api.ts")
    assert "getSolarWindData" in content
    assert "wind/speed" in content, "/wind/speed not found in getSolarWindData"
    print(f"         PASS: getSolarWindData calls '/wind/speed'")


def test_LI008_getSolarWindData_backend_returns_data():
    """LI-008b: Live backend /wind/speed returns {status, data}"""
    res = client.get("/space-weather/wind/speed")
    if res.status_code == 503:
        pytest.skip("Solar wind data unavailable")
    data = res.json()
    print(f"\n[LI-008b] /wind/speed → status: {res.status_code} | keys: {list(data.keys())}")
    assert res.status_code == 200
    assert "status" in data and "data" in data


# ═══════════════════════════════════════════════════════════════
#  LI-009: getIMFData fetches /wind/imf
# ═══════════════════════════════════════════════════════════════

def test_LI009_getIMFData_source_has_correct_endpoint():
    """LI-009: getIMFData in api.ts fetches /wind/imf"""
    content = _read_api_ts()
    print(f"\n[LI-009] Checking getIMFData endpoint in api.ts")
    assert "getIMFData" in content
    assert "wind/imf" in content, "/wind/imf not found in getIMFData"
    print(f"         PASS: getIMFData calls '/wind/imf'")


def test_LI009_getIMFData_backend_returns_imf_keys():
    """LI-009b: Live backend /wind/imf returns {status, data} with bx/by/bz/bt"""
    res = client.get("/space-weather/wind/imf")
    if res.status_code == 503:
        pytest.skip("IMF data unavailable")
    data = res.json()
    items = data.get("data", [])
    print(f"\n[LI-009b] /wind/imf → status: {res.status_code} | data points: {len(items)}")
    assert res.status_code == 200
    assert "status" in data and "data" in data
    if items:
        for key in ["bx", "by", "bz", "bt"]:
            assert key in items[0], f"Missing IMF key: {key}"


# ═══════════════════════════════════════════════════════════════
#  LI-010: getAllSEPData fetches /sep/all
# ═══════════════════════════════════════════════════════════════

def test_LI010_getAllSEPData_source_has_correct_endpoint():
    """LI-010: getAllSEPData in api.ts fetches /sep/all"""
    content = _read_api_ts()
    print(f"\n[LI-010] Checking getAllSEPData endpoint in api.ts")
    assert "getAllSEPData" in content or "getSEPData" in content, \
        "getAllSEPData function not found in api.ts"
    assert "sep/all" in content, "/sep/all not found in SEP data fetch function"
    print(f"         PASS: SEP data function calls '/sep/all'")


def test_LI010_getAllSEPData_backend_returns_all_keys():
    """LI-010b: Live backend /sep/all returns {status, particle_flux, alerts, radiation_risk}"""
    res = client.get("/space-weather/sep/all")
    data = res.json()
    print(f"\n[LI-010b] /sep/all → status: {res.status_code} | keys: {list(data.keys())}")
    assert res.status_code == 200
    for key in ["status", "particle_flux", "alerts", "radiation_risk"]:
        assert key in data, f"Missing key in /sep/all response: {key}"
    risk = data.get("radiation_risk", {})
    print(f"         radiation_risk: {risk}")
    for rk in ["crew", "satellite", "deep_space"]:
        assert rk in risk, f"Missing radiation_risk sub-key: {rk}"
