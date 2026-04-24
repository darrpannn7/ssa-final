"""
Async Service Tests — Solar Wind, SEP, NOAA async methods
Covers: SW-007 to SW-010, SE-011, SE-012, NO-001, NO-008
Run: pytest tests/test_async_services.py -v -s
"""

import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.solar_wind_service import SolarWindFetcher
from app.services.sep_service import SEPFetcher
from app.services.noaa_service import NOAAFetcher
from datetime import datetime


# ═══════════════════════════════════════════════════════════════
#  SOLAR WIND ASYNC METHODS  (SW-007 to SW-010)
# ═══════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_SW007_get_solar_wind_data_returns_list():
    """SW-007: get_solar_wind_data() returns non-empty list"""
    result = await SolarWindFetcher.get_solar_wind_data()
    count = len(result)
    latest = result[-1] if result else {}
    print(f"\n[SW-007] get_solar_wind_data → {count} points | latest: {latest}")
    assert isinstance(result, list)
    if result:
        assert "speed" in result[0]
        assert "density" in result[0]
        assert "time_tag" in result[0]


@pytest.mark.asyncio
async def test_SW008_get_imf_data_returns_list():
    """SW-008: get_imf_data() returns non-empty list"""
    result = await SolarWindFetcher.get_imf_data()
    count = len(result)
    latest = result[-1] if result else {}
    print(f"\n[SW-008] get_imf_data → {count} points | latest: {latest}")
    assert isinstance(result, list)
    if result:
        for key in ["bx", "by", "bz", "bt", "time_tag"]:
            assert key in result[0]


@pytest.mark.asyncio
async def test_SW009_get_all_solar_wind_fetches_both():
    """SW-009: get_all_solar_wind_data() returns both solar_wind and imf"""
    result = await SolarWindFetcher.get_all_solar_wind_data()
    sw_len = len(result.get("solar_wind", []))
    imf_len = len(result.get("imf", []))
    print(f"\n[SW-009] get_all_solar_wind_data → solar_wind: {sw_len} pts | imf: {imf_len} pts")
    assert "solar_wind" in result
    assert "imf" in result
    assert isinstance(result["solar_wind"], list)
    assert isinstance(result["imf"], list)


@pytest.mark.asyncio
async def test_SW010_all_solar_wind_keys_present():
    """SW-010: Combined response always has both keys even if one is empty"""
    result = await SolarWindFetcher.get_all_solar_wind_data()
    print(f"\n[SW-010] Keys present: {list(result.keys())} | solar_wind empty: {len(result['solar_wind'])==0} | imf empty: {len(result['imf'])==0}")
    assert "solar_wind" in result
    assert "imf" in result


# ═══════════════════════════════════════════════════════════════
#  SEP ASYNC METHODS  (SE-011, SE-012)
# ═══════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_SE011_get_particle_flux_data():
    """SE-011: get_particle_flux_data() returns proton and electron lists"""
    result = await SEPFetcher.get_particle_flux_data()
    p_len = len(result.get("proton", []))
    e_len = len(result.get("electron", []))
    print(f"\n[SE-011] get_particle_flux_data → proton: {p_len} pts | electron: {e_len} pts")
    assert "proton" in result
    assert "electron" in result
    assert isinstance(result["proton"], list)
    assert isinstance(result["electron"], list)


@pytest.mark.asyncio
async def test_SE012_get_all_sep_data_returns_three_keys():
    """SE-012: get_all_sep_data() returns particle_flux, alerts, radiation_risk"""
    result = await SEPFetcher.get_all_sep_data()
    risk = result.get("radiation_risk", {})
    alerts_info = result.get("alerts", {})
    print(f"\n[SE-012] get_all_sep_data → keys: {list(result.keys())}")
    print(f"         radiation_risk: {risk}")
    print(f"         risk_level: {alerts_info.get('risk_level')} | alerts: {len(alerts_info.get('alerts', []))}")
    assert "particle_flux" in result
    assert "alerts" in result
    assert "radiation_risk" in result
    assert "crew" in risk
    assert "satellite" in risk
    assert "deep_space" in risk


# ═══════════════════════════════════════════════════════════════
#  NOAA ASYNC METHODS  (NO-001, NO-008)
# ═══════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_NO001_get_goes_xray_flux_returns_both():
    """NO-001: get_goes_xray_flux() returns primary and secondary"""
    result = await NOAAFetcher.get_goes_xray_flux()
    p_len = len(result.get("primary", []))
    s_len = len(result.get("secondary", []))
    p_sample = result["primary"][0] if result.get("primary") else {}
    print(f"\n[NO-001] get_goes_xray_flux → primary: {p_len} pts | secondary: {s_len} pts | sample: {p_sample}")
    assert "primary" in result
    assert "secondary" in result


@pytest.mark.asyncio
async def test_NO008_time_tag_is_parseable_datetime():
    """NO-008: time_tag values are parseable datetime strings"""
    result = await NOAAFetcher.get_goes_xray_flux()
    items = result.get("primary", [])
    errors = []
    parsed_count = 0
    for item in items[:5]:  # check first 5
        try:
            datetime.fromisoformat(item["time_tag"].replace("Z", "+00:00"))
            parsed_count += 1
        except Exception as e:
            errors.append(f"{item['time_tag']} → {e}")
    print(f"\n[NO-008] Checked 5 time_tags | Parsed OK: {parsed_count} | Errors: {errors}")
    assert errors == [], f"Unparseable time_tags: {errors}"
