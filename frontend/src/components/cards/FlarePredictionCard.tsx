"use client";

/**
 * FlarePredictionCard.tsx
 * -----------------------
 * Drop this file into:
 *   frontend/src/components/solar-flare/FlarePredictionCard.tsx
 *
 * Then import and add it inside solar-flare/page.tsx:
 *   import FlarePredictionCard from "@/components/solar-flare/FlarePredictionCard";
 *   ...
 *   <FlarePredictionCard />
 */

import { useEffect, useState, useCallback } from "react";
import { Activity, AlertTriangle, CheckCircle, Zap, RefreshCw } from "lucide-react";

// ── Types ──────────────────────────────────────────────────────────
type FlareClass = "no_flare" | "A" | "B" | "C" | "M" | "X";

type PredictionData = {
  predicted_class:           FlareClass;
  confidence:                string;
  onset_window_minutes:      number;
  reasoning:                 string;
  surya_flare_risk:          string;
  surya_magnetic_complexity: number;
  goes_peak_flux:            number;
  model_source:              string;
  timestamp:                 string;
};

// ── Config ─────────────────────────────────────────────────────────
const CLASS_CONFIG: Record<FlareClass, {
  label: string;
  color: string;
  bg: string;
  border: string;
  glow: string;
  icon: React.FC<{ size?: number; className?: string }>;
}> = {
  no_flare: {
    label:  "No Flare",
    color:  "text-emerald-400",
    bg:     "bg-emerald-500/10",
    border: "border-emerald-500/30",
    glow:   "shadow-emerald-500/20",
    icon:   CheckCircle,
  },
  A: {
    label:  "A-Class",
    color:  "text-sky-400",
    bg:     "bg-sky-500/10",
    border: "border-sky-500/30",
    glow:   "shadow-sky-500/20",
    icon:   Activity,
  },
  B: {
    label:  "B-Class",
    color:  "text-blue-400",
    bg:     "bg-blue-500/10",
    border: "border-blue-500/30",
    glow:   "shadow-blue-500/20",
    icon:   Activity,
  },
  C: {
    label:  "C-Class",
    color:  "text-yellow-400",
    bg:     "bg-yellow-500/10",
    border: "border-yellow-500/30",
    glow:   "shadow-yellow-500/20",
    icon:   Activity,
  },
  M: {
    label:  "M-Class",
    color:  "text-orange-400",
    bg:     "bg-orange-500/10",
    border: "border-orange-500/30",
    glow:   "shadow-orange-500/20",
    icon:   AlertTriangle,
  },
  X: {
    label:  "X-Class",
    color:  "text-red-400",
    bg:     "bg-red-500/10",
    border: "border-red-500/30",
    glow:   "shadow-red-500/20",
    icon:   AlertTriangle,
  },
};

const REFRESH_INTERVAL_MS = 5 * 60 * 1000; // 5 minutes

// ── Helpers ────────────────────────────────────────────────────────

function formatFlux(flux: number): string {
  if (!flux || flux <= 0) return "N/A";
  return flux.toExponential(2);
}

function formatTimestamp(ts: string): string {
  try {
    return new Date(ts).toLocaleTimeString([], {
      hour: "2-digit", minute: "2-digit",
    });
  } catch {
    return ts;
  }
}

function RiskBar({ value, label }: { value: number; label: string }) {
  const pct = Math.min(Math.max(value * 100, 0), 100);
  const color =
    pct > 70 ? "bg-red-500" :
    pct > 45 ? "bg-orange-400" :
               "bg-emerald-500";

  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs text-white/50">
        <span>{label}</span>
        <span className="font-mono">{value.toFixed(3)}</span>
      </div>
      <div className="h-1.5 w-full rounded-full bg-white/10">
        <div
          className={`h-full rounded-full transition-all duration-700 ${color}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

function Skeleton() {
  return (
    <div className="animate-pulse space-y-4">
      <div className="h-16 rounded-xl bg-white/5" />
      <div className="h-4 w-3/4 rounded bg-white/5" />
      <div className="h-4 w-1/2 rounded bg-white/5" />
      <div className="h-2 rounded bg-white/5" />
    </div>
  );
}

// ── Main component ─────────────────────────────────────────────────

export default function FlarePredictionCard() {
  const [data,      setData]      = useState<PredictionData | null>(null);
  const [loading,   setLoading]   = useState(true);
  const [error,     setError]     = useState<string | null>(null);
  const [lastFetch, setLastFetch] = useState<Date | null>(null);

  const fetchPrediction = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/flare-predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ use_live_data: true, include_explanation: true }),
        cache: "no-store",
      });
      if (!res.ok) {
        const text = await res.text().catch(() => "");
        throw new Error(`${res.status}: ${text || res.statusText}`);
      }
      const json: PredictionData = await res.json();
      setData(json);
      setLastFetch(new Date());
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Fetch failed";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial fetch + auto-refresh every 5 min
  useEffect(() => {
    fetchPrediction();
    const id = setInterval(fetchPrediction, REFRESH_INTERVAL_MS);
    return () => clearInterval(id);
  }, [fetchPrediction]);

  const cls     = (data?.predicted_class as FlareClass) ?? "no_flare";
  const cfg     = CLASS_CONFIG[cls] ?? CLASS_CONFIG["no_flare"];
  const Icon    = cfg.icon;
  const isFineT = data?.model_source?.includes("lora");

  return (
    <div className={`
      glass rounded-2xl p-5 border ${cfg.border}
      shadow-lg ${cfg.glow}
      transition-all duration-500
    `}>

      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Zap size={14} className="text-amber-400" />
          <span className="text-sm font-medium text-white/70">
            AI Flare Prediction
          </span>
        </div>
        <div className="flex items-center gap-2">
          {lastFetch && (
            <span className="text-xs text-white/30">
              {formatTimestamp(lastFetch.toISOString())}
            </span>
          )}
          <button
            onClick={fetchPrediction}
            disabled={loading}
            className="p-1 rounded-lg hover:bg-white/10 transition disabled:opacity-40"
            title="Refresh prediction"
          >
            <RefreshCw
              size={12}
              className={`text-white/40 ${loading ? "animate-spin" : ""}`}
            />
          </button>
        </div>
      </div>

      {/* Content */}
      {loading && !data ? (
        <Skeleton />
      ) : error ? (
        <div className="text-red-400 text-sm py-4 text-center">
          ⚠ {error}
          <button
            onClick={fetchPrediction}
            className="block mx-auto mt-2 text-xs text-white/40 hover:text-white/70"
          >
            Retry
          </button>
        </div>
      ) : data ? (
        <div className="space-y-4">

          {/* Class badge + onset */}
          <div className={`
            flex items-center justify-between
            rounded-xl px-4 py-3
            ${cfg.bg} border ${cfg.border}
          `}>
            <div className="flex items-center gap-3">
              <Icon size={22} className={cfg.color} />
              <div>
                <p className={`text-xl font-bold ${cfg.color}`}>
                  {cfg.label}
                </p>
                <p className="text-xs text-white/40 capitalize">
                  {data.confidence} confidence
                </p>
              </div>
            </div>
            {data.predicted_class !== "no_flare" && (
              <div className="text-right">
                <p className="text-sm font-semibold text-white/80">
                  ~{data.onset_window_minutes} min
                </p>
                <p className="text-xs text-white/30">onset</p>
              </div>
            )}
          </div>

          {/* GOES flux */}
          <div className="flex justify-between text-xs text-white/50">
            <span>Peak GOES flux</span>
            <span className="font-mono text-white/70">
              {formatFlux(data.goes_peak_flux)} W/m²
            </span>
          </div>

          {/* Surya risk bars */}
          <div className="space-y-2">
            <RiskBar
              value={
                data.surya_flare_risk.startsWith("High")   ? 0.85 :
                data.surya_flare_risk.startsWith("Moderate") ? 0.55 : 0.25
              }
              label="Surya flare risk"
            />
            <RiskBar
              value={data.surya_magnetic_complexity}
              label="Magnetic complexity"
            />
          </div>

          {/* Reasoning */}
          {data.reasoning && (
            <p className="text-xs text-white/40 leading-relaxed border-t border-white/5 pt-3">
              {data.reasoning.slice(0, 200)}
              {data.reasoning.length > 200 ? "…" : ""}
            </p>
          )}

          {/* Model source badge */}
          <div className="flex items-center gap-1.5 pt-1">
            <span className={`
              inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full border
              ${isFineT
                ? "bg-purple-500/10 text-purple-300 border-purple-500/20"
                : "bg-blue-500/10 text-blue-300 border-blue-500/20"
              }
            `}>
              <Zap size={9} />
              {isFineT ? "Fine-tuned LLaMA 3.1" : "Groq fallback"}
            </span>
          </div>

        </div>
      ) : null}
    </div>
  );
}
