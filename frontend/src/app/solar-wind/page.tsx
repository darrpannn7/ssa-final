"use client";

import { useEffect, useState, useCallback } from "react";
import { getAllSolarWindData } from "@/lib/api";
import { SolarWindDataPoint, IMFDataPoint } from "@/types/solar-wind";
import GlassCard from "@/components/GlassCard";
import ServiceCards from "@/components/home/ServiceCards";
import { SOLAR_WIND_CARDS } from "@/constants/solar-wind-cards";

// ─── Helpers ────────────────────────────────────────────────────────────────

function last<T>(arr: T[]): T | undefined {
  return arr[arr.length - 1];
}

function average(arr: number[]): number {
  if (arr.length === 0) return 0;
  return arr.reduce((a, b) => a + b, 0) / arr.length;
}

function formatTime(tag: string): string {
  return new Date(tag).toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

// ─── Sub-components ─────────────────────────────────────────────────────────

function StatCard({
  title,
  value,
  unit,
  sub,
  timestamp,
  color = "text-cyan-400",
}: {
  title: string;
  value: string;
  unit: string;
  sub: string;
  timestamp?: string;
  color?: string;
}) {
  return (
    <GlassCard>
      <div className="p-8">
        <h3 className="text-lg font-semibold text-gray-300 mb-2">{title}</h3>
        <div className="flex items-baseline gap-2">
          <p className={`text-5xl font-bold ${color}`}>{value}</p>
          <p className="text-xl text-gray-400">{unit}</p>
        </div>
        <p className="text-sm text-gray-500 mt-4">{sub}</p>
        {timestamp && (
          <p className="text-xs text-gray-600 mt-2">Updated: {timestamp}</p>
        )}
      </div>
    </GlassCard>
  );
}

function LoadingSkeleton() {
  return (
    <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
      {[1, 2, 3].map((i) => (
        <GlassCard key={i}>
          <div className="p-8 animate-pulse space-y-4">
            <div className="h-4 bg-white/10 rounded w-1/2" />
            <div className="h-12 bg-white/10 rounded w-3/4" />
            <div className="h-3 bg-white/10 rounded w-1/3" />
          </div>
        </GlassCard>
      ))}
    </div>
  );
}

// ─── Main Page ───────────────────────────────────────────────────────────────

export default function SolarWindPage() {
  const [solarWindData, setSolarWindData] = useState<SolarWindDataPoint[]>([]);
  const [imfData, setIMFData] = useState<IMFDataPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastFetched, setLastFetched] = useState<Date | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await getAllSolarWindData();
      setSolarWindData(response.solar_wind || []);
      setIMFData(response.imf || []);
      setLastFetched(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch data");
      console.error("Solar wind fetch error:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [fetchData]);

  // ── Derived values ──
  const latestWind = last(solarWindData);
  const latestIMF = last(imfData);

  const currentSpeed = latestWind?.speed ?? 0;
  const currentDensity = latestWind?.density ?? 0;
  const currentBz = latestIMF?.bz ?? 0;
  const currentBt = latestIMF?.bt ?? 0;
  const currentTemp = latestWind?.temperature ?? 0;

  const avgSpeed = average(solarWindData.map((d) => d.speed));
  const avgDensity = average(solarWindData.map((d) => d.density));

  const bzStatus =
    currentBz < -10
      ? { label: "⚠️ Strong southward — storm risk", color: "text-red-400" }
      : currentBz < -5
      ? { label: "⚠️ Southward — geomagnetic activity", color: "text-orange-400" }
      : currentBz >= 0
      ? { label: "✅ Northward — quiet conditions", color: "text-green-400" }
      : { label: "Northward/Variable", color: "text-green-400" };

  const speedStatus =
    currentSpeed > 700
      ? "⚠️ High speed stream"
      : currentSpeed > 500
      ? "Elevated solar wind"
      : "Nominal solar wind";

  return (
    <>
      {/* Hero */}
      <section className="min-h-screen h-[110vh] flex flex-col items-center justify-center text-center gap-6 pt-20">
        <h1 className="text-7xl font-black uppercase">Solar Wind</h1>
        <p className="text-gray-400 text-lg max-w-xl">
          Real-time plasma and interplanetary magnetic field data from NOAA SWPC
        </p>
        {lastFetched && (
          <p className="text-xs text-gray-600">
            Last updated: {lastFetched.toLocaleTimeString()} · refreshes every 5 min
          </p>
        )}
      </section>

      {/* Stat Cards */}
      <section className="py-24 px-6 bg-gradient-to-b from-black via-purple-900/10 to-black">
        {loading ? (
          <LoadingSkeleton />
        ) : (
          <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
            <StatCard
              title="Solar Wind Speed"
              value={currentSpeed.toFixed(0)}
              unit="km/s"
              sub={`${speedStatus} · Avg: ${avgSpeed.toFixed(0)} km/s`}
              timestamp={latestWind ? formatTime(latestWind.time_tag) : undefined}
              color="text-cyan-400"
            />
            <StatCard
              title="Plasma Density"
              value={currentDensity.toFixed(2)}
              unit="p/cm³"
              sub={`Avg: ${avgDensity.toFixed(2)} p/cm³ · ${solarWindData.length} data points`}
              timestamp={latestWind ? formatTime(latestWind.time_tag) : undefined}
              color="text-blue-400"
            />
            <StatCard
              title="IMF Bz Component"
              value={currentBz.toFixed(2)}
              unit="nT"
              sub={bzStatus.label}
              timestamp={latestIMF ? formatTime(latestIMF.time_tag) : undefined}
              color={bzStatus.color}
            />
          </div>
        )}

        {/* Secondary Cards */}
        {!loading && !error && (
          <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-8 mb-16">
            <StatCard
              title="Total IMF Magnitude (Bt)"
              value={currentBt.toFixed(2)}
              unit="nT"
              sub="Total interplanetary magnetic field strength"
              timestamp={latestIMF ? formatTime(latestIMF.time_tag) : undefined}
              color="text-purple-400"
            />
            <StatCard
              title="Solar Wind Temperature"
              value={
                currentTemp > 0
                  ? (currentTemp / 1e6).toFixed(2)
                  : "N/A"
              }
              unit={currentTemp > 0 ? "MK" : ""}
              sub="Proton temperature of solar wind plasma"
              timestamp={latestWind ? formatTime(latestWind.time_tag) : undefined}
              color="text-yellow-400"
            />
          </div>
        )}

        {/* Error Banner */}
        {error && (
          <div className="max-w-7xl mx-auto mb-8 p-4 bg-red-900/30 border border-red-500/50 rounded-lg flex items-center justify-between">
            <p className="text-red-300">⚠️ {error}</p>
            <button
              onClick={fetchData}
              className="text-sm text-red-300 border border-red-500/50 px-3 py-1 rounded hover:bg-red-900/40 transition"
            >
              Retry
            </button>
          </div>
        )}

        {/* Data Summary Row */}
        {!loading && !error && solarWindData.length > 0 && (
          <div className="max-w-7xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: "Wind Data Points", value: solarWindData.length },
              { label: "IMF Data Points", value: imfData.length },
              {
                label: "Time Range",
                value: solarWindData.length > 1
                  ? `${formatTime(solarWindData[0].time_tag)} → ${formatTime(last(solarWindData)!.time_tag)}`
                  : "—",
              },
              {
                label: "Storm Risk",
                value: currentBz < -10 ? "High" : currentBz < -5 ? "Moderate" : "Low",
              },
            ].map((item) => (
              <GlassCard key={item.label}>
                <div className="p-4">
                  <p className="text-xs text-gray-500 mb-1">{item.label}</p>
                  <p className="text-sm font-semibold text-gray-200">{item.value}</p>
                </div>
              </GlassCard>
            ))}
          </div>
        )}
      </section>

      {/* Service Cards */}
      <ServiceCards cards={SOLAR_WIND_CARDS} />
    </>
  );
}
