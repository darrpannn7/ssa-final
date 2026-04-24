"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Home,
  Sun,
  Activity,
  Wind,
  BarChart2,
  MessageSquare,
} from "lucide-react";

const items = [
  { href: "/dashboard/overview", icon: Home },
  { href: "/dashboard/sunspots", icon: Sun },
  { href: "/dashboard/flares", icon: Activity },
  { href: "/dashboard/solarwind", icon: Wind },
  { href: "/dashboard/analytics", icon: BarChart2 },
  { href: "/dashboard/copilot", icon: MessageSquare },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-16 border-r border-white/10 flex flex-col items-center py-6 gap-6 text-gray-400">
      {items.map((i, idx) => {
        const active = pathname === i.href;

        return (
          <Link key={idx} href={i.href}>
            <i.icon
              className={`w-5 h-5 transition ${
                active ? "text-amber-400" : "hover:text-amber-400"
              }`}
            />
          </Link>
        );
      })}
    </aside>
  );
}
