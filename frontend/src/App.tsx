import { useState } from "react";
import { Analytics } from "./pages/Analytics";
import { BattleArena } from "./pages/BattleArena";
import { RegistryExplorer } from "./pages/RegistryExplorer";
import { Settings } from "./pages/Settings";

type Page = "battle" | "registry" | "analytics" | "settings";

export default function App() {
  const [page, setPage] = useState<Page>("battle");
  return (
    <div className="min-h-screen bg-slate-950 p-6 text-slate-100">
      <header className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold">GOAT-Evolution</h1>
        <nav className="flex gap-2">
          {(["battle", "registry", "analytics", "settings"] as const).map((p) => (
            <button key={p} onClick={() => setPage(p)} className={`rounded px-3 py-1 text-sm ${page === p ? "bg-indigo-600" : "bg-slate-800"}`}>
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
