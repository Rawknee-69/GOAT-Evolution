export function ConversationFeed({ events }: { events: any[] }) {
  return (
    <div className="h-96 overflow-auto rounded-xl border border-slate-700 bg-slate-900/70 p-3 text-xs">
      {events.length === 0 ? <p className="text-slate-400">No events yet.</p> : null}
      {events.map((e, i) => (
        <div key={i} className="mb-2 rounded border border-slate-800 bg-slate-950 p-2">
          <div className="font-mono text-emerald-400">{e.event}</div>
          <pre className="whitespace-pre-wrap text-slate-300">{JSON.stringify(e.payload, null, 2)}</pre>
        </div>
      ))}
    </div>
  );
}
