"use client";

import { useEffect, useLayoutEffect, useRef, useState } from "react";
import dynamic from "next/dynamic";
import { getGoesXrayFlux } from "@/lib/api";

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

// SSR-safe layout effect
const useIsomorphicLayoutEffect =
  typeof window !== "undefined" ? useLayoutEffect : useEffect;

interface FluxPoint {
  time_tag: string;
  flux: number;
}

export default function GOESFluxChart() {
  const [primary, setPrimary] = useState<FluxPoint[]>([]);
  const [secondary, setSecondary] = useState<FluxPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [containerWidth, setContainerWidth] = useState<number>(700);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    getGoesXrayFlux()
      .then((data) => {
        setPrimary(data.primary ?? []);
        setSecondary(data.secondary ?? []);
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
  const isTiny  = containerWidth < 340;

  // On high-res monitors, scaler triggers > 1.
  const scale = containerWidth > 700 ? containerWidth / 700 : 1;

  if (loading)
    return <div className="text-white/40 text-sm">Loading GOES X-Ray Data...</div>;
  if (!primary.length && !secondary.length)
    return <div className="text-white/40 text-sm">No flux data available.</div>;

  return (
    <div ref={containerRef} className="w-full h-80 lg:h-96 min-h-[300px]">
      <Plot
        key={`plotly-scale-${Math.round(scale * 10)}`}
        data={[
          {
            x: primary.map((d) => d.time_tag),
            y: primary.map((d) => d.flux),
            type: "scatter",
            mode: "lines",
            name: isTiny ? "P" : isSmall ? "Primary" : "Primary",
            line: { color: "#ff4500", width: 1.5 * scale },
          },
          {
            x: secondary.map((d) => d.time_tag),
            y: secondary.map((d) => d.flux),
            type: "scatter",
            mode: "lines",
            name: isTiny ? "S" : isSmall ? "Secondary" : "Secondary",
            line: { color: "#00bfff", width: 1.5 * scale, dash: "dot" },
          },
        ]}
        layout={{
          paper_bgcolor: "transparent",
          plot_bgcolor: "transparent",
          autosize: true,

          title: {
            text: isSmall ? "GOES X-Ray Flux" : "GOES X-Ray Flux (0.1–0.8 nm)",
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
            title: isSmall ? undefined : { text: "Flux (W/m²)", font: { size: 11 * scale } },
            type: "log",
            color: "#aaa",
            showgrid: true,
            gridcolor: "#ffffff15",
            tickfont: { size: (isSmall ? 8 : 10) * scale },
            tickformat: isSmall ? ".2s" : undefined,
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