import React from 'react';

export default function RangeSlider({
  label,
  value,
  onChange,
  min,
  max,
  step = 1,
  suffix,
  id,
}: {
  id: string;
  label: string;
  value: number;
  onChange: (v: number) => void;
  min: number;
  max: number;
  step?: number;
  suffix?: string;
}) {
  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <div className="text-muted font-mono text-[10px] uppercase tracking-widest">
          {label}
        </div>
        <div className="font-mono text-[14px] text-pink">
          {value}
          {suffix ?? ''}
        </div>
      </div>
      <input
        id={id}
        className="range-slider"
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
      />
    </div>
  );
}

