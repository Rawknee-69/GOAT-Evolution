import { useEffect } from "react";
import { getRegistry } from "../lib/api";
import { RegistryGrid } from "../components/registry/RegistryGrid";
import { useRegistryStore } from "../stores/registryStore";

export function RegistryExplorer() {
  const entries = useRegistryStore((s) => s.entries);
  const setEntries = useRegistryStore((s) => s.setEntries);
  useEffect(() => {
    getRegistry().then(setEntries).catch(() => undefined);
  }, [setEntries]);
  return <RegistryGrid entries={entries} />;
}
