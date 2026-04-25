import { useCallback, useEffect } from "react";
import { Play, RotateCcw, Shield, Square, Swords, X } from "lucide-react";
import { runBattle, startBattle, stopBattle } from "../../lib/api";
import type { Provider } from "../../lib/types";
import { useBattleStore } from "../../stores/battleStore";
import { useSettingsStore } from "../../stores/settingsStore";

const providers: Provider[] = ["huggingface", "nvidia", "openai", "gemini", "scripted"];
const modelProfiles = ["weak_model", "standard_model", "hardened_model"] as const;

const inputClass =
  "mt-1 w-full rounded-lg border border-emerald-200/20 bg-slate-950/70 px-3 py-2 text-sm text-slate-100 outline-none transition focus:border-emerald-300/60 focus:ring-2 focus:ring-emerald-300/30";

interface SettingsModalProps {
  open: boolean;
  onClose: () => void;
}

export function SettingsModal({ open, onClose }: SettingsModalProps) {
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
      onClose();
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

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 p-4 backdrop-blur-sm">
      <section className="w-full max-w-3xl rounded-2xl border border-emerald-200/20 bg-slate-900/95 p-5 shadow-[0_0_80px_rgba(74,222,128,0.2)]">
        <div className="mb-4 flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm uppercase tracking-[0.2em] text-emerald-100/80">
            <Shield size={15} /> Game Settings
          </div>
          <button className="rounded-lg border border-slate-700 bg-slate-800/80 p-2 text-slate-200 hover:border-emerald-300/40" onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          <div className="rounded-xl border border-emerald-200/20 bg-slate-950/60 p-3">
            <div className="mb-2 text-xs uppercase tracking-[0.15em] text-emerald-200/80">Simulation</div>
            <label className="block text-sm">
              Task
              <input className={inputClass} type="number" min={4} max={6} value={taskId} onChange={(e) => setTaskId(Number(e.target.value))} />
            </label>
            <label className="mt-3 block text-sm">
              Model Profile
              <select className={inputClass} value={modelProfile} onChange={(e) => setModelProfile(e.target.value as (typeof modelProfiles)[number])}>
                {modelProfiles.map((profile) => (
                  <option key={profile}>{profile}</option>
                ))}
              </select>
            </label>
          </div>

          <div className="rounded-xl border border-emerald-200/20 bg-slate-950/60 p-3">
            <div className="mb-2 text-xs uppercase tracking-[0.15em] text-emerald-200/80">Providers</div>
            <label className="block text-sm">
              Red Team (Attacker)
              <select className={inputClass} value={redProvider} onChange={(e) => setRedProvider(e.target.value as Provider)}>
                {providers.map((provider) => (
                  <option key={provider}>{provider}</option>
                ))}
              </select>
            </label>
            <label className="mt-3 block text-sm">
              Blue Team (Defender)
              <select className={inputClass} value={blueProvider} onChange={(e) => setBlueProvider(e.target.value as Provider)}>
                {providers.map((provider) => (
                  <option key={provider}>{provider}</option>
                ))}
              </select>
            </label>
          </div>

          <div className="rounded-xl border border-emerald-200/20 bg-slate-950/60 p-3">
            <div className="mb-2 text-xs uppercase tracking-[0.15em] text-emerald-200/80">Advanced</div>
            <label className="block text-sm">
              Seed
              <input className={inputClass} type="number" value={seed} placeholder="random" onChange={(e) => setSeed(e.target.value === "" ? "" : Number(e.target.value))} />
            </label>
            <label className="mt-3 block text-sm">
              Sim Speed: {speed.toFixed(1)}x
              <input className="mt-2 w-full accent-emerald-300" type="range" min={0.5} max={2.5} step={0.1} value={speed} onChange={(e) => setSpeed(Number(e.target.value))} />
            </label>
            <label className="mt-3 flex items-center justify-between rounded-lg border border-emerald-200/20 bg-slate-900/80 px-3 py-2 text-sm">
              Autoplay
              <input type="checkbox" className="h-4 w-4 accent-emerald-300" checked={autoplay} onChange={(e) => setAutoplay(e.target.checked)} />
            </label>
          </div>
        </div>

        <div className="mt-4 grid grid-cols-2 gap-2 md:grid-cols-4">
          <button onClick={onStart} className="flex items-center justify-center gap-1 rounded-lg bg-gradient-to-r from-emerald-400 to-teal-300 px-3 py-2 text-sm font-semibold text-slate-950">
            <Play size={14} /> Start
          </button>
          <button
            onClick={onRun}
            disabled={!sessionId}
            className="flex items-center justify-center gap-1 rounded-lg bg-gradient-to-r from-sky-500 to-blue-400 px-3 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-40"
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
            className="flex items-center justify-center gap-1 rounded-lg border border-emerald-300/40 bg-emerald-300/10 px-3 py-2 text-sm font-semibold text-emerald-100"
          >
            <RotateCcw size={14} /> Reset
          </button>
        </div>
        <div className="mt-3 text-xs text-emerald-50/70">
          Session: <span className="font-mono">{sessionId ?? "none"}</span> | Status: {status}
        </div>
      </section>
    </div>
  );
}
