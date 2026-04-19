import React from 'react';

import type { RiskItem } from '../../types';

function stylesFor(level: string) {
  const l = level.toLowerCase();
  if (l === 'high') {
    return {
      bg: 'rgba(239,68,68,0.12)',
      border: 'rgba(239,68,68,0.3)',
      color: '#f87171',
    };
  }
  if (l === 'medium') {
    return {
      bg: 'rgba(245,158,11,0.12)',
      border: 'rgba(245,158,11,0.3)',
      color: '#fbbf24',
    };
  }
  return {
    bg: 'rgba(34,197,94,0.12)',
    border: 'rgba(34,197,94,0.3)',
    color: '#4ade80',
  };
}

export default function RiskBadges({ risks }: { risks: RiskItem[] }) {
  return (
    <div className="flex flex-wrap gap-2">
      {risks.map((r) => {
        const st = stylesFor(r.level);
        return (
          <span
            key={r.label}
            className="font-mono text-[9px] uppercase tracking-[1px] px-3 py-2 rounded-full"
            style={{ background: st.bg, border: `1px solid ${st.border}`, color: st.color }}
          >
            {r.label}
          </span>
        );
      })}
    </div>
  );
}

