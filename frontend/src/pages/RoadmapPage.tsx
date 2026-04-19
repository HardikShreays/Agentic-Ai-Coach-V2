import React, { useEffect, useMemo, useState } from 'react';

import { generateRoadmap } from '../api/client';
import { useSessionStore } from '../store/useSessionStore';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';

import StepProgress from '../components/roadmap/StepProgress';
import ProfileStep from '../components/roadmap/ProfileStep';
import GoalsStep from '../components/roadmap/GoalsStep';
import SkillGapBars from '../components/roadmap/SkillGapBars';
import MilestoneTimeline from '../components/roadmap/MilestoneTimeline';
import CourseChips from '../components/roadmap/CourseChips';
import InternshipList from '../components/roadmap/InternshipList';

import type { RoadmapRequest } from '../types';

const LOADING_MESSAGES = [
  'ANALYSING PROFILE...',
  'QUERYING MARKET DATA...',
  'FINDING SKILL GAPS...',
  'GENERATING ROADMAP...',
] as const;

export default function RoadmapPage() {
  const roadmapResult = useSessionStore((s) => s.roadmapResult);
  const setRoadmapResult = useSessionStore((s) => s.setRoadmapResult);
  const setRoadmapMeta = useSessionStore((s) => s.setRoadmapMeta);

  const [step, setStep] = useState<0 | 1 | 2>(0);
  const [loading, setLoading] = useState(false);
  const [loadingMessageIdx, setLoadingMessageIdx] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const [name, setName] = useState('');
  const [stage, setStage] = useState('');
  const [field, setField] = useState('');
  const [academicScore, setAcademicScore] = useState('');
  const [selectedSkills, setSelectedSkills] = useState<string[]>(['Python']);

  const [dreamRole, setDreamRole] = useState('');
  const [timeline, setTimeline] = useState('12 months');
  const [weeklyHours, setWeeklyHours] = useState('10–20');
  const [context, setContext] = useState('');

  useEffect(() => {
    if (!loading) return;
    const id = window.setInterval(() => {
      setLoadingMessageIdx((i) => (i + 1) % LOADING_MESSAGES.length);
    }, 1900);
    return () => window.clearInterval(id);
  }, [loading]);

  useEffect(() => {
    // Keep errors unless user returns to the very first step.
    if (step !== 2) setLoading(false);
    if (step === 0) setError(null);
  }, [step]);

  const step1Valid = useMemo(() => !!name.trim() && !!stage.trim() && !!field.trim(), [name, stage, field]);
  const step2Valid = useMemo(() => !!dreamRole.trim(), [dreamRole]);

  const roadmapRequest: RoadmapRequest = useMemo(
    () => ({
      name: name.trim(),
      stage,
      field,
      score: academicScore.trim() || null,
      skills: selectedSkills,
      dreamRole: dreamRole.trim(),
      timeline,
      weeklyHours,
      context: context.trim() || null,
    }),
    [name, stage, field, academicScore, selectedSkills, dreamRole, timeline, weeklyHours, context],
  );

  const runRoadmap = async () => {
    setLoading(true);
    setError(null);
    setLoadingMessageIdx(0);
    try {
      const res = await generateRoadmap(roadmapRequest);
      setRoadmapResult(res);
      setRoadmapMeta({ dreamRole: dreamRole.trim(), timelineGoal: timeline });
      setStep(2);
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Roadmap failed');
      setStep(1);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <StepProgress currentStep={step} />

      {step === 0 ? (
        <>
          <ProfileStep
            name={name}
            stage={stage}
            field={field}
            academicScore={academicScore}
            selectedSkills={selectedSkills}
            onChange={({ name, stage, field, academicScore, selectedSkills }) => {
              setName(name);
              setStage(stage);
              setField(field);
              setAcademicScore(academicScore);
              setSelectedSkills(selectedSkills);
            }}
          />

          {error ? <div className="text-pink font-mono text-[12px]">{error}</div> : null}

          <div className="flex justify-end">
            <Button
              variant="primary"
              disabled={!step1Valid || loading}
              onClick={() => {
                if (!step1Valid) {
                  setError('Please fill Name, Current Stage, and Field.');
                  return;
                }
                setStep(1);
              }}
            >
              Next
            </Button>
          </div>
        </>
      ) : null}

      {step === 1 ? (
        <>
          <GoalsStep
            dreamRole={dreamRole}
            timeline={timeline}
            weeklyHours={weeklyHours}
            context={context}
            onChange={({ dreamRole, timeline, weeklyHours, context }) => {
              setDreamRole(dreamRole);
              setTimeline(timeline);
              setWeeklyHours(weeklyHours);
              setContext(context);
            }}
          />

          {error ? <div className="text-pink font-mono text-[12px]">{error}</div> : null}

          <div className="flex justify-between mt-2">
            <Button variant="ghost" disabled={loading} onClick={() => setStep(0)}>
              Back
            </Button>
            <Button
              variant="primary"
              disabled={!step2Valid || loading}
              onClick={() => {
                if (!step2Valid) {
                  setError('Dream Role is required.');
                  return;
                }
                setStep(2);
                runRoadmap();
              }}
            >
              Generate Roadmap
            </Button>
          </div>
        </>
      ) : null}

      {step === 2 ? (
        <>
          {loading ? (
            <div className="flex flex-col items-center justify-center min-h-[420px] gap-4">
              <div
                className="rounded-full border-4"
                style={{
                  width: 44,
                  height: 44,
                  borderColor: 'rgba(240,23,122,0.2)',
                  borderTopColor: '#f0177a',
                  animation: 'spin 900ms linear infinite',
                }}
              />
              <div className="font-mono text-[12px] uppercase tracking-widest text-pink">{LOADING_MESSAGES[loadingMessageIdx]}</div>
              <div className="text-muted text-[13px] text-center max-w-lg">
                We’re building an India-focused roadmap based on your profile and goals.
              </div>
            </div>
          ) : roadmapResult ? (
            <div className="flex flex-col gap-6">
              <Card title="Skill Gaps">
                <SkillGapBars skillGaps={roadmapResult.skillGaps} />
              </Card>

              <Card title="Milestones Timeline">
                <MilestoneTimeline timeline={roadmapResult.timeline} />
              </Card>

              <Card title="Courses">
                <CourseChips courses={roadmapResult.courses} />
              </Card>

              <Card title="Internships">
                <InternshipList internships={roadmapResult.internships} />
              </Card>

              <Card title="Resume Tips">
                <ul className="resume-tips">
                  {roadmapResult.resumeTips.map((t, i) => (
                    <li key={`${t}-${i}`}>{t}</li>
                  ))}
                </ul>
              </Card>
            </div>
          ) : (
            <div className="acad-card min-h-[420px] flex items-center justify-center">
              <div className="text-muted font-sans">Generate a roadmap to see results here.</div>
            </div>
          )}

          {error ? <div className="text-pink font-mono text-[12px] mt-4">{error}</div> : null}

          <div className="flex justify-start mt-4">
            <Button variant="ghost" disabled={loading} onClick={() => setStep(0)}>
              Start Over
            </Button>
          </div>
        </>
      ) : null}
    </div>
  );
}

