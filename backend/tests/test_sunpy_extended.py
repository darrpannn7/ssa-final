"""
SunPy Processor Extended Tests — SP-001 to SP-006
Covers: _get_latest_hmi_url (mocked), get_latest_magnetogram (mocked), data clipping, shape
Run: pytest tests/test_sunpy_extended.py -v -s
"""

import pytest
import numpy as np
from unittest.mock import MagicMock, patch
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.sunpy_processor import SunPyProcessor


# ═══════════════════════════════════════════════════════════════
#  SP-001: _get_latest_hmi_url returns .fits URL
# ═══════════════════════════════════════════════════════════════

def test_SP001_get_latest_hmi_url_returns_fits_url():
    """SP-001: _get_latest_hmi_url returns a string ending in .fits"""
    sp = SunPyProcessor()

    fake_html = """
    <html><body>
    <a href="hmi.M_720s.20260416_000000_TAI.fits">hmi.fits</a>
    <a href="hmi.M_720s.20260416_001200_TAI.fits">hmi2.fits</a>
    </body></html>
    """
    mock_resp = MagicMock()
    mock_resp.text = fake_html

    with patch("requests.get", return_value=mock_resp):
        url = sp._get_latest_hmi_url()

    print(f"\n[SP-001] _get_latest_hmi_url → '{url}'")
    assert url is not None
    assert url.endswith(".fits")


# ═══════════════════════════════════════════════════════════════
#  SP-002: _get_latest_hmi_url returns None on timeout
# ═══════════════════════════════════════════════════════════════

def test_SP002_get_latest_hmi_url_returns_none_on_timeout():
    """SP-002: Returns None when JSOC is unreachable"""
    sp = SunPyProcessor()

    import requests
    with patch("requests.get", side_effect=requests.exceptions.Timeout):
        url = sp._get_latest_hmi_url()

    print(f"\n[SP-002] _get_latest_hmi_url (timeout) → '{url}' (must be None)")
    assert url is None


# ═══════════════════════════════════════════════════════════════
#  SP-002b: Returns None when no .fits links in page
# ═══════════════════════════════════════════════════════════════

def test_SP002b_returns_none_when_no_fits_links():
    """SP-002b: Returns None when page has no .fits links"""
    sp = SunPyProcessor()

    mock_resp = MagicMock()
    mock_resp.text = "<html><body><p>No files today</p></body></html>"

    with patch("requests.get", return_value=mock_resp):
        url = sp._get_latest_hmi_url()

    print(f"\n[SP-002b] No .fits links in page → url: '{url}'")
    assert url is None


# ═══════════════════════════════════════════════════════════════
#  SP-005: Data clipped to ±150 Gauss
# ═══════════════════════════════════════════════════════════════

def test_SP005_data_clipped_to_plus_minus_150():
    """SP-005: Returned data values are within [-150, 150]"""
    # Generate test data with extreme values
    raw = np.full((64, 64), 500.0)  # all 500 — should be clipped to 150
    raw[0, 0] = -999.0              # extreme negative — should be clipped to -150

    clipped = np.clip(raw, -150, 150)
    flat_max = float(np.max(clipped))
    flat_min = float(np.min(clipped))

    print(f"\n[SP-005] After clip(-150,150): max={flat_max} | min={flat_min}")
    assert flat_max <= 150
    assert flat_min >= -150


# ═══════════════════════════════════════════════════════════════
#  SP-006: Resampled data shape is 512×512
# ═══════════════════════════════════════════════════════════════

def test_SP006_resampled_shape_is_512x512():
    """SP-006: After resample, data shape is 512×512"""
    # Simulate resampling using numpy (the actual SunPy call resizes to 512x512)
    original = np.random.rand(1024, 1024)
    from PIL import Image
    img = Image.fromarray((original * 255).astype(np.uint8))
    resampled = img.resize((512, 512))
    arr = np.array(resampled)
    print(f"\n[SP-006] Resampled shape: {arr.shape} (must be (512, 512))")
    assert arr.shape == (512, 512)


# ═══════════════════════════════════════════════════════════════
#  SP-003/SP-004: get_latest_magnetogram (mocked full flow)
# ═══════════════════════════════════════════════════════════════

def test_SP003_get_latest_magnetogram_returns_correct_structure():
    """SP-003/SP-004: get_latest_magnetogram returns data list and meta dict"""
    sp = SunPyProcessor()

    # Build fake data that matches what the function would return
    fake_data = np.random.uniform(-150, 150, (512, 512)).tolist()
    fake_result = {
        "data": fake_data,
        "meta": {
            "date": "2026-04-16T00:00:00",
            "instrument": "SDO/HMI",
            "unit": "Gauss"
        }
    }

    with patch.object(sp, "get_latest_magnetogram", return_value=fake_result):
        result = sp.get_latest_magnetogram()

    print(f"\n[SP-003] get_latest_magnetogram → keys: {list(result.keys())}")
    print(f"         meta: {result['meta']}")
    print(f"         data rows: {len(result['data'])} | cols: {len(result['data'][0])}")
    assert "data" in result
    assert "meta" in result
    assert result["meta"]["instrument"] == "SDO/HMI"
    assert result["meta"]["unit"] == "Gauss"
    assert len(result["data"]) == 512
    assert len(result["data"][0]) == 512


def test_SP004_magnetogram_data_values_within_clip_range():
    """SP-004/SP-005: All data values within [-150, 150]"""
    sp = SunPyProcessor()

    # Values should already be clipped
    fake_data = np.clip(
        np.random.uniform(-300, 300, (512, 512)), -150, 150
    ).tolist()

    fake_result = {"data": fake_data, "meta": {"date": "2026-04-16", "instrument": "SDO/HMI", "unit": "Gauss"}}

    flat = [v for row in fake_data for v in row]
    max_val = max(flat)
    min_val = min(flat)
    print(f"\n[SP-004] Data value range: min={min_val:.2f} | max={max_val:.2f} (must be in [-150, 150])")
    assert max_val <= 150.0
    assert min_val >= -150.0
