import type { BattleStartRequest, BattleStateSnapshot, RegistryEntry } from "./types";

const base = "";

export async function startBattle(payload: BattleStartRequest): Promise<{ session_id: string }> {
  const res = await fetch(`${base}/api/battle/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function runBattle(sessionId: string): Promise<any> {
  const res = await fetch(`${base}/api/battle/run/${sessionId}`, { method: "POST" });
  return res.json();
}

export async function stopBattle(sessionId: string): Promise<{ status: string; session_id: string }> {
  const res = await fetch(`${base}/api/battle/stop/${sessionId}`, { method: "POST" });
  return res.json();
}

export async function getBattleState(sessionId: string): Promise<BattleStateSnapshot> {
  const res = await fetch(`${base}/api/battle/state/${sessionId}`);
  return res.json();
}

export async function getRegistry(): Promise<RegistryEntry[]> {
  const res = await fetch(`${base}/api/registry`);
  return res.json();
}

export async function getMetrics(): Promise<{ registry_size: number; emergent_attacks: number }> {
  const res = await fetch(`${base}/api/metrics`);
  return res.json();
}
