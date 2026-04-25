import { startBattle, runBattle } from "../../lib/api";
import { useBattleStore } from "../../stores/battleStore";
import { useSettingsStore } from "../../stores/settingsStore";

export function BattleControls() {
  const { taskId, redProvider, blueProvider } = useSettingsStore();
  const setSessionId = useBattleStore((s) => s.setSessionId);
  const sessionId = useBattleStore((s) => s.sessionId);

  const onStart = async () => {
    const out = await startBattle({ task_id: taskId, model_profile: "standard_model", red_provider: redProvider, blue_provider: blueProvider });
    setSessionId(out.session_id);
  };

  const onRun = async () => {
    if (!sessionId) return;
    await runBattle(sessionId);
  };

  return (
    <div className="flex gap-2">
      <button onClick={onStart} className="rounded bg-emerald-600 px-3 py-2 text-sm font-semibold">Start Battle</button>
      <button onClick={onRun} className="rounded bg-indigo-600 px-3 py-2 text-sm font-semibold">Run Episode</button>
      <span className="self-center text-xs text-slate-400">Session: {sessionId ?? "none"}</span>
    </div>
  );
}
