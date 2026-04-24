from fastapi import APIRouter
from app.services.noaa_service import NOAAFetcher

router = APIRouter()

@router.get("/goes-xray")
async def get_goes_xray():
    return await NOAAFetcher.get_goes_xray_flux()
