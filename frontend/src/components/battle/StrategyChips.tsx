export function StrategyChips({ items }: { items: string[] }) {
  return (
    <div className="flex flex-wrap gap-2">
      {items.map((s) => (
        <span key={s} className="rounded-full border border-slate-600 px-2 py-1 text-xs text-slate-300">{s}</span>
      ))}
    </div>
  );
}
