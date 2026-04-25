import { create } from "zustand";
import type { BattleStateSnapshot } from "../lib/types";

interface BattleState {
  sessionId?: string;
  events: any[];
  status: "idle" | "starting" | "running" | "stopped" | "error" | "done";
  lastError?: string;
  snapshot?: BattleStateSnapshot;
  resetVersion: number;
  setSessionId: (id?: string) => void;
  setStatus: (status: BattleState["status"]) => void;
  setError: (message?: string) => void;
  setSnapshot: (snapshot?: BattleStateSnapshot) => void;
  pushEvent: (evt: any) => void;
  clear: () => void;
  bumpReset: () => void;
}

export const useBattleStore = create<BattleState>((set) => ({
  sessionId: undefined,
  events: [],
  status: "idle",
  lastError: undefined,
  snapshot: undefined,
  resetVersion: 0,
  setSessionId: (sessionId) =>
    set((state) => ({
      sessionId,
      events: [],
      snapshot: undefined,
      status: sessionId ? "starting" : "idle",
      lastError: undefined,
      resetVersion: state.resetVersion + 1,
    })),
  setStatus: (status) => set({ status }),
  setError: (message) => set({ lastError: message, status: message ? "error" : "idle" }),
  setSnapshot: (snapshot) => set({ snapshot, status: snapshot?.is_done ? "done" : "running" }),
  pushEvent: (evt) => set((state) => ({ events: [...state.events.slice(-199), evt] })),
  clear: () =>
    set((state) => ({
      sessionId: undefined,
      events: [],
      status: "idle",
      snapshot: undefined,
      lastError: undefined,
      resetVersion: state.resetVersion + 1,
    })),
  bumpReset: () => set((state) => ({ resetVersion: state.resetVersion + 1 })),
}));
