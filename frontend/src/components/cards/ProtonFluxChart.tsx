"use client";

import { useEffect, useLayoutEffect, useRef, useState } from "react";
import dynamic from "next/dynamic";
import { getAllSEPData } from "@/lib/api";

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

// SSR-safe layout effect
const useIsomorphicLayoutEffect =
  typeof window !== "undefined" ? useLayoutEffect : useEffect;

export default function ProtonFluxChart() {
  const [protonData, setProtonData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [containerWidth, setContainerWidth] = useState<number>(700);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    getAllSEPData()
      .then((data) => {
        setProtonData(data.particle_flux?.proton ?? []);
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
  const scale = containerWidth > 700 ? containerWidth / 700 : 1;

  if (loading)
    return <div className="text-white/40 text-sm h-full flex items-center justify-center">Loading Proton Flux Data...</div>;
  if (!protonData.length)
    return <div className="text-white/40 text-sm h-full flex items-center justify-center">No proton flux data available.</div>;

  // Group data by energy band
  const energies = Array.from(new Set(protonData.map((d) => d.energy)));
  
  // Create a visually distinct color palette for different bands
  const colors = ["#FF5252", "#FFAB40", "#69F0AE", "#448AFF", "#E040FB"];

  const traces = energies.map((energy, idx) => {
    const pts = protonData.filter((d) => d.energy === energy);
    return {
      x: pts.map((d) => d.time_tag),
      y: pts.map((d) => d.flux),
      type: "scatter" as const,
      mode: "lines" as const,
      name: isSmall ? energy.replace("MeV", "").trim() : energy,
      line: { color: colors[idx % colors.length], width: 1.5 * scale },
    };
  });

  return (
    <div ref={containerRef} className="w-full h-80 lg:h-96 min-h-[300px]">
      <Plot
        key={`plotly-scale-${Math.round(scale * 10)}`}
        data={traces}
        layout={{
          paper_bgcolor: "transparent",
          plot_bgcolor: "transparent",
          autosize: true,

          title: {
            text: isSmall ? "Proton Flux" : "GOES Proton Flux",
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
            title: isSmall ? undefined : { text: "Flux (pfu)", font: { size: 11 * scale } },
            type: "log",
            color: "#aaa",
            showgrid: true,
            gridcolor: "#ffffff15",
            tickfont: { size: (isSmall ? 8 : 10) * scale },
            tickformat: isSmall ? ".1s" : undefined,
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
            ? { t: 36, l: 42, r: 8,  b: 60 }
            : { t: 40 * scale, l: 60 * scale, r: 20 * scale, b: 70 * scale },

          font: { family: "Arial", size: 11 * scale, color: "#ccc" },
        }}
        config={{ displayModeBar: false, responsive: true }}
        useResizeHandler
        style={{ width: "100%", height: "100%" }}
      />
    </div>
  );
}
