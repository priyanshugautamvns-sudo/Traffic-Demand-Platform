import Link from "next/link";
import { ArrowRight, ChevronRight, Layers3, Sparkles, WandSparkles } from "lucide-react";
import { TrafficHero } from "@/components/TrafficHero";
import { GlassCard } from "@/components/GlassCard";
import { MetricCard } from "@/components/MetricCard";

const cards = [
  {
    label: "Validation R2",
    value: "0.9564",
    note: "Leakage-safe target encoding plus LightGBM folds"
  },
  {
    label: "Inference",
    value: "< 1s",
    note: "Fast batched CSV scoring"
  },
  {
    label: "Bundle size",
    value: "Lean",
    note: "File-based storage and cached model loading"
  }
];

export default function HomePage() {
  return (
    <div className="mx-auto max-w-7xl space-y-8 px-4 py-8 sm:px-6 lg:px-8">
      <TrafficHero />

      <section className="grid gap-4 lg:grid-cols-3">
        {cards.map((card) => (
          <MetricCard key={card.label} label={card.label} value={card.value} note={card.note} icon={<Sparkles size={16} />} />
        ))}
      </section>

      <section className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <GlassCard className="p-6">
          <div className="flex items-center justify-between gap-4">
            <div>
              <div className="text-xs uppercase tracking-[0.2em] text-slate-400">Analysis flow</div>
              <h2 className="mt-2 text-2xl font-semibold text-white">Explore the data, then inspect what drives demand.</h2>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-3 text-cyan-200">
              <WandSparkles size={20} />
            </div>
          </div>

          <div className="mt-6 grid gap-3 sm:grid-cols-3">
            {["Open analytics", "Review trends", "Check model signals"].map((step, index) => (
              <div key={step} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                <div className="text-xs text-cyan-300">0{index + 1}</div>
                <div className="mt-2 text-sm text-slate-100">{step}</div>
              </div>
            ))}
          </div>
        </GlassCard>

        <GlassCard className="p-6">
          <div className="text-xs uppercase tracking-[0.2em] text-slate-400">Quick actions</div>
          <div className="mt-3 space-y-3">
            <Link
              href="/analytics"
              className="flex items-center justify-between rounded-2xl border border-cyan-400/20 bg-cyan-400/10 px-4 py-4 text-white transition hover:bg-cyan-400/15"
            >
              <span className="inline-flex items-center gap-2">
                <Sparkles size={16} /> Open analytics dashboard
              </span>
              <ArrowRight size={16} />
            </Link>
            <Link
              href="/insights"
              className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/5 px-4 py-4 text-slate-100 transition hover:bg-white/8"
            >
              <span className="inline-flex items-center gap-2">
                <Layers3 size={16} /> View model insights
              </span>
              <ArrowRight size={16} />
            </Link>
          </div>
        </GlassCard>
      </section>

      <section className="grid gap-4 lg:grid-cols-[1.15fr_0.85fr]">
        <GlassCard className="p-6">
          <div className="flex items-start justify-between gap-4">
            <div>
              <div className="text-xs uppercase tracking-[0.2em] text-slate-400">Judge ready</div>
              <h2 className="mt-2 text-2xl font-semibold text-white">Compact enough to demo, strong enough to impress.</h2>
              <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-300">
                The stack stays lean, but the signals are real: road type, lane count, geohash, cyclic time, weather, and a validated
                LightGBM model powering the analytics and insights views.
              </p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-3 text-cyan-200">
              <Layers3 size={20} />
            </div>
          </div>

          <div className="mt-6 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            {["Road behavior", "Geospatial signal", "Weather context", "Time patterns"].map((item) => (
              <div key={item} className="rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-4">
                <div className="text-sm text-slate-100">{item}</div>
              </div>
            ))}
          </div>
        </GlassCard>

        <GlassCard className="p-6">
          <div className="text-xs uppercase tracking-[0.2em] text-slate-400">Quick steps</div>
          <div className="mt-4 space-y-3">
            {[
              ["1", "Open the analytics dashboard"],
              ["2", "Inspect weather and road patterns"],
              ["3", "Switch to model insights"]
            ].map(([n, label]) => (
              <div key={n} className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
                <div className="inline-flex items-center gap-3">
                  <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-cyan-400/10 text-xs font-medium text-cyan-200">
                    {n}
                  </span>
                  <span className="text-sm text-slate-100">{label}</span>
                </div>
                <ChevronRight size={16} className="text-slate-500" />
              </div>
            ))}
          </div>
        </GlassCard>
      </section>
    </div>
  );
}
