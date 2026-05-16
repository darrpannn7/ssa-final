"use client";

import { useEffect, useState, useCallback } from "react";
import DashboardHeader from "./DashboardHeader";
import StatusRow from "./StatusRow";
import AlertBanners from "./AlertBanners";
import DashboardImages from "./DashboardImages";
import MetricsRow from "./MetricsRow";
import {
  getSolarFlares,
  getAllSolarWindData,
  getAllSEPData,
  getCMEData,
  getGoesXrayFlux,
  getKpIndex,
} from "@/lib/api";

// ─── Types ────────────────────────────────────────────────────────────────────

interface DashboardState {
  flareClass: string;
  cmeCount: number;
  highestCmeRisk: string;
  sepRisk: string;
  windSpeed: number;
  windDensity: number;
  kpIndex: number;
  xrayFlux: number[];
  protonFlux: number[];
  alerts: string[];
  summaryText: string;
  loading: boolean;
}


// ─── Summary text builder ─────────────────────────────────────────────────────

function buildSummary(
  flareClass: string,
  cmeCount: number,
  highestCmeRisk: string,
  sepRisk: string,
  windSpeed: number,
  windDensity: number
): string {
  const parts: string[] = [];
  if (flareClass.startsWith("X") || flareClass.startsWith("M")) {
    parts.push(`Active solar region producing ${flareClass.startsWith("X") ? "strong" : "moderate"} flares.`);
  } else {
    parts.push("Solar activity is at background or low levels.");
  }
  if (cmeCount > 0) {
    if (highestCmeRisk === "High") {
      parts.push(`${cmeCount} CME${cmeCount > 1 ? "s" : ""} observed with HIGH earth-impact probability — severe geomagnetic storms expected.`);
    } else if (highestCmeRisk === "Moderate") {
      parts.push(`${cmeCount} CME${cmeCount > 1 ? "s" : ""} observed — possible geomagnetic impact in next 24–48 hours.`);
    } else {
      parts.push(`${cmeCount} CME${cmeCount > 1 ? "s" : ""} observed, but trajectory indicates low probability of Earth impact.`);
    }
  }
  if (windSpeed > 500 || windDensity > 10) {
    parts.push("Solar wind conditions are moderately disturbed; satellite operators should remain alert for charging and drag variations.");
  } else {
    parts.push("Solar wind conditions are nominal.");
  }
  if (sepRisk !== "quiet" && sepRisk !== "low") {
    parts.push("Elevated particle flux detected — enhanced radiation risk for high-latitude aviation and space assets.");
  }
  return parts.join(" ");
}

// ─── Main Dashboard ───────────────────────────────────────────────────────────

export default function SpaceWeatherDashboard() {
  const [state, setState] = useState<DashboardState>({
    flareClass: "C1.0",
    cmeCount: 0,
    highestCmeRisk: "Low",
    sepRisk: "quiet",
    windSpeed: 400,
    windDensity: 5,
    kpIndex: 1,
    xrayFlux: [],
    protonFlux: [],
    alerts: [],
    summaryText: "Loading space weather data...",
    loading: true,
  });

  const fetchAll = useCallback(async () => {
    try {
      const [flareRes, windRes, sepRes, cmeRes, xrayRes, kpRes] = await Promise.allSettled([
        getSolarFlares(),
        getAllSolarWindData(),
        getAllSEPData(),
        getCMEData(),
        getGoesXrayFlux(),
        getKpIndex(),
      ]);

      // Flares
      let flareClass = "C1.0";
      if (flareRes.status === "fulfilled" && flareRes.value?.flares?.length > 0) {
        flareClass = flareRes.value.flares.at(-1)?.classType ?? "C1.0";
      }

      // Solar Wind
      let windSpeed = 400;
      let windDensity = 5;
      if (windRes.status === "fulfilled") {
        const sw = windRes.value?.solar_wind ?? [];
        if (sw.length > 0) {
          const latest = sw.at(-1);
          windSpeed = latest?.speed ?? 400;
          windDensity = latest?.density ?? 5;
        }
      }

      // SEP
      let sepRisk = "quiet";
      let alerts: string[] = [];
      let protonFlux: number[] = [];
      if (sepRes.status === "fulfilled") {
        sepRisk = sepRes.value?.alerts?.risk_level ?? "quiet";
        const rawAlerts = sepRes.value?.alerts?.alerts ?? [];
        alerts = rawAlerts.slice(0, 3).map((a: { message: string }) =>
          a.message?.replace(/\r\n/g, " ").trim() ?? ""
        );
        const protonPoints = sepRes.value?.particle_flux?.proton ?? [];
        protonFlux = protonPoints.slice(-20).map((p: { flux: number }) => p.flux ?? 0);
      }

      // CME
      let cmeCount = 0;
      let highestCmeRisk = "Low";
      if (cmeRes.status === "fulfilled") {
        cmeCount = cmeRes.value?.total ?? 0;
        const events = cmeRes.value?.cme_events ?? [];
        if (events.some((e: any) => e.impactProbability === "High")) {
          highestCmeRisk = "High";
        } else if (events.some((e: any) => e.impactProbability === "Moderate")) {
          highestCmeRisk = "Moderate";
        }
      }

      // X-Ray flux — API returns { primary: [{time_tag, flux}], secondary: [...] }
      let xrayFlux: number[] = [];
      if (xrayRes.status === "fulfilled") {
        const data = xrayRes.value;
        const primary: { flux?: number }[] = data?.primary ?? [];
        xrayFlux = primary.slice(-20).map((d) => d?.flux ?? 0);
      }

      // Kp Index — real NOAA Planetary K-index
      let kpIndex = 1;
      if (kpRes.status === "fulfilled" && kpRes.value?.current_kp != null) {
        kpIndex = Math.min(9, Math.max(0, kpRes.value.current_kp));
      }

      const summaryText = buildSummary(flareClass, cmeCount, highestCmeRisk, sepRisk, windSpeed, windDensity);



      setState({
        flareClass,
        cmeCount,
        highestCmeRisk,
        sepRisk,
        windSpeed,
        windDensity,
        kpIndex,
        xrayFlux,
        protonFlux,
        alerts,
        summaryText,
        loading: false,
      });
    } catch (e) {
      console.error("Dashboard fetch error:", e);
      setState((prev) => ({ ...prev, loading: false }));
    }
  }, []);

  useEffect(() => {
    fetchAll();
    const id = setInterval(fetchAll, 5 * 60 * 1000);
    return () => clearInterval(id);
  }, [fetchAll]);

  const satRisk: "CAUTION" | "NORMAL" | "HIGH" =
    state.windSpeed > 700 || state.windDensity > 15 || state.kpIndex >= 6 ? "HIGH" :
    state.windSpeed > 450 || state.windDensity > 8 || state.kpIndex >= 4 ? "CAUTION" : "NORMAL";

  return (
    <div className="w-full min-h-screen bg-black flex flex-col pt-[72px]">
      {/* Loading overlay */}
      {state.loading && (
        <div className="fixed inset-0 z-50 bg-[#05070c]/80 backdrop-blur-sm flex items-center justify-center">
          <div className="flex flex-col items-center gap-4">
            <div className="w-10 h-10 border-2 border-white/20 border-t-cyan-400 rounded-full animate-spin" />
            <p className="text-white/40 text-sm tracking-widest uppercase">Loading Dashboard...</p>
          </div>
        </div>
      )}

      {/* Dashboard layout — fluid width that scales with viewport */}
      <div className="flex flex-col gap-0 w-[94vw] mx-auto">
        {/* Row 1: Header */}
        <DashboardHeader />

        {/* Row 2: Status Tiles */}
        <StatusRow
          flareClass={state.flareClass}
          sepRisk={state.sepRisk}
          cmeCount={state.cmeCount}
          highestCmeRisk={state.highestCmeRisk}
          windSpeed={state.windSpeed}
          windDensity={state.windDensity}
          kpIndex={state.kpIndex}
        />

        {/* Row 3: Alert Banners */}
        <AlertBanners
          summaryText={state.summaryText}
          hasAlerts={state.alerts.length > 0}
          alerts={state.alerts}
        />

        {/* Row 4: Solar Images */}
        <DashboardImages />

        {/* Row 5: Metrics Row */}
        <MetricsRow
          xrayFluxData={state.xrayFlux}
          protonFluxData={state.protonFlux}
          windSpeed={state.windSpeed}
          windDensity={state.windDensity}
          kpIndex={state.kpIndex}
          satelliteRisk={satRisk}
        />

        {/* Footer spacer */}
        <div className="h-6" />
      </div>
    </div>
  );
}
