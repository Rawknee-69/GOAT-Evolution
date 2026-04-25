export function EventLog({ events }: { events: any[] }) {
  return <pre className="max-h-64 overflow-auto rounded-xl border border-slate-700 bg-slate-900/70 p-3 text-xs">{JSON.stringify(events.slice(-20), null, 2)}</pre>;
}
