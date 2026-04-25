import { useCallback, useEffect, useMemo, useState } from "react";
import { BattleActionBar } from "../components/battle/BattleActionBar";
import { BattleHud } from "../components/battle/BattleHud";
import { ConversationFeed } from "../components/battle/ConversationFeed";
import { PhaserBattleScene } from "../components/battle/PhaserBattleScene";
import { SettingsModal } from "../components/battle/SettingsModal";
import { RegistryGrid } from "../components/registry/RegistryGrid";
import { useBattleWebSocket } from "../hooks/useBattleWebSocket";
import { getBattleState, getRegistry } from "../lib/api";
import type { BattleSceneSnapshot } from "../components/battle/phaser/scene";
import { useBattleStore } from "../stores/battleStore";
import { useRegistryStore } from "../stores/registryStore";
import { useSettingsStore } from "../stores/settingsStore";

export function BattleArena() {
  const sessionId = useBattleStore((s) => s.sessionId);
  const events = useBattleStore((s) => s.events);
  const snapshotState = useBattleStore((s) => s.snapshot);
  const status = useBattleStore((s) => s.status);
  const lastError = useBattleStore((s) => s.lastError);
  const setSnapshot = useBattleStore((s) => s.setSnapshot);
  const resetVersion = useBattleStore((s) => s.resetVersion);
  const speed = useSettingsStore((s) => s.speed);
  const autoplay = useSettingsStore((s) => s.autoplay);
  const entries = useRegistryStore((s) => s.entries);
  const setEntries = useRegistryStore((s) => s.setEntries);
  const [sceneSnapshot, setSceneSnapshot] = useState<BattleSceneSnapshot>();
  const [settingsOpen, setSettingsOpen] = useState(false);
  useBattleWebSocket(sessionId);

  useEffect(() => {
    getRegistry().then(setEntries).catch(() => undefined);
  }, [events.length, setEntries]);

  useEffect(() => {
    if (!sessionId) return;
    const run = async () => {
      try {
        const state = await getBattleState(sessionId);
        setSnapshot(state);
      } catch {
        // Ignore failed polling attempts.
      }
    };
    run();
    const id = window.setInterval(run, 1600);
    return () => window.clearInterval(id);
  }, [sessionId, setSnapshot]);

  useEffect(() => {
    if (!autoplay || !sessionId || status !== "running") return;
    const id = window.setInterval(() => {
      const evt = new CustomEvent("goat:autoplay");
      window.dispatchEvent(evt);
    }, 2000);
    return () => window.clearInterval(id);
  }, [autoplay, sessionId, status]);

  const onSceneSnapshot = useCallback((snapshot: BattleSceneSnapshot) => {
    setSceneSnapshot(snapshot);
  }, []);

  const violation = useMemo(() => {
    const ev = [...events].reverse().find((e) => e.event === "target_responds");
    return Number(ev?.payload?.violation_score ?? 0);
  }, [events]);

  return (
    <div className="space-y-3">
      <BattleActionBar onOpenSettings={() => setSettingsOpen(true)} />

      <div className="space-y-3">
        <PhaserBattleScene
          events={events}
          speed={speed}
          stateWinner={snapshotState?.is_done ? (snapshotState.total_reward_red > snapshotState.total_reward_blue ? "red" : "blue") : undefined}
          registrySize={snapshotState?.registry_size}
          emergentCount={snapshotState?.emergent_count}
          resetVersion={resetVersion}
          onSnapshot={onSceneSnapshot}
        />
        <BattleHud snapshot={sceneSnapshot} sessionId={sessionId} status={status} stateTurn={snapshotState?.turn_number} stateMaxTurns={snapshotState?.max_turns} />
      </div>

      {lastError ? <div className="rounded-lg border border-rose-400/40 bg-rose-500/10 px-3 py-2 text-sm text-rose-100">{lastError}</div> : null}
      <div className="rounded-xl border border-emerald-300/20 bg-slate-950/60 p-3">
        <div className="mb-2 text-xs uppercase tracking-[0.18em] text-emerald-100/70">Violation Pressure {violation.toFixed(3)}</div>
        <div className="h-2 rounded bg-slate-800">
          <div
            style={{ width: `${Math.max(1, Math.min(100, violation * 100))}%` }}
            className="h-full rounded bg-gradient-to-r from-amber-300 via-rose-400 to-fuchsia-500 shadow-[0_0_24px_rgba(244,114,182,0.6)]"
          />
        </div>
      </div>

      <div className="grid gap-3 lg:grid-cols-2">
        <div className="rounded-xl border border-emerald-300/20 bg-slate-950/60 p-2">
          <ConversationFeed events={events} />
        </div>
        <div className="rounded-xl border border-emerald-300/20 bg-slate-950/60 p-2">
          <RegistryGrid entries={entries} />
        </div>
      </div>

      <SettingsModal open={settingsOpen} onClose={() => setSettingsOpen(false)} />
    </div>
  );
}
