"use client";

import { useState } from "react";
import { getMagnetogramImageUrl, getAIAImageUrl, getCMEImageUrl } from "@/lib/api";

interface DashboardImage {
  title: string;
  subtitle: string;
  url: string;
  source: string;
}

function ImagePanel({ img }: { img: DashboardImage }) {
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState(false);

  return (
    <div className="relative overflow-hidden rounded-xl bg-black border border-white/10 flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-white/10">
        <div>
          <p className="text-[10px] text-white/40 uppercase tracking-widest">{img.subtitle}</p>
          <p className="text-[12px] text-white/80 font-semibold">{img.title}</p>
        </div>
        <span className="relative flex h-1.5 w-1.5">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-60" />
          <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-green-400" />
        </span>
      </div>

      {/* Image — height = 32% of viewport height, always proportional */}
      <div className="relative bg-black flex items-center justify-center" style={{ height: "clamp(220px, 32vh, 700px)" }}>
        {!loaded && !error && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-6 h-6 border-2 border-white/20 border-t-white/60 rounded-full animate-spin" />
          </div>
        )}
        {error && (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-2">
            <svg className="w-8 h-8 text-white/20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                d="M12 9v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="text-white/25 text-[11px]">Image unavailable</p>
          </div>
        )}
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={img.url}
          alt={img.title}
          className={`max-w-full max-h-full w-auto h-auto object-contain transition-opacity duration-500 ${loaded ? "opacity-100" : "opacity-0"}`}
          style={{ maxHeight: "clamp(220px, 32vh, 700px)" }}
          onLoad={() => setLoaded(true)}
          onError={() => setError(true)}
        />
      </div>

      {/* Footer */}
      <div className="px-3 py-1.5 border-t border-white/5">
        <p className="text-[10px] text-white/30 font-mono">{img.source}</p>
      </div>
    </div>
  );
}

export default function DashboardImages() {
  const images: DashboardImage[] = [
    {
      title: "Solar Magnetogram",
      subtitle: "HMI / SDO",
      url: getMagnetogramImageUrl(),
      source: "SDO/HMI — Line-of-sight magnetic flux",
    },
    {
      title: "Solar Corona",
      subtitle: "AIA 171Å",
      url: getAIAImageUrl("171Å"),
      source: "SDO/AIA 171Å — Extreme Ultraviolet",
    },
    {
      title: "CME / Coronagraph",
      subtitle: "SOHO/LASCO C2",
      url: getCMEImageUrl(),
      source: "SOHO/LASCO C2 — Coronagraph imaging",
    },
  ];

  return (
    <div className="px-3 py-2">
      <div className="flex items-center gap-2 mb-2">
        <div className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
        <p className="text-[10px] text-cyan-400 uppercase tracking-[0.2em] font-semibold">
          Near-Real-Time Solar Imagery
        </p>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {images.map((img) => (
          <ImagePanel key={img.title} img={img} />
        ))}
      </div>
    </div>
  );
}
