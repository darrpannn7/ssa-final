"use client";

import { LineChart, Line, ResponsiveContainer, Tooltip, YAxis } from "recharts";

// ─── Gauge ───────────────────────────────────────────────────────────────────

function Gauge({ value, min, max, unit, label, color = "#38bdf8" }: {
  value: number; min: number; max: number; unit: string; label: string; color?: string;
}) {
  const clampedValue = Math.max(min, Math.min(max, value));
  const pct = (clampedValue - min) / (max - min);
  // Half-circle: from -180 (left) to 0 (right)
  const angle = -180 + pct * 180;
  const r = 50;
  const cx = 70, cy = 65; // Shifted center down to account for missing bottom half

  const startAngle = -180;
  const endAngle = 0;
  const arcPath = (start: number, end: number, radius: number) => {
    // Prevent invalid SVG paths if start == end (0% fill)
    if (Math.abs(end - start) < 0.01) return "";
    const s = (start * Math.PI) / 180;
    const e = (end * Math.PI) / 180;
    const x1 = cx + radius * Math.cos(s);
    const y1 = cy + radius * Math.sin(s);
    const x2 = cx + radius * Math.cos(e);
    const y2 = cy + radius * Math.sin(e);
    const largeArc = end - start > 180 ? 1 : 0;
    return `M ${x1} ${y1} A ${radius} ${radius} 0 ${largeArc} 1 ${x2} ${y2}`;
  };

  const fillEnd = startAngle + pct * 180;
  const needleX = cx + (r - 10) * Math.cos((angle * Math.PI) / 180);
  const needleY = cy + (r - 10) * Math.sin((angle * Math.PI) / 180);

  return (
    <div className="flex flex-col items-center gap-0.5 w-full">
      {/* SVG scales with container width via viewBox */}
      <svg viewBox="0 0 140 115" className="w-full" style={{ maxWidth: "8em" }}>
        {/* Background track (semi-circle) */}
        <path d={arcPath(startAngle, endAngle, r)} stroke="rgba(255,255,255,0.08)" strokeWidth="8" fill="none" strokeLinecap="round" />
        {/* Fill arc */}
        {pct > 0 && <path d={arcPath(startAngle, fillEnd, r)} stroke={color} strokeWidth="8" fill="none" strokeLinecap="round" opacity="0.85" />}
        {/* Needle */}
        <line x1={cx} y1={cy} x2={needleX} y2={needleY} stroke="white" strokeWidth="2.5" strokeLinecap="round" opacity="0.9" />
        <circle cx={cx} cy={cy} r="4" fill="white" opacity="0.9" />
        {/* Min/Max Labels - Positioned exactly under the ends of the half-circle */}
        <text x={cx - r} y={cy + 18} fontSize="10" fill="rgba(255,255,255,0.4)" textAnchor="middle">{min}</text>
        <text x={cx + r} y={cy + 18} fontSize="10" fill="rgba(255,255,255,0.4)" textAnchor="middle">{max}</text>
        {/* Primary Value - Positioned centered below the needle pivot */}
        <text x={cx} y={cy + 30} fontSize="22" fontWeight="900" fill={color} textAnchor="middle">{value.toFixed(0)}</text>
      </svg>
      <p className="text-[0.6em] text-white/40 -mt-2">{unit}</p>
      <p className="text-[0.6em] text-white/60 uppercase tracking-widest text-center">{label}</p>
    </div>
  );
}

// ─── KpGauge (bar chart style) ────────────────────────────────────────────────

function KpGauge({ kp }: { kp: number }) {
  const bars = Array.from({ length: 9 }, (_, i) => ({
    i: i + 1,
    active: i + 1 <= kp,
    color: i < 4 ? "#22c55e" : i < 6 ? "#eab308" : "#ef4444",
  }));

  return (
    <div className="flex flex-col items-center gap-1 w-full">
      <div className="flex items-end gap-[0.2em] w-full justify-center" style={{ height: "3em" }}>
        {bars.map((b) => (
          <div
            key={b.i}
            className="flex-1 rounded-sm transition-all"
            style={{
              height: `${(b.i / 9) * 100}%`,
              background: b.active ? b.color : "rgba(255,255,255,0.08)",
            }}
          />
        ))}
      </div>
      <p className="text-base font-black text-white leading-none mt-1">{kp.toFixed(1)}</p>
      <p className="text-[0.6em] text-white/40">Kp</p>
      <p className="text-[0.6em] text-white/60 uppercase tracking-widest">Kp Index</p>
    </div>
  );
}

// ─── Mini Sparkline ──────────────────────────────────────────────────────────

function Sparkline({ data, color, logScale = false }: {
  data: { value: number }[];
  color: string;
  logScale?: boolean;
}) {
  const displayData = logScale
    ? data.map((d) => ({ value: d.value > 0 ? Math.log10(d.value) : -9 }))
    : data;

  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={displayData}>
        <YAxis domain={["auto", "auto"]} hide />
        <Line
          type="monotone"
          dataKey="value"
          stroke={color}
          strokeWidth={1.5}
          dot={false}
          isAnimationActive={false}
        />
        <Tooltip
          contentStyle={{ background: "#0a0a14", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8, padding: "4px 8px" }}
          labelStyle={{ display: "none" }}
          itemStyle={{ color, fontSize: 11 }}
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          formatter={(v: any) => [
            logScale && typeof v === "number"
              ? `10^${v.toFixed(1)}`
              : typeof v === "number" ? v.toFixed(2) : String(v ?? ""),
            "",
          ]}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

// ─── Metric Card ─────────────────────────────────────────────────────────────

function MetricCard({ children, label }: { children: React.ReactNode; label?: string }) {
  return (
    <div className="flex flex-col items-center justify-between bg-white/[0.03] border border-white/10 rounded-xl px-3 py-3 gap-2 h-full">
      {label && (
        <p className="text-[0.6em] uppercase tracking-widest text-white/30 text-center w-full">{label}</p>
      )}
      {children}
    </div>
  );
}

// ─── Satellite Gauge ──────────────────────────────────────────────────────────

function SatGauge({ risk }: { risk: "CAUTION" | "NORMAL" | "HIGH" }) {
  const color = risk === "HIGH" ? "#ef4444" : risk === "CAUTION" ? "#eab308" : "#22c55e";
  const needleAngle = -180 + (risk === "HIGH" ? 160 : risk === "CAUTION" ? 100 : 40);
  const nx = 40 + 25 * Math.cos(needleAngle * Math.PI / 180);
  const ny = 50 + 25 * Math.sin(needleAngle * Math.PI / 180);
  const dashOffset = risk === "HIGH" ? 10 : risk === "CAUTION" ? 50 : 90;

  return (
    <div className="flex flex-col items-center gap-2 w-full">
      {/* SVG uses viewBox so it scales with container */}
      <svg viewBox="0 0 80 60" className="w-full" style={{ maxWidth: "7em" }}>
        <path d="M 8 50 A 32 32 0 0 1 72 50" stroke="rgba(255,255,255,0.08)" strokeWidth="8" fill="none" strokeLinecap="round" />
        <path
          d="M 8 50 A 32 32 0 0 1 72 50"
          stroke={color}
          strokeWidth="8"
          fill="none"
          strokeLinecap="round"
          strokeDasharray="100 200"
          strokeDashoffset={dashOffset}
        />
        <line x1="40" y1="50" x2={nx} y2={ny} stroke="white" strokeWidth="2" strokeLinecap="round" />
        <circle cx="40" cy="50" r="3" fill="white" />
      </svg>
      <div className="text-center">
        <p className="text-sm font-black" style={{ color }}>{risk}</p>
        <p className="text-[0.6em] text-white/30 uppercase tracking-widest">G2</p>
      </div>
    </div>
  );
}

// ─── Props ───────────────────────────────────────────────────────────────────

interface MetricsRowProps {
  xrayFluxData: number[];
  protonFluxData: number[];
  windSpeed: number;
  windDensity: number;
  kpIndex: number;
  satelliteRisk: "CAUTION" | "NORMAL" | "HIGH";
}

// ─── Main Component ──────────────────────────────────────────────────────────

export default function MetricsRow({
  xrayFluxData,
  protonFluxData,
  windSpeed,
  windDensity,
  kpIndex,
  satelliteRisk,
}: MetricsRowProps) {
  const xrayPoints = xrayFluxData.map((v) => ({ value: v }));
  const protonPoints = protonFluxData.map((v) => ({ value: v }));

  const latestXray = xrayFluxData.at(-1) ?? 0;
  const latestProton = protonFluxData.at(-1) ?? 0;

  return (
    <div className="px-3 py-2">
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2" style={{ minHeight: "clamp(120px, 14vh, 280px)" }}>

        {/* X-Ray Flux */}
        <MetricCard label="X-Ray Flux (GOES-16)">
          <div className="w-full flex flex-col gap-1 flex-1">
            <p className="text-[0.7em] font-mono text-yellow-400 font-bold text-center">
              {latestXray > 0 ? latestXray.toExponential(1) : "--"} W/m²
            </p>
            <div className="flex-1" style={{ minHeight: "2.5em" }}>
              <Sparkline data={xrayPoints} color="#facc15" logScale />
            </div>
          </div>
        </MetricCard>

        {/* Proton Flux */}
        <MetricCard label="Proton Flux (>10 MeV)">
          <div className="w-full flex flex-col gap-1 flex-1">
            <p className="text-[0.7em] font-mono text-pink-400 font-bold text-center">
              {latestProton.toFixed(1)} pfu
            </p>
            <div className="flex-1" style={{ minHeight: "2.5em" }}>
              <Sparkline data={protonPoints} color="#f472b6" logScale />
            </div>
          </div>
        </MetricCard>

        {/* Solar Wind Speed Gauge */}
        <MetricCard label="Solar Wind Speed (DSCOVR)">
          <Gauge value={windSpeed} min={300} max={900} unit="km/s" label="Wind Speed" color="#38bdf8" />
        </MetricCard>

        {/* Solar Wind Density Gauge */}
        <MetricCard label="Solar Wind Density (DSCOVR)">
          <Gauge value={windDensity} min={1} max={100} unit="p/cm³" label="Density" color="#a78bfa" />
        </MetricCard>

        {/* Kp Index */}
        <MetricCard label="Kp Index (Planetary)">
          <KpGauge kp={kpIndex} />
        </MetricCard>

        {/* Satellite Risk */}
        <MetricCard label="Satellite Risk (Overall)">
          <SatGauge risk={satelliteRisk} />
        </MetricCard>

      </div>
    </div>
  );
}
