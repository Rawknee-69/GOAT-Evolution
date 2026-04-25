import type { BattleSceneSnapshot } from "./phaser/scene";

interface BattleHudProps {
  snapshot?: BattleSceneSnapshot;
  sessionId?: string;
  status: string;
  stateTurn?: number;
  stateMaxTurns?: number;
}

function meterClass(team: "red" | "blue") {
  return team === "red"
    ? "from-rose-500/90 to-pink-300/80 shadow-[0_0_18px_rgba(244,63,94,0.65)]"
    : "from-cyan-400/90 to-blue-300/80 shadow-[0_0_18px_rgba(34,211,238,0.65)]";
}

export function BattleHud({ snapshot, sessionId, status, stateTurn, stateMaxTurns }: BattleHudProps) {
  const redHp = snapshot?.redHp ?? 300;
  const blueHp = snapshot?.blueHp ?? 300;
  const redPct = Math.max(0, Math.min(100, (redHp / 300) * 100));
  const bluePct = Math.max(0, Math.min(100, (blueHp / 300) * 100));
  const winner = snapshot?.winner;

  return (
    <div className="space-y-3 rounded-2xl border border-cyan-300/20 bg-slate-950/70 p-4 backdrop-blur">
      <div className="flex items-center justify-between text-xs uppercase tracking-[0.18em] text-cyan-100/70">
        <span>Session {sessionId ? `#${sessionId.slice(0, 8)}` : "Offline"}</span>
        <span className="rounded bg-cyan-300/15 px-2 py-1 text-cyan-100">{status}</span>
      </div>
      <div className="space-y-2">
        <div>
          <div className="mb-1 flex justify-between text-xs text-rose-200">
            <span>Red Strike Force</span>
            <span>{redHp}</span>
          </div>
          <div className="h-2 rounded bg-slate-800">
            <div style={{ width: `${redPct}%` }} className={`h-full rounded bg-gradient-to-r ${meterClass("red")}`} />
          </div>
        </div>
        <div>
          <div className="mb-1 flex justify-between text-xs text-cyan-200">
            <span>Blue Guard Mesh</span>
            <span>{blueHp}</span>
          </div>
          <div className="h-2 rounded bg-slate-800">
            <div style={{ width: `${bluePct}%` }} className={`h-full rounded bg-gradient-to-r ${meterClass("blue")}`} />
          </div>
        </div>
      </div>
      <div className="flex items-center justify-between text-sm text-slate-200">
        <span>
          Turn {stateTurn ?? snapshot?.turn ?? 0}
          {stateMaxTurns ? ` / ${stateMaxTurns}` : ""}
        </span>
        <span className="text-xs uppercase tracking-[0.16em] text-cyan-100/80">{winner ? `${winner} wins` : "combat active"}</span>
      </div>
    </div>
  );
}
