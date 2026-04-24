"use client"

import { useEffect, useState } from "react"
import { getSolarFlares } from "@/lib/api"

interface FlareEvent {
  classType: string
  startTime: string
  peakTime: string
  endTime: string
  activeRegion: string | number | null
}

function getClassColor(classType: string) {
  if (!classType) return { bg: "bg-white/10", text: "text-white/50" }
  const c = classType[0].toUpperCase()
  if (c === "X") return { bg: "bg-red-500/20", text: "text-red-300" }
  if (c === "M") return { bg: "bg-orange-500/20", text: "text-orange-300" }
  if (c === "C") return { bg: "bg-yellow-500/20", text: "text-yellow-300" }
  if (c === "B") return { bg: "bg-green-500/20", text: "text-green-300" }
  return { bg: "bg-blue-500/20", text: "text-blue-300" }
}

function formatTime(t: string) {
  if (!t) return "—"
  return new Date(t).toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "UTC",
    timeZoneName: "short",
  })
}

export default function FlareEventLog() {
  const [flares, setFlares] = useState<FlareEvent[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchFlares = async () => {
      try {
        const data = await getSolarFlares()

        // ✅ FIX: ensure it's always an array
        const flaresArray = Array.isArray(data)
          ? data
          : data?.flares || []

        // ✅ safe slicing
        setFlares(flaresArray.slice(-16).reverse())
      } catch (err) {
        console.error("Flare fetch error:", err)
        setFlares([])
      } finally {
        setLoading(false)
      }
    }

    fetchFlares()
  }, [])

  return (
    <div className="w-full h-full mt-6 flex flex-col overflow-hidden">

      {/* HEADER */}
      <div className="sticky top-0 z-10 grid grid-cols-5 gap-2 px-3 pb-2 border-b border-white/10">
        <span className="text-white/40 text-xs uppercase tracking-widest">Class</span>
        <span className="text-white/40 text-xs uppercase tracking-widest">Start</span>
        <span className="text-white/40 text-xs uppercase tracking-widest">Peak</span>
        <span className="text-white/40 text-xs uppercase tracking-widest">End</span>
        <span className="text-white/40 text-xs uppercase tracking-widest">Region</span>
      </div>

      {/* CONTENT */}
      <div className="flex-1 overflow-y-auto space-y-1 mt-2 pr-2 pb-6 custom-scroll">

        {loading && (
          <p className="text-white/30 text-sm text-center mt-8">
            Loading flare events...
          </p>
        )}

        {!loading && flares.length === 0 && (
          <p className="text-white/30 text-sm text-center mt-8">
            No flare events found.
          </p>
        )}

        {flares.map((flare, i) => {
          const { bg, text } = getClassColor(flare.classType)

          return (
            <div
              key={i}
              className="grid grid-cols-5 gap-2 px-3 py-2 rounded-xl hover:bg-white/5 transition"
            >
              <span className={`text-xs font-bold px-2 py-0.5 rounded-full w-fit ${bg} ${text}`}>
                {flare.classType ?? "—"}
              </span>

              <span className="text-white/60 text-xs">
                {formatTime(flare.startTime)}
              </span>

              <span className="text-white text-xs font-medium">
                {formatTime(flare.peakTime)}
              </span>

              <span className="text-white/60 text-xs">
                {formatTime(flare.endTime)}
              </span>

              <span className="text-white/50 text-xs">
                {flare.activeRegion ? `AR ${flare.activeRegion}` : "—"}
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}