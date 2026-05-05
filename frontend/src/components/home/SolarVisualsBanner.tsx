"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { getMagnetogramImageUrl, getAIAImageUrl, getCMEImageUrl } from "@/lib/api"

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type ImageState = "loading" | "loaded" | "error"

interface VisualConfig {
  id: string
  label: string
  sublabel: string
  description: string
  getUrl: () => string
  accentFrom: string
  accentTo: string
  borderColor: string
  dotColor: string
  shimmerColor: string
}

// ---------------------------------------------------------------------------
// Visual config — one entry per solar image
// ---------------------------------------------------------------------------

const VISUALS: VisualConfig[] = [
  {
    id: "magnetogram",
    label: "HMI Magnetogram",
    sublabel: "Solar Magnetic Field",
    description:
      "Photospheric line-of-sight magnetic flux density captured by NASA SDO/HMI.",
    getUrl: getMagnetogramImageUrl,
    accentFrom: "from-blue-600/[0.12]",
    accentTo: "to-indigo-600/[0.06]",
    borderColor: "border-blue-400/20",
    dotColor: "bg-blue-400",
    shimmerColor: "from-blue-900/40 via-blue-800/20 to-blue-900/40",
  },
  {
    id: "aia171",
    label: "171 Å AIA Image",
    sublabel: "Extreme Ultraviolet",
    description:
      "SDO/AIA full-disk EUV imaging at 171 Å — quiet corona and upper transition region.",
    getUrl: () => getAIAImageUrl("171Å"),
    accentFrom: "from-amber-500/[0.12]",
    accentTo: "to-orange-600/[0.06]",
    borderColor: "border-amber-400/20",
    dotColor: "bg-amber-400",
    shimmerColor: "from-amber-900/40 via-amber-800/20 to-amber-900/40",
  },
  {
    id: "cme",
    label: "CME Coronagraph",
    sublabel: "LASCO C2",
    description:
      "SOHO/LASCO coronagraph occludes the solar disk to reveal coronal mass ejections.",
    getUrl: () => "https://soho.nascom.nasa.gov/data/LATEST/current_c2.gif",
    accentFrom: "from-rose-600/[0.12]",
    accentTo: "to-pink-600/[0.06]",
    borderColor: "border-rose-400/20",
    dotColor: "bg-rose-400",
    shimmerColor: "from-rose-900/40 via-rose-800/20 to-rose-900/40",
  },
]

// ---------------------------------------------------------------------------
// Sub-component: single visual card
// ---------------------------------------------------------------------------

const cardVariants = {
  hidden: { opacity: 0, y: 28 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: {
      delay: i * 0.12,
      duration: 0.55,
      ease: [0.22, 1, 0.36, 1] as [number, number, number, number],
    },
  }),
}

function SolarImageCard({
  config,
  index,
}: {
  config: VisualConfig
  index: number
}) {
  const [state, setState] = useState<ImageState>("loading")
  const imageUrl = config.getUrl()

  return (
    <motion.div
      custom={index}
      variants={cardVariants}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: "-60px" }}
      className={`
        relative flex flex-col overflow-hidden rounded-2xl
        bg-gradient-to-b ${config.accentFrom} ${config.accentTo}
        border ${config.borderColor}
        backdrop-blur-xl
        shadow-2xl
        group
      `}
      style={{
        background: `
          linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%)
        `,
        boxShadow: "0 8px 40px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.07)",
      }}
    >
      {/* ── Header ── */}
      <div className="px-5 pt-5 pb-3 flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-white/35 mb-0.5">
            {config.sublabel}
          </p>
          <h3 className="text-sm font-semibold text-white/90 leading-tight truncate">
            {config.label}
          </h3>
        </div>

        {/* Live indicator */}
        <span className="flex items-center gap-1.5 shrink-0 mt-0.5">
          <span className="relative flex h-2 w-2">
            <span
              className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-60 ${config.dotColor}`}
            />
            <span
              className={`relative inline-flex rounded-full h-2 w-2 ${config.dotColor}`}
            />
          </span>
          <span className="text-[10px] text-white/30 font-medium tracking-wide">LIVE</span>
        </span>
      </div>

      {/* ── Image area ── */}
      <div className="relative mx-4 rounded-xl overflow-hidden bg-black/40 aspect-square">
        {/* Loading shimmer */}
        {state === "loading" && (
          <div
            className={`absolute inset-0 bg-gradient-to-r ${config.shimmerColor} animate-pulse`}
          >
            <div className="absolute inset-0 flex items-center justify-center">
              <svg
                className="w-6 h-6 text-white/20 animate-spin"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="2"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                />
              </svg>
            </div>
          </div>
        )}

        {/* Error state */}
        {state === "error" && (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-2">
            <svg
              className="w-8 h-8 text-white/20"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M12 9v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <p className="text-white/25 text-xs">Image unavailable</p>
          </div>
        )}

        {/* The image itself */}
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
  src={imageUrl}
  alt={config.label}
  loading={config.id === "cme" ? "eager" : "lazy"}   // ⭐ ADD THIS LINE
  decoding="async"                                   // ⭐ ADD THIS LINE
  onLoad={() => setState("loaded")}
  onError={() => setState("error")}
          className={`
            w-full h-full object-cover transition-opacity duration-500
            ${state === "loaded" ? "opacity-100" : "opacity-0"}
            group-hover:scale-[1.02] transition-transform duration-700
          `}
        />

        {/* Subtle vignette overlay */}
        <div
          className="absolute inset-0 pointer-events-none rounded-xl"
          style={{
            background:
              "radial-gradient(ellipse at center, transparent 55%, rgba(0,0,0,0.45) 100%)",
          }}
        />
      </div>

      {/* ── Description ── */}
      <div className="px-5 py-4">
        <p className="text-[11px] leading-relaxed text-white/35">
          {config.description}
        </p>
      </div>
    </motion.div>
  )
}

// ---------------------------------------------------------------------------
// Main export
// ---------------------------------------------------------------------------

export default function SolarVisualsBanner() {
  return (
    <section className="relative px-4 sm:px-6 lg:px-8 pb-24">
      {/* Section header */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-40px" }}
        transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
        className="mb-8 flex items-end justify-between"
      >
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-white/30 mb-1">
            Real-time Imaging
          </p>
          <h2 className="text-xl sm:text-2xl font-black tracking-tight text-white/90">
            Solar Observatory
          </h2>
        </div>
        <span className="hidden sm:flex items-center gap-2 text-[10px] text-white/25 uppercase tracking-widest">
          <span className="w-8 h-px bg-white/10" />
          NASA SDO · SOHO
        </span>
      </motion.div>

      {/* 3-column grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5">
        {VISUALS.map((config, i) => (
          <SolarImageCard key={config.id} config={config} index={i} />
        ))}
      </div>
    </section>
  )
}
