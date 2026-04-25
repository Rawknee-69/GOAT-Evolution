import { useEffect } from "react";
import { useBattleStore } from "../stores/battleStore";

export function useBattleWebSocket(sessionId?: string) {
  const pushEvent = useBattleStore((s) => s.pushEvent);
  const setStatus = useBattleStore((s) => s.setStatus);
  const setError = useBattleStore((s) => s.setError);

  useEffect(() => {
    if (!sessionId) return;

    const proto = window.location.protocol === "https:" ? "wss" : "ws";
    const ws = new WebSocket(`${proto}://${window.location.host}/ws/battle/${sessionId}`);
    setStatus("running");

    ws.onmessage = (evt) => {
      try {
        const payload = JSON.parse(evt.data);
        if (payload?.event === "ping") return;
        pushEvent(payload);
      } catch {
        // Ignore malformed packets.
      }
    };

    ws.onerror = () => setError("WebSocket disconnected.");
    ws.onclose = () => setStatus("stopped");

    return () => ws.close();
  }, [sessionId, pushEvent, setError, setStatus]);
}
