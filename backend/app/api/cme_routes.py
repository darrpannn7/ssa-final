from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.services.cme_processor import CMEProcessor

router = APIRouter()
processor = CMEProcessor()

@router.get("/cme/full")
def get_cme_full():
    try:
        return processor.get_full_cme_package()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cme/image")
def get_cme_image():
    try:
        image_path = processor.get_latest_lasco_image()
        return FileResponse(image_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))