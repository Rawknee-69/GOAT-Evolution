import { useEffect } from "react";
import { useBattleStore } from "../stores/battleStore";

export function useBattleWebSocket(sessionId?: string) {
  const pushEvent = useBattleStore((s) => s.pushEvent);

  useEffect(() => {
    if (!sessionId) return;

    const proto = window.location.protocol === "https:" ? "wss" : "ws";
    const ws = new WebSocket(`${proto}://${window.location.host}/ws/battle/${sessionId}`);

    ws.onmessage = (evt) => {
      try {
        const payload = JSON.parse(evt.data);
        pushEvent(payload);
      } catch {
        // Ignore malformed packets.
      }
    };

    return () => ws.close();
  }, [sessionId, pushEvent]);
}
