export function ViolationMeter({ score }: { score: number }) {
  return (
    <div className="rounded-xl border border-slate-700 bg-slate-900/70 p-3">
      <div className="mb-2 text-sm text-slate-300">Violation Meter</div>
      <div className="h-3 rounded bg-slate-800">
        <div className="h-3 rounded bg-rose-500" style={{ width: `${Math.max(0, Math.min(100, score * 100))}%` }} />
      </div>
    </div>
  );
}
