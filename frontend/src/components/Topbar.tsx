export default function Topbar() {
  return (
    <div className="flex justify-between items-center mb-6">
      <h1 className="font-medium">Solar Dashboard</h1>
      <span className="text-sm text-gray-400">Live Data</span>
      <div className="w-8 h-8 rounded-full bg-white/20" />
    </div>
  );
}
