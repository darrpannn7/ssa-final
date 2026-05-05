export default function HomePage() {
  return (
    <>
      <section
        className="
          min-h-screen
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
      </section>
    </>
  );
}
