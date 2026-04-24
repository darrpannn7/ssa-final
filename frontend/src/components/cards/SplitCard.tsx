"use client";

type Props = {
  title: string;
  description: string;
  children: React.ReactNode;
};

export default function SplitCard({
  title,
  description,
  children,
}: Props) {
  return (
    <div className="w-full max-w-[1100px] bg-white/[0.04] border border-white/10 rounded-[30px] backdrop-blur-xl shadow-xl p-10 flex gap-12 items-center">

      {/* LEFT SIDE → TEXT */}
      <div className="flex-1 space-y-6">

        <h2 className="text-4xl font-bold">
          {title}
        </h2>

        <p className="text-white/70 leading-relaxed text-lg">
          {description}
        </p>

      </div>

      {/* RIGHT SIDE → LIVE CONTENT */}
      <div className="flex-1 flex justify-center">
        {children}
      </div>

    </div>
  );
}