import React from 'react';

import type { TimelineItem } from '../../types';

export default function MilestoneTimeline({ timeline }: { timeline: TimelineItem[] }) {
  return (
    <div className="relative pl-10">
      <div
        aria-hidden
        className="absolute"
        style={{
          left: 12,
          width: 1,
          top: 0,
          bottom: 0,
          background: 'rgba(240,23,122,0.3)',
        }}
      />

      <div className="flex flex-col gap-4">
        {timeline.map((item, i) => (
          <div
            key={`${item.month}-${item.title}-${i}`}
            className="flex gap-4 animate-fadeUp"
            style={{ animationDelay: `${i * 120}ms` }}
          >
            <div
              className="w-[24px] h-[24px] rounded-full border flex items-center justify-center text-[12px]"
              style={{
                background: 'rgba(240,23,122,0.12)',
                borderColor: 'rgba(240,23,122,0.35)',
                color: '#f0177a',
              }}
            >
              {item.emoji}
            </div>

            <div>
              <div className="font-mono text-[10px] uppercase tracking-widest text-cyan">{item.month}</div>
              <div className="font-syne text-[16px] font-bold mt-1">{item.title}</div>
              <div className="text-muted text-[13px] leading-relaxed mt-1">{item.description}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

