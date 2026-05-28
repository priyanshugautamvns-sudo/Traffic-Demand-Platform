import { type ReactNode } from "react";
import { GlassCard } from "./GlassCard";

export function MetricCard({
  label,
  value,
  note,
  icon
}: {
  label: string;
  value: string;
  note?: string;
  icon?: ReactNode;
}) {
  return (
    <GlassCard className="p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="text-xs uppercase tracking-[0.2em] text-slate-400">{label}</div>
          <div className="mt-2 text-2xl font-semibold text-white">{value}</div>
          {note ? <div className="mt-2 text-sm text-slate-400">{note}</div> : null}
        </div>
        {icon ? <div className="rounded-xl border border-white/10 bg-white/5 p-2 text-cyan-300">{icon}</div> : null}
      </div>
    </GlassCard>
  );
}

