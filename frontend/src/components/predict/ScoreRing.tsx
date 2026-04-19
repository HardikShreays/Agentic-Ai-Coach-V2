import React, { useEffect, useMemo, useState } from 'react';

function gradePillColor(grade: string) {
  const g = grade.toUpperCase();
  if (g === 'A+' || g === 'A') return { bg: 'rgba(34,197,94,0.12)', border: 'rgba(34,197,94,0.35)', text: '#4ade80' };
  if (g === 'B' || g === 'C') return { bg: 'rgba(245,158,11,0.12)', border: 'rgba(245,158,11,0.35)', text: '#fbbf24' };
  return { bg: 'rgba(239,68,68,0.12)', border: 'rgba(239,68,68,0.35)', text: '#f87171' };
}

export default function ScoreRing({
  score,
  grade,
  gradeLabel,
}: {
  score: number;
  grade: string;
  gradeLabel: string;
}) {
  const radius = 45;
  const circumference = useMemo(() => 2 * Math.PI * radius, []);
  const targetOffset = useMemo(() => circumference - (circumference * score) / 100, [circumference, score]);

  const [dashOffset, setDashOffset] = useState(circumference);

  useEffect(() => {
    const id = requestAnimationFrame(() => setDashOffset(targetOffset));
    return () => cancelAnimationFrame(id);
  }, [targetOffset]);

  const c = gradePillColor(grade);

  return (
    <div className="flex flex-col items-center gap-4">
      <div className="relative flex items-center justify-center" style={{ width: 108, height: 108 }}>
        <svg width="108" height="108" viewBox="0 0 100 100" style={{ transform: 'rotate(-90deg)' }}>
          <circle cx="50" cy="50" r={radius} fill="transparent" stroke="rgba(255,255,255,0.06)" strokeWidth="10" />
          <defs>
            <linearGradient id="scoreGradient" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stopColor="#8b5cf6" />
              <stop offset="100%" stopColor="#f0177a" />
            </linearGradient>
          </defs>
          <circle
            cx="50"
            cy="50"
            r={radius}
            fill="transparent"
            stroke="url(#scoreGradient)"
            strokeWidth="10"
            strokeDasharray={`${circumference}`}
            strokeDashoffset={dashOffset}
            strokeLinecap="round"
            style={{ transition: 'stroke-dashoffset 900ms cubic-bezier(0.4,0,0.2,1)' }}
          />
        </svg>

        <div className="absolute text-center">
          <div className="font-syne font-bold" style={{ fontSize: 22, lineHeight: 1 }}>
            {score.toFixed(1)}
          </div>
          <div className="font-mono text-[12px] text-muted" style={{ marginTop: 2 }}>
            /100
          </div>
        </div>
      </div>

      <div className="flex flex-col items-center gap-1">
        <div className="font-syne font-bold" style={{ color: '#ede9f8', fontSize: 18 }}>
          {gradeLabel}
        </div>
        <div
          className="font-mono text-[11px] uppercase tracking-widest px-4 py-1 rounded-full"
          style={{ background: c.bg, border: `1px solid ${c.border}`, color: c.text }}
        >
          {grade}
        </div>
      </div>
    </div>
  );
}

