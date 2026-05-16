"use client";

interface AlertBannersProps {
  summaryText: string;
  hasAlerts: boolean;
  alerts: string[];
}

export default function AlertBanners({ summaryText }: AlertBannersProps) {
  return (
    <div className="px-3 py-1">
      {/* Summary — full width */}
      <div className="flex items-start gap-3 bg-white/[0.04] border border-white/10 rounded-xl px-4 py-3">
        <div className="shrink-0 mt-0.5">
          <div className="w-6 h-6 rounded-full bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center">
            <svg className="w-3.5 h-3.5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
        <div>
          <p className="text-[10px] uppercase tracking-widest font-bold text-cyan-400 mb-1">Summary</p>
          <p className="text-[12px] text-white/60 leading-relaxed">{summaryText}</p>
        </div>
      </div>
    </div>
  );
}
