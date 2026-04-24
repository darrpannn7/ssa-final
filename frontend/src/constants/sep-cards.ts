import { ServiceCard } from "@/types/service-card";

export const SEP_CARDS: ServiceCard[] = [
  {
    id: "01",
    title: "Particle Flux",
    type: "chart",
    desc:
      "Solar Energetic Particles (SEPs) are high-energy protons and heavy ions accelerated during solar flares and CME-driven shocks. Particle flux represents the number of particles detected per unit area and time.",
    color: "from-pink-500/20 via-rose-500/20 to-red-500/20",
    border: "border-pink-400/20",
  },

  {
    id: "02",
    title: "Energy Spectrum",
    type: "text",
    desc:
      "The energy spectrum describes how solar energetic particles are distributed across different energy levels. High-energy particles can penetrate spacecraft shielding and pose radiation risks.",
    color: "from-indigo-500/20 via-purple-500/20 to-violet-500/20",
    border: "border-indigo-400/20",
  },

  {
    id: "03",
    title: "Radiation Mode",
    type: "options",
    options: ["Crew", "Satellite", "Deep Space"],
    desc:
      "Radiation exposure levels depend on mission type. Crew missions require stricter radiation protection compared to satellites or deep-space probes.",
    color: "from-fuchsia-500/20 via-purple-500/20 to-pink-500/20",
    border: "border-purple-400/20",
  },

  {
    id: "04",
    title: "Proton Flux Monitor",
    type: "image",
    imageSrc:
      "https://services.swpc.noaa.gov/images/goes-proton-flux.png",
    desc:
      "GOES satellites continuously monitor energetic proton flux in near-Earth space, helping detect SEP events that may affect astronauts, satellites, and aviation systems.",
    color: "from-red-500/20 via-orange-500/20 to-pink-500/20",
    border: "border-red-400/20",
  },
];