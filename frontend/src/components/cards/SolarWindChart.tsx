"use client";

import { useEffect, useLayoutEffect, useRef, useState } from "react";
import dynamic from "next/dynamic";
import { getAllSolarWindData } from "@/lib/api";

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

// SSR-safe layout effect
const useIsomorphicLayoutEffect =
  typeof window !== "undefined" ? useLayoutEffect : useEffect;

export default function SolarWindChart() {
  const [solarWind, setSolarWind] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [containerWidth, setContainerWidth] = useState<number>(700);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    getAllSolarWindData()
      .then((data) => {
        setSolarWind(data.solar_wind ?? []);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  useIsomorphicLayoutEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    setContainerWidth(el.getBoundingClientRect().width);

    const observer = new ResizeObserver(([entry]) => {
      if (entry.contentRect.width > 0) {
        setContainerWidth(entry.contentRect.width);
      }
    });
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  const isSmall = containerWidth < 500;
  
  // High-res scalar
  const scale = containerWidth > 700 ? containerWidth / 700 : 1;

  if (loading)
    return <div className="text-white/40 text-sm h-full flex items-center justify-center">Loading Solar Wind Data...</div>;
  if (!solarWind.length)
    return <div className="text-white/40 text-sm h-full flex items-center justify-center">No solar wind data available.</div>;

  return (
    <div ref={containerRef} className="w-full h-80 lg:h-96 min-h-[300px]">
      <Plot
        key={`plotly-scale-${Math.round(scale * 10)}`}
        data={[
          {
            x: solarWind.map((d) => d.time_tag),
            y: solarWind.map((d) => d.speed),
            type: "scatter",
            mode: "lines",
            name: "Speed (km/s)",
            line: { color: "#00E5FF", width: 1.5 * scale },
            yaxis: "y",
          },
          {
            x: solarWind.map((d) => d.time_tag),
            y: solarWind.map((d) => d.density),
            type: "scatter",
            mode: "lines",
            name: "Density (p/cm³)",
            line: { color: "#B388FF", width: 1.5 * scale },
            yaxis: "y2",
          },
        ]}
        layout={{
          paper_bgcolor: "transparent",
          plot_bgcolor: "transparent",
          autosize: true,

          title: {
            text: "Solar Wind Speed & Density",
            font: { color: "#fff", size: (isSmall ? 11 : 13) * scale },
            pad: { t: 4 },
          },

          xaxis: {
            title: isSmall ? undefined : { text: "Time (UTC)", font: { size: 11 * scale } },
            color: "#aaa",
            showgrid: true,
            gridcolor: "#ffffff15",
            tickfont: { size: (isSmall ? 8 : 10) * scale },
            tickangle: isSmall ? -45 : 0,
            nticks: isSmall ? 5 : 8,
          },

          yaxis: {
            title: isSmall ? undefined : { text: "Speed (km/s)", font: { size: 11 * scale } },
            color: "#00E5FF",
            showgrid: true,
            gridcolor: "#ffffff15",
            tickfont: { size: (isSmall ? 8 : 10) * scale },
          },

          yaxis2: {
            title: isSmall ? undefined : { text: "Density (p/cm³)", font: { size: 11 * scale } },
            color: "#B388FF",
            overlaying: "y",
            side: "right",
            showgrid: false,
            tickfont: { size: (isSmall ? 8 : 10) * scale },
          },

          legend: {
            orientation: "h",
            x: 0.5,
            xanchor: "center",
            y: -0.22,
            yanchor: "top",
            font: { color: "#ccc", size: (isSmall ? 9 : 11) * scale },
            bgcolor: "transparent",
          },

          margin: isSmall
            ? { t: 36, l: 42, r: 42, b: 60 }
            : { t: 40 * scale, l: 60 * scale, r: 60 * scale, b: 70 * scale },

          font: { family: "Arial", size: 11 * scale, color: "#ccc" },
        }}
        config={{ displayModeBar: false, responsive: true }}
        useResizeHandler
        style={{ width: "100%", height: "100%" }}
      />
    </div>
  );
}
