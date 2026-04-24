import httpx
import asyncio
from typing import Dict, List, Any


class SolarWindFetcher:
    """
    Handles data fetching from NOAA SWPC for solar wind parameters.
    Fetches: solar wind speed, plasma density, and interplanetary magnetic field (IMF).

    NOAA /products/ endpoints return a list of lists:
      Row 0: headers  → ["time_tag", "density", "speed", ...]
      Row 1+: data    → ["2026-03-12 11:26:00.000", "0.69", "437.1", ...]
    All values are strings and must be cast to float.
    """

    SOLAR_WIND_URL = "https://services.swpc.noaa.gov/products/solar-wind/plasma-7-day.json"
    IMF_URL = "https://services.swpc.noaa.gov/products/solar-wind/mag-7-day.json"

    @staticmethod
    def _process_solar_wind(response) -> List[Dict[str, Any]]:
        """
        Parses solar wind JSON into a list of { time_tag, speed, density, temperature } dicts.
        """
        if isinstance(response, Exception):
            print(f"Solar wind fetch failed: {response}")
            return []

        try:
            response.raise_for_status()
            data = response.json()

            # Expect list of lists — first row is headers
            if not data or not isinstance(data[0], list):
                print("Solar wind: unexpected data format")
                return []

            headers = data[0]  # ["time_tag", "density", "speed", "temperature"]
            rows = data[1:]

            processed = []
            for row in rows:
                entry = dict(zip(headers, row))
                time_tag = entry.get("time_tag")
                density = entry.get("density")
                speed = entry.get("speed")

                if not time_tag or density is None or speed is None:
                    continue

                try:
                    processed.append({
                        "time_tag": time_tag,
                        "speed": float(speed),
                        "density": float(density),
                        "temperature": float(entry.get("temperature") or 0),
                    })
                except (ValueError, TypeError):
                    continue  # skip malformed rows

            return processed[-200:] if processed else []

        except httpx.HTTPStatusError as e:
            print(f"Solar wind HTTP error: {e.response.status_code} - {e.response.text}")
            return []
        except Exception as e:
            print(f"Solar wind processing error: {e}")
            return []

    @staticmethod
    def _process_imf(response) -> List[Dict[str, Any]]:
        """
        Parses IMF JSON into a list of { time_tag, bx, by, bz, bt } dicts.
        NOAA field names: bx_gsm, by_gsm, bz_gsm, bt
        """
        if isinstance(response, Exception):
            print(f"IMF fetch failed: {response}")
            return []

        try:
            response.raise_for_status()
            data = response.json()

            if not data or not isinstance(data[0], list):
                print("IMF: unexpected data format")
                return []

            headers = data[0]  # ["time_tag", "bx_gsm", "by_gsm", "bz_gsm", "lon_gsm", "lat_gsm", "bt"]
            rows = data[1:]

            processed = []
            for row in rows:
                entry = dict(zip(headers, row))
                time_tag = entry.get("time_tag")
                bz = entry.get("bz_gsm")

                if not time_tag or bz is None:
                    continue

                try:
                    processed.append({
                        "time_tag": time_tag,
                        "bx": float(entry.get("bx_gsm") or 0),
                        "by": float(entry.get("by_gsm") or 0),
                        "bz": float(bz),
                        "bt": float(entry.get("bt") or 0),
                    })
                except (ValueError, TypeError):
                    continue  # skip malformed rows

            return processed[-200:] if processed else []

        except httpx.HTTPStatusError as e:
            print(f"IMF HTTP error: {e.response.status_code} - {e.response.text}")
            return []
        except Exception as e:
            print(f"IMF processing error: {e}")
            return []

    @staticmethod
    async def get_solar_wind_data() -> List[Dict[str, Any]]:
        """Fetches solar wind speed, density, and temperature data."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(SolarWindFetcher.SOLAR_WIND_URL, timeout=10.0)
                return SolarWindFetcher._process_solar_wind(response)
            except Exception as e:
                return SolarWindFetcher._process_solar_wind(e)

    @staticmethod
    async def get_imf_data() -> List[Dict[str, Any]]:
        """Fetches Interplanetary Magnetic Field (IMF) data."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(SolarWindFetcher.IMF_URL, timeout=10.0)
                return SolarWindFetcher._process_imf(response)
            except Exception as e:
                return SolarWindFetcher._process_imf(e)

    @staticmethod
    async def get_all_solar_wind_data() -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetches both solar wind and IMF data simultaneously using a shared client.
        """
        async with httpx.AsyncClient() as client:
            wind_res, imf_res = await asyncio.gather(
                client.get(SolarWindFetcher.SOLAR_WIND_URL, timeout=10.0),
                client.get(SolarWindFetcher.IMF_URL, timeout=10.0),
                return_exceptions=True
            )

        return {
            "solar_wind": SolarWindFetcher._process_solar_wind(wind_res),
            "imf": SolarWindFetcher._process_imf(imf_res),
        }
