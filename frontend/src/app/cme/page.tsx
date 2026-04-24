import ServiceCards from "@/components/home/ServiceCards";
import { CME_CARDS } from "@/constants/cme-cards";

export default function CMEPage() {
  return (
    <>
      <section className="h-[110vh] min-h-screen flex items-center justify-center text-center">
        <h1 className="text-7xl font-black uppercase">
          CME
        </h1>
      </section>

      <ServiceCards cards={CME_CARDS} />
    </>
  );
}
