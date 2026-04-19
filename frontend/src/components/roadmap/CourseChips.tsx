import React from 'react';

import type { Course } from '../../types';

export default function CourseChips({ courses }: { courses: Course[] }) {
  return (
    <div className="flex flex-wrap gap-3">
      {courses.map((c) => (
        <div
          key={`${c.name}-${c.platform}`}
          className="px-4 py-3 rounded-full border border-border2"
          style={{ background: 'rgba(255,255,255,0.02)' }}
        >
          <div className="font-syne font-bold text-[14px]">{c.name}</div>
          <div className="font-mono text-muted text-[11px] uppercase tracking-widest mt-1">
            {c.platform} • {c.duration} • {c.type}
          </div>
        </div>
      ))}
    </div>
  );
}

