"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  motion,
  useMotionValue,
  useSpring,
  useTransform,
  AnimatePresence,
  type MotionValue,
} from "framer-motion";
import { useRef, useState, useEffect } from "react";

const NAV_ITEMS = [
  { label: "Overview", href: "/" },
  { label: "Solar Flare", href: "/solar-flare" },
  { label: "CME", href: "/cme" },
  { label: "Solar Wind", href: "/solar-wind" },
  { label: "SEP", href: "/sep" },
  { label: "LLM", href: "/llm" },
];

export default function Navbar() {
  const mouseX = useMotionValue(Infinity);
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  // Close menu on route change
  useEffect(() => {
    setOpen(false);
  }, [pathname]);

  // Close menu on outside click
  useEffect(() => {
    if (!open) return;
    const handler = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (!target.closest("[data-navbar]")) setOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [open]);

  return (
    <nav
      data-navbar
      className="fixed top-4 left-1/2 -translate-x-1/2 z-50 w-full max-w-3xl px-4"
    >
      {/* ── Desktop ── */}
      <motion.div
        onMouseMove={(e) => mouseX.set(e.pageX)}
        onMouseLeave={() => mouseX.set(Infinity)}
        className="hidden md:flex items-center justify-center gap-2 px-4 py-3 rounded-full border border-white/10 bg-black/20 backdrop-blur-md shadow-2xl w-fit mx-auto"
      >
        {NAV_ITEMS.map((item) => (
          <NavItem
            key={item.href}
            title={item.label}
            href={item.href}
            mouseX={mouseX}
            active={pathname === item.href}
          />
        ))}
      </motion.div>

      {/* ── Mobile shell ── */}
      <div className="md:hidden">
        <div className="flex justify-between items-center bg-black/40 backdrop-blur-md border border-white/10 rounded-full px-5 py-2.5">
          <span className="text-white font-semibold tracking-wide text-sm">
            Dashboard
          </span>

          {/* Animated hamburger */}
          <button
            onClick={() => setOpen((v) => !v)}
            aria-label="Toggle menu"
            className="relative w-7 h-7 flex flex-col items-center justify-center gap-[5px] group"
          >
            <motion.span
              animate={open ? { rotate: 45, y: 7 } : { rotate: 0, y: 0 }}
              transition={{ duration: 0.25, ease: "easeInOut" }}
              className="block w-5 h-0.5 bg-white origin-center rounded-full"
            />
            <motion.span
              animate={open ? { opacity: 0, scaleX: 0 } : { opacity: 1, scaleX: 1 }}
              transition={{ duration: 0.2 }}
              className="block w-5 h-0.5 bg-white rounded-full"
            />
            <motion.span
              animate={open ? { rotate: -45, y: -7 } : { rotate: 0, y: 0 }}
              transition={{ duration: 0.25, ease: "easeInOut" }}
              className="block w-5 h-0.5 bg-white origin-center rounded-full"
            />
          </button>
        </div>

        {/* Animated dropdown */}
        <AnimatePresence>
          {open && (
            <motion.div
              key="mobile-menu"
              initial={{ opacity: 0, y: -8, scale: 0.97 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -8, scale: 0.97 }}
              transition={{ duration: 0.2, ease: "easeOut" }}
              className="mt-2 bg-black/80 backdrop-blur-xl border border-white/10 rounded-2xl p-3 space-y-1 shadow-2xl"
            >
              {NAV_ITEMS.map((item, i) => (
                <motion.div
                  key={item.href}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.04, duration: 0.2 }}
                >
                  <Link href={item.href} onClick={() => setOpen(false)}>
                    <div
                      className={cn(
                        "px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-150",
                        pathname === item.href
                          ? "bg-white text-black shadow-[0_0_12px_rgba(255,255,255,0.25)]"
                          : "text-white/60 hover:text-white hover:bg-white/10"
                      )}
                    >
                      {item.label}
                    </div>
                  </Link>
                </motion.div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </nav>
  );
}

function NavItem({
  mouseX,
  title,
  href,
  active,
}: {
  mouseX: MotionValue<number>;
  title: string;
  href: string;
  active: boolean;
}) {
  const ref = useRef<HTMLButtonElement>(null);

  const distance = useTransform(mouseX, (val) => {
    const bounds = ref.current?.getBoundingClientRect() ?? { x: 0, width: 0 };
    return val - (bounds.x + bounds.width / 2);
  });

  const width = useSpring(
    useTransform(distance, [-150, 0, 150], [80, 120, 80]),
    { mass: 0.1, stiffness: 150, damping: 12 }
  );

  const height = useSpring(
    useTransform(distance, [-150, 0, 150], [42, 50, 42]),
    { mass: 0.1, stiffness: 150, damping: 12 }
  );

  const fontSize = useSpring(
    useTransform(distance, [-150, 0, 150], [13, 18, 13]),
    { mass: 0.1, stiffness: 150, damping: 12 }
  );

  return (
    <Link href={href}>
      <motion.button
        ref={ref}
        style={{ width, height, fontSize }}
        className={cn(
          "relative flex items-center justify-center rounded-full font-medium",
          active ? "text-black" : "text-white/70 hover:text-white"
        )}
      >
        <div
          className={cn(
            "absolute inset-0 rounded-full border border-white/10",
            active
              ? "bg-white shadow-[0_0_15px_rgba(255,255,255,0.3)]"
              : "bg-white/10 backdrop-blur-sm"
          )}
        />
        <span className="relative z-10 whitespace-nowrap">{title}</span>
      </motion.button>
    </Link>
  );
}