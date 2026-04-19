import React from 'react';

import type { Internship } from '../../types';

export default function InternshipList({ internships }: { internships: Internship[] }) {
  return (
    <div className="flex flex-col gap-4">
      {internships.map((ins, i) => (
        <div key={`${ins.title}-${ins.platform}-${i}`} className="flex gap-4">
          <div
            className="w-[32px] h-[32px] rounded-[8px] flex items-center justify-center border"
            style={{ background: 'rgba(240,23,122,0.12)', borderColor: 'rgba(240,23,122,0.35)' }}
          >
            <span className="text-[16px]">{ins.emoji}</span>
          </div>
          <div>
            <div className="font-syne font-bold text-[15px]">{ins.title}</div>
            <div className="font-mono text-muted text-[12px] uppercase tracking-widest mt-1">
              {ins.platform}
            </div>
            <div className="text-muted text-[13px] leading-relaxed mt-1">{ins.tips}</div>
          </div>
        </div>
      ))}
    </div>
  );
}

