import { useEffect, useMemo } from "react";
import { AgentCard } from "../components/battle/AgentCard";
import { BattleControls } from "../components/battle/BattleControls";
import { ConversationFeed } from "../components/battle/ConversationFeed";
import { ViolationMeter } from "../components/battle/ViolationMeter";
import { RegistryGrid } from "../components/registry/RegistryGrid";
import { useBattleWebSocket } from "../hooks/useBattleWebSocket";
import { getRegistry } from "../lib/api";
import { useBattleStore } from "../stores/battleStore";
import { useRegistryStore } from "../stores/registryStore";

export function BattleArena() {
  const sessionId = useBattleStore((s) => s.sessionId);
  const events = useBattleStore((s) => s.events);
  const entries = useRegistryStore((s) => s.entries);
  const setEntries = useRegistryStore((s) => s.setEntries);
  useBattleWebSocket(sessionId);

  useEffect(() => {
    getRegistry().then(setEntries).catch(() => undefined);
  }, [events.length, setEntries]);

  const violation = useMemo(() => {
    const ev = [...events].reverse().find((e) => e.event === "target_responds");
    return Number(ev?.payload?.violation_score ?? 0);
  }, [events]);

  return (
    <div className="space-y-4">
      <BattleControls />
      <div className="grid gap-3 md:grid-cols-3">
        <AgentCard title="Red" subtitle="Attacker" />
        <ConversationFeed events={events} />
        <AgentCard title="Blue" subtitle="Defender" />
      </div>
      <ViolationMeter score={violation} />
      <RegistryGrid entries={entries} />
    </div>
  );
}
