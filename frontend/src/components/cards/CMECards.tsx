"use client"

import { useEffect, useState } from "react"
import { getCMEData, getCMEImageUrl } from "@/lib/api"

interface CMEEvent {
  activityID: string
  startTime: string
  sourceLocation: string
  speed?: number
  latitude?: number
  longitude?: number
  halfAngle?: number
  type?: string
  impactProbability?: string
  note?: string
  instruments: string[]
}

// shared hook — fetches once, used by all 4 cards
export function useCMEData() {
  const [events, setEvents] = useState<CMEEvent[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getCMEData()
      .then((data) => setEvents(data.cme_events ?? []))
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  return { events, loading, latest: events[events.length - 1] ?? null }
}

// ─── Card 01: CME Velocity ────────────────────────────────────────────────────
export function CMEVelocityContent() {
  const { latest, loading } = useCMEData()

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12 items-center w-full h-full mt-6">
      <div className="flex flex-col justify-center space-y-4">
        <p className="text-lg text-zinc-300 leading-relaxed">
          Coronal Mass Ejections are massive eruptions of plasma and magnetic
          field from the Sun's corona.
        </p>
        {loading && <p className="text-white/40 text-sm">Loading CME data...</p>}
        {latest && (
          <div className="space-y-2">
            <p className="text-sm text-white/50 uppercase tracking-widest">Latest CME</p>
            <p className="text-xs text-white/40">{latest.activityID}</p>
            <p className="text-xs text-white/40">
              {new Date(latest.startTime).toUTCString()}
            </p>
          </div>
        )}
      </div>

      {/* Speed gauge */}
      <div className="flex flex-col items-center justify-center space-y-2">
        {latest?.speed ? (
          <>
            <p className="text-7xl font-black text-orange-400">
              {latest.speed.toLocaleString()}
            </p>
            <p className="text-white/50 text-sm uppercase tracking-widest">km/s</p>
            <p className="text-white/30 text-xs">
              {latest.speed > 1500 ? "Extreme" : latest.speed > 800 ? "Fast" : "Moderate"} CME
            </p>
          </>
        ) : (
          !loading && <p className="text-white/40 text-sm">No speed data</p>
        )}
      </div>
    </div>
  )
}

// ─── Card 02: Magnetic Structure ──────────────────────────────────────────────
export function CMEMagneticContent() {
  const { latest, loading } = useCMEData()

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12 items-center w-full h-full mt-6">
      <div className="flex flex-col justify-center space-y-4">
        <p className="text-lg text-zinc-300 leading-relaxed">
          The magnetic structure determines how the CME interacts with Earth's
          magnetosphere.
        </p>
      </div>

      <div className="flex flex-col justify-center space-y-3">
        {loading && <p className="text-white/40 text-sm">Loading...</p>}
        {latest && (
          <>
            <div className="flex justify-between border-b border-white/10 pb-2">
              <span className="text-white/50 text-sm">Type</span>
              <span className="text-white text-sm font-medium">{latest.type ?? "N/A"}</span>
            </div>
            <div className="flex justify-between border-b border-white/10 pb-2">
              <span className="text-white/50 text-sm">Latitude</span>
              <span className="text-white text-sm font-medium">
                {latest.latitude != null ? `${latest.latitude}°` : "N/A"}
              </span>
            </div>
            <div className="flex justify-between border-b border-white/10 pb-2">
              <span className="text-white/50 text-sm">Longitude</span>
              <span className="text-white text-sm font-medium">
                {latest.longitude != null ? `${latest.longitude}°` : "N/A"}
              </span>
            </div>
            <div className="flex justify-between border-b border-white/10 pb-2">
              <span className="text-white/50 text-sm">Half Angle</span>
              <span className="text-white text-sm font-medium">
                {latest.halfAngle != null ? `${latest.halfAngle}°` : "N/A"}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-white/50 text-sm">Location</span>
              <span className="text-white text-sm font-medium">
                {latest.sourceLocation || "Unknown"}
              </span>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

// ─── Card 03: Impact Probability ─────────────────────────────────────────────
export function CMEImpactContent() {
  const { events, loading } = useCMEData()

  const counts = { High: 0, Moderate: 0, Low: 0 }
  events.forEach((e) => {
    if (e.impactProbability === "High") counts.High++
    else if (e.impactProbability === "Moderate") counts.Moderate++
    else counts.Low++
  })

  const latest = events[events.length - 1]

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12 items-center w-full h-full mt-6">
      <div className="flex flex-col justify-center space-y-4">
        <p className="text-lg text-zinc-300 leading-relaxed">
          Impact probability depends on CME trajectory, angular width, and
          speed relative to the Sun-Earth line.
        </p>
        {latest && (
          <div>
            <p className="text-sm text-white/50 uppercase tracking-widest mb-2">
              Latest Event
            </p>
            <span
              className={`px-4 py-2 rounded-full text-sm font-bold ${
                latest.impactProbability === "High"
                  ? "bg-red-500/20 text-red-300"
                  : latest.impactProbability === "Moderate"
                  ? "bg-yellow-500/20 text-yellow-300"
                  : "bg-green-500/20 text-green-300"
              }`}
            >
              {latest.impactProbability} Impact Risk
            </span>
          </div>
        )}
      </div>

      {/* Last 10 events breakdown */}
      <div className="flex flex-col justify-center space-y-4">
        {loading && <p className="text-white/40 text-sm">Loading...</p>}
        {!loading && (
          <>
            <p className="text-sm text-white/50 uppercase tracking-widest">
              Last 10 Events
            </p>
            <div className="space-y-3">
              {(["High", "Moderate", "Low"] as const).map((level) => (
                <div key={level} className="flex items-center gap-3">
                  <span className="text-white/60 text-sm w-20">{level}</span>
                  <div className="flex-1 bg-white/10 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all ${
                        level === "High"
                          ? "bg-red-400"
                          : level === "Moderate"
                          ? "bg-yellow-400"
                          : "bg-green-400"
                      }`}
                      style={{ width: `${(counts[level] / 10) * 100}%` }}
                    />
                  </div>
                  <span className="text-white/40 text-sm w-4">{counts[level]}</span>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  )
}

// ─── Card 04: Coronagraph Image ───────────────────────────────────────────────
export function CMEImageContent() {
  return (
    <div className="flex flex-col lg:flex-row items-center justify-between gap-8 lg:gap-12 w-full h-full min-h-0 mt-4 lg:mt-0">

      {/* LEFT */}
      <div className="flex flex-col justify-center max-w-xl space-y-4 w-full">
        <p className="text-lg text-zinc-300 leading-relaxed">
          LASCO coronagraph blocks the bright solar disk to reveal faint
          coronal structures and CMEs propagating outward.
        </p>
      </div>

      {/* RIGHT */}
      <div className="flex items-center justify-center w-full h-full min-h-0 py-4">
        <img
          src="https://soho.nascom.nasa.gov/data/LATEST/current_c2.gif"
          alt="LASCO CME Coronagraph"
          className="h-full max-h-[350px] w-auto max-w-[90%] lg:max-w-full aspect-square object-contain rounded-xl shadow-2xl"
        />
      </div>

    </div>
  )
}

// ─── Card 05: CME Event Log (scrollable table) ────────────────────────────────
  export function CMEEventLog() {
    const { events, loading } = useCMEData()

    return (
      <div className="w-full h-full mt-6 flex flex-col overflow-hidden">

        {/* header row - hidden on mobile if too small, or let it scroll horizontally */}
        <div className="w-full overflow-x-auto custom-scroll -mx-2 px-2">
          <div className="min-w-[500px]">
        <div className="grid grid-cols-6 gap-2 px-3 pb-2 border-b border-white/10">
          <span className="text-white/40 text-xs uppercase tracking-widest">ID</span>
          <span className="text-white/40 text-xs uppercase tracking-widest">Time</span>
          <span className="text-white/40 text-xs uppercase tracking-widest">Speed</span>
          <span className="text-white/40 text-xs uppercase tracking-widest">Type</span>
          <span className="text-white/40 text-xs uppercase tracking-widest">Location</span>
          <span className="text-white/40 text-xs uppercase tracking-widest">Risk</span>
        </div>

        {/* scrollable rows */}
        <div className="flex-1 overflow-y-auto space-y-1 mt-2 pr-2 pb-6 custom-scroll"
          style={{ maxHeight: "calc(65vh - 160px)" }}
        >
          {loading && (
            <p className="text-white/30 text-sm text-center mt-8">
              Loading CME events...
            </p>
          )}

          {!loading && events.length === 0 && (
            <p className="text-white/30 text-sm text-center mt-8">
              No CME events found.
            </p>
          )}

          {events.map((cme, i) => (
            <div
              key={i}
              className="grid grid-cols-6 gap-2 px-3 py-2 rounded-xl hover:bg-white/5 transition group"
            >
              {/* ID */}
              <span className="text-white/50 text-xs truncate" title={cme.activityID}>
                {cme.activityID?.split("-").slice(-2).join("-") ?? "—"}
              </span>

              {/* Time */}
              <span className="text-white/60 text-xs">
                {cme.startTime
                  ? new Date(cme.startTime).toLocaleDateString("en-US", {
                      month: "short", day: "numeric", hour: "2-digit", minute: "2-digit"
                    })
                  : "—"}
              </span>

              {/* Speed */}
              <span className="text-orange-300 text-xs font-medium">
                {cme.speed ? `${cme.speed} km/s` : "N/A"}
              </span>

              {/* Type */}
              <span className="text-white/60 text-xs">
                {cme.type ?? "—"}
              </span>

              {/* Location */}
              <span className="text-white/60 text-xs">
                {cme.sourceLocation || "—"}
              </span>

              {/* Risk badge */}
              <span
                className={`text-xs font-bold px-2 py-0.5 rounded-full w-fit ${
                  cme.impactProbability === "High"
                    ? "bg-red-500/20 text-red-300"
                    : cme.impactProbability === "Moderate"
                    ? "bg-yellow-500/20 text-yellow-300"
                    : "bg-green-500/20 text-green-300"
                }`}
              >
                {cme.impactProbability ?? "Low"}
              </span>
            </div>
          ))}
          </div></div>
        </div>

      </div>
    )
  }
