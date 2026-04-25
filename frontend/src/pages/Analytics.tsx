import { useMemo } from "react";
import { ASRChart } from "../components/analytics/ASRChart";
import { useBattleStore } from "../stores/battleStore";

export function Analytics() {
  const events = useBattleStore((s) => s.events);
  const data = useMemo(() => {
    let i = 0;
    return events
      .filter((e) => e.event === "target_responds")
      .map((e) => ({ x: i++, y: Number(e.payload?.violation_score ?? 0) }));
  }, [events]);
  return <ASRChart data={data} />;
}
