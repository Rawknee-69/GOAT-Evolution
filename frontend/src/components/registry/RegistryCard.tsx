import type { RegistryEntry } from "../../lib/types";

export function RegistryCard({ entry }: { entry: RegistryEntry }) {
  return (
    <div className={`rounded-xl border p-3 ${entry.is_emergent ? "border-emerald-600 bg-emerald-950/20" : "border-slate-700 bg-slate-900/70"}`}>
      <div className="text-sm font-semibold">{entry.attack_id}</div>
      <div className="text-xs text-slate-400">{entry.name}</div>
      <div className="mt-2 flex flex-wrap gap-1">
        {entry.components.map((c) => (
          <span key={c} className="rounded border border-slate-700 px-1 py-0.5 text-[10px]">{c}</span>
        ))}
      </div>
    </div>
  );
}
