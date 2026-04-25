import { useSettingsStore } from "../stores/settingsStore";

const providers = ["huggingface", "nvidia", "openai", "gemini", "scripted"] as const;

export function Settings() {
  const { redProvider, blueProvider, taskId, setRedProvider, setBlueProvider, setTaskId } = useSettingsStore();
  return (
    <div className="space-y-3 rounded-xl border border-slate-700 bg-slate-900/70 p-4">
      <h2 className="text-lg font-semibold">Settings</h2>
      <div className="grid gap-3 md:grid-cols-3">
        <label className="text-sm">Task
          <input className="mt-1 w-full rounded border border-slate-700 bg-slate-950 p-2" type="number" min={4} max={6} value={taskId} onChange={(e) => setTaskId(Number(e.target.value))} />
        </label>
        <label className="text-sm">Red Provider
          <select className="mt-1 w-full rounded border border-slate-700 bg-slate-950 p-2" value={redProvider} onChange={(e) => setRedProvider(e.target.value as any)}>
            {providers.map((p) => <option key={p}>{p}</option>)}
          </select>
        </label>
        <label className="text-sm">Blue Provider
          <select className="mt-1 w-full rounded border border-slate-700 bg-slate-950 p-2" value={blueProvider} onChange={(e) => setBlueProvider(e.target.value as any)}>
            {providers.map((p) => <option key={p}>{p}</option>)}
          </select>
        </label>
      </div>
    </div>
  );
}
