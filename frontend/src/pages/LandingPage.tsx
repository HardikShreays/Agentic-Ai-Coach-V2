import React from 'react';
import { Link } from 'react-router-dom';

import { useAuthStore } from '../store/useAuthStore';

const features = [
  {
    title: 'Predict',
    desc: 'Estimate performance from study habits and get peer-aware risk signals tailored to your profile.',
    to: '/predict',
    accent: '#f0177a',
  },
  {
    title: 'Roadmap',
    desc: 'Turn your dream role and timeline into a structured India-market plan: skills, courses, and milestones.',
    to: '/roadmap',
    accent: '#8b5cf6',
  },
  {
    title: 'AI Coach',
    desc: 'Chat with AcadCoach using your predict and roadmap context for placement-ready guidance.',
    to: '/coach',
    accent: '#06d6c7',
  },
] as const;

export default function LandingPage() {
  const user = useAuthStore((s) => s.user);

  return (
    <div className="flex flex-col gap-14 pb-8">
      <section className="relative overflow-hidden rounded-2xl border border-pink-500/20 bg-[rgba(30,16,53,0.5)] px-6 py-14 md:px-12 md:py-20">
        <div
          className="pointer-events-none absolute -right-20 -top-20 h-64 w-64 rounded-full opacity-40 blur-3xl"
          style={{ background: 'radial-gradient(circle, rgba(240,23,122,0.5), transparent 70%)' }}
        />
        <div
          className="pointer-events-none absolute -bottom-24 -left-16 h-72 w-72 rounded-full opacity-35 blur-3xl"
          style={{ background: 'radial-gradient(circle, rgba(139,92,246,0.45), transparent 70%)' }}
        />

        <div className="relative max-w-2xl">
          <p className="font-mono text-[11px] uppercase tracking-[0.25em] text-cyan mb-4">India-focused academic & career OS</p>
          <h1 className="font-syne font-bold text-[clamp(2rem,5vw,3.25rem)] leading-tight text-[#ede9f8] mb-5">
            Predict outcomes. Plan your path. Coach every step.
          </h1>
          <p className="text-muted text-[15px] leading-relaxed max-w-xl mb-8">
            AcadPipeline combines ML prediction, AI-generated roadmaps, and a context-aware coach so students can prepare
            for placements with clarity—not guesswork.
          </p>
          <div className="flex flex-wrap gap-3">
            {user ? (
              <Link to="/predict" className="acad-btn acad-btn-primary inline-flex text-center no-underline">
                Go to app
              </Link>
            ) : (
              <>
                <Link to="/signup" className="acad-btn acad-btn-primary inline-flex text-center no-underline">
                  Create free account
                </Link>
                <Link to="/login" className="acad-btn acad-btn-ghost inline-flex text-center no-underline">
                  Sign in
                </Link>
              </>
            )}
          </div>
        </div>
      </section>

      <section>
        <h2 className="font-syne font-bold text-[20px] text-text mb-2">What you unlock</h2>
        <p className="text-muted text-[13px] mb-8 max-w-xl">
          Predict, Roadmap, and AI Coach are available after you sign in—your session and coach history stay with your account.
        </p>
        <div className="grid gap-5 md:grid-cols-3">
          {features.map((f) => (
            <article
              key={f.title}
              className="acad-card flex flex-col gap-3 !py-6"
              style={{ borderColor: `${f.accent}33` }}
            >
              <div className="font-syne font-bold text-[18px]" style={{ color: f.accent }}>
                {f.title}
              </div>
              <p className="text-muted text-[13px] leading-relaxed flex-1">{f.desc}</p>
              {user ? (
                <Link to={f.to} className="font-mono text-[11px] uppercase tracking-widest" style={{ color: f.accent }}>
                  Open →
                </Link>
              ) : (
                <Link
                  to={`/login?redirect=${encodeURIComponent(f.to)}`}
                  className="font-mono text-[11px] uppercase tracking-widest"
                  style={{ color: f.accent }}
                >
                  Sign in to use →
                </Link>
              )}
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
