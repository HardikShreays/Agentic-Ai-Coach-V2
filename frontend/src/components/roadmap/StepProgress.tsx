import React from 'react';

function Step({
  index,
  label,
  state,
}: {
  index: number;
  label: string;
  state: 'inactive' | 'active' | 'done';
}) {
  const isDone = state === 'done';
  const isActive = state === 'active';

  const circleStyle: React.CSSProperties = isActive
    ? {
        background: 'rgba(240,23,122,1)',
        boxShadow: '0 0 22px rgba(240,23,122,0.45)',
        borderColor: 'rgba(240,23,122,0.9)',
        color: '#fff',
      }
    : isDone
      ? {
          background: 'rgba(240,23,122,0.12)',
          borderColor: 'rgba(240,23,122,0.4)',
          color: '#f0177a',
        }
      : {
          background: 'transparent',
          borderColor: 'rgba(139,92,246,0.2)',
          color: 'rgba(139,92,246,0.9)',
        };

  return (
    <div className="flex flex-col items-center gap-3">
      <div
        className="w-[26px] h-[26px] rounded-full border flex items-center justify-center font-mono text-[12px] font-bold"
        style={{ borderWidth: 1, ...circleStyle }}
      >
        {index + 1}
      </div>
      <div
        className="text-center"
        style={{
          color: isActive ? '#f0177a' : isDone ? '#f0177a' : 'rgba(139,92,246,0.9)',
          fontFamily: "'Space Mono', monospace",
          fontSize: 11,
          letterSpacing: '0.08em',
          textTransform: 'uppercase',
        }}
      >
        {label}
      </div>
    </div>
  );
}

export default function StepProgress({ currentStep }: { currentStep: number }) {
  const steps = [
    { label: 'Profile' },
    { label: 'Goals' },
    { label: 'Result' },
  ];

  return (
    <div className="relative mb-6">
      <div className="flex items-center justify-between">
        {steps.map((s, i) => {
          const state = i < currentStep ? 'done' : i === currentStep ? 'active' : 'inactive';
          return <Step key={s.label} index={i} label={s.label} state={state} />;
        })}
      </div>
      <div
        aria-hidden
        className="absolute left-[50px] right-[50px] top-1/2 -translate-y-1/2"
        style={{
          height: 1,
          background: 'rgba(139,92,246,0.2)',
          zIndex: -1,
        }}
      />
    </div>
  );
}

