import { useState } from "react";
import { Analytics } from "./pages/Analytics";
import { BattleArena } from "./pages/BattleArena";
import { RegistryExplorer } from "./pages/RegistryExplorer";
import { Settings } from "./pages/Settings";

type Page = "battle" | "registry" | "analytics" | "settings";

export default function App() {
  const [page, setPage] = useState<Page>("battle");
  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(34,211,238,0.22),_transparent_45%),radial-gradient(circle_at_80%_20%,_rgba(244,63,94,0.2),_transparent_40%),#04040b] p-6 text-slate-100">
      <header className="mb-6 flex items-center justify-between rounded-2xl border border-cyan-300/20 bg-slate-950/70 px-5 py-4 shadow-[0_0_40px_rgba(56,189,248,0.13)] backdrop-blur">
        <h1 className="text-2xl font-black uppercase tracking-[0.14em] text-cyan-100">GOAT-Evolution</h1>
        <nav className="flex gap-2">
          {(["battle", "registry", "analytics", "settings"] as const).map((p) => (
            <button
              key={p}
              onClick={() => setPage(p)}
              className={`rounded-lg border px-3 py-1 text-sm uppercase tracking-[0.11em] transition ${
                page === p
                  ? "border-cyan-200/50 bg-cyan-300/20 text-cyan-50 shadow-[0_0_20px_rgba(34,211,238,0.35)]"
                  : "border-slate-700 bg-slate-900/70 text-slate-300 hover:border-cyan-300/50 hover:text-cyan-100"
              }`}
            >
              {p}
            </button>
          ))}
        </nav>
      </header>
      {page === "battle" ? <BattleArena /> : null}
      {page === "registry" ? <RegistryExplorer /> : null}
      {page === "analytics" ? <Analytics /> : null}
      {page === "settings" ? <Settings /> : null}
    </div>
  );
}
