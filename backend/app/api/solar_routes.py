import os
from fastapi import APIRouter, HTTPException
import httpx
from fastapi.responses import StreamingResponse
from app.services.solar_wind_service import SolarWindFetcher
from dotenv import load_dotenv
from fastapi.responses import Response

load_dotenv()
NASA_API_KEY = os.getenv("NASA_API_KEY", "DEMO_KEY")
router = APIRouter()


@router.get("/flares")
async def get_solar_flares():
    """
    Returns solar flare events from CCMC DONKI.
    """
    url = "https://kauai.ccmc.gsfc.nasa.gov/DONKI/WS/get/FLR"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url,params={"api_key": NASA_API_KEY}, timeout=10.0)
            response.raise_for_status()
            data = response.json()

        formatted = [
            {
                "id": flare.get("flrID"),
                "classType": flare.get("classType") or "Unknown",
                "startTime": flare.get("beginTime"),
                "peakTime": flare.get("peakTime"),
                "endTime": flare.get("endTime"),
                "activeRegion": flare.get("activeRegionNum"),
                "sourceLocation": flare.get("sourceLocation"),
            }
            for flare in data[-10:]  # last 10 events
        ]

        return {
            "status": "success",
            "total": len(formatted),
            "flares": formatted
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/aia-image")
async def get_aia_image(wavelength: str = "0171"):

    VALID_WAVELENGTHS = {"0094", "0131", "0171", "0193"}

    if wavelength not in VALID_WAVELENGTHS:
        raise HTTPException(status_code=400, detail="Invalid wavelength")

    url = f"https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_{wavelength}.jpg"

    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(10.0),
            follow_redirects=True
        ) as client:
            response = await client.get(url)

        response.raise_for_status()

        return Response(
            content=response.content,
            media_type="image/jpeg",
            headers={"Cache-Control": "public, max-age=120"}
        )

    except Exception as e:
        print("AIA IMAGE ERROR:", repr(e))
        raise HTTPException(status_code=502, detail=str(e))

# Solar Wind Data Endpoints

@router.get("/wind/speed")
async def get_solar_wind_speed():
    """
    Returns solar wind speed, density, and temperature data from NOAA SWPC.
    """
    data = await SolarWindFetcher.get_solar_wind_data()

    if not data:
        raise HTTPException(status_code=503, detail="Solar wind data unavailable")

    return {
        "status": "success",
        "data": data
    }


@router.get("/wind/imf")
async def get_imf_data():
    """
    Returns Interplanetary Magnetic Field (IMF) data from NOAA SWPC.
    Includes Bx, By, Bz components and total magnitude.
    """
    data = await SolarWindFetcher.get_imf_data()

    if not data:
        raise HTTPException(status_code=503, detail="IMF data unavailable")

    return {
        "status": "success",
        "data": data
    }


@router.get("/wind/all")
async def get_all_solar_wind():
    """
    Returns combined solar wind speed, density, temperature, and IMF data.
    """
    data = await SolarWindFetcher.get_all_solar_wind_data()

    if not data["solar_wind"] and not data["imf"]:
        raise HTTPException(status_code=503, detail="All solar wind data unavailable")

    return {
        "status": "success",
        "solar_wind": data["solar_wind"],
        "imf": data["imf"]
    }

# Solar Energetic Particle (SEP) Endpoints

from app.services.sep_service import SEPFetcher

@router.get("/sep/particle-flux")
async def get_particle_flux():
    """Returns proton and electron flux data from NOAA SWPC."""
    data = await SEPFetcher.get_particle_flux_data()
    if not data["proton"] and not data["electron"]:
        raise HTTPException(status_code=503, detail="Particle flux data unavailable")
    return {"status": "success", "proton": data["proton"], "electron": data["electron"]}


@router.get("/sep/alerts")
async def get_radiation_alerts():
    """Returns current radiation alerts and risk levels."""
    data = await SEPFetcher.get_radiation_alerts()
    return {"status": "success", "risk_level": data["risk_level"], "alerts": data["alerts"]}


@router.get("/sep/all")
async def get_all_sep_data():
    """Returns combined SEP data: particle flux, alerts, and risk assessment."""
    data = await SEPFetcher.get_all_sep_data()
    return {
        "status": "success",
        "particle_flux": data["particle_flux"],
        "alerts": data["alerts"],
        "radiation_risk": data["radiation_risk"],
    }