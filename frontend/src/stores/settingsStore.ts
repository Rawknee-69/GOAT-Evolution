import { create } from "zustand";
import type { ModelProfile, Provider } from "../lib/types";

interface SettingsState {
  redProvider: Provider;
  blueProvider: Provider;
  modelProfile: ModelProfile;
  seed: number | "";
  speed: number;
  autoplay: boolean;
  taskId: number;
  setRedProvider: (v: Provider) => void;
  setBlueProvider: (v: Provider) => void;
  setModelProfile: (v: ModelProfile) => void;
  setSeed: (v: number | "") => void;
  setSpeed: (v: number) => void;
  setAutoplay: (v: boolean) => void;
  setTaskId: (v: number) => void;
}

export const useSettingsStore = create<SettingsState>((set) => ({
  redProvider: "scripted",
  blueProvider: "scripted",
  modelProfile: "standard_model",
  seed: "",
  speed: 1,
  autoplay: false,
  taskId: 4,
  setRedProvider: (v) => set({ redProvider: v }),
  setBlueProvider: (v) => set({ blueProvider: v }),
  setModelProfile: (v) => set({ modelProfile: v }),
  setSeed: (v) => set({ seed: v }),
  setSpeed: (v) => set({ speed: Math.min(2.5, Math.max(0.5, v)) }),
  setAutoplay: (v) => set({ autoplay: v }),
  setTaskId: (v) => set({ taskId: v }),
}));
