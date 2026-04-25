import { create } from "zustand";
import type { RegistryEntry } from "../lib/types";

interface RegistryState {
  entries: RegistryEntry[];
  setEntries: (entries: RegistryEntry[]) => void;
}

export const useRegistryStore = create<RegistryState>((set) => ({
  entries: [],
  setEntries: (entries) => set({ entries }),
}));
