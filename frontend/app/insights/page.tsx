"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { BrainCircuit, Sigma } from "lucide-react";
import { GlassCard } from "@/components/GlassCard";
import { MetricCard } from "@/components/MetricCard";
import { fetchJson } from "@/lib/api";
import type { MetricsPayload } from "@/lib/types";

const FeatureImportanceChart = dynamic(() => import("@/components/charts/FeatureImportanceChart").then((mod) => mod.FeatureImportanceChart), {
  ssr: false
});
const ResidualScatter = dynamic(() => import("@/components/charts/ResidualScatter").then((mod) => mod.ResidualScatter), {
  ssr: false
});

export default function InsightsPage() {
  const [payload, setPayload] = useState<MetricsPayload | null>(null);

  useEffect(() => {
    fetchJson<MetricsPayload>("/metrics").then(setPayload).catch(() => setPayload(null));
  }, []);

  const metrics = payload?.metrics;

  return (
    <div className="mx-auto max-w-7xl space-y-6 px-4 py-8 sm:px-6 lg:px-8">
      <div className="grid gap-4 md:grid-cols-3">
        <MetricCard label="Validation R²" value={metrics ? metrics.cv_r2.toFixed(4) : "—"} note="Primary score" icon={<BrainCircuit size={16} />} />
        <MetricCard label="OOF mean residual" value={metrics ? metrics.oof_residual_mean.toFixed(6) : "—"} note="Near zero is better" icon={<Sigma size={16} />} />
        <MetricCard label="OOF residual std" value={metrics ? metrics.oof_residual_std.toFixed(6) : "—"} note="Error spread" icon={<BrainCircuit size={16} />} />
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr]">
        <GlassCard className="h-[500px] p-5">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <div className="text-xs uppercase tracking-[0.2em] text-slate-400">Feature importance</div>
              <div className="mt-1 text-lg font-medium text-white">Top model drivers</div>
            </div>
          </div>
          <div className="h-[420px]">
            {payload?.feature_importance ? <FeatureImportanceChart data={payload.feature_importance} /> : null}
          </div>
        </GlassCard>

        <GlassCard className="h-[500px] p-5">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <div className="text-xs uppercase tracking-[0.2em] text-slate-400">Residuals</div>
              <div className="mt-1 text-lg font-medium text-white">Predicted vs actual demand</div>
            </div>
          </div>
          <div className="h-[420px]">
            {payload?.analytics?.residual_sample ? <ResidualScatter data={payload.analytics.residual_sample as any} /> : null}
          </div>
        </GlassCard>
      </div>
    </div>
  );
}

