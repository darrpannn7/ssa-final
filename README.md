# Analytics Dashboard for SSA
### Space Situational Awareness — Real-Time Solar Weather Dashboard

A full-stack web application for monitoring real-time solar weather events including Solar Flares, Coronal Mass Ejections (CMEs), Solar Energetic Particles (SEPs), and Solar Wind conditions. Built with **Next.js + FastAPI**.

---

## Table of Contents
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Backend Overview](#backend-overview)
- [Frontend Overview](#frontend-overview)
- [API Endpoints](#api-endpoints)
- [Data Sources](#data-sources)
- [Pages & Features](#pages--features)
- [Environment Variables](#environment-variables)
- [Important Notes](#important-notes)
- [Contributing](#contributing)

---

## Project Structure

```
Analytics-Dashboard-for-SSA/
├── backend/
│   ├── requirements.txt                 # Python dependencies
│   └── app/
│       ├── main.py                      # FastAPI app entry point
│       ├── api/
│       │   ├── solar_routes.py          # Solar flare, AIA proxy, Solar Wind + SEP endpoints
│       │   ├── magnetogram_routes.py    # HMI magnetogram endpoints
│       │   ├── space_weather.py         # Solar flare data router
│       │   ├── noaa.py                  # GOES X-ray flux router
│       │   ├── cme_routes.py            # CME data endpoints
│       │   └── system_routes.py         # Health check endpoint
│       └── services/
│           ├── sunpy_processor.py       # HMI FITS download + flare probability
│           ├── noaa_service.py          # GOES-16 & GOES-17 X-ray flux fetcher
│           ├── nasa_service.py          # NASA DONKI solar flare fetcher
│           ├── cme_processor.py         # CME metadata + LASCO image fetcher
│           ├── solar_wind_service.py    # Solar wind speed, density, IMF fetcher
│           └── sep_service.py           # Solar Energetic Particle flux + alerts fetcher
│
├── frontend/
│   ├── package.json
│   └── src/
│       ├── app/
│       │   ├── solar-flare/page.tsx
│       │   ├── cme/page.tsx
│       │   ├── sep/page.tsx
│       │   └── solar-wind/page.tsx
│       ├── components/
│       │   ├── home/
│       │   │   └── ServiceCards.tsx     # Scroll-stacked card layout
│       │   ├── cards/
│       │   │   ├── SplitCard.tsx        # Reusable split layout card wrapper
│       │   │   ├── GOESFluxChart.tsx    # Dual GOES Plotly chart
│       │   │   ├── CMECards.tsx         # All 5 CME card components
│       │   │   └── FlareEventLog.tsx    # Recent flare events table
│       │   ├── canvas/
│       │   ├── chat/
│       │   ├── layout/
│       │   ├── GlassCard.tsx
│       │   ├── Sidebar.tsx
│       │   └── TopBar.tsx
│       ├── constants/
│       │   ├── nav.ts
│       │   ├── solar-flare-cards.ts
│       │   ├── cme-cards.ts
│       │   ├── sep-cards.ts
│       │   └── solar-wind-cards.ts
│       ├── types/
│       │   └── service-card.ts
│       ├── hooks/
│       ├── styles/
│       └── lib/
│           └── api.ts                   # All frontend API call functions
│
└── README.md
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14, TypeScript, Tailwind CSS, Framer Motion |
| Charts | React-Plotly.js |
| Backend | FastAPI, Python 3.12 |
| Data Processing | SunPy, Astropy, NumPy, Pandas |
| HTTP Clients | httpx (async), requests |
| Machine Learning | PyTorch, Transformers, Unsloth, PEFT |
| Image Processing | Matplotlib, Pillow, OpenCV |

---

## Getting Started

### Prerequisites
- Python 3.12+
- Node.js 18+
- Git

## Running on GitHub Codespaces

Codespaces gives you a full development environment in the browser — no local install needed.

### 1. Open in Codespaces
- Go to the GitHub repo
- Click the green **"Code"** button
- Click **"Codespaces"** tab
- Click **"Create codespace on main"**

### 2. Connect frontend to backend
Open `frontend/src/lib/api.ts` and make sure the `BASE_URL` reads from the environment variable:
```typescript
const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
```
If you are running the backend on a different port or a remote server, update the URL in `frontend/.env.local` accordingly and restart the frontend dev server.

### 3. Backend setup

Once the codespace loads, open the terminal and run:
```bash
cd backend
pip install -r requirements.txt
pip install "sunpy[all]"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

> If the above command doesn’t work, you can try:
```bash
uvicorn app.main:app --reload
```
Codespaces will show a popup saying **"Port 8000 is available"** — click **"Open in Browser"** to confirm it's running. Then copy that forwarded URL (looks like `https://xxxx-8000.app.github.dev`).( Make sure the port is public. You can go to the Ports tab besides the terminal and make them public manually too. For more detail check below. )

### 4. Update the frontend env variable
```bash
cd frontend
echo "NEXT_PUBLIC_API_URL=https://xxxx-8000.app.github.dev" > .env.local
```
Replace `xxxx-8000.app.github.dev` with your actual forwarded URL from step 2.

### 5. Frontend setup
```bash
cd frontend
npm install
npm run dev -- --hostname 0.0.0.0
```
> If the above command doesn’t work, you can try:
```bash
npm run dev
```
Codespaces will show another popup for **Port 3000** — click **"Open in Browser"** to view the app.

### Important — Port visibility
By default Codespaces ports are **private**. If you get CORS or fetch errors:
1. Go to the **"Ports"** tab in the bottom panel
2. Right-click port **8000**
3. Click **"Port Visibility"** → **"Public"**
4. Do the same for port **3000**

Also you need to create .env files in the backend. For reference check the section below. 

###  For running locally on your pc

### 1. Clone the repository
```bash
git clone https://github.com/Tripti-Anand/Analytics-Dashboard-for-SSA.git
cd Analytics-Dashboard-for-SSA
```

### 2. Backend setup

**Windows**
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install "sunpy[all]"
uvicorn app.main:app --reload
```

**Mac / Linux**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install "sunpy[all]"
uvicorn app.main:app --reload
```

Backend runs at `http://localhost:8000`

### 3. Frontend setup
```bash
cd frontend
npm install
npm run dev
```
Frontend runs at `http://localhost:3000`

> This is the same on Windows, Mac, and Linux.

### 4. Environment variables

**Windows** — create `frontend\.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Mac / Linux** — create `frontend/.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```
> The content is the same on all platforms, only the path separator differs (`\` on Windows, `/` on Mac/Linux).

### 5. Connect frontend to backend
Open `frontend/src/lib/api.ts` and make sure the `BASE_URL` reads from the environment variable:
```typescript
const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
```
If you are running the backend on a different port or a remote server, update the URL in `frontend/.env.local` accordingly and restart the frontend dev server.

---

## Backend Overview

### `main.py`
FastAPI entry point. Registers all routers with their prefixes and enables CORS for frontend access.

| Router | Prefix |
|---|---|
| space_weather | `/space-weather` |
| noaa | `/noaa` |
| magnetogram_routes | `/space-weather` |
| system_routes | `/system` |
| cme_routes | `/space-weather` |
| solar_routes | `/space-weather` |

---

### Services

#### `sunpy_processor.py`
Handles SDO/HMI magnetogram data.
- Downloads latest HMI FITS file from JSOC Stanford
- Caches locally for 30 minutes to avoid redundant downloads
- Resamples from 1024×1024 to 512×512 for performance
- Analyzes magnetic field strength, gradient, and polarity mixing
- Computes C/M/X class flare probability scores

#### `noaa_service.py`
Fetches real-time X-ray flux from NOAA SWPC.
- Fetches **GOES-16 (primary)** and **GOES-17 (secondary)** simultaneously using `asyncio.gather`
- Filters for the 0.1–0.8nm long channel used for flare classification
- Returns last 200 data points (~3 hours) for each satellite separately

#### `nasa_service.py`
Fetches solar flare event records from NASA DONKI API.
- Returns last 30 days of flare events
- Fields: class type, start/peak/end time, active region number

#### `cme_processor.py`
Handles Coronal Mass Ejection data.
- Fetches latest 10 CME events from NASA DONKI
- Extracts speed, latitude, longitude, half angle, and type from CME analyses
- Calculates Earth impact probability (Low / Moderate / High) based on speed, direction, and halo type
- Downloads latest LASCO C2 coronagraph image from SOHO

#### `solar_wind_service.py`
Fetches real-time solar wind data from NOAA SWPC.
- Returns solar wind speed, density, and temperature
- Returns Interplanetary Magnetic Field (IMF) components — Bx, By, Bz, and total magnitude

#### `sep_service.py`
Fetches Solar Energetic Particle data from NOAA SWPC.
- Returns proton and electron flux measurements
- Returns current radiation alerts and risk level assessment

---

## Frontend Overview

### Scroll-Stacked Card Layout
Each page uses a scroll-driven stacked card animation built with **Framer Motion**. Cards stack and scale as the user scrolls, giving a layered depth effect. Each card occupies one full viewport height.

### `ServiceCards.tsx`
The central card renderer. Routes each card to its specific content component based on `card.title`. Falls back to showing the description text for cards without a dedicated backend component.

### `lib/api.ts`
Single source of truth for all API calls from the frontend. All fetch functions live here and read `NEXT_PUBLIC_API_URL` from the environment. **If you change the backend port or host, update only `.env.local` and restart the frontend dev server.**

---

## API Endpoints

### Solar Flare
| Method | Endpoint | Description |
|---|---|---|
| GET | `/space-weather/magnetogram/latest` | Raw HMI magnetogram data |
| GET | `/space-weather/magnetogram/image` | Rendered magnetogram PNG |
| GET | `/space-weather/magnetogram/flare-risk` | Flare probability (C/M/X class) |
| GET | `/space-weather/flares` | Recent solar flare events from NASA DONKI |

### GOES X-ray
| Method | Endpoint | Description |
|---|---|---|
| GET | `/noaa/goes-xray` | Dual GOES-16 + GOES-17 X-ray flux data |

### AIA Solar Images
| Method | Endpoint | Description |
|---|---|---|
| GET | `/space-weather/aia-image?wavelength=0171` | Streams latest AIA image for given wavelength |

### CME
| Method | Endpoint | Description |
|---|---|---|
| GET | `/space-weather/cme/latest` | Latest 10 CME event metadata |
| GET | `/space-weather/cme/image` | LASCO C2 coronagraph image |
| GET | `/space-weather/cme/full` | CME metadata + image combined |
| GET | `/space-weather/cme/animation` | LASCO animation GIF URL |

### Solar Wind
| Method | Endpoint | Description |
|---|---|---|
| GET | `/space-weather/wind/speed` | Solar wind speed, density, temperature |
| GET | `/space-weather/wind/imf` | IMF Bx, By, Bz components |
| GET | `/space-weather/wind/all` | Combined solar wind + IMF data |

### SEP
| Method | Endpoint | Description |
|---|---|---|
| GET | `/space-weather/sep/particle-flux` | Proton and electron flux data |
| GET | `/space-weather/sep/alerts` | Radiation alerts and risk level |
| GET | `/space-weather/sep/all` | Combined SEP data |

### System
| Method | Endpoint | Description |
|---|---|---|
| GET | `/system/status` | Backend health check + cache status |

> Full interactive API docs available at `http://localhost:8000/docs` when backend is running.

---

## Data Sources

| Source | Data | URL |
|---|---|---|
| JSOC Stanford | HMI Magnetogram FITS | jsoc.stanford.edu |
| NASA DONKI | Solar Flares, CME Events | kauai.ccmc.gsfc.nasa.gov |
| NOAA SWPC | GOES X-ray Flux, Solar Wind, SEP | services.swpc.noaa.gov |
| SOHO LASCO | CME Coronagraph Images | soho.nascom.nasa.gov |
| SDO NASA | AIA EUV Solar Images | sdo.gsfc.nasa.gov |

---

## Pages & Features

### Solar Flare (`/solar-flare`)
| Card | Content |
|---|---|
| HMI Magnetogram | Live magnetogram image + C/M/X flare probability badges |
| GOES X-ray Flux | Current flare class + dual GOES-16/17 Plotly chart |
| AIA EUV Viewer | Wavelength selector (94Å / 131Å / 171Å / 193Å) |
| Recent Flare Events | Scrollable table — class, peak time, active region |

### CME (`/cme`)
| Card | Content |
|---|---|
| CME Velocity | Latest CME speed in km/s |
| Magnetic Structure | Type, latitude, longitude, half angle |
| Impact Probability | Color-coded risk badge + last 10 events bar breakdown |
| CME Coronagraph Image | Live LASCO C2 GIF |
| CME Event Log | Scrollable table of last 10 CME events |

### SEP (`/sep`)
| Card | Content |
|---|---|
| Particle Flux | Proton + electron flux chart |
| Energy Spectrum | Energy distribution description |
| Radiation Mode | Mode selector — Crew / Satellite / Deep Space |
| Proton Flux Monitor | Dual-axis GOES interactive Plotly chart |

### Solar Wind (`/solar-wind`)
| Card | Content |
|---|---|
| Solar Wind Speed | Speed, density, temperature data |
| Plasma Density | Plasma concentration chart |
| Interplanetary Magnetic Field | IMF Bx, By, Bz components chart |
| Solar Wind Visualization | Real-time dual-axis Plotly chart |

---

## Environment Variables

| Variable | Location | Value |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `frontend/.env.local` | `http://localhost:8000` |

---

## Important Notes

### NASA API Key Rate Limits
The project uses a NASA API key in `solar_routes.py` to fetch solar flare and CME data from NASA DONKI. The default key has a rate limit of **30 requests per hour** and **50 requests per day**. If data stops loading on the solar flare or CME pages:

1. Get a free personal API key at [https://api.nasa.gov](https://api.nasa.gov) — takes 1 minute
2. Open `backend/app/api/solar_routes.py`
3. Replace the existing key:
   ```python
   NASA_API_KEY = "your_new_api_key_here"
   ```
4. Restart the backend

### Changing the Backend URL
If your backend runs on a different port or you deploy it to a remote server, update the base URL in **two places**:
1. `frontend/.env.local` → update `NEXT_PUBLIC_API_URL`
2. Restart the frontend dev server (`Ctrl+C` then `npm run dev`) — environment variable changes only take effect on restart

### Auto-generated Files
The following files are **not committed to git** and are auto-generated at runtime:
- `backend/app/api/__pycache__/` — created by Python on first run
- `backend/assets/flare/magnetogram/latest_hmi.fits` — downloaded by `sunpy_processor.py` on first magnetogram request
- `backend/app/assets/cme/latest_cme.gif` — downloaded by `cme_processor.py` on first CME image request
- `backend/assets/flare/magnetogram/latest.png` — generated by `magnetogram_routes.py` on first image request

These will be created automatically when you run the backend and hit the relevant endpoints for the first time.

---

## Contributing

1. Create a branch from `main` with your name or feature:
   ```bash
   git checkout -b yourname
   ```
2. Make your changes
3. Push your branch:
   ```bash
   git push origin yourname
   ```
4. Open a Pull Request on GitHub with **base:** `main` and describe your changes

> Do not commit `__pycache__/`, `*.pyc`, `*.fits`, or runtime-generated asset files. These are listed in `.gitignore` and get auto-generated when the backend runs.

---

*Built as part of the Space Situational Awareness Analytics Dashboard project.*
