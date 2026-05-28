"use client";

import { motion } from "framer-motion";

export function TrafficHero() {
  const lanes = [18, 44, 28, 63, 37, 72, 31, 52];

  return (
    <div className="relative overflow-hidden rounded-[28px] border border-white/10 bg-[linear-gradient(180deg,rgba(15,23,42,0.9),rgba(4,7,15,0.9))] p-8 shadow-glass">
      <div className="absolute inset-0 grid-bg opacity-25" />
      <div className="absolute inset-0 bg-mesh opacity-80" />
      <div className="relative grid gap-8 lg:grid-cols-[1.2fr_0.8fr] lg:items-end">
        <div className="max-w-3xl">
          <div className="inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-1 text-xs uppercase tracking-[0.22em] text-cyan-200">
            Traffic demand intelligence
          </div>
          <h1 className="mt-5 text-4xl font-semibold tracking-tight text-white sm:text-5xl">
            High-signal demand analytics for the hackathon lane.
          </h1>
          <p className="mt-5 max-w-2xl text-base leading-7 text-slate-300">
            A compact LightGBM system with leakage-safe encodings and a polished dashboard for exploring road, weather, and time patterns
            fast.
          </p>
          <div className="mt-7 flex flex-wrap gap-2">
            {["KFold CV", "Target encoding", "FastAPI", "LightGBM"].map((tag) => (
              <span key={tag} className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-200">
                {tag}
              </span>
            ))}
          </div>
        </div>

        <div className="glass-soft rounded-3xl p-4">
          <div className="mb-4 flex items-center justify-between text-sm text-slate-300">
            <span>Live traffic signal</span>
            <span className="text-cyan-300">animated</span>
          </div>
          <div className="mb-4 grid grid-cols-3 gap-2 text-center">
            {[
              ["R2", "0.9564"],
              ["RMSE", "0.02969"],
              ["Rows", "41,778"]
            ].map(([label, value]) => (
              <div key={label} className="rounded-2xl border border-white/8 bg-white/5 px-3 py-2">
                <div className="text-[10px] uppercase tracking-[0.18em] text-slate-400">{label}</div>
                <div className="mt-1 text-sm font-semibold text-white">{value}</div>
              </div>
            ))}
          </div>
          <div className="space-y-3">
            {lanes.map((height, index) => (
              <div key={index} className="flex items-center gap-3">
                <div className="h-2 w-10 rounded-full bg-slate-700" />
                <div className="relative h-6 flex-1 overflow-hidden rounded-full bg-white/5">
                  <motion.div
                    className="absolute inset-y-0 left-0 rounded-full bg-gradient-to-r from-cyan-400 via-sky-300 to-emerald-300"
                    initial={{ width: 0 }}
                    animate={{ width: `${height}%` }}
                    transition={{ duration: 0.9, delay: index * 0.08, ease: "easeOut" }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
