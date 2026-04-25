import { Line, LineChart, ResponsiveContainer, XAxis, YAxis } from "recharts";

export function ASRChart({ data }: { data: { x: number; y: number }[] }) {
  return (
    <div className="h-56 rounded-xl border border-slate-700 bg-slate-900/70 p-3">
      <div className="mb-2 text-sm">ASR Trend</div>
      <ResponsiveContainer width="100%" height="90%">
        <LineChart data={data}>
          <XAxis dataKey="x" stroke="#94a3b8" />
          <YAxis stroke="#94a3b8" />
          <Line type="monotone" dataKey="y" stroke="#22c55e" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
