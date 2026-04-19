export type FactorItem = {
  label: string;
  value: number;
};

export type RiskItem = {
  label: string;
  level: 'high' | 'medium' | 'low' | string;
};

export type PredictRequest = {
  hoursStudied: number;
  attendance: number;
  previousScores: number;
  sleepHours: number;
  tutoringSessions: number;
  parentalInvolvement: number; // 1–3
  accessToResources: number; // 1–3
  motivationLevel: number; // 1–3
  internetAccess: number; // 0 or 1
};

export type PredictResult = {
  score: number;
  grade: string;
  gradeLabel: string;
  factors: FactorItem[];
  risks: RiskItem[];
  cluster: number;
  clusterLabel: string;
  clusterDescription: string;
};

export type RoadmapRequest = {
  name: string;
  stage: string;
  field: string;
  score?: string | null;
  skills: string[];
  dreamRole: string;
  timeline: string;
  weeklyHours: string;
  context?: string | null;
};

export type SkillGap = {
  skill: string;
  current: number;
  required: number;
  priority: 'High' | 'Medium' | 'Low' | string;
};

export type TimelineItem = {
  month: string;
  title: string;
  description: string;
  emoji: string;
};

export type Course = {
  name: string;
  platform: string;
  duration: string;
  type: 'Free' | 'Paid' | string;
};

export type Internship = {
  title: string;
  platform: string;
  emoji: string;
  tips: string;
};

export type RoadmapResult = {
  summary: string;
  skillGaps: SkillGap[];
  timeline: TimelineItem[];
  courses: Course[];
  internships: Internship[];
  resumeTips: string[];
};

export type SessionContext = {
  predictedScore?: number;
  grade?: string;
  clusterLabel?: string;
  riskFlags?: string[];
  targetRole?: string;
  timeline?: string;
};

export type ChatMessage = {
  role: 'user' | 'assistant';
  content: string;
};

export type CoachRequest = {
  message: string;
  history: ChatMessage[];
  topic: 'career' | 'skills' | 'interview' | 'resume' | 'motivation' | string;
  sessionContext?: SessionContext | null;
  /** Plain-text resume; sent to the model for this request only (not shown in chat bubbles). */
  resumeText?: string | null;
};

export type CoachResponse = {
  reply: string;
};

