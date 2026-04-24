from operator import neg, pos
import os
from pyexpat import features
import requests
import numpy as np
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from sunpy.map import Map
import astropy.units as u
from scipy.ndimage import label, find_objects

class SunPyProcessor:
    """
    Handles downloading and processing of scientific FITS files (HMI Magnetograms).
    """
    
    ASSETS_DIR = "./assets/flare/magnetogram"
    HMI_URL_BASE = "http://jsoc.stanford.edu/data/hmi/fits/"

    def __init__(self):
        os.makedirs(self.ASSETS_DIR, exist_ok=True)

    def _get_latest_hmi_url(self):
        """Scrapes the JSOC directory to find the absolute latest FITS file."""
        now = datetime.utcnow()
        # HMI data is usually 15-30 mins behind, so check today's folder
        date_str = now.strftime('%Y/%m/%d/')
        url = f"{self.HMI_URL_BASE}{date_str}"
        
        try:
            resp = requests.get(url, timeout=5)
            soup = BeautifulSoup(resp.text, 'html.parser')
            links = soup.select('a[href$=".fits"]')
            if not links:
                return None
            # Return the last link (most recent time)
            return f"{url}{links[-1]['href']}"
        except:
            return None

    def get_latest_magnetogram(self):
        """
        Downloads HMI FITS if a new one exists, or loads the cached local copy.
        Returns: Numpy array (image data) and Metadata.
        """
        local_file = f"{self.ASSETS_DIR}/latest_hmi.fits"
        
        # 1. CACHING STRATEGY: 
        # If file exists and is less than 30 mins old, use it. Don't redownload.
        should_download = True
        if os.path.exists(local_file):
            file_time = datetime.fromtimestamp(os.path.getmtime(local_file))
            if datetime.now() - file_time < timedelta(minutes=30):
                should_download = False
                print("Loading cached HMI FITS...")

        # 2. DOWNLOAD (If needed)
        if should_download:
            print("Fetching new HMI FITS...")
            latest_url = self._get_latest_hmi_url()
            if latest_url:
                with requests.get(latest_url, stream=True) as r:
                    r.raise_for_status()
                    with open(local_file, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)

        # 3. PROCESS WITH SUNPY
        # Load the FITS file into a SunPy Map
        hmi_map = Map(local_file)
        hmi_map = hmi_map.rotate() # Align Solar North up

        # Downsample for web performance (1024x1024 -> 512x512)
        # This makes the API response 4x faster
        new_dim = [512, 512] * u.pixel
        hmi_resampled = hmi_map.resample(new_dim)

        # Normalize data (clipping magnetic field values for visualization)
        data = np.nan_to_num(hmi_resampled.data, nan=0)
        data = np.clip(data, -150, 150) # Clip extreme gauss values

        return {
            "data": data.tolist(), # Convert numpy -> list for JSON
            "meta": {
                "date": hmi_map.meta['date-obs'],
                "instrument": "SDO/HMI",
                "unit": "Gauss"
            }
        }

    def analyze_magnetogram(self, data):

        arr = np.array(data)

        # Mean magnetic strength
        mean_field = float(np.mean(np.abs(arr)))

        # Magnetic gradient (detect complexity)
        gx, gy = np.gradient(arr)
        gradient_strength = float(np.mean(np.sqrt(gx**2 + gy**2)))

        # Polarity mixing
        pos = np.sum(arr > 0)
        neg = np.sum(arr < 0)

        polarity_mix = float(min(pos, neg) / max(pos, neg)) if max(pos, neg) != 0 else 0

        return {
            "mean_field": round(mean_field, 2),
            "gradient_strength": round(gradient_strength, 2),
            "polarity_mix": round(polarity_mix, 3)
        }    

    def calculate_flare_probability(self, strength, area):
        """
        Continuous heuristic model for flare probability.
        Returns A, B, C, M, X class probabilities.
        """
        strength_factor = min(strength / 150, 1.0)
        area_factor = min(area / 3000, 1.0)
        score = (0.6 * strength_factor) + (0.4 * area_factor)

        if score > 0.80:
            return {"A": 2,  "B": 5,  "C": 18, "M": 45, "X": 30}
        elif score > 0.65:
            return {"A": 5,  "B": 10, "C": 30, "M": 40, "X": 15}
        elif score > 0.50:
            return {"A": 8,  "B": 15, "C": 42, "M": 28, "X": 7}
        elif score > 0.35:
            return {"A": 12, "B": 22, "C": 45, "M": 18, "X": 3}
        elif score > 0.20:
            return {"A": 20, "B": 35, "C": 35, "M": 9,  "X": 1}
        else:
            return {"A": 40, "B": 40, "C": 16, "M": 3,  "X": 1}
        
    def detect_active_regions(self, data):

        arr = np.array(data)

        # Balanced threshold
        threshold = 60
        mask = np.abs(arr) > threshold

        labeled, num = label(mask)
        objects = find_objects(labeled)

        regions = []

        for obj in objects:

            if obj is None:
                continue

            y_slice, x_slice = obj

            x1 = x_slice.start
            x2 = x_slice.stop
            y1 = y_slice.start
            y2 = y_slice.stop

            width = x2 - x1
            height = y2 - y1
            area = width * height

            # Balanced filtering
            if area < 100:
                continue

            region = arr[y1:y2, x1:x2]

            mean_strength = float(np.mean(np.abs(region)))

            if mean_strength < 50:
                continue

            flare_prob = self.calculate_flare_probability(mean_strength, area)

            regions.append({
                "id": len(regions) + 1,
                "bbox": [x1, y1, x2, y2],
                "strength": round(mean_strength, 2),
                "area": area,
                "flare": flare_prob
            })

        regions.sort(key=lambda r: r["strength"], reverse=True)

        for i, r in enumerate(regions):
            r["id"]=i+1;    

        return regions[:8]        