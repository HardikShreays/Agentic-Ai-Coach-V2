import React, { useEffect, useState } from 'react';

import type { SkillGap } from '../../types';

function priorityStyle(p: string) {
  const s = p.toLowerCase();
  if (s === 'high') return { bg: 'rgba(239,68,68,0.12)', border: 'rgba(239,68,68,0.3)', color: '#f87171' };
  if (s === 'medium') return { bg: 'rgba(245,158,11,0.12)', border: 'rgba(245,158,11,0.3)', color: '#fbbf24' };
  return { bg: 'rgba(34,197,94,0.12)', border: 'rgba(34,197,94,0.3)', color: '#4ade80' };
}

export default function SkillGapBars({ skillGaps }: { skillGaps: SkillGap[] }) {
  const [animate, setAnimate] = useState(false);

  useEffect(() => {
    const id = requestAnimationFrame(() => setAnimate(true));
    return () => cancelAnimationFrame(id);
  }, []);

  return (
    <div className="flex flex-col gap-5">
      {skillGaps.map((sg) => {
        const pct = Math.max(0, Math.min(100, sg.current));
        const st = priorityStyle(sg.priority);
        return (
          <div key={sg.skill} className="flex items-center gap-4">
            <div style={{ width: 130 }} className="font-mono text-[10px] text-muted uppercase tracking-widest">
              {sg.skill}
            </div>
            <div className="flex-1">
              <div style={{ height: 5, background: 'rgba(255,255,255,0.06)', borderRadius: 3 }}>
                <div
                  style={{
                    height: 5,
                    width: animate ? `${pct}%` : '0%',
                    background: 'linear-gradient(90deg, rgba(139,92,246,1), rgba(240,23,122,1))',
                    borderRadius: 3,
                    transition: 'width 1000ms cubic-bezier(0.4,0,0.2,1)',
                  }}
                />
              </div>
            </div>
            <div className="font-mono text-[12px] text-pink" style={{ width: 54, textAlign: 'right' }}>
              {Math.round(pct)}%
            </div>
            <div
              className="font-mono text-[9px] uppercase tracking-widest px-3 py-2 rounded-full"
              style={{
                background: st.bg,
                border: `1px solid ${st.border}`,
                color: st.color,
              }}
            >
              {sg.priority}
            </div>
          </div>
        );
      })}
    </div>
  );
}

