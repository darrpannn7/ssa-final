"use client";

import { useEffect, useState } from "react";

export default function DashboardHeader() {
  const [time, setTime] = useState<string>("");
  const [date, setDate] = useState<string>("");
  const [istTime, setIstTime] = useState<string>("");
  const [lastUpdated, setLastUpdated] = useState<string>("--");

  useEffect(() => {
    const tick = () => {
      const now = new Date();
      setTime(now.toUTCString().split(" ").slice(4, 5)[0]);
      setDate(now.toUTCString().split(" ").slice(0, 4).join(" "));
      // IST = UTC + 5:30
      const ist = new Date(now.getTime() + 5.5 * 60 * 60 * 1000);
      const hh = String(ist.getUTCHours()).padStart(2, "0");
      const mm = String(ist.getUTCMinutes()).padStart(2, "0");
      const ss = String(ist.getUTCSeconds()).padStart(2, "0");
      setIstTime(`${hh}:${mm}:${ss}`);
    };
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, []);

  // Sync last-updated from dashboard fetch (expose via window event)
  useEffect(() => {
    const handler = () => setLastUpdated("just now");
    window.addEventListener("dashboard:refreshed", handler);
    return () => window.removeEventListener("dashboard:refreshed", handler);
  }, []);

  return (
    <div
      className="flex items-center justify-between bg-black border-b border-white/10"
      style={{ padding: "clamp(8px, 1.5vh, 28px) clamp(12px, 2vw, 40px)" }}
    >
      {/* Left: timestamp — scales with em */}
      <div className="text-left" style={{ minWidth: "12em" }}>
        <p style={{ fontSize: "0.65em" }} className="text-white/50 font-mono">
          {date}
        </p>
        <p
          style={{ fontSize: "clamp(11px, 0.85em, 28px)", letterSpacing: "0.12em" }}
          className="text-cyan-400 font-mono font-semibold"
        >
          {time} UTC
        </p>
        <p
          style={{ fontSize: "clamp(10px, 0.80em, 26px)", letterSpacing: "0.12em" }}
          className="text-amber-400/80 font-mono font-semibold"
        >
          {istTime} IST
        </p>
        <p style={{ fontSize: "0.6em" }} className="text-white/30 mt-0.5">
          Last Updated: {lastUpdated}
        </p>
      </div>

      {/* Center: title — scales fluidly with viewport */}
      <div className="text-center flex-1 px-4">
        <h1
          className="font-black tracking-[0.15em] text-white uppercase"
          style={{ fontSize: "clamp(1.2rem, 3.5vw, 6rem)" }}
        >
          Orbital Perception
        </h1>
        <p
          className="text-white/40 tracking-wide mt-1"
          style={{ fontSize: "clamp(9px, 0.7em, 20px)" }}
        >
          Future of Space Weather Analytics is here
        </p>
      </div>

      {/* Right: live badge — scales with em */}
      <div style={{ minWidth: "12em" }} className="flex justify-end">
        <div
          className="flex items-center gap-2 bg-white/5 border border-white/10 rounded-full"
          style={{ padding: "0.4em 0.9em" }}
        >
          <span className="relative flex" style={{ width: "0.6em", height: "0.6em" }}>
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-60" />
            <span className="relative inline-flex rounded-full bg-green-400 w-full h-full" />
          </span>
          <span
            style={{ fontSize: "clamp(9px, 0.7em, 18px)" }}
            className="text-green-400 font-semibold tracking-wide"
          >
            LIVE
          </span>
        </div>
      </div>
    </div>
  );
}
