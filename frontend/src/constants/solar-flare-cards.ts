import { getMagnetogramImageUrl } from "@/lib/api"
import { ServiceCard } from "@/types/service-card"

export const SOLAR_FLARE_CARDS: ServiceCard[] = [
  {
    id: "01",
    title: "HMI Magnetogram",
    type: "image",
    imageSrc: getMagnetogramImageUrl(),
    dataUrl: "/space-weather/magnetogram/flare-risk",
    desc: "Magnetograms reveal solar magnetic field structures.",
    color: "from-blue-500/20 via-indigo-500/20 to-purple-500/20",
    border: "border-blue-400/20",
  },
  {
    id: "02",
    title: "GOES X-ray Flux",
    type: "chart",
    dataUrl: "/noaa/goes-xray",
    desc: "GOES satellites measure solar X-ray flux used to classify flares.",
    color: "from-orange-500/20 via-red-500/20 to-pink-500/20",
    border: "border-red-400/20",
  },
  {
    id: "03",
    title: "AIA EUV Viewer",
    type: "options",
    options: ["94Å", "131Å", "171Å", "193Å"],
    desc: "AIA observes the Sun in extreme ultraviolet wavelengths.",
    color: "from-purple-500/20 via-violet-500/20 to-fuchsia-500/20",
    border: "border-purple-400/20",
  },
    // ─── NEW 4th card ───────────────────────────────────────────────────────
  {
    id: "04",
    title: "Recent Flare Events",
    type: "table",
    desc: "Latest solar flare events from NASA DONKI showing class, peak time, and active region.",
    color: "from-rose-500/20 via-red-500/20 to-orange-500/20",
    border: "border-rose-400/20",
  },
  
]