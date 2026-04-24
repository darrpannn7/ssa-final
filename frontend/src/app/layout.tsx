import "@/styles/globals.css";
import Starfield from "@/components/canvas/Starfield";
import Navbar from "@/components/layout/Navbar";
import ServiceCards from "@/components/home/ServiceCards";

export const metadata = {
  title: "STELAR",
  description: "SSA Analytics Dashboard",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-black text-white selection:bg-blue-500">
        {/* Persistent Background */}
        <div className="fixed inset-0 z-0">
          <Starfield />
        </div>

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
