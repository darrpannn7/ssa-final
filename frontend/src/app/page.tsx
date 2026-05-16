import SpaceWeatherDashboard from "@/components/dashboard/SpaceWeatherDashboard";

export const metadata = {
  title: "Orbital Perception — Future of Space Weather Analytics",
  description:
    "Future of Space Weather Analytics: real-time solar flares, CMEs, solar wind, SEPs, Kp index, and satellite risk assessment.",
};

export default function HomePage() {
  return (
    <main className="w-full">
      <SpaceWeatherDashboard />
    </main>
  );
}
