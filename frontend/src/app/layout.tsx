import "@/styles/globals.css";
import Navbar from "@/components/layout/Navbar";
import ServiceCards from "@/components/home/ServiceCards";

export const metadata = {
  title: "Orbital Perception",
  description: "Future of Space Weather Analytics",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-black text-white selection:bg-blue-500">
        {/* Persistent Navbar */}
        <Navbar />

        {/* Page Content */}
        <main className="relative z-10">
          {children}
        </main>
      </body>
    </html>
  );
}
