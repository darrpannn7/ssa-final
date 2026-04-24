"use client";

import ChatUI from "@/components/chat/ChatUI";

export default function LLMPage() {
  return (
    <div className="w-full flex justify-center px-6 pt-[90px] pb-10">
      <div className="w-full max-w-6xl h-[calc(100vh-140px)] bg-white/[0.05] backdrop-blur-2xl border border-white/10 rounded-[30px] shadow-[0_30px_120px_rgba(0,0,0,0.8)] flex flex-col overflow-hidden">
        <ChatUI />
      </div>
    </div>
  );
}