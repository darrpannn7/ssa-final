from fastapi import APIRouter
import os
from datetime import datetime

router = APIRouter()

@router.get("/status")
def system_status():
    magnetogram_path = "./assets/flare/magnetogram/latest_hmi.fits"

    return {
        "service": "Space Weather Backend",
        "time": datetime.utcnow(),
        "magnetogram_cached": os.path.exists(magnetogram_path),
        "cache_location": magnetogram_path
    }
