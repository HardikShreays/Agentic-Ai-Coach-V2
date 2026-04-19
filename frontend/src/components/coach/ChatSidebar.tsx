import React from 'react';

import type { SessionContext } from '../../types';

type Topic = {
  key: 'career' | 'skills' | 'interview' | 'resume' | 'motivation';
  icon: string;
  title: string;
  subtitle: string;
};

const TOPICS: Topic[] = [
  { key: 'career', icon: '🎯', title: 'Career Planning', subtitle: 'Roles, paths, strategy' },
  { key: 'skills', icon: '⚡', title: 'Skill Building', subtitle: 'What to learn & how' },
  { key: 'interview', icon: '💬', title: 'Interview Prep', subtitle: 'DSA, HR, system design' },
  { key: 'resume', icon: '📄', title: 'Resume Tips', subtitle: 'Optimise & improve' },
  { key: 'motivation', icon: '🔥', title: 'Motivation', subtitle: 'Mindset & consistency' },
];

export default function ChatSidebar({
  activeTopic,
  onSelectTopic,
  sessionContext,
  onClearChat,
}: {
  activeTopic: string;
  onSelectTopic: (t: Topic['key']) => void;
  sessionContext: SessionContext | null;
  onClearChat: () => void;
}) {
  return (
    <aside className="flex flex-col gap-4 acad-card h-full">
      <div>
        <div className="acad-card-title">Quick Topics</div>
        <div className="flex flex-col gap-3 mt-3">
          {TOPICS.map((t) => {
            const selected = activeTopic === t.key;
            return (
              <button
                key={t.key}
                type="button"
                onClick={() => onSelectTopic(t.key)}
                className="text-left rounded-2xl p-3 border transition-colors"
                style={{
                  background: selected ? 'rgba(240,23,122,0.12)' : 'rgba(255,255,255,0.03)',
                  borderColor: selected ? 'rgba(240,23,122,0.35)' : 'rgba(139,92,246,0.2)',
                }}
              >
                <div className="flex items-center gap-3">
                  <div
                    className="w-9 h-9 rounded-full flex items-center justify-center border"
                    style={{
                      background: selected ? 'rgba(240,23,122,0.12)' : 'rgba(139,92,246,0.10)',
                      borderColor: selected ? 'rgba(240,23,122,0.35)' : 'rgba(139,92,246,0.2)',
                    }}
                  >
                    {t.icon}
                  </div>
                  <div>
                    <div className="font-syne font-bold text-[14px]">{t.title}</div>
                    <div className="font-mono text-[11px] uppercase tracking-widest text-muted mt-1">
                      {t.subtitle}
                    </div>
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      <div className="mt-auto">
        <div className="acad-card-title">Session Context</div>
        <div className="mt-3">
          {sessionContext ? (
            <div className="flex flex-col gap-2 text-[13px] leading-relaxed">
              <div className="font-mono text-muted uppercase tracking-widest text-[11px]">Score</div>
              <div className="font-sans">
                Score:{' '}
                {typeof sessionContext.predictedScore === 'number' ? `${sessionContext.predictedScore.toFixed(1)}/100` : '—'}
                {sessionContext.grade ? ` (${sessionContext.grade})` : ''}
              </div>
              {sessionContext.clusterLabel ? (
                <div className="font-sans">
                  Cluster: <span style={{ color: '#ede9f8' }}>{sessionContext.clusterLabel}</span>
                </div>
              ) : null}
              {sessionContext.targetRole ? (
                <div className="font-sans">
                  Target: <span style={{ color: '#ede9f8' }}>{sessionContext.targetRole}</span>
                </div>
              ) : null}
              {sessionContext.riskFlags && sessionContext.riskFlags.length ? (
                <div className="font-mono text-muted text-[11px] uppercase tracking-widest">
                  Risks: {sessionContext.riskFlags.join(', ')}
                </div>
              ) : null}
            </div>
          ) : (
            <div className="text-muted text-[13px] leading-relaxed">
              No session context yet. Use <span style={{ color: '#f0177a' }}>PREDICT</span> or{' '}
              <span style={{ color: '#8b5cf6' }}>ROADMAP</span> first.
            </div>
          )}
        </div>

        <div className="mt-4">
          <button
            type="button"
            onClick={onClearChat}
            className="font-mono text-[11px] uppercase tracking-widest rounded-full px-4 py-2 border"
            style={{
              background: 'rgba(255,255,255,0.02)',
              borderColor: 'rgba(139,92,246,0.2)',
              color: 'rgba(139,92,246,0.95)',
            }}
          >
            Clear Chat
          </button>
        </div>
      </div>
    </aside>
  );
}

