import type { RegistryEntry } from "../../lib/types";
import { RegistryCard } from "./RegistryCard";

export function RegistryGrid({ entries }: { entries: RegistryEntry[] }) {
  return <div className="grid gap-2 md:grid-cols-2 lg:grid-cols-3">{entries.map((entry) => <RegistryCard key={entry.attack_id} entry={entry} />)}</div>;
}
