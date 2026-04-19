import React from 'react';

export default function HeroTag({ children }: { children: React.ReactNode }) {
  return (
    <span
      className="inline-flex items-center rounded-full border border-border2 px-3 py-1 font-mono text-[11px] uppercase tracking-widest"
      style={{ color: '#8b7aaa' }}
    >
      {children}
    </span>
  );
}

