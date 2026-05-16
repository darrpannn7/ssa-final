"use client";

import Link from "next/link";

// ─── Types ───────────────────────────────────────────────────────────────────

type AlertLevel = "R1" | "R2" | "R3" | "R4" | "R5" | "S1" | "S2" | "S3" | "G1" | "G2" | "G3";

interface StatusCardData {
  label: string;
  status: string;
  scale: AlertLevel;
  sub: string;
  href: string;
  icon: React.ReactNode;
  colorClass: string;
  borderClass: string;
  bgClass: string;
}

// ─── Color Code: Green=Nominal, Yellow=Moderate, Orange=Strong, Red=Extreme ──

function getStatusColor(status: string) {
  const s = status.toUpperCase();
  if (s === "EXTREME" || s === "SEVERE") {
    return { text: "text-red-400", bg: "bg-red-500/20", border: "border-red-500/50" };
  }
  if (s === "STRONG" || s === "HIGH" || s === "WARNING") {
    return { text: "text-orange-400", bg: "bg-orange-500/20", border: "border-orange-500/50" };
  }
  if (s === "MODERATE" || s === "CAUTION" || s === "WATCH") {
    return { text: "text-yellow-400", bg: "bg-yellow-500/20", border: "border-yellow-500/50" };
  }
  // NOMINAL, NONE, QUIET, NORMAL
  return { text: "text-green-400", bg: "bg-green-500/20", border: "border-green-500/50" };
}

// ─── Icons ───────────────────────────────────────────────────────────────────

const FlareIcon = () => (
  <svg viewBox="0 0 40 40" fill="none" className="w-9 h-9">
    <circle cx="20" cy="20" r="9" fill="#f97316" opacity="0.9" />
    {[0, 45, 90, 135, 180, 225, 270, 315].map((angle) => (
      <line
        key={angle}
        x1="20" y1="20"
        x2={20 + Math.cos((angle * Math.PI) / 180) * 18}
        y2={20 + Math.sin((angle * Math.PI) / 180) * 18}
        stroke="#f97316" strokeWidth="2.5" strokeLinecap="round" opacity="0.6"
      />
    ))}
  </svg>
);

const SEPIcon = () => (
  <svg viewBox="0 0 40 40" fill="none" className="w-9 h-9">
    <circle cx="20" cy="20" r="8" stroke="#facc15" strokeWidth="2" fill="none" opacity="0.6" />
    <circle cx="20" cy="20" r="14" stroke="#facc15" strokeWidth="1" fill="none" opacity="0.3" strokeDasharray="3 3" />
    <circle cx="20" cy="20" r="4" fill="#facc15" opacity="0.9" />
    {[30, 90, 150, 210, 270, 330].map((angle) => (
      <circle
        key={angle}
        cx={20 + Math.cos((angle * Math.PI) / 180) * 14}
        cy={20 + Math.sin((angle * Math.PI) / 180) * 14}
        r="1.5" fill="#facc15" opacity="0.5"
      />
    ))}
  </svg>
);

const CMEIcon = () => (
  <svg viewBox="0 0 40 40" fill="none" className="w-9 h-9">
    <circle cx="20" cy="20" r="7" fill="#ef4444" opacity="0.8" />
    <path d="M27 13 Q35 5 38 15 Q35 20 30 18" fill="#ef4444" opacity="0.5" />
    <path d="M27 20 Q36 18 39 26 Q36 30 30 25" fill="#ef4444" opacity="0.4" />
  </svg>
);

const WindIcon = () => (
  <svg viewBox="0 0 40 40" fill="none" className="w-9 h-9">
    <path d="M5 18 Q15 14 25 18 Q32 20 38 16" stroke="#38bdf8" strokeWidth="2.5" strokeLinecap="round" fill="none" />
    <path d="M5 22 Q15 26 25 22 Q32 20 38 24" stroke="#38bdf8" strokeWidth="1.5" strokeLinecap="round" fill="none" opacity="0.5" />
    <path d="M5 14 Q12 10 20 14" stroke="#38bdf8" strokeWidth="1" strokeLinecap="round" fill="none" opacity="0.3" />
  </svg>
);

const SatelliteIcon = () => (
  <svg viewBox="0 0 40 40" fill="none" className="w-9 h-9">
    <rect x="17" y="17" width="6" height="6" fill="#eab308" rx="1" />
    <rect x="4" y="18" width="12" height="4" fill="#eab308" opacity="0.6" rx="1" />
    <rect x="24" y="18" width="12" height="4" fill="#eab308" opacity="0.6" rx="1" />
    <line x1="23" y1="20" x2="28" y2="12" stroke="#eab308" strokeWidth="1.5" opacity="0.5" />
    <circle cx="29" cy="11" r="2" fill="#eab308" opacity="0.7" />
  </svg>
);

// ─── Status Card ─────────────────────────────────────────────────────────────

function StatusCard({ card }: { card: StatusCardData }) {
  const colors = getStatusColor(card.status);
  return (
    <Link href={card.href} className="block group">
      <div className={`
        flex items-center gap-3 p-3 rounded-xl border transition-all duration-200
        ${colors.bg} ${colors.border}
        hover:scale-[1.02] cursor-pointer
      `}>
        <div className="shrink-0">{card.icon}</div>
        <div className="min-w-0">
          <p className="text-[10px] text-white/50 uppercase tracking-widest font-semibold leading-none mb-0.5">
            {card.label}
          </p>
          <p className={`text-lg font-black uppercase leading-none ${colors.text}`}>
            {card.status}
          </p>
          <div className="flex items-center gap-1.5 mt-0.5">
            <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${colors.bg} ${colors.text} border ${colors.border}`}>
              {card.scale}
            </span>
            <p className="text-[10px] text-white/40 leading-tight truncate">{card.sub}</p>
          </div>
        </div>
      </div>
    </Link>
  );
}

// ─── Status Row ──────────────────────────────────────────────────────────────

interface StatusRowProps {
  flareClass: string;
  sepRisk: string;
  cmeCount: number;
  highestCmeRisk: string;
  windSpeed: number;
  windDensity: number;
  kpIndex: number;
}

function deriveFlareStatus(cls: string): { status: string; scale: AlertLevel; sub: string } {
  const letter = cls.charAt(0).toUpperCase();
  const number = parseFloat(cls.substring(1)) || 0;

  let flux = 0;
  if (letter === 'A') flux = number * 1e-8;
  else if (letter === 'B') flux = number * 1e-7;
  else if (letter === 'C') flux = number * 1e-6;
  else if (letter === 'M') flux = number * 1e-5;
  else if (letter === 'X') flux = number * 1e-4;

  if (flux >= 5e-4) {
    return { status: "EXTREME", scale: "R4", sub: "Extreme Flares (>= X5)" };
  } else if (flux >= 1e-4) {
    return { status: "STRONG", scale: "R3", sub: "Strong Flares (X-class)" };
  } else if (flux >= 1e-5) {
    return { status: "MODERATE", scale: "R2", sub: "Moderate Flares (M-class)" };
  } else {
    return { status: "NOMINAL", scale: "R1", sub: "Nominal Activity" };
  }
}

function deriveSEPStatus(risk: string): { status: string; scale: AlertLevel; sub: string } {
  if (risk === "extreme" || risk === "severe") return { status: "EXTREME", scale: "S3", sub: "High Proton Levels" };
  if (risk === "high") return { status: "STRONG", scale: "S2", sub: "Enhanced Proton Levels" };
  if (risk === "moderate") return { status: "MODERATE", scale: "S2", sub: "Enhanced Proton Levels" };
  return { status: "NOMINAL", scale: "S1", sub: "Nominal Activity" };
}

function deriveCMEStatus(count: number, highestRisk: string): { status: string; scale: AlertLevel; sub: string } {
  if (count === 0) return { status: "NONE", scale: "R1", sub: "No CME Detected" };

  if (highestRisk === "High") return { status: "STRONG", scale: "R3", sub: `${count} CMEs — High Earth Impact Risk` };
  if (highestRisk === "Moderate") return { status: "MODERATE", scale: "R2", sub: `${count} CMEs — Moderate Impact Risk` };

  // All CMEs are Low risk (not Earth-directed)
  return { status: "NOMINAL", scale: "R1", sub: `${count} CMEs — Low Impact Risk` };
}

function deriveWindStatus(speed: number, density: number): { status: string; scale: AlertLevel; sub: string } {
  if (speed > 800 || density > 20) return { status: "EXTREME", scale: "G3", sub: "Severe Wind Conditions" };
  if (speed > 700 || density > 15) return { status: "STRONG", scale: "G2", sub: "Speed & Density Elevated" };
  if (speed > 500 || density > 8) return { status: "MODERATE", scale: "G2", sub: "Speed & Density Elevated" };
  return { status: "NOMINAL", scale: "G1", sub: "Nominal Conditions" };
}

function deriveSatelliteStatus(
  speed: number,
  density: number,
  kp: number
): { status: string; scale: AlertLevel; sub: string } {
  // HIGH: severe wind OR strong geomagnetic storm (Kp>=6)
  if (speed > 700 || density > 15 || kp >= 6)
    return { status: "HIGH", scale: "G3", sub: "High Risk of Charging, Drag & Upsets" };
  // CAUTION: moderate wind OR moderate geomagnetic activity (Kp>=4)
  if (speed > 450 || density > 8 || kp >= 4)
    return { status: "CAUTION", scale: "G2", sub: "Increased Risk of Charging & Drag" };
  return { status: "NOMINAL", scale: "G1", sub: "Normal Operations" };
}

export default function StatusRow({ flareClass, sepRisk, cmeCount, highestCmeRisk, windSpeed, windDensity, kpIndex }: StatusRowProps) {
  const flare = deriveFlareStatus(flareClass);
  const sep = deriveSEPStatus(sepRisk);
  const cme = deriveCMEStatus(cmeCount, highestCmeRisk);
  const wind = deriveWindStatus(windSpeed, windDensity);
  const sat = deriveSatelliteStatus(windSpeed, windDensity, kpIndex);

  const cards: StatusCardData[] = [
    {
      label: "Flares",
      ...flare,
      href: "/solar-flare",
      icon: <FlareIcon />,
      colorClass: "",
      borderClass: "",
      bgClass: "",
    },
    {
      label: "SEPs",
      ...sep,
      href: "/sep",
      icon: <SEPIcon />,
      colorClass: "",
      borderClass: "",
      bgClass: "",
    },
    {
      label: "CMEs",
      ...cme,
      href: "/cme",
      icon: <CMEIcon />,
      colorClass: "",
      borderClass: "",
      bgClass: "",
    },
    {
      label: "Solar Wind",
      ...wind,
      href: "/solar-wind",
      icon: <WindIcon />,
      colorClass: "",
      borderClass: "",
      bgClass: "",
    },
    {
      label: "Satellites",
      ...sat,
      href: "/solar-wind",
      icon: <SatelliteIcon />,
      colorClass: "",
      borderClass: "",
      bgClass: "",
    },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2 px-3 py-2">
      {cards.map((card) => (
        <StatusCard key={card.label} card={card} />
      ))}
    </div>
  );
}
