from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.space_weather import router as space_weather_router
from app.api.noaa import router as noaa_router
from app.api import magnetogram_routes
from app.api import system_routes
from app.api import cme_routes
from app.api import solar_routes
from app.api import ai_inference

from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="SSA Backend")

# ✅ Static files (keep as-is)
app.mount("/static", StaticFiles(directory="static"), name="static")

# =========================
# ✅ FIXED CORS CONFIG
# =========================

frontend_url = os.getenv("FRONTEND_URL")

origins = [
    "http://localhost:3000",  # local dev
]

# Add Vercel URL if provided
if frontend_url:
    origins.append(frontend_url)

# TEMP: allow all (to make sure everything works)
# You can remove "*" later after confirming
origins.append("*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================

@app.get("/")
def root():
    return {"message": "SSA Backend running successfully"}


# Routes
app.include_router(space_weather_router, prefix="/space-weather")
app.include_router(noaa_router, prefix="/noaa")
app.include_router(magnetogram_routes.router, prefix="/space-weather")
app.include_router(system_routes.router, prefix="/system")
app.include_router(cme_routes.router, prefix="/space-weather")
app.include_router(solar_routes.router, prefix="/space-weather")
app.include_router(ai_inference.router, prefix="/ai")
