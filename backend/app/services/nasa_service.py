import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()
NASA_API_KEY = os.getenv("NASA_API_KEY", "DEMO_KEY")

NASA_DONKI_FLARES_URL = "https://kauai.ccmc.gsfc.nasa.gov/DONKI/WS/get/FLR"

def get_solar_flares():
    """
    Fetch solar flare data from NASA DONKI API
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)

    params = {
        "startDate": start_date.strftime("%Y-%m-%d"),
        "endDate": end_date.strftime("%Y-%m-%d"),
        "api_key": NASA_API_KEY
    }

    response = requests.get(NASA_DONKI_FLARES_URL, params=params)

    if response.status_code != 200:
        return []

    return response.json()