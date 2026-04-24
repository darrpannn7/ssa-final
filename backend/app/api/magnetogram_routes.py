from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.services.sunpy_processor import SunPyProcessor

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
import os

router = APIRouter()
processor = SunPyProcessor()


@router.get("/magnetogram/latest")
def get_latest_magnetogram():
    try:
        result = processor.get_latest_magnetogram()
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def apply_solar_disk_mask(data):
    """
    Converts raw magnetogram array into a clean circular sun disk image
    with black background
    """

    h, w = data.shape

    y, x = np.ogrid[:h, :w]

    center_x = w // 2
    center_y = h // 2

    radius = min(center_x, center_y) * 0.95

    mask = (x - center_x) ** 2 + (y - center_y) ** 2 > radius ** 2

    processed = data.copy()

    processed = processed.astype(float)

    # Contrast normalization
    vmin = np.percentile(processed, 1)
    vmax = np.percentile(processed, 99)

    processed = np.clip(processed, vmin, vmax)

    processed = (processed - vmin) / (vmax - vmin)

    # Apply mask
    processed[mask] = 0

    return processed


@router.get("/magnetogram/image")
def get_magnetogram_image():

    try:
        processor = SunPyProcessor()
        result = processor.get_latest_magnetogram()

        data = np.array(result["data"])

        image_path = "./assets/flare/magnetogram/latest.png"

        os.makedirs(os.path.dirname(image_path), exist_ok=True)

        processed = apply_solar_disk_mask(data)

        plt.figure(figsize=(7, 7), facecolor='black')

        plt.imshow(processed, cmap="gray")
        plt.axis("off")

        plt.savefig(image_path, bbox_inches="tight", facecolor='black')
        plt.close()

        return FileResponse(image_path)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/magnetogram/regions")
def get_active_regions():

    try:

        result = processor.get_latest_magnetogram()

        data = result["data"]

        regions = processor.detect_active_regions(data)

        return {
            "status": "success",
            "total_regions": len(regions),
            "regions": regions
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))