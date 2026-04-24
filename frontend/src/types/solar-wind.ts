export interface SolarWindDataPoint {
  time_tag: string;
  speed: number;        // km/s
  density: number;      // particles/cm³
  temperature: number;  // K — always a number (defaults to 0 if NOAA returns null)
}

export interface IMFDataPoint {
  time_tag: string;
  bx: number;  // nT
  by: number;  // nT
  bz: number;  // nT
  bt: number;  // Total magnitude in nT
}

export interface SolarWindResponse {
  status: string;
  data: SolarWindDataPoint[];
  error?: string;  // present if status is "error"
}

export interface IMFResponse {
  status: string;
  data: IMFDataPoint[];
  error?: string;  // present if status is "error"
}

export interface CombinedSolarWindResponse {
  status: string;
  solar_wind: SolarWindDataPoint[];
  imf: IMFDataPoint[];
  error?: string;  // present if status is "error"
}