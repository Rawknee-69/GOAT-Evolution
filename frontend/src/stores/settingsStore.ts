import { create } from "zustand";
import type { Provider } from "../lib/types";

interface SettingsState {
  redProvider: Provider;
  blueProvider: Provider;
  taskId: number;
  setRedProvider: (v: Provider) => void;
  setBlueProvider: (v: Provider) => void;
  setTaskId: (v: number) => void;
}

export const useSettingsStore = create<SettingsState>((set) => ({
  redProvider: "scripted",
  blueProvider: "scripted",
  taskId: 4,
  setRedProvider: (v) => set({ redProvider: v }),
  setBlueProvider: (v) => set({ blueProvider: v }),
  setTaskId: (v) => set({ taskId: v }),
}));
