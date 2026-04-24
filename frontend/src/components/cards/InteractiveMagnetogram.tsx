"use client"

import { useEffect, useState } from "react"

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"

interface Flare {
  A: number; B: number; C: number; M: number; X: number
}

interface Region {
  id: number
  bbox: [number, number, number, number]
  strength: number
  area: number
  flare: Flare
}

export default function InteractiveMagnetogram() {
  const [regions, setRegions] = useState<Region[]>([])
  const [clicked, setClicked] = useState<Region | null>(null)
  const [loading, setLoading] = useState(true)
  const [imgSize, setImgSize] = useState({ w: 0, h: 0 })
  const [scale, setScale] = useState(1);
  const baseSize = 280;

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 1920) {
        setScale(window.innerWidth / 1920);
      } else {
        setScale(1);
      }
    };
    handleResize(); // Initial check
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const displaySize = { w: baseSize * scale, h: baseSize * scale };

  useEffect(() => {
    fetch(`${BASE_URL}/space-weather/magnetogram/regions`)
      .then(r => r.json())
      .then(data => setRegions(data.regions ?? []))
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  // Scale bbox from data coords (512x512) to display size
  function scaleBbox(bbox: [number, number, number, number]) {
    const [x1, y1, x2, y2] = bbox
    const scaleX = displaySize.w / 512
    const scaleY = displaySize.h / 512
    return {
      left: x1 * scaleX,
      top: y1 * scaleY,
      width: (x2 - x1) * scaleX,
      height: (y2 - y1) * scaleY,
    }
  }

  const flareClasses = ["A", "B", "C", "M", "X"] as const

  return (
    <div className="grid grid-cols-2 gap-12 items-center w-full h-full mt-6">

      {/* LEFT — info panel */}
      <div className="flex flex-col justify-center space-y-4 h-full">
        {!clicked ? (
          <>
            <p className="text-zinc-300 text-base leading-relaxed">
              Magnetograms reveal solar magnetic field structures.
              Click a <span className="text-yellow-400 font-semibold">yellow region</span> on the image for flare risk.
            </p>
            {loading && <p className="text-white/30 text-xs">Loading regions...</p>}
            {!loading && regions.length > 0 && (
              <div className="space-y-1">
                <p className="text-white/30 text-xs uppercase tracking-widest">Detected</p>
                <p className="text-white/60 text-sm">
                  {regions.length} active region{regions.length > 1 ? "s" : ""}
                </p>
              </div>
            )}
            {!loading && regions.length === 0 && (
              <p className="text-white/30 text-xs">No active regions detected</p>
            )}
          </>
        ) : (
          <div className="space-y-4 w-full">
            <div className="flex items-center justify-between">
              <p className="text-white/40 text-xs uppercase tracking-widest">
                Active Region AR{clicked.id}
              </p>
              <button
                onClick={() => setClicked(null)}
                className="text-white/30 hover:text-white/60 text-xs transition"
              >
                ✕ clear
              </button>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between border-b border-white/10 pb-1">
                <span className="text-white/50 text-sm">Field strength</span>
                <span className="text-white text-sm font-mono">{clicked.strength} G</span>
              </div>
              <div className="flex justify-between border-b border-white/10 pb-1">
                <span className="text-white/50 text-sm">Area</span>
                <span className="text-white text-sm font-mono">{clicked.area} px²</span>
              </div>
            </div>
            <div className="space-y-2">
              <p className="text-white/40 text-xs uppercase tracking-widest">Flare Probability</p>
              {flareClasses.map((cls) => {
                const val = clicked.flare[cls] ?? 0
                const color =
                  cls === "X" ? { bar: "bg-red-400", text: "text-red-400" } :
                    cls === "M" ? { bar: "bg-orange-400", text: "text-orange-400" } :
                      cls === "C" ? { bar: "bg-yellow-400", text: "text-yellow-400" } :
                        cls === "B" ? { bar: "bg-green-400", text: "text-green-400" } :
                          { bar: "bg-blue-400", text: "text-blue-400" }
                return (
                  <div key={cls} className="flex items-center gap-3">
                    <span className={`text-sm font-bold w-4 ${color.text}`}>{cls}</span>
                    <div className="flex-1 bg-white/10 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all duration-500 ${color.bar}`}
                        style={{ width: `${val}%` }}
                      />
                    </div>
                    <span className="text-white/40 text-sm w-8 text-right">{val}%</span>
                  </div>
                )
              })}
            </div>
          </div>
        )}
      </div>

      {/* RIGHT — image with clickable region overlays */}
      <div className="flex items-center justify-center w-full h-full">
        <div
          style={{
            position: "relative",
            width: `${displaySize.w}px`,
            height: `${displaySize.h}px`,
            flexShrink: 0,
          }}
        >
          {/* Magnetogram image from backend */}
          <img
            src={`${BASE_URL}/space-weather/magnetogram/image`}
            alt="HMI Magnetogram"
            style={{
              width: `${displaySize.w}px`,
              height: `${displaySize.h}px`,
              borderRadius: "50%",
              border: "1px solid rgba(255,255,255,0.1)",
              display: "block",
              objectFit: "cover",
            }}
          />

          {/* Clickable region overlays */}
          {regions.map((region) => {
            const s = scaleBbox(region.bbox)
            const isSelected = clicked?.id === region.id
            return (
              <div
                key={region.id}
                onClick={() => setClicked(region)}
                style={{
                  position: "absolute",
                  left: s.left,
                  top: s.top,
                  width: s.width,
                  height: s.height,
                  border: `1.5px solid ${isSelected ? "rgba(255,100,0,0.9)" : "rgba(255,200,0,0.85)"}`,
                  background: isSelected ? "rgba(255,100,0,0.15)" : "rgba(255,200,0,0.05)",
                  cursor: "pointer",
                  boxSizing: "border-box",
                }}
              >
                <span style={{
                  position: "absolute",
                  top: -14 * scale,
                  left: 0,
                  fontSize: `${9 * scale}px`,
                  fontFamily: "monospace",
                  fontWeight: "bold",
                  color: isSelected ? "rgba(255,100,0,1)" : "rgba(255,200,0,1)",
                  whiteSpace: "nowrap",
                }}>
                  AR{region.id}
                </span>
              </div>
            )
          })}
        </div>
      </div>

    </div>
  )
}