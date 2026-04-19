import React from 'react';

import Card from '../ui/Card';

const TIMELINES = ['3 months', '6 months', '12 months', '2 years'] as const;
const WEEKLY_HOURS = ['5–10', '10–20', '20–30', '30+'] as const;

export default function GoalsStep({
  dreamRole,
  timeline,
  weeklyHours,
  context,
  onChange,
}: {
  dreamRole: string;
  timeline: string;
  weeklyHours: string;
  context: string;
  onChange: (next: { dreamRole: string; timeline: string; weeklyHours: string; context: string }) => void;
}) {
  return (
    <Card title="Goals">
      <div className="grid grid-cols-2 gap-6 max-[660px]:grid-cols-1">
        <div className="col-span-2">
          <div className="text-muted font-mono text-[10px] uppercase tracking-widest mb-2">Dream Role</div>
          <input
            className="acad-input"
            value={dreamRole}
            onChange={(e) => onChange({ dreamRole: e.target.value, timeline, weeklyHours, context })}
            placeholder="e.g. ML Engineer"
          />
        </div>

        <div>
          <div className="text-muted font-mono text-[10px] uppercase tracking-widest mb-2">Timeline</div>
          <select className="acad-select" value={timeline} onChange={(e) => onChange({ dreamRole, timeline: e.target.value, weeklyHours, context })}>
            {TIMELINES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </div>

        <div>
          <div className="text-muted font-mono text-[10px] uppercase tracking-widest mb-2">Weekly Hours Free</div>
          <select
            className="acad-select"
            value={weeklyHours}
            onChange={(e) => onChange({ dreamRole, timeline, weeklyHours: e.target.value, context })}
          >
            {WEEKLY_HOURS.map((h) => (
              <option key={h} value={h}>
                {h}
              </option>
            ))}
          </select>
        </div>

        <div className="col-span-2">
          <div className="text-muted font-mono text-[10px] uppercase tracking-widest mb-2">Context / Challenges</div>
          <textarea
            className="acad-textarea"
            value={context}
            onChange={(e) => onChange({ dreamRole, timeline, weeklyHours, context: e.target.value })}
            placeholder="Anything that affects your plan: syllabus pressure, limited time, gaps, etc."
          />
        </div>
      </div>
    </Card>
  );
}

