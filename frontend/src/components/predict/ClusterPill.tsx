import React from 'react';

export default function ClusterPill({
  cluster,
  label,
  description,
}: {
  cluster: number;
  label: string;
  description: string;
}) {
  const st =
    cluster === 0
      ? {
          bg: 'rgba(240,23,122,0.12)',
          border: 'rgba(240,23,122,0.35)',
          color: '#f0177a',
        }
      : cluster === 1
        ? {
            bg: 'rgba(139,92,246,0.12)',
            border: 'rgba(139,92,246,0.35)',
            color: '#8b5cf6',
          }
        : {
            bg: 'rgba(6,214,199,0.10)',
            border: 'rgba(6,214,199,0.35)',
            color: '#06d6c7',
          };

  return (
    <div className="flex flex-col gap-3">
      <div
        className="inline-flex items-center gap-2 rounded-full px-4 py-2 border"
        style={{ background: st.bg, borderColor: st.border, color: st.color }}
      >
        <span className="font-mono text-[12px] uppercase tracking-widest">CLUSTER {cluster}</span>
        <span className="font-syne text-[14px] font-bold" style={{ color: st.color }}>
          {label}
        </span>
      </div>
      <div className="text-muted font-sans text-[13px] leading-relaxed">{description}</div>
    </div>
  );
}

