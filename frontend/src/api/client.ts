import axios from 'axios';

import type {
  CoachRequest,
  CoachResponse,
  PredictRequest,
  PredictResult,
  RoadmapRequest,
  RoadmapResult,
  SessionContext,
} from '../types';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true,
});

function toPredictResult(payload: any): PredictResult {
  return {
    score: payload.score,
    grade: payload.grade,
    gradeLabel: payload.grade_label,
    factors: (payload.factors || []).map((f: any) => ({ label: f.label, value: Number(f.value) })),
    risks: (payload.risks || []).map((r: any) => ({ label: r.label, level: r.level })),
    cluster: payload.cluster,
    clusterLabel: payload.cluster_label,
    clusterDescription: payload.cluster_description,
  };
}

function toRoadmapResult(payload: any): RoadmapResult {
  const gaps = payload.skill_gaps ?? payload.skillGaps ?? [];
  const tips = payload.resume_tips ?? payload.resumeTips ?? [];
  return {
    summary: payload.summary,
    skillGaps: gaps.map((s: any) => ({
      skill: s.skill,
      current: Number(s.current),
      required: Number(s.required),
      priority: s.priority,
    })),
    timeline: (payload.timeline || []).map((t: any) => ({
      month: t.month,
      title: t.title,
      description: t.description,
      emoji: t.emoji,
    })),
    courses: (payload.courses || []).map((c: any) => ({
      name: c.name,
      platform: c.platform,
      duration: c.duration,
      type: c.type,
    })),
    internships: (payload.internships || []).map((i: any) => ({
      title: i.title,
      platform: i.platform,
      emoji: i.emoji,
      tips: i.tips,
    })),
    resumeTips: tips,
  };
}

function sessionContextToSnake(ctx?: SessionContext | null) {
  if (!ctx) return undefined;
  return {
    predicted_score: ctx.predictedScore,
    grade: ctx.grade,
    cluster_label: ctx.clusterLabel,
    risk_flags: ctx.riskFlags,
    target_role: ctx.targetRole,
    timeline: ctx.timeline,
  };
}

function sessionContextFromSnake(payload: any): SessionContext {
  return {
    predictedScore: payload?.predicted_score ?? undefined,
    grade: payload?.grade ?? undefined,
    clusterLabel: payload?.cluster_label ?? undefined,
    riskFlags: payload?.risk_flags ?? undefined,
    targetRole: payload?.target_role ?? undefined,
    timeline: payload?.timeline ?? undefined,
  };
}

export type AuthUser = {
  userId: string;
  email: string;
};

export const signup = async (data: { email: string; password: string }): Promise<AuthUser> => {
  const resp = await api.post('/api/auth/signup', data);
  return { userId: resp.data.user_id, email: resp.data.email };
};

export const login = async (data: { email: string; password: string }): Promise<AuthUser> => {
  const resp = await api.post('/api/auth/login', data);
  return { userId: resp.data.user_id, email: resp.data.email };
};

export const getMe = async (): Promise<AuthUser> => {
  const resp = await api.get('/api/auth/me');
  return { userId: resp.data.user_id, email: resp.data.email };
};

export const logout = async (): Promise<{ ok: boolean }> => {
  const resp = await api.post('/api/auth/logout');
  return resp.data;
};

export const fetchSessionContext = async (): Promise<SessionContext> => {
  const resp = await api.get('/api/session/context');
  return sessionContextFromSnake(resp.data);
};

export const predictScore = async (data: PredictRequest): Promise<PredictResult> => {
  const resp = await api.post('/api/predict', {
    hours_studied: data.hoursStudied,
    attendance: data.attendance,
    previous_scores: data.previousScores,
    sleep_hours: data.sleepHours,
    tutoring_sessions: data.tutoringSessions,
    parental_involvement: data.parentalInvolvement,
    access_to_resources: data.accessToResources,
    motivation_level: data.motivationLevel,
    internet_access: data.internetAccess,
  });
  return toPredictResult(resp.data);
};

export const generateRoadmap = async (data: RoadmapRequest): Promise<RoadmapResult> => {
  const resp = await api.post('/api/roadmap', {
    name: data.name,
    stage: data.stage,
    field: data.field,
    score: data.score ?? null,
    skills: data.skills,
    dream_role: data.dreamRole,
    timeline: data.timeline,
    weekly_hours: data.weeklyHours,
    context: data.context ?? null,
  });
  return toRoadmapResult(resp.data);
};

export const sendCoachMessage = async (data: CoachRequest): Promise<CoachResponse> => {
  const payload: Record<string, unknown> = {
    message: data.message,
    history: data.history,
    topic: data.topic,
    session_context: sessionContextToSnake(data.sessionContext),
  };
  const rt = data.resumeText?.trim();
  if (rt) payload.resume_text = rt;
  const resp = await api.post('/api/coach', payload);
  return resp.data as CoachResponse;
};

