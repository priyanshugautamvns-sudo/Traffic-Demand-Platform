"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { BarChart3, CloudRain, MapPin, ThermometerSun, TrafficCone } from "lucide-react";
import { GlassCard } from "@/components/GlassCard";
import { MetricCard } from "@/components/MetricCard";
import { fetchJson } from "@/lib/api";
import type { MetricsPayload } from "@/lib/types";

const PeakTrafficChart = dynamic(() => import("@/components/charts/PeakTrafficChart").then((mod) => mod.PeakTrafficChart), {
  ssr: false
});
const CategoryBarChart = dynamic(() => import("@/components/charts/CategoryBarChart").then((mod) => mod.CategoryBarChart), {
  ssr: false
});

export default function AnalyticsPage() {
  const [payload, setPayload] = useState<MetricsPayload | null>(null);

  useEffect(() => {
    fetchJson<MetricsPayload>("/metrics").then(setPayload).catch(() => setPayload(null));
  }, []);

  const metrics = payload?.metrics;
  const analytics = payload?.analytics;
  const sanitize = (rows?: Array<{ label: string | null; value: number }>) =>
    (rows ?? [])
      .filter((row): row is { label: string; value: number } => Boolean(row && row.label))
      .map((row) => ({ ...row, label: String(row.label) }));

  return (
    <div className="mx-auto max-w-7xl space-y-6 px-4 py-8 sm:px-6 lg:px-8">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="CV R²" value={metrics ? metrics.cv_r2.toFixed(4) : "—"} note="Cross-validated" icon={<TrafficCone size={16} />} />
        <MetricCard label="RMSE" value={metrics ? metrics.cv_rmse.toFixed(5) : "—"} note="Validation error" icon={<BarChart3 size={16} />} />
        <MetricCard label="Residual p95" value={metrics ? metrics.oof_abs_residual_p95.toFixed(5) : "—"} note="95th percentile" icon={<CloudRain size={16} />} />
        <MetricCard label="Best fold" value={metrics?.best_iterations?.length ? String(Math.max(...metrics.best_iterations)) : "—"} note="Boosting rounds" icon={<ThermometerSun size={16} />} />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <GlassCard className="h-[420px] p-5">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <div className="text-xs uppercase tracking-[0.2em] text-slate-400">Peak traffic</div>
              <div className="mt-1 text-lg font-medium text-white">Average demand by hour</div>
            </div>
            <MapPin size={18} className="text-cyan-300" />
          </div>
          <div className="h-[340px]">
            {analytics?.peak_traffic ? <PeakTrafficChart data={analytics.peak_traffic as any} /> : null}
          </div>
        </GlassCard>

        <GlassCard className="h-[420px] p-5">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <div className="text-xs uppercase tracking-[0.2em] text-slate-400">Weather</div>
              <div className="mt-1 text-lg font-medium text-white">Weather versus demand</div>
            </div>
            <CloudRain size={18} className="text-cyan-300" />
          </div>
          <div className="h-[340px]">
            {analytics?.weather_vs_demand ? <CategoryBarChart data={sanitize(analytics.weather_vs_demand as any)} color="#22d3ee" /> : null}
          </div>
        </GlassCard>

        <GlassCard className="h-[420px] p-5">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <div className="text-xs uppercase tracking-[0.2em] text-slate-400">Road insights</div>
              <div className="mt-1 text-lg font-medium text-white">Road type impact</div>
            </div>
            <TrafficCone size={18} className="text-cyan-300" />
          </div>
          <div className="h-[340px]">
            {analytics?.road_vs_demand ? <CategoryBarChart data={sanitize(analytics.road_vs_demand as any)} color="#38bdf8" /> : null}
          </div>
        </GlassCard>

        <GlassCard className="h-[420px] p-5">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <div className="text-xs uppercase tracking-[0.2em] text-slate-400">Temperature</div>
              <div className="mt-1 text-lg font-medium text-white">Demand by temperature band</div>
            </div>
            <ThermometerSun size={18} className="text-cyan-300" />
          </div>
          <div className="h-[340px]">
            {analytics?.temperature_pattern ? <CategoryBarChart data={sanitize(analytics.temperature_pattern as any)} color="#34d399" /> : null}
          </div>
        </GlassCard>
      </div>
    </div>
  );
}
