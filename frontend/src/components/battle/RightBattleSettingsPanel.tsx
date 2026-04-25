import { useCallback, useEffect } from "react";
import { Play, Shield, Swords, Square, RotateCcw } from "lucide-react";
import { startBattle, runBattle, stopBattle } from "../../lib/api";
import type { Provider } from "../../lib/types";
import { useBattleStore } from "../../stores/battleStore";
import { useSettingsStore } from "../../stores/settingsStore";

const providers: Provider[] = ["huggingface", "nvidia", "openai", "gemini", "scripted"];
const modelProfiles = ["weak_model", "standard_model", "hardened_model"] as const;

const inputClass =
  "mt-1 w-full rounded-lg border border-cyan-200/20 bg-slate-950/60 px-3 py-2 text-sm text-slate-100 outline-none transition focus:border-cyan-300/60 focus:ring-2 focus:ring-cyan-300/30";

export function RightBattleSettingsPanel() {
  const { taskId, redProvider, blueProvider, modelProfile, seed, speed, autoplay, setTaskId, setRedProvider, setBlueProvider, setModelProfile, setSeed, setSpeed, setAutoplay } =
    useSettingsStore();
  const { sessionId, status, setSessionId, setStatus, setError, clear } = useBattleStore();

  const onStart = async () => {
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
  };

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

  return (
    <aside className="space-y-4 rounded-2xl border border-cyan-200/20 bg-slate-950/65 p-4 shadow-[0_0_45px_rgba(34,211,238,0.15)] backdrop-blur">
      <div className="mb-1 flex items-center gap-2 text-xs uppercase tracking-[0.2em] text-cyan-100/75">
        <Shield size={14} /> Tactical Control
      </div>

      <label className="block text-sm">
        Task
        <input className={inputClass} type="number" min={4} max={6} value={taskId} onChange={(e) => setTaskId(Number(e.target.value))} />
      </label>
      <label className="block text-sm">
        Model Profile
        <select className={inputClass} value={modelProfile} onChange={(e) => setModelProfile(e.target.value as (typeof modelProfiles)[number])}>
          {modelProfiles.map((profile) => (
            <option key={profile} value={profile}>
              {profile}
            </option>
          ))}
        </select>
      </label>
      <label className="block text-sm">
        Red Provider
        <select className={inputClass} value={redProvider} onChange={(e) => setRedProvider(e.target.value as Provider)}>
          {providers.map((provider) => (
            <option key={provider} value={provider}>
              {provider}
            </option>
          ))}
        </select>
      </label>
      <label className="block text-sm">
        Blue Provider
        <select className={inputClass} value={blueProvider} onChange={(e) => setBlueProvider(e.target.value as Provider)}>
          {providers.map((provider) => (
            <option key={provider} value={provider}>
              {provider}
            </option>
          ))}
        </select>
      </label>
      <label className="block text-sm">
        Seed (optional)
        <input
          className={inputClass}
          type="number"
          value={seed}
          placeholder="random"
          onChange={(e) => setSeed(e.target.value === "" ? "" : Number(e.target.value))}
        />
      </label>
      <label className="block text-sm">
        Sim Speed: {speed.toFixed(1)}x
        <input className="mt-2 w-full accent-cyan-300" type="range" min={0.5} max={2.5} step={0.1} value={speed} onChange={(e) => setSpeed(Number(e.target.value))} />
      </label>
      <label className="flex items-center justify-between rounded-lg border border-cyan-200/20 bg-slate-900/60 px-3 py-2 text-sm">
        Autoplay run
        <input type="checkbox" className="h-4 w-4 accent-cyan-300" checked={autoplay} onChange={(e) => setAutoplay(e.target.checked)} />
      </label>

      <div className="grid grid-cols-2 gap-2 pt-2">
        <button onClick={onStart} className="flex items-center justify-center gap-1 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-500 px-3 py-2 text-sm font-semibold text-slate-950">
          <Play size={14} /> Start
        </button>
        <button
          onClick={onRun}
          disabled={!sessionId}
          className="flex items-center justify-center gap-1 rounded-lg bg-gradient-to-r from-rose-500 to-fuchsia-500 px-3 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-40"
        >
          <Swords size={14} /> Run
        </button>
        <button
          onClick={onStop}
          disabled={!sessionId}
          className="flex items-center justify-center gap-1 rounded-lg border border-amber-300/50 bg-amber-300/10 px-3 py-2 text-sm font-semibold text-amber-100 disabled:cursor-not-allowed disabled:opacity-40"
        >
          <Square size={14} /> Stop
        </button>
        <button
          onClick={clear}
          className="flex items-center justify-center gap-1 rounded-lg border border-cyan-300/40 bg-cyan-300/10 px-3 py-2 text-sm font-semibold text-cyan-100"
        >
          <RotateCcw size={14} /> Reset
        </button>
      </div>
      <div className="text-xs text-cyan-50/70">
        Session: <span className="font-mono">{sessionId ?? "none"}</span>
        <br />
        Status: {status}
      </div>
    </aside>
  );
}
