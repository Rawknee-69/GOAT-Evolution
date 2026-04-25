import { useCallback, useEffect } from "react";
import { Play, RotateCcw, Settings, Square, Swords } from "lucide-react";
import { runBattle, startBattle, stopBattle } from "../../lib/api";
import { useBattleStore } from "../../stores/battleStore";
import { useSettingsStore } from "../../stores/settingsStore";

interface BattleActionBarProps {
  onOpenSettings: () => void;
}

export function BattleActionBar({ onOpenSettings }: BattleActionBarProps) {
  const { taskId, redProvider, blueProvider, modelProfile, seed } = useSettingsStore();
  const { sessionId, status, setSessionId, setStatus, setError, clear } = useBattleStore();

  const onStart = useCallback(async () => {
    try {
      setStatus("starting");
      setError(undefined);
      const out = await startBattle({
        task_id: taskId,
        model_profile: modelProfile,
        red_provider: redProvider,
        blue_provider: blueProvider,
        seed: seed === "" ? undefined : seed,
      });
      setSessionId(out.session_id);
      setStatus("running");
    } catch {
      setError("Unable to start session.");
    }
  }, [taskId, redProvider, blueProvider, modelProfile, seed, setSessionId, setStatus, setError]);

  const onRun = useCallback(async () => {
    if (!sessionId) return;
    try {
      setStatus("running");
      setError(undefined);
      await runBattle(sessionId);
    } catch {
      setError("Episode run failed.");
    }
  }, [sessionId, setError, setStatus]);

  useEffect(() => {
    const handler = () => {
      void onRun();
    };
    window.addEventListener("goat:autoplay", handler);
    return () => window.removeEventListener("goat:autoplay", handler);
  }, [onRun]);

  const onStop = async () => {
    if (!sessionId) return;
    try {
      await stopBattle(sessionId);
      setStatus("stopped");
    } catch {
      setError("Stop request failed.");
    }
  };

  const baseBtn =
    "flex items-center gap-1 rounded-lg px-3 py-2 text-xs font-semibold uppercase tracking-[0.14em] transition";

  return (
    <div className="relative z-20 flex flex-wrap items-center gap-2 rounded-2xl border border-emerald-300/30 bg-slate-950/85 px-3 py-2 shadow-[0_0_30px_rgba(74,222,128,0.25)] backdrop-blur">
      <button onClick={onStart} className={`${baseBtn} bg-gradient-to-r from-emerald-400 to-teal-300 text-slate-950`}>
        <Play size={14} /> Start Episode
      </button>
      <button
        onClick={onRun}
        disabled={!sessionId}
        className={`${baseBtn} bg-gradient-to-r from-sky-500 to-blue-400 text-white disabled:cursor-not-allowed disabled:opacity-40`}
      >
        <Swords size={14} /> Run
      </button>
      <button
        onClick={onStop}
        disabled={!sessionId}
        className={`${baseBtn} border border-amber-300/50 bg-amber-300/10 text-amber-100 disabled:cursor-not-allowed disabled:opacity-40`}
      >
        <Square size={14} /> Stop
      </button>
      <button onClick={clear} className={`${baseBtn} border border-emerald-300/40 bg-emerald-300/10 text-emerald-100`}>
        <RotateCcw size={14} /> Reset
      </button>
      <div className="ml-auto flex items-center gap-3 text-[11px] text-emerald-50/80">
        <span className="rounded bg-emerald-400/10 px-2 py-1 font-mono uppercase tracking-[0.1em]">
          {status}
        </span>
        <span className="font-mono text-emerald-50/60">{sessionId ? sessionId.slice(0, 8) : "no session"}</span>
        <button
          onClick={onOpenSettings}
          className={`${baseBtn} relative z-30 pointer-events-auto border border-emerald-300/40 bg-emerald-300/10 text-emerald-100`}
          aria-label="Open settings"
          type="button"
        >
          <Settings size={14} /> Settings
        </button>
      </div>
    </div>
  );
}
