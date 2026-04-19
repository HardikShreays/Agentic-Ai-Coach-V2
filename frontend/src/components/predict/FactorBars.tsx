import React, { useEffect, useState } from 'react';

import type { FactorItem } from '../../types';

function FactorRow({ factor, animate }: { factor: FactorItem; animate: boolean }) {
  const width = `${Math.max(0, Math.min(100, factor.value))}%`;
  return (
    <div className="flex items-center gap-4">
      <div style={{ width: 115 }} className="font-mono text-[10px] text-muted uppercase tracking-widest">
        {factor.label}
      </div>
      <div className="flex-1">
        <div className="w-full" style={{ height: 5, background: 'rgba(255,255,255,0.06)', borderRadius: 3 }}>
          <div
            style={{
              height: 5,
              width: animate ? width : '0%',
              background: 'linear-gradient(90deg, rgba(139,92,246,1), rgba(240,23,122,1))',
              borderRadius: 3,
              transition: 'width 1000ms cubic-bezier(0.4,0,0.2,1)',
            }}
          />
        </div>
      </div>
      <div className="font-mono text-[12px] text-pink" style={{ width: 44, textAlign: 'right' }}>
        {Math.round(factor.value)}%
      </div>
    </div>
  );
}

export default function FactorBars({ factors }: { factors: FactorItem[] }) {
  const [animate, setAnimate] = useState(false);

  useEffect(() => {
    const t = requestAnimationFrame(() => setAnimate(true));
    return () => cancelAnimationFrame(t);
  }, []);

  return <div className="flex flex-col gap-4">{factors.map((f) => <FactorRow key={f.label} factor={f} animate={animate} />)}</div>;
}

