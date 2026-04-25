import { create } from "zustand";

interface BattleState {
  sessionId?: string;
  events: any[];
  setSessionId: (id?: string) => void;
  pushEvent: (evt: any) => void;
}

export const useBattleStore = create<BattleState>((set) => ({
  sessionId: undefined,
  events: [],
  setSessionId: (sessionId) => set({ sessionId, events: [] }),
  pushEvent: (evt) => set((state) => ({ events: [...state.events.slice(-199), evt] })),
}));
