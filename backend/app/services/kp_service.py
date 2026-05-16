import httpx
import asyncio
import time
from typing import Dict, Any

# ─── Simple in-memory TTL cache ───────────────────────────────────────────────

_cache: Dict[str, Dict[str, Any]] = {}

def _get_cached(key: str, ttl_seconds: int):
    entry = _cache.get(key)
    if entry and (time.time() - entry["ts"]) < ttl_seconds:
        return entry["data"]
    return None

def _set_cached(key: str, data: Any):
    _cache[key] = {"data": data, "ts": time.time()}


class KpFetcher:
    """
    Fetches the real NOAA Planetary K-index from NOAA SWPC.
    Data source: https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json
    Format: [{"time_tag": "2026-05-16T00:00:00", "Kp": 5.67, "a_running": 67, "station_count": 8}, ...]
    Updated every 3 hours by NOAA.
    """

    KP_URL = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
    CACHE_KEY = "kp_index"
    CACHE_TTL = 180  # 3 minutes (Kp updates every 3 hours, but poll more often for freshness)

    @staticmethod
    async def get_kp_index() -> Dict[str, Any]:
        """
        Returns the latest and recent Kp index values.
        Cached for 3 minutes to avoid hammering NOAA.
        """
        cached = _get_cached(KpFetcher.CACHE_KEY, KpFetcher.CACHE_TTL)
        if cached is not None:
            return cached

        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                response = await client.get(KpFetcher.KP_URL)
                response.raise_for_status()
                data = response.json()

            if not data or not isinstance(data, list):
                raise ValueError("Unexpected Kp data format")

            # Take last 8 entries (last 24 hours, one per 3h interval)
            recent = data[-8:]

            # Latest valid entry
            latest = recent[-1]
            current_kp = float(latest.get("Kp", 1.0))
            time_tag = latest.get("time_tag", "")
            station_count = latest.get("station_count", 0)

            # History for sparkline (last 8 readings = 24h)
            history = [
                {
                    "time_tag": e.get("time_tag"),
                    "kp": float(e.get("Kp", 0)),
                    "a_running": int(e.get("a_running", 0)),
                }
                for e in recent
            ]

            result = {
                "status": "success",
                "current_kp": round(current_kp, 2),
                "time_tag": time_tag,
                "station_count": station_count,
                "history": history,
            }

            _set_cached(KpFetcher.CACHE_KEY, result)
            return result

        except Exception as e:
            print(f"[KpFetcher] Error: {e}")
            fallback = {
                "status": "error",
                "current_kp": 1.0,
                "time_tag": "",
                "station_count": 0,
                "history": [],
                "error": str(e),
            }
            return fallback
