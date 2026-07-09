import { ReactNode } from "react";

export default function SummaryCard({
  label, value, sub, tone = "muted", onClick,
}: {
  label: string;
  value: ReactNode;
  sub?: string;
  tone?: "muted" | "success" | "warning" | "critical" | "accent";
  onClick?: () => void;
}) {
  const toneClass: Record<string, string> = {
    muted: "text-ink",
    success: "text-success",
    warning: "text-warning",
    critical: "text-critical",
    accent: "text-accent",
  };
  return (
    <button
      onClick={onClick}
      className="card p-5 text-left w-full hover:border-accent/40 transition"
    >
      <p className="text-xs text-muted uppercase tracking-wide">{label}</p>
      <p className={`text-2xl font-mono font-semibold mt-2 ${toneClass[tone]}`}>{value}</p>
      {sub && <p className="text-xs text-muted mt-1">{sub}</p>}
    </button>
  );
}
