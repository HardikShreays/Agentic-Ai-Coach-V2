import React from 'react';

import Card from '../ui/Card';
import TagSelector from '../ui/TagSelector';

const STAGES = [
  'High School',
  '1st Year',
  '2nd Year',
  '3rd Year',
  'Final Year',
  'Career Switcher',
] as const;

const FIELDS = [
  'CS/IT',
  'ECE',
  'Mechanical',
  'Commerce/MBA',
  'Data Science/AI',
  'Science (PCB)',
  'Arts/Humanities',
] as const;

const SKILLS = [
  'Python',
  'Java',
  'JavaScript',
  'C/C++',
  'ML/AI',
  'Data Analysis',
  'SQL',
  'React',
  'DSA',
  'Excel',
  'Communication',
  'Leadership',
  'Git',
  'Cloud',
] as const;

export default function ProfileStep({
  name,
  stage,
  field,
  academicScore,
  selectedSkills,
  onChange,
}: {
  name: string;
  stage: string;
  field: string;
  academicScore: string;
  selectedSkills: string[];
  onChange: (next: {
    name: string;
    stage: string;
    field: string;
    academicScore: string;
    selectedSkills: string[];
  }) => void;
}) {
  const toggleSkill = (skill: string) => {
    const exists = selectedSkills.includes(skill);
    const next = exists ? selectedSkills.filter((s) => s !== skill) : [...selectedSkills, skill];
    onChange({ name, stage, field, academicScore, selectedSkills: next });
  };

  return (
    <div className="grid grid-cols-2 gap-6 max-[660px]:grid-cols-1">
      <Card title="Academic Profile">
        <div className="flex flex-col gap-4">
          <div>
            <div className="text-muted font-mono text-[10px] uppercase tracking-widest mb-2">Name</div>
            <input
              className="acad-input"
              value={name}
              onChange={(e) => onChange({ name: e.target.value, stage, field, academicScore, selectedSkills })}
              placeholder="Your name"
            />
          </div>

          <div>
            <div className="text-muted font-mono text-[10px] uppercase tracking-widest mb-2">Current Stage</div>
            <select
              className="acad-select"
              value={stage}
              onChange={(e) => onChange({ name, stage: e.target.value, field, academicScore, selectedSkills })}
            >
              <option value="">Select stage</option>
              {STAGES.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </div>

          <div>
            <div className="text-muted font-mono text-[10px] uppercase tracking-widest mb-2">Field</div>
            <select
              className="acad-select"
              value={field}
              onChange={(e) => onChange({ name, stage, field: e.target.value, academicScore, selectedSkills })}
            >
              <option value="">Select field</option>
              {FIELDS.map((f) => (
                <option key={f} value={f}>
                  {f}
                </option>
              ))}
            </select>
          </div>

          <div>
            <div className="text-muted font-mono text-[10px] uppercase tracking-widest mb-2">Academic Score</div>
            <input
              className="acad-input"
              value={academicScore}
              onChange={(e) => onChange({ name, stage, field, academicScore: e.target.value, selectedSkills })}
              placeholder="e.g. 7.8 CGPA or 76%"
            />
          </div>
        </div>
      </Card>

      <Card title="Current Skills">
        <div>
          <div className="flex flex-wrap gap-2">
            {SKILLS.map((skill) => (
              <TagSelector key={skill} tag={skill} selected={selectedSkills.includes(skill)} onToggle={() => toggleSkill(skill)} />
            ))}
          </div>
        </div>
      </Card>
    </div>
  );
}

