"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";

export function PeakTrafficChart({
  data
}: {
  data: Array<{ label: string; value: number }>;
}) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={data} margin={{ top: 10, right: 12, left: -8, bottom: 0 }}>
        <defs>
          <linearGradient id="peakFill" x1="0" x2="0" y1="0" y2="1">
            <stop offset="5%" stopColor="#22d3ee" stopOpacity={0.45} />
            <stop offset="95%" stopColor="#22d3ee" stopOpacity={0.03} />
          </linearGradient>
        </defs>
        <CartesianGrid stroke="rgba(148,163,184,0.12)" strokeDasharray="3 3" />
        <XAxis dataKey="label" tick={{ fill: "#94a3b8", fontSize: 11 }} interval={3} />
        <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} />
        <Tooltip
          contentStyle={{
            background: "rgba(2,6,23,0.92)",
            border: "1px solid rgba(148,163,184,0.2)",
            borderRadius: 12
          }}
        />
        <Area type="monotone" dataKey="value" stroke="#22d3ee" fill="url(#peakFill)" strokeWidth={2} />
      </AreaChart>
    </ResponsiveContainer>
  );
}

