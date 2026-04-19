import { create } from 'zustand';

import type {
  ChatMessage,
  PredictResult,
  RoadmapResult,
  SessionContext,
} from '../types';

type RoadmapMeta = {
  dreamRole?: string;
  timelineGoal?: string;
};

type SessionStore = {
  // Predict state
  predictResult: PredictResult | null;
  setPredictResult: (r: PredictResult) => void;

  // Roadmap state
  roadmapResult: RoadmapResult | null;
  setRoadmapResult: (r: RoadmapResult) => void;

  roadmapMeta: RoadmapMeta;
  setRoadmapMeta: (m: RoadmapMeta) => void;

  // Coach state
  chatHistory: ChatMessage[];
  addMessage: (msg: ChatMessage) => void;
  clearChat: () => void;
  activeTopic: string;
  setActiveTopic: (t: string) => void;

  // DB-backed session context (hydrated after login)
  dbSessionContext: SessionContext | null;
  setDbSessionContext: (ctx: SessionContext | null) => void;

  // Computed session context (passed to coach API)
  getSessionContext: () => SessionContext | null;
};

export const useSessionStore = create<SessionStore>((set, get) => ({
  predictResult: null,
  setPredictResult: (r) => set({ predictResult: r }),

  roadmapResult: null,
  setRoadmapResult: (r) => set({ roadmapResult: r }),

  roadmapMeta: {},
  setRoadmapMeta: (m) => set({ roadmapMeta: { ...get().roadmapMeta, ...m } }),

  chatHistory: [],
  addMessage: (msg) =>
    set((s) => ({
      chatHistory: [...s.chatHistory, msg],
    })),
  clearChat: () => set({ chatHistory: [] }),

  activeTopic: 'career',
  setActiveTopic: (t) => set({ activeTopic: t }),

  dbSessionContext: null,
  setDbSessionContext: (ctx) => set({ dbSessionContext: ctx }),

  getSessionContext: () => {
    const s = get();
    if (s.dbSessionContext) return s.dbSessionContext;
    if (!s.predictResult && !s.roadmapResult) return null;

    const predictedScore = s.predictResult?.score;
    const grade = s.predictResult?.grade;
    const clusterLabel = s.predictResult?.clusterLabel;
    const riskFlags = s.predictResult?.risks?.map((r) => r.label);

    return {
      predictedScore: predictedScore ?? undefined,
      grade: grade ?? undefined,
      clusterLabel: clusterLabel ?? undefined,
      riskFlags: riskFlags && riskFlags.length ? riskFlags : undefined,
      targetRole: s.roadmapMeta.dreamRole ?? undefined,
      timeline: s.roadmapMeta.timelineGoal ?? undefined,
    };
  },
}));

