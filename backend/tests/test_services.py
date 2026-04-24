"""
Services Unit Tests — SunPy, CME, SEP, Solar Wind, NOAA
Run: pytest tests/test_services.py -v -s
The -s flag prints actual output → copy into Excel "Actual Result" column
"""

import pytest
import numpy as np
from unittest.mock import MagicMock
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


# ═══════════════════════════════════════════════════════════════
#  SUNPY PROCESSOR
# ═══════════════════════════════════════════════════════════════

from app.services.sunpy_processor import SunPyProcessor
sp = SunPyProcessor()

def _sample_data(size=64):
    rng = np.random.default_rng(0)
    return rng.uniform(-150, 150, (size, size)).tolist()


def test_SP007_returns_three_keys():
    """SP-007: analyze_magnetogram returns mean_field, gradient_strength, polarity_mix"""
    result = sp.analyze_magnetogram(_sample_data())
    print(f"\n[SP-007] analyze_magnetogram result: {result}")
    assert "mean_field" in result
    assert "gradient_strength" in result
    assert "polarity_mix" in result


def test_SP007_mean_field_non_negative():
    """SP-007: mean_field >= 0"""
    result = sp.analyze_magnetogram(_sample_data())
    print(f"\n[SP-007b] mean_field: {result['mean_field']} (must be >= 0)")
    assert result["mean_field"] >= 0


def test_SP008_polarity_mix_in_range():
    """SP-008: polarity_mix in [0, 1]"""
    result = sp.analyze_magnetogram(_sample_data())
    print(f"\n[SP-008] polarity_mix: {result['polarity_mix']} (must be in [0,1])")
    assert 0 <= result["polarity_mix"] <= 1


def test_SP009_high_strength_high_x_prob():
    """SP-009: High strength + area returns high X probability"""
    result = sp.calculate_flare_probability(150, 3000)
    print(f"\n[SP-009] calc_flare_probability(150, 3000): {result}")
    assert result["X"] >= 15


def test_SP010_low_strength_high_ab_prob():
    """SP-010: Low strength + area returns high A/B probability"""
    result = sp.calculate_flare_probability(10, 50)
    print(f"\n[SP-010] calc_flare_probability(10, 50): {result} | A+B={result['A']+result['B']}")
    assert result["A"] + result["B"] >= 70


def test_SP011_probabilities_sum_to_100_high():
    """SP-011a: Probabilities sum to 100 (high input)"""
    result = sp.calculate_flare_probability(150, 3000)
    total = sum(result.values())
    print(f"\n[SP-011a] calc_flare_probability(150,3000): {result} | Sum={total}")
    assert total == 100


def test_SP011_probabilities_sum_to_100_medium():
    """SP-011b: Probabilities sum to 100 (medium input)"""
    result = sp.calculate_flare_probability(80, 1000)
    total = sum(result.values())
    print(f"\n[SP-011b] calc_flare_probability(80,1000): {result} | Sum={total}")
    assert total == 100


def test_SP011_probabilities_sum_to_100_low():
    """SP-011c: Probabilities sum to 100 (low input)"""
    result = sp.calculate_flare_probability(10, 50)
    total = sum(result.values())
    print(f"\n[SP-011c] calc_flare_probability(10,50): {result} | Sum={total}")
    assert total == 100


def test_SP012_returns_at_most_8_regions():
    """SP-012: detect_active_regions returns ≤ 8 regions"""
    data = _sample_data(512)
    regions = sp.detect_active_regions(data)
    print(f"\n[SP-012] detect_active_regions → {len(regions)} regions found")
    for r in regions:
        print(f"         Region {r['id']}: strength={r['strength']}, area={r['area']}, bbox={r['bbox']}")
    assert len(regions) <= 8


def test_SP012_regions_have_required_keys():
    """SP-012b: Each region has id, bbox, strength, area, flare"""
    data = _sample_data(512)
    regions = sp.detect_active_regions(data)
    for r in regions:
        for key in ["id", "bbox", "strength", "area", "flare"]:
            assert key in r, f"Missing key '{key}' in region {r}"
    print(f"\n[SP-012b] All {len(regions)} regions have correct keys")


# ═══════════════════════════════════════════════════════════════
#  CME PROCESSOR
# ═══════════════════════════════════════════════════════════════

from app.services.cme_processor import CMEProcessor
cme = CMEProcessor()


def test_CM005_halo_high_speed_returns_high():
    """CM-005: Halo + speed>1500 + lon in [-30,30] = High"""
    result = cme.calculate_impact_probability(1600, 10, "halo")
    print(f"\n[CM-005] calc_impact_probability(1600, 10, 'halo') = '{result}'")
    assert result == "High"


def test_CM006_slow_far_returns_low():
    """CM-006: speed<400 + lon>30 = Low"""
    result = cme.calculate_impact_probability(300, 60, "S")
    print(f"\n[CM-006] calc_impact_probability(300, 60, 'S') = '{result}'")
    assert result == "Low"


def test_CM007_medium_returns_moderate():
    """CM-007: speed 800-1500, near-Earth = Moderate"""
    result = cme.calculate_impact_probability(900, 20, "C")
    print(f"\n[CM-007] calc_impact_probability(900, 20, 'C') = '{result}'")
    assert result == "Moderate"


def test_CM008_none_inputs_no_crash():
    """CM-008: None inputs handled without crash"""
    result = cme.calculate_impact_probability(None, None, None)
    print(f"\n[CM-008] calc_impact_probability(None, None, None) = '{result}'")
    assert result in {"Low", "Moderate", "High"}


def test_CM_all_combinations_valid():
    """CM-extra: Various inputs always return valid value"""
    cases = [(2000, 5, "halo"), (500, 45, "S"), (1000, -15, "C"), (None, 25, "halo")]
    for speed, lon, ctype in cases:
        result = cme.calculate_impact_probability(speed, lon, ctype)
        print(f"\n[CM-extra] ({speed}, {lon}, '{ctype}') → '{result}'")
        assert result in {"Low", "Moderate", "High"}


# ═══════════════════════════════════════════════════════════════
#  SEP SERVICE
# ═══════════════════════════════════════════════════════════════

from app.services.sep_service import SEPFetcher

def _mock_resp(data):
    r = MagicMock()
    r.raise_for_status = MagicMock()
    r.json.return_value = data
    return r

def _flux_list(avg, n=10):
    return [{"flux": avg, "energy": ">=10 MeV"} for _ in range(n)]


def test_SE001_valid_proton_flux_parsed():
    """SE-001: Valid proton flux response parsed correctly"""
    data = [
        {"time_tag": "2026-04-16T00:00Z", "flux": 1.5, "energy": ">=10 MeV", "satellite": 16},
        {"time_tag": "2026-04-16T01:00Z", "flux": 2.0, "energy": ">=10 MeV", "satellite": 16},
    ]
    result = SEPFetcher._process_proton_flux(_mock_resp(data))
    print(f"\n[SE-001] _process_proton_flux → {len(result)} items | first: {result[0]}")
    assert len(result) == 2
    assert result[0]["flux"] == 1.5


def test_SE002_exception_returns_empty():
    """SE-002: Exception → []"""
    result = SEPFetcher._process_proton_flux(Exception("network error"))
    print(f"\n[SE-002] _process_proton_flux(Exception) → {result}")
    assert result == []


def test_SE003_at_most_300_items():
    """SE-003: Returns ≤ 300 items"""
    data = [{"time_tag": f"T{i}", "flux": 1.0, "energy": ">=10 MeV", "satellite": 16} for i in range(400)]
    result = SEPFetcher._process_proton_flux(_mock_resp(data))
    print(f"\n[SE-003] 400 input rows → {len(result)} returned (must be ≤ 300)")
    assert len(result) <= 300


def test_SE004_filters_sep_keywords():
    """SE-004: Only SEP-keyword alerts pass filter"""
    alerts = [
        {"product_id": "ALTEF3", "issue_datetime": "2026-04-16T00:00Z", "message": "PROTON event detected"},
        {"product_id": "FXME08", "issue_datetime": "2026-04-16T00:00Z", "message": "X-ray flux nominal"},
        {"product_id": "WATA20", "issue_datetime": "2026-04-16T00:00Z", "message": "RADIATION WARNING"},
    ]
    result = SEPFetcher._process_alerts(_mock_resp(alerts))
    ids = [a["product_id"] for a in result["alerts"]]
    print(f"\n[SE-004] Input: 3 alerts | Filtered: {ids} | risk_level: {result['risk_level']}")
    assert "ALTEF3" in ids
    assert "WATA20" in ids
    assert "FXME08" not in ids


def test_SE005_wa_product_severe():
    """SE-005: WA product_id → risk_level = severe"""
    alerts = [{"product_id": "WATA20", "issue_datetime": "2026-04-16T00:00Z", "message": "RADIATION WARNING issued"}]
    result = SEPFetcher._process_alerts(_mock_resp(alerts))
    print(f"\n[SE-005] WA product_id → risk_level: '{result['risk_level']}'")
    assert result["risk_level"] == "severe"


def test_SE006_empty_alerts_quiet():
    """SE-006: No alerts → risk_level quiet"""
    result = SEPFetcher._process_alerts(_mock_resp([]))
    print(f"\n[SE-006] Empty alerts → risk_level: '{result['risk_level']}' | alerts: {result['alerts']}")
    assert result["risk_level"] == "quiet"
    assert result["alerts"] == []


def test_SE007_message_truncated_300():
    """SE-007: Long message truncated to 300 chars"""
    long_msg = "PROTON " + "x" * 1000
    alerts = [{"product_id": "ALTEF3", "issue_datetime": "2026-04-16T00:00Z", "message": long_msg}]
    result = SEPFetcher._process_alerts(_mock_resp(alerts))
    for a in result["alerts"]:
        print(f"\n[SE-007] Message length: {len(a['message'])} (must be ≤ 300) | preview: {a['message'][:40]}...")
        assert len(a["message"]) <= 300


def test_SE008_high_flux_severe():
    """SE-008: avg_flux > 1000 → crew=severe"""
    result = SEPFetcher._calculate_radiation_risk(_flux_list(1500))
    print(f"\n[SE-008] _calculate_radiation_risk(avg=1500) → {result}")
    assert result["crew"] == "severe"
    assert result["satellite"] == "high"
    assert result["deep_space"] == "extreme"


def test_SE009_medium_flux_moderate():
    """SE-009: avg_flux 10-100 → crew=moderate"""
    result = SEPFetcher._calculate_radiation_risk(_flux_list(50))
    print(f"\n[SE-009] _calculate_radiation_risk(avg=50) → {result}")
    assert result["crew"] == "moderate"


def test_SE010_empty_list_low_risk():
    """SE-010: Empty list → crew=low"""
    result = SEPFetcher._calculate_radiation_risk([])
    print(f"\n[SE-010] _calculate_radiation_risk([]) → {result}")
    assert result["crew"] == "low"
    assert result["satellite"] == "low"


# ═══════════════════════════════════════════════════════════════
#  SOLAR WIND SERVICE
# ═══════════════════════════════════════════════════════════════

from app.services.solar_wind_service import SolarWindFetcher

def _wind_resp(rows):
    headers = ["time_tag", "density", "speed", "temperature"]
    r = MagicMock(); r.raise_for_status = MagicMock()
    r.json.return_value = [headers] + rows
    return r

def _imf_resp(rows):
    headers = ["time_tag", "bx_gsm", "by_gsm", "bz_gsm", "lon_gsm", "lat_gsm", "bt"]
    r = MagicMock(); r.raise_for_status = MagicMock()
    r.json.return_value = [headers] + rows
    return r


def test_SW001_valid_wind_parsed():
    """SW-001: Valid solar wind response parsed to list"""
    rows = [
        ["2026-04-16 00:00:00.000", "5.5", "430.2", "85000"],
        ["2026-04-16 00:01:00.000", "6.0", "435.0", "90000"],
    ]
    result = SolarWindFetcher._process_solar_wind(_wind_resp(rows))
    print(f"\n[SW-001] _process_solar_wind → {len(result)} items | first: {result[0]}")
    assert len(result) == 2
    assert result[0]["speed"] == 430.2
    assert result[0]["density"] == 5.5


def test_SW002_wind_exception_returns_empty():
    """SW-002: Exception → []"""
    result = SolarWindFetcher._process_solar_wind(Exception("timeout"))
    print(f"\n[SW-002] _process_solar_wind(Exception) → {result}")
    assert result == []


def test_SW003_malformed_row_skipped():
    """SW-003: Malformed row skipped, valid row kept"""
    rows = [
        ["2026-04-16 00:00:00.000", "5.5", "INVALID", "85000"],
        ["2026-04-16 00:01:00.000", "6.0", "435.0",   "90000"],
    ]
    result = SolarWindFetcher._process_solar_wind(_wind_resp(rows))
    print(f"\n[SW-003] 2 rows (1 bad) → {len(result)} valid rows | valid: {result}")
    assert len(result) == 1
    assert result[0]["speed"] == 435.0


def test_SW004_returns_at_most_200():
    """SW-004: Returns ≤ 200 data points"""
    rows = [[f"2026-04-16 {i:05d}:00.000", "5.0", "430.0", "80000"] for i in range(300)]
    result = SolarWindFetcher._process_solar_wind(_wind_resp(rows))
    print(f"\n[SW-004] 300 input rows → {len(result)} returned (must be ≤ 200)")
    assert len(result) <= 200


def test_SW005_valid_imf_parsed():
    """SW-005: Valid IMF response parsed with bx, by, bz, bt"""
    rows = [["2026-04-16 00:00:00.000", "-2.1", "3.5", "-5.0", "10.0", "-5.0", "6.7"]]
    result = SolarWindFetcher._process_imf(_imf_resp(rows))
    print(f"\n[SW-005] _process_imf → {len(result)} items | first: {result[0]}")
    assert result[0]["bz"] == -5.0
    assert result[0]["bx"] == -2.1
    assert "bt" in result[0]


def test_SW006_imf_exception_returns_empty():
    """SW-006: IMF Exception → []"""
    result = SolarWindFetcher._process_imf(Exception("timeout"))
    print(f"\n[SW-006] _process_imf(Exception) → {result}")
    assert result == []


# ═══════════════════════════════════════════════════════════════
#  NOAA SERVICE
# ═══════════════════════════════════════════════════════════════

from app.services.noaa_service import NOAAFetcher

def _noaa_resp(data):
    r = MagicMock()
    r.json.return_value = data
    return r


def test_NO002_filters_to_0108nm():
    """NO-002: Only 0.1-0.8nm channel rows returned"""
    data = [
        {"energy": "0.1-0.8nm",  "observed_flux": 1.2e-8, "time_tag": "2026-04-16T00:00Z", "flux": 1.2e-8},
        {"energy": "0.05-0.4nm", "observed_flux": 5e-9,   "time_tag": "2026-04-16T00:00Z", "flux": 5e-9},
    ]
    result = NOAAFetcher._process(_noaa_resp(data))
    print(f"\n[NO-002] 2 rows (mixed energy) → {len(result)} rows with 0.1-0.8nm: {result}")
    assert len(result) == 1


def test_NO003_flux_values_positive():
    """NO-003: Non-positive flux filtered out"""
    data = [
        {"energy": "0.1-0.8nm", "observed_flux": 1.2e-8, "time_tag": "T1", "flux": 1.2e-8},
        {"energy": "0.1-0.8nm", "observed_flux": 0,      "time_tag": "T2", "flux": 0},
    ]
    result = NOAAFetcher._process(_noaa_resp(data))
    print(f"\n[NO-003] 2 rows (1 zero flux) → {len(result)} positive-flux rows: {result}")
    for item in result:
        assert item["flux"] > 0


def test_NO004_max_200_items():
    """NO-004: Returns ≤ 200 data points"""
    data = [
        {"energy": "0.1-0.8nm", "observed_flux": 1e-8, "time_tag": f"T{i}", "flux": 1e-8}
        for i in range(300)
    ]
    result = NOAAFetcher._process(_noaa_resp(data))
    print(f"\n[NO-004] 300 input rows → {len(result)} returned (must be ≤ 200)")
    assert len(result) <= 200


def test_NO005_exception_returns_empty():
    """NO-005: Exception → []"""
    result = NOAAFetcher._process(Exception("network error"))
    print(f"\n[NO-005] _process(Exception) → {result}")
    assert result == []


def test_NO006_both_outages_return_empty():
    """NO-006: Both primary and secondary channel outages each return empty list"""
    result_primary = NOAAFetcher._process(Exception("primary down"))
    result_secondary = NOAAFetcher._process(Exception("secondary down"))
    print(f"\n[NO-006] primary outage → {result_primary} | secondary outage → {result_secondary}")
    assert result_primary == []
    assert result_secondary == []


def test_NO007_items_have_time_tag_and_flux():
    """NO-007: Items have time_tag and flux keys"""
    data = [{"energy": "0.1-0.8nm", "observed_flux": 1.2e-8, "time_tag": "2026-04-16T00:00Z", "flux": 1.2e-8}]
    result = NOAAFetcher._process(_noaa_resp(data))
    print(f"\n[NO-007] Item keys: {list(result[0].keys())}")
    assert "time_tag" in result[0]
    assert "flux" in result[0]
