import httpx
import asyncio
import time
import pandas as pd
from typing import Dict, Any

# ─── Simple in-memory TTL cache ───────────────────────────────────────────────
_cache: Dict[str, Dict[str, Any]] = {}

def _get_cached(key: str, ttl: int):
    e = _cache.get(key)
    if e and (time.time() - e["ts"]) < ttl:
        return e["data"]
    return None

def _set_cached(key: str, data: Any):
    _cache[key] = {"data": data, "ts": time.time()}


class NOAAFetcher:
    """
    Handles lightweight data fetching from NOAA SWPC (Space Weather Prediction Center).
    """

    GOES_URL_PRIMARY = "https://services.swpc.noaa.gov/json/goes/primary/xrays-6-hour.json"
    GOES_URL_SECONDARY = "https://services.swpc.noaa.gov/json/goes/secondary/xrays-6-hour.json"

    @staticmethod
    def _process(response) -> list:
        """
        Cleans raw GOES JSON into a list of { time_tag, flux } dicts.
        Returns empty list if fetch failed.
        """
        if isinstance(response, Exception):
            print(f"GOES fetch failed: {response}")
            return []

        df = pd.DataFrame(response.json())

        long_flux = df[
            (df['energy'] == '0.1-0.8nm') &
            (df['observed_flux'] > 0)
        ].copy()

        return long_flux[['time_tag', 'flux']].tail(200).to_dict(orient='records')

    @staticmethod
    async def get_goes_xray_flux():
        """
        Fetches GOES-16 (primary) and GOES-17 (secondary) simultaneously.
        Cached for 90 seconds to reduce upstream load.
        """
        cached = _get_cached("goes_xray", 90)
        if cached is not None:
            return cached

        async with httpx.AsyncClient() as client:
            primary_res, secondary_res = await asyncio.gather(
                client.get(NOAAFetcher.GOES_URL_PRIMARY, timeout=5.0),
                client.get(NOAAFetcher.GOES_URL_SECONDARY, timeout=5.0),
                return_exceptions=True
            )

        result = {
            "primary": NOAAFetcher._process(primary_res),
            "secondary": NOAAFetcher._process(secondary_res)
        }
        _set_cached("goes_xray", result)
        return result