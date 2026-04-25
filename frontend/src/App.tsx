import { useEffect, useMemo, useRef, useState } from "react";

type BattleEvent = {
  type: string;
  [key: string]: unknown;
};

type BattleObservation = {
  session_id: string;
  turn: number;
  max_turns: number;
  cumulative_red_reward: number;
  cumulative_blue_reward: number;
  done: boolean;
};

function App() {
  const apiBase = useMemo(() => window.location.origin, []);
  const [sessionId, setSessionId] = useState<string>("");
  const [observation, setObservation] = useState<BattleObservation | null>(null);
  const [events, setEvents] = useState<BattleEvent[]>([]);
  const [registryCount, setRegistryCount] = useState<number>(0);
  const wsRef = useRef<WebSocket | null>(null);

  async function refreshRegistry() {
    const res = await fetch(`${apiBase}/api/registry`);
    if (res.ok) {
      const entries = (await res.json()) as unknown[];
      setRegistryCount(entries.length);
    }
  }

  async function startBattle() {
    const res = await fetch(`${apiBase}/api/battle/start`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ task_id: 4, max_turns: 8 }),
    });
    const json = await res.json();
    setSessionId(json.session_id);
    setObservation(json.observation as BattleObservation);
    setEvents([]);
  }

  async function step(role: "red" | "blue") {
    if (!sessionId) {
      return;
    }
    const action =
      role === "red"
        ? {
            role: "red",
            red_payload: {
              strategy: ["crescendo", "detail_escalation"],
              thought: "Escalate details gradually.",
              predicted_target_response: "partial",
            },
          }
        : {
            role: "blue",
            blue_payload: {
              defense: ["early_intervention", "pattern_flag"],
              threat_level: "high",
              thought: "Block unsafe progression.",
            },
          };
    const res = await fetch(`${apiBase}/api/battle/step`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, action }),
    });
    const json = await res.json();
    setObservation(json.observation as BattleObservation);
    await refreshRegistry();
  }

  useEffect(() => {
    refreshRegistry().catch(() => undefined);
  }, []);

  useEffect(() => {
    if (!sessionId) {
      return;
    }
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws/battle/${sessionId}`);
    ws.onmessage = (event) => {
      const payload = JSON.parse(event.data) as BattleEvent;
      setEvents((prev) => [payload, ...prev].slice(0, 40));
    };
    wsRef.current = ws;
    return () => {
      ws.close();
      wsRef.current = null;
    };
  }, [sessionId]);

  return (
    <main className="page">
      <header>
        <h1>GOAT-Evolution</h1>
        <p>Co-evolving Red vs Blue safety environment</p>
      </header>

      <section className="cards">
        <article className="card">
          <h2>Battle Arena</h2>
          <div className="row">
            <button onClick={startBattle}>Start Battle</button>
            <button onClick={() => step("red")} disabled={!sessionId}>
              Red Step
            </button>
            <button onClick={() => step("blue")} disabled={!sessionId}>
              Blue Step
            </button>
          </div>
          <pre>{JSON.stringify(observation, null, 2)}</pre>
        </article>

        <article className="card">
          <h2>Registry Explorer</h2>
          <p>Total attacks: {registryCount}</p>
        </article>

        <article className="card">
          <h2>Live Event Log</h2>
          <div className="event-log">
            {events.length === 0 ? (
              <p>No events yet.</p>
            ) : (
              events.map((event, i) => <pre key={`${event.type}-${i}`}>{JSON.stringify(event, null, 2)}</pre>)
            )}
          </div>
        </article>
      </section>
    </main>
  );
}

export default App;
