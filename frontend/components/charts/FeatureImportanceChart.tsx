"use client";

export function FeatureImportanceChart({
  data
}: {
  data: Array<{ feature: string; importance: number }>;
}) {
  const items = data.slice(0, 12);
  const maxValue = Math.max(...items.map((item) => item.importance), 1);

  return (
    <div className="flex h-full flex-col gap-3 overflow-hidden pr-1">
      {items.map((item) => {
        const width = Math.max((item.importance / maxValue) * 100, 3);
        return (
          <div key={item.feature} className="grid grid-cols-[160px_1fr_64px] items-center gap-3">
            <div className="truncate text-xs text-slate-300" title={item.feature}>
              {item.feature}
            </div>
            <div className="h-3 overflow-hidden rounded-full bg-white/6">
              <div className="h-full rounded-full bg-gradient-to-r from-cyan-400 via-sky-400 to-emerald-300" style={{ width: `${width}%` }} />
            </div>
            <div className="text-right text-xs tabular-nums text-slate-400">{item.importance.toFixed(0)}</div>
          </div>
        );
      })}
    </div>
  );
}

