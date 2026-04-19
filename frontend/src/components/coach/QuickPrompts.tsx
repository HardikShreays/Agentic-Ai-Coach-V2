import React from 'react';

const PROMPTS = ['How do I start with ML?', 'Path to FAANG?', 'How to build projects?', 'I feel demotivated'] as const;

export default function QuickPrompts({ onPick }: { onPick: (p: string) => void }) {
  return (
    <div className="flex flex-wrap items-center gap-2 font-mono text-[11px] uppercase tracking-widest text-muted">
      {PROMPTS.map((p, i) => (
        <React.Fragment key={p}>
          <button
            type="button"
            onClick={() => onPick(p)}
            className="rounded-full px-3 py-1 border"
            style={{ background: 'rgba(255,255,255,0.02)', borderColor: 'rgba(139,92,246,0.2)', color: 'rgba(139,92,246,0.95)' }}
          >
            {p}
          </button>
          {i < PROMPTS.length - 1 ? <span className="text-muted">|</span> : null}
        </React.Fragment>
      ))}
    </div>
  );
}

