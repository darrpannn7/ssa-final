import SolarVisualsBanner from "../components/home/SolarVisualsBanner"

export default function HomePage() {
  return (
    <>
      {/* ── Hero ── */}
      <section
        className="
          relative min-h-screen
          flex flex-col items-center justify-center
          text-center
          px-4 sm:px-6 lg:px-8
        "
      >
        <h1
          className="
            font-black tracking-tight
            text-4xl
            sm:text-5xl
            md:text-6xl
            lg:text-7xl
            xl:text-8xl
          "
        >
          Orbital Perception
        </h1>

        <p
          className="
            text-zinc-400
            mt-4 sm:mt-6
            max-w-xs sm:max-w-xl lg:max-w-2xl
            text-sm
            sm:text-base
            md:text-lg
            lg:text-xl
            leading-relaxed
          "
        >
          Future of Space Weather Analytics and Prediction
        </p>

        {/* Scroll cue */}
        <div className="absolute bottom-10 left-1/2 -translate-x-1/2 flex flex-col items-center gap-1">
          <span className="text-[10px] uppercase tracking-[0.2em] text-white/20">Scroll</span>
          <svg
            className="w-4 h-4 text-white/20 animate-bounce"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </section>

      {/* ── Solar Observatory Visuals ── */}
      <SolarVisualsBanner />
    </>
  );
}
