"use client";

import { useEffect, useRef, useState, type KeyboardEvent } from "react";
import {
  Paperclip,
  Loader2,
  Zap,
  Activity,
  AlertTriangle,
  X,
  Send,
} from "lucide-react";
import MessageBubble from "./MessageBubble";

type SuryaData = {
  intensity: number;
  magnetic_complexity: number;
  flare_risk: string;
  embedding_dim: number;
};

type Source = "llava+surya" | "groq+surya" | "error" | undefined;

type Region = {
  id: string;
  polarity: "positive" | "negative";
  bbox: [number, number, number, number];
  area: number;
  complexity: string;
  flare_risk: string;
};

type Message = {
  role: "user" | "assistant";
  content: string;
  image?: string;
  suryaData?: SuryaData;
  source?: Source;
  annotatedImage?: string;
  regions?: Region[];
};

function SourceBadge({ source }: { source: Source }) {
  if (!source) return null;

  const config: Record<string, { label: string; color: string }> = {
    "llava+surya": {
      label: "LLaVA vision + Surya ViT",
      color: "bg-purple-500/20 text-purple-300 border-purple-500/30",
    },
    "groq+surya": {
      label: "Groq LLM + Surya ViT",
      color: "bg-blue-500/20 text-blue-300 border-blue-500/30",
    },
    error: {
      label: "Fallback mode",
      color: "bg-red-500/20 text-red-300 border-red-500/30",
    },
  };

  const { label, color } = config[source] ?? {
    label: source,
    color: "bg-white/10 text-white/50 border-white/10",
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 text-xs px-2 py-0.5 rounded-full border ${color} mb-2`}
    >
      <Zap size={10} />
      {label}
    </span>
  );
}

function SuryaPanel({ data }: { data: SuryaData }) {
  const riskColor = data.flare_risk.startsWith("High")
    ? "text-red-400"
    : data.flare_risk.startsWith("Moderate")
    ? "text-yellow-400"
    : "text-green-400";

  const riskIcon = data.flare_risk.startsWith("High") ? (
    <AlertTriangle size={12} className="text-red-400" />
  ) : (
    <Activity size={12} className="text-yellow-400" />
  );

  return (
    <div className="mt-2 rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm space-y-2">
      <p className="text-white/40 text-xs uppercase tracking-wider">
        Surya ViT embedding
      </p>
      <div className="grid grid-cols-2 gap-x-6 gap-y-1">
        <MetricRow label="Intensity" value={data.intensity.toFixed(4)} />
        <MetricRow
          label="Complexity"
          value={data.magnetic_complexity.toFixed(4)}
        />
        <MetricRow label="Embedding dim" value={String(data.embedding_dim)} />
      </div>
      <div className="flex items-center justify-between pt-1 border-t border-white/10">
        <span className="text-white/50 text-xs">Flare risk</span>
        <span
          className={`flex items-center gap-1 text-xs font-medium ${riskColor}`}
        >
          {riskIcon}
          {data.flare_risk}
        </span>
      </div>
      <p className="text-white/30 text-xs">
        ⚠ Based on replicated single-channel input — not true 13ch SDO inference
      </p>
    </div>
  );
}

function MetricRow({ label, value }: { label: string; value: string }) {
  return (
    <>
      <span className="text-white/50">{label}</span>
      <span className="text-white/90 font-mono text-xs">{value}</span>
    </>
  );
}

export default function ChatUI() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [image, setImage] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  useEffect(() => {
    if (!image) {
      setPreviewUrl(null);
      return;
    }

    const url = URL.createObjectURL(image);
    setPreviewUrl(url);

    return () => URL.revokeObjectURL(url);
  }, [image]);

  const clearImage = () => {
    setImage(null);
    if (fileRef.current) fileRef.current.value = "";
  };

  const sendMessage = async () => {
    if ((!input.trim() && !image) || loading) return;

    const userMsg: Message = {
      role: "user",
      content: input,
      image: previewUrl ?? undefined,
    };

    setMessages((prev) => [...prev, userMsg]);

    const fd = new FormData();
    fd.append("message", input);
    if (image) fd.append("image", image);

    setInput("");
    setImage(null);
    if (fileRef.current) fileRef.current.value = "";
    setLoading(true);

    try {
      const res = await fetch("/api/chat", { method: "POST", body: fd });
      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error ?? "Server error");
      }

      const assistantMsg: Message = {
        role: "assistant",
        content: data.response ?? "No response received.",
        suryaData: data.surya_data ?? undefined,
        source: data.source ?? undefined,
        annotatedImage: data.annotated_image ?? undefined,
        regions: data.regions ?? [],
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Request failed";
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `⚠️ Error: ${msg}` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto custom-scroll px-8 py-6 space-y-4">
        {messages.map((msg, i) => (
          <div key={i}>
            {msg.role === "assistant" && msg.source && (
              <SourceBadge source={msg.source} />
            )}

            <MessageBubble message={msg} />

            {msg.role === "assistant" && msg.suryaData && (
              <div className="ml-4 mt-1 max-w-sm">
                <SuryaPanel data={msg.suryaData} />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-2 text-white/40 text-sm">
            <Loader2 size={14} className="animate-spin" />
            {image
              ? "Analysing magnetogram with LLaVA + Surya…"
              : "Running Surya inference…"}
          </div>
        )}
      </div>

      {image && (
        <div className="px-6 pb-2 flex items-center gap-2 text-sm text-white/60">
          <Paperclip size={12} />
          <span>{image.name}</span>
          <button
            onClick={clearImage}
            className="text-white/30 hover:text-white/60 ml-1"
          >
            <X size={14} />
          </button>
        </div>
      )}

      <div className="border-t border-white/10 p-4">
        <div className="flex items-center gap-3">
          <input
            type="file"
            accept="image/*"
            id="imageUpload"
            className="hidden"
            ref={fileRef}
            onChange={(e) => setImage(e.target.files?.[0] ?? null)}
          />

          <label
            htmlFor="imageUpload"
            className="flex items-center justify-center w-10 h-10 rounded-lg border border-white/10 bg-white/[0.05] hover:bg-white/10 cursor-pointer transition shrink-0"
          >
            <Paperclip size={18} />
          </label>

          <input
            className="flex-1 min-w-0 bg-white/[0.05] border border-white/10 rounded-xl px-4 py-3 outline-none text-white disabled:opacity-40"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={image ? "Ask about this magnetogram…" : "Ask the solar AI…"}
            disabled={loading}
          />

          <button
            onClick={sendMessage}
            disabled={loading}
            className="bg-white text-black w-10 h-10 rounded-xl hover:opacity-90 disabled:opacity-40 flex items-center justify-center shrink-0"
            aria-label="Send message"
          >
            {loading ? (
              <Loader2 size={16} className="animate-spin" />
            ) : (
              <Send size={16} />
            )}
          </button>
        </div>
      </div>
    </div>
  );
}