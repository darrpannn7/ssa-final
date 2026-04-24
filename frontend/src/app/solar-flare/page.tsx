"use client";

import ServiceCards from "@/components/home/ServiceCards";
import { SOLAR_FLARE_CARDS } from "@/constants/solar-flare-cards";
import FlarePredictionCard from "@/components/cards/FlarePredictionCard";

export default function SolarFlarePage() {
  return (
    <>
      <section className="min-h-[55vh] sm:min-h-[65vh] md:min-h-[75vh] lg:min-h-[90vh] flex items-center justify-center text-center px-4 sm:px-6">
        <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-black uppercase">
          Solar Flare
        </h1>
      </section>

      <section className="px-4 sm:px-6 lg:px-8 pb-10 sm:pb-14 flex justify-center">
        <div className="w-full max-w-md">
          <FlarePredictionCard />
        </div>
      </section>

      <ServiceCards cards={SOLAR_FLARE_CARDS} />
    </>
  );
}