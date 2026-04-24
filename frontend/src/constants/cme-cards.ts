import { ServiceCard } from "@/types/service-card";

export const CME_CARDS: ServiceCard[] = [
  {
    id: "01",
    title: "CME Velocity",
    type: "text",
    desc:
      "Coronal Mass Ejections (CMEs) are massive eruptions of plasma and magnetic field from the Sun’s corona. CME velocity determines how quickly the ejected material travels through interplanetary space and whether it can impact Earth's magnetosphere.",
    color: "from-yellow-500/20 via-orange-500/20 to-red-500/20",
    border: "border-orange-400/20",
  },

  {
    id: "02",
    title: "Magnetic Structure",
    type: "chart",
    desc:
      "The magnetic structure of a CME determines how it interacts with Earth’s magnetic field. Strong southward magnetic fields embedded within CMEs can trigger geomagnetic storms and auroral activity.",
    color: "from-emerald-400/20 via-teal-500/20 to-cyan-500/20",
    border: "border-emerald-400/20",
  },

  {
    id: "03",
    title: "Impact Probability",
    type: "options",
    options: ["Low", "Medium", "High"],
    desc:
      "Impact probability estimates the likelihood that a CME will intersect Earth’s orbit. This prediction depends on the CME trajectory, angular width, and speed relative to the Sun-Earth line.",
    color: "from-purple-500/20 via-violet-500/20 to-fuchsia-500/20",
    border: "border-purple-400/20",
  },

  {
    id: "04",
    title: "CME Coronagraph Image",
    type: "image",
    imageSrc:
      "https://soho.nascom.nasa.gov/data/LATEST/current_c2.gif",
    desc:
      "Coronagraph instruments such as LASCO block the bright solar disk to reveal faint coronal structures and CMEs propagating away from the Sun.",
    color: "from-red-500/20 via-orange-500/20 to-yellow-500/20",
    border: "border-red-400/20",
  },
    // ─── NEW 5th card ───────────────────────────────────────────────────────
  {
    id: "05",
    title: "CME Event Log",
    type: "table",
    desc: "Full log of the last 10 recorded CME events from NASA DONKI, including speed, trajectory, and Earth impact risk assessment.",
    color: "from-slate-500/20 via-gray-500/20 to-zinc-500/20",
    border: "border-slate-400/20",
  },
];