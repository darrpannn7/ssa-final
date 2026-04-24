"use client";

import ReactMarkdown from "react-markdown";

type Region = {
  id:         string;
  polarity:   "positive" | "negative";
  bbox:       [number, number, number, number];
  area:       number;
  complexity: string;
  flare_risk: string;
};

type Props = {
  message: {
    role:           "user" | "assistant";
    content:        string;
    image?:         string;
    annotatedImage?: string;
    regions?:       Region[];
  };
};

export default function MessageBubble({ message }: Props) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`
          max-w-[75%] border border-white/10 px-5 py-3
          rounded-2xl backdrop-blur-md
          ${isUser ? "bg-white/[0.10]" : "bg-white/[0.06]"}
        `}
      >
        {/* Original uploaded image (user side) */}
        {message.image && (
          <img
            src={message.image}
            className="mb-2 rounded-lg max-h-[220px] object-contain"
            alt="uploaded"
          />
        )}

        {/* Annotated image (assistant side) */}
        {message.annotatedImage && (
          <div className="mb-4">
            <p className="text-white/40 text-xs uppercase tracking-wider mb-2">
              Active region detection
            </p>
            <img
              src={`data:image/png;base64,${message.annotatedImage}`}
              className="rounded-xl w-full object-contain border border-white/10"
              alt="annotated magnetogram"
            />
          </div>
        )}

        {/* Region summary table */}
        {message.regions && message.regions.length > 0 && (
          <div className="mb-4 overflow-x-auto">
            <p className="text-white/40 text-xs uppercase tracking-wider mb-2">
              Detected regions — {message.regions.length} total
            </p>
            <table className="w-full text-xs border-collapse">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="text-left text-white/50 px-2 py-1.5">ID</th>
                  <th className="text-left text-white/50 px-2 py-1.5">Polarity</th>
                  <th className="text-left text-white/50 px-2 py-1.5">Class</th>
                  <th className="text-left text-white/50 px-2 py-1.5">Complexity</th>
                  <th className="text-left text-white/50 px-2 py-1.5">Flare risk</th>
                </tr>
              </thead>
              <tbody>
                {message.regions.map((r) => (
                  <tr
                    key={r.id}
                    className="border-b border-white/[0.06] hover:bg-white/[0.03]"
                  >
                    <td className="text-white/80 px-2 py-1.5 font-mono">{r.id}</td>
                    <td className="px-2 py-1.5">
                      <span
                        className={`
                          text-xs px-1.5 py-0.5 rounded-full
                          ${r.polarity === "positive"
                            ? "bg-cyan-500/20 text-cyan-300"
                            : "bg-orange-500/20 text-orange-300"
                          }
                        `}
                      >
                        {r.polarity === "positive" ? "+ pos" : "− neg"}
                      </span>
                    </td>
                    <td className="text-white/70 px-2 py-1.5 font-mono">{r.complexity}</td>
                    <td className="text-white/70 px-2 py-1.5">{r.complexity}</td>
                    <td className="px-2 py-1.5">
                      <Flarebadge cls={r.flare_risk} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Markdown text response */}
        {isUser ? (
          <p className="text-white/90">{message.content}</p>
        ) : (
          <ReactMarkdown
            components={{
              h1: ({ children }) => (
                <h1 className="text-lg font-semibold text-white mt-4 mb-2 first:mt-0">
                  {children}
                </h1>
              ),
              h2: ({ children }) => (
                <h2 className="text-base font-semibold text-white/90 mt-4 mb-2 pb-1 border-b border-white/10 first:mt-0">
                  {children}
                </h2>
              ),
              h3: ({ children }) => (
                <h3 className="text-sm font-semibold text-white/80 mt-3 mb-1">
                  {children}
                </h3>
              ),
              p: ({ children }) => (
                <p className="text-white/80 mb-3 last:mb-0 leading-relaxed">
                  {children}
                </p>
              ),
              ul: ({ children }) => (
                <ul className="mb-3 last:mb-0 space-y-1 pl-1">{children}</ul>
              ),
              ol: ({ children }) => (
                <ol className="mb-3 last:mb-0 space-y-1 pl-4 list-decimal">
                  {children}
                </ol>
              ),
              li: ({ children }) => (
                <li className="text-white/80 flex gap-2 leading-relaxed">
                  <span className="text-white/30 shrink-0 mt-1">•</span>
                  <span>{children}</span>
                </li>
              ),
              strong: ({ children }) => (
                <strong className="text-white font-semibold">{children}</strong>
              ),
              em: ({ children }) => (
                <em className="text-white/70 italic">{children}</em>
              ),
              code: ({ children }) => (
                <code className="bg-white/10 text-green-300 px-1.5 py-0.5 rounded text-xs font-mono">
                  {children}
                </code>
              ),
              hr: () => <hr className="border-white/10 my-4" />,
              blockquote: ({ children }) => (
                <blockquote className="border-l-2 border-white/20 pl-3 my-2 text-white/50 italic text-xs">
                  {children}
                </blockquote>
              ),
              table: ({ children }) => (
                <div className="overflow-x-auto mb-3">
                  <table className="w-full text-xs border-collapse">
                    {children}
                  </table>
                </div>
              ),
              th: ({ children }) => (
                <th className="text-left text-white/50 font-medium px-3 py-2 border-b border-white/10 bg-white/[0.04]">
                  {children}
                </th>
              ),
              td: ({ children }) => (
                <td className="text-white/70 px-3 py-2 border-b border-white/[0.06]">
                  {children}
                </td>
              ),
            }}
          >
            {message.content}
          </ReactMarkdown>
        )}
      </div>
    </div>
  );
}

// ── Flare class badge ─────────────────────────────────────────────
function Flarebadge({ cls }: { cls: string }) {
  const colors: Record<string, string> = {
    X: "bg-red-500/20 text-red-300 border-red-500/30",
    M: "bg-orange-500/20 text-orange-300 border-orange-500/30",
    C: "bg-yellow-500/20 text-yellow-300 border-yellow-500/30",
    B: "bg-green-500/20 text-green-300 border-green-500/30",
    A: "bg-white/10 text-white/40 border-white/10",
  };
  const color = colors[cls] ?? colors["A"];
  return (
    <span className={`text-xs px-1.5 py-0.5 rounded border ${color}`}>
      {cls}-class
    </span>
  );
}