import httpx
import asyncio
from typing import Dict, List, Any


class SEPFetcher:
    """
    Handles data fetching from NOAA SWPC for Solar Energetic Particle (SEP) events.

    Data formats:
      - Proton/Electron flux: list of dicts with time_tag, satellite, flux, energy
      - Alerts: list of dicts with product_id, issue_datetime, message
    """

    PROTON_FLUX_URL = "https://services.swpc.noaa.gov/json/goes/primary/integral-protons-3-day.json"
    ELECTRON_FLUX_URL = "https://services.swpc.noaa.gov/json/goes/primary/integral-electrons-3-day.json"
    ALERTS_URL = "https://services.swpc.noaa.gov/products/alerts.json"

    @staticmethod
    def _process_proton_flux(response) -> List[Dict[str, Any]]:
        """
        Parses proton flux JSON into a list of { time_tag, flux, energy } dicts.
        Filters to >=10 MeV channel which is the standard SEP event threshold.
        """
        if isinstance(response, Exception):
            print(f"Proton flux fetch failed: {response}")
            return []

        try:
            response.raise_for_status()
            data = response.json()

            processed = []
            for entry in data:
                if entry.get("time_tag") and entry.get("flux") is not None:
                    processed.append({
                        "time_tag": entry.get("time_tag"),
                        "flux": float(entry.get("flux") or 0),
                        "energy": entry.get("energy", "unknown"),
                        "satellite": entry.get("satellite"),
                    })

            return processed[-300:] if processed else []

        except httpx.HTTPStatusError as e:
            print(f"Proton flux HTTP error: {e.response.status_code} - {e.response.text}")
            return []
        except Exception as e:
            print(f"Proton flux processing error: {e}")
            return []

    @staticmethod
    def _process_electron_flux(response) -> List[Dict[str, Any]]:
        """
        Parses electron flux JSON into a list of { time_tag, flux, energy } dicts.
        """
        if isinstance(response, Exception):
            print(f"Electron flux fetch failed: {response}")
            return []

        try:
            response.raise_for_status()
            data = response.json()

            processed = []
            for entry in data:
                if entry.get("time_tag") and entry.get("flux") is not None:
                    processed.append({
                        "time_tag": entry.get("time_tag"),
                        "flux": float(entry.get("flux") or 0),
                        "energy": entry.get("energy", "unknown"),
                        "satellite": entry.get("satellite"),
                    })

            return processed[-300:] if processed else []

        except httpx.HTTPStatusError as e:
            print(f"Electron flux HTTP error: {e.response.status_code} - {e.response.text}")
            return []
        except Exception as e:
            print(f"Electron flux processing error: {e}")
            return []

    @staticmethod
    def _process_alerts(response) -> Dict[str, Any]:
        """
        Parses alerts JSON.
        NOAA alerts format: { product_id, issue_datetime, message }
        Filters for SEP/radiation-related alerts based on product_id and message content.
        """
        if isinstance(response, Exception):
            print(f"Alerts fetch failed: {response}")
            return {"risk_level": "unknown", "alerts": []}

        try:
            response.raise_for_status()
            data = response.json()

            SEP_KEYWORDS = ["SEP", "PROTON", "ELECTRON", "RADIATION", "PARTICLE", "ALTEF", "WATA"]

            alerts = []
            for alert in data:
                product_id = alert.get("product_id", "")
                message = alert.get("message", "")

                # Match by product_id prefix or message content
                if any(kw in product_id.upper() or kw in message.upper() for kw in SEP_KEYWORDS):
                    alerts.append({
                        "product_id": product_id,
                        "issue_datetime": alert.get("issue_datetime"),
                        "message": message[:300],  # truncate long messages
                    })

            # Determine risk level from product_id patterns
            # EF = Electron Flux, PF = Proton Flux, WA = Watch/Warning
            has_warning = any("WA" in a["product_id"] for a in alerts)
            has_electron = any("EF" in a["product_id"] for a in alerts)
            has_proton = any("PF" in a["product_id"] for a in alerts)

            if has_warning:
                risk_level = "severe"
            elif has_proton:
                risk_level = "high"
            elif has_electron:
                risk_level = "moderate"
            elif alerts:
                risk_level = "low"
            else:
                risk_level = "quiet"

            return {
                "risk_level": risk_level,
                "alerts": alerts[-10:],  # last 10 relevant alerts
            }

        except httpx.HTTPStatusError as e:
            print(f"Alerts HTTP error: {e.response.status_code} - {e.response.text}")
            return {"risk_level": "unknown", "alerts": []}
        except Exception as e:
            print(f"Alerts processing error: {e}")
            return {"risk_level": "unknown", "alerts": []}

    @staticmethod
    def _calculate_radiation_risk(proton_flux: List[Dict]) -> Dict[str, str]:
        """
        Calculates radiation risk for different mission types based on >=10 MeV proton flux.
        SEP event threshold: >10 pfu at >=10 MeV
        """
        # Filter to >=10 MeV channel for standard SEP assessment
        ten_mev = [p for p in proton_flux if "10" in str(p.get("energy", ""))]
        relevant = ten_mev if ten_mev else proton_flux

        avg_flux = (
            sum(p.get("flux", 0) for p in relevant) / len(relevant)
            if relevant else 0
        )

        if avg_flux > 1000:
            return {"crew": "severe", "satellite": "high", "deep_space": "extreme"}
        elif avg_flux > 100:
            return {"crew": "high", "satellite": "moderate", "deep_space": "severe"}
        elif avg_flux > 10:
            return {"crew": "moderate", "satellite": "low", "deep_space": "high"}
        else:
            return {"crew": "low", "satellite": "low", "deep_space": "moderate"}

    @staticmethod
    async def get_particle_flux_data() -> Dict[str, List]:
        """Fetches proton and electron flux data concurrently."""
        async with httpx.AsyncClient() as client:
            proton_res, electron_res = await asyncio.gather(
                client.get(SEPFetcher.PROTON_FLUX_URL, timeout=10.0),
                client.get(SEPFetcher.ELECTRON_FLUX_URL, timeout=10.0),
                return_exceptions=True
            )

        return {
            "proton": SEPFetcher._process_proton_flux(proton_res),
            "electron": SEPFetcher._process_electron_flux(electron_res),
        }

    @staticmethod
    async def get_radiation_alerts() -> Dict[str, Any]:
        """Fetches current radiation alerts and risk levels."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(SEPFetcher.ALERTS_URL, timeout=10.0)
                return SEPFetcher._process_alerts(response)
            except Exception as e:
                return SEPFetcher._process_alerts(e)

    @staticmethod
    async def get_all_sep_data() -> Dict[str, Any]:
        """Fetches all SEP data: particle flux, alerts, and radiation risk."""
        async with httpx.AsyncClient() as client:
            proton_res, electron_res, alerts_res = await asyncio.gather(
                client.get(SEPFetcher.PROTON_FLUX_URL, timeout=10.0),
                client.get(SEPFetcher.ELECTRON_FLUX_URL, timeout=10.0),
                client.get(SEPFetcher.ALERTS_URL, timeout=10.0),
                return_exceptions=True
            )

        proton_data = SEPFetcher._process_proton_flux(proton_res)
        electron_data = SEPFetcher._process_electron_flux(electron_res)
        alerts_data = SEPFetcher._process_alerts(alerts_res)
        radiation_risk = SEPFetcher._calculate_radiation_risk(proton_data)

        return {
            "particle_flux": {
                "proton": proton_data,
                "electron": electron_data,
            },
            "alerts": alerts_data,
            "radiation_risk": radiation_risk,
        }