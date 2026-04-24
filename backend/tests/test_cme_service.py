"""
CME Service Extended Tests
Covers: CM-001 to CM-004, CM-009, CM-010 (mocked network calls)
Run: pytest tests/test_cme_service.py -v -s
"""

import pytest
from unittest.mock import MagicMock, patch
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.cme_processor import CMEProcessor

cme = CMEProcessor()


# ─── Helper: build a fake CME API item ────────────────────────────

def _fake_item(speed=800, lat=10, lon=15, half_angle=30, ctype="C", halo=False):
    return {
        "activityID": f"2026-04-16T00:00:00-CME-001",
        "startTime": "2026-04-16T00:00Z",
        "sourceLocation": "N10E15",
        "note": "Test CME event",
        "instruments": [{"displayName": "LASCO/C2"}],
        "cmeAnalyses": [{
            "speed": speed,
            "latitude": lat,
            "longitude": lon,
            "halfAngle": half_angle,
            "type": "halo" if halo else ctype,
        }]
    }


def _fake_item_no_analysis():
    return {
        "activityID": "2026-04-16T00:00:00-CME-002",
        "startTime": "2026-04-16T00:00Z",
        "sourceLocation": "S05W20",
        "note": "",
        "instruments": [],
        "cmeAnalyses": []     # ← empty
    }


# ═══════════════════════════════════════════════════════════════
#  CM-001: get_full_cme_package returns correct structure
# ═══════════════════════════════════════════════════════════════

def test_CM001_get_full_cme_package_structure():
    """CM-001: get_full_cme_package returns status, total, cme_events"""
    fake_data = [_fake_item(speed=900, lon=10) for _ in range(5)]

    with patch.object(cme, "_get_session") as mock_sess:
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = fake_data
        mock_sess.return_value.get.return_value = mock_resp

        result = cme.get_full_cme_package()

    print(f"\n[CM-001] status: {result['status']} | total: {result['total']} | first event keys: {list(result['cme_events'][0].keys())}")
    assert result["status"] == "success"
    assert result["total"] == 5
    assert isinstance(result["cme_events"], list)
    first = result["cme_events"][0]
    for key in ["activityID", "startTime", "speed", "latitude", "longitude", "impactProbability"]:
        assert key in first, f"Missing key: {key}"


def test_CM001_returns_at_most_10_events():
    """CM-001b: Returns at most 10 events (last 10 from API)"""
    fake_data = [_fake_item() for _ in range(20)]

    with patch.object(cme, "_get_session") as mock_sess:
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = fake_data
        mock_sess.return_value.get.return_value = mock_resp

        result = cme.get_full_cme_package()

    # code uses data[-10:] so 20 items → 10 returned
    print(f"\n[CM-001b] 20 items in API → returned: {result['total']} (must be exactly 10)")
    assert result["total"] == 10


# ═══════════════════════════════════════════════════════════════
#  CM-002: Retries on 5xx errors
# ═══════════════════════════════════════════════════════════════

def test_CM002_retries_on_server_error():
    """CM-002: Session is configured with Retry (3 retries on 5xx)"""
    session = cme._get_session()
    https_adapter = session.get_adapter("https://")
    retry = https_adapter.max_retries
    total = getattr(retry, "total", None)
    backoff = getattr(retry, "backoff_factor", None)
    forcelist = set(getattr(retry, "status_forcelist", []) or [])
    print(f"\n[CM-002] Retry config → total: {total} | backoff_factor: {backoff} | status_forcelist: {forcelist}")
    assert total == 3, f"Expected 3 retries, got {total}"
    assert backoff == 1
    assert 500 in forcelist
    assert 503 in forcelist


# ═══════════════════════════════════════════════════════════════
#  CM-003: Raises exception when all retries fail
# ═══════════════════════════════════════════════════════════════

def test_CM003_raises_exception_on_persistent_failure():
    """CM-003: Raises Exception when network completely fails"""
    with patch.object(cme, "_get_session") as mock_sess:
        mock_sess.return_value.get.side_effect = Exception("Connection refused")
        try:
            cme.get_full_cme_package()
            assert False, "Should have raised exception"
        except Exception as e:
            print(f"\n[CM-003] Exception raised: '{e}'")
            assert "CME fetch failed" in str(e)


# ═══════════════════════════════════════════════════════════════
#  CM-004: Missing cmeAnalyses handled gracefully
# ═══════════════════════════════════════════════════════════════

def test_CM004_missing_cme_analyses_no_crash():
    """CM-004: Items with empty cmeAnalyses handled without crash"""
    fake_data = [_fake_item_no_analysis()]

    with patch.object(cme, "_get_session") as mock_sess:
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = fake_data
        mock_sess.return_value.get.return_value = mock_resp

        result = cme.get_full_cme_package()

    event = result["cme_events"][0]
    print(f"\n[CM-004] Event with no cmeAnalyses → speed: {event['speed']} | lat: {event['latitude']} | type: {event['type']}")
    assert event["speed"] is None
    assert event["latitude"] is None
    assert event["longitude"] is None
    assert event["type"] is None
    # Should still have valid impact probability
    assert event["impactProbability"] in {"Low", "Moderate", "High"}


# ═══════════════════════════════════════════════════════════════
#  CM-009: get_latest_lasco_image downloads and returns path
# ═══════════════════════════════════════════════════════════════

def test_CM009_get_latest_lasco_image_returns_path():
    """CM-009: get_latest_lasco_image returns a valid file path"""
    fake_gif = b"GIF89a" + b"\x00" * 100  # fake GIF bytes

    with patch.object(cme, "_get_session") as mock_sess:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.iter_content = MagicMock(return_value=[fake_gif])
        mock_sess.return_value.get.return_value = mock_resp

        path = cme.get_latest_lasco_image()

    print(f"\n[CM-009] get_latest_lasco_image → returned path: '{path}'")
    assert isinstance(path, str)
    assert path.endswith(".gif")


# ═══════════════════════════════════════════════════════════════
#  CM-010: get_latest_lasco_image raises on 404
# ═══════════════════════════════════════════════════════════════

def test_CM010_raises_exception_when_soho_returns_404():
    """CM-010: Raises exception when SOHO returns non-200"""
    with patch.object(cme, "_get_session") as mock_sess:
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_sess.return_value.get.return_value = mock_resp

        try:
            cme.get_latest_lasco_image()
            assert False, "Should have raised exception"
        except Exception as e:
            print(f"\n[CM-010] Exception raised: '{e}'")
            assert "CME Image Error" in str(e)


# ═══════════════════════════════════════════════════════════════
#  CME event fields match expected types
# ═══════════════════════════════════════════════════════════════

def test_CM001_event_fields_correct_types():
    """CM-001c: Event fields have correct types"""
    fake_data = [_fake_item(speed=1200, lat=5, lon=-20, half_angle=45, ctype="C")]

    with patch.object(cme, "_get_session") as mock_sess:
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = fake_data
        mock_sess.return_value.get.return_value = mock_resp

        result = cme.get_full_cme_package()

    event = result["cme_events"][0]
    print(f"\n[CM-001c] Event field types: speed={type(event['speed']).__name__} | lat={type(event['latitude']).__name__} | impactProb={event['impactProbability']}")
    assert isinstance(event["speed"], (int, float))
    assert isinstance(event["latitude"], (int, float))
    assert event["impactProbability"] in {"Low", "Moderate", "High"}
    assert isinstance(event["instruments"], list)
