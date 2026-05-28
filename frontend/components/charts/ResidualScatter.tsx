"use client";

import {
  CartesianGrid,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  ZAxis
} from "recharts";

export function ResidualScatter({
  data
}: {
  data: Array<{ demand: number; oof_pred: number; residual: number }>;
}) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <ScatterChart margin={{ top: 10, right: 12, left: -8, bottom: 0 }}>
        <CartesianGrid stroke="rgba(148,163,184,0.12)" strokeDasharray="3 3" />
        <XAxis dataKey="demand" name="Actual" tick={{ fill: "#94a3b8", fontSize: 11 }} />
        <YAxis dataKey="oof_pred" name="Predicted" tick={{ fill: "#94a3b8", fontSize: 11 }} />
        <ZAxis dataKey="residual" range={[40, 120]} />
        <Tooltip
          contentStyle={{
            background: "rgba(2,6,23,0.92)",
            border: "1px solid rgba(148,163,184,0.2)",
            borderRadius: 12
          }}
        />
        <Scatter data={data} fill="#22c55e" />
      </ScatterChart>
    </ResponsiveContainer>
  );
}

