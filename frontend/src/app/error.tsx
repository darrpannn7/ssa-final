"use client";

import { useEffect } from "react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error("Global Application Error:", error);
  }, [error]);

  return (
    <div className="min-h-screen bg-neutral-950 flex flex-col items-center justify-center text-white relative overflow-hidden">
      {/* Background gradients similar to dashboard */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-900/40 via-neutral-950 to-neutral-950" />
      <div className="absolute inset-0 bg-[url('/noise.png')] opacity-10 mix-blend-overlay pointer-events-none" />

      <div className="relative z-10 p-8 rounded-2xl border border-white/10 bg-white/5 backdrop-blur-md max-w-xl text-center shadow-2xl">
        <h2 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-red-500 to-orange-400 mb-4">
          Atmospheric Interference Detected
        </h2>
        <p className="text-gray-300 mb-6 text-lg">
          We encountered an error connecting to the Space Weather network. This might be due to a temporary backend outage or API rate limit.
        </p>
        <p className="text-sm font-mono text-gray-400 p-4 bg-black/40 rounded-lg mb-8 break-all border border-white/5 shadow-inner">
          {error.message || "Unknown communication failure"}
        </p>
        
        <button
          onClick={() => reset()}
          className="px-6 py-3 rounded-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-medium transition-all shadow-lg hover:shadow-indigo-500/25 active:scale-95"
        >
          Re-establish Connection
        </button>
      </div>
    </div>
  );
}
