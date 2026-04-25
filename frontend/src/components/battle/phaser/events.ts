export type BattleActionType = "attack" | "defend" | "impact" | "ko";

export interface BattleAction {
  actorTeam: "red" | "blue";
  targetTeam: "red" | "blue";
  lane: number;
  type: BattleActionType;
  strength: number;
}

const actionByEvent: Record<string, BattleActionType> = {
  red_action: "attack",
  target_responds: "impact",
  blue_action: "defend",
  battle_done: "ko",
};

export function eventToBattleAction(event: any): BattleAction | null {
  const eventType = String(event?.event ?? "");
  const mapped = actionByEvent[eventType];
  if (!mapped) return null;
  const laneSeed = Number(event?.payload?.turn_number ?? event?.turn_number ?? 0);
  const lane = Math.abs(laneSeed) % 3;
  const violation = Number(event?.payload?.violation_score ?? 0.5);

  switch (mapped) {
    case "attack":
      return { actorTeam: "red", targetTeam: "blue", lane, type: "attack", strength: 0.65 + violation * 0.35 };
    case "defend":
      return { actorTeam: "blue", targetTeam: "blue", lane, type: "defend", strength: 0.5 + (1 - violation) * 0.5 };
    case "impact":
      return { actorTeam: "red", targetTeam: "blue", lane, type: "impact", strength: 0.6 + violation * 0.4 };
    case "ko":
      return { actorTeam: "red", targetTeam: "blue", lane, type: "ko", strength: 1 };
    default:
      return null;
  }
}
