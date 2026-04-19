import React from 'react';

export default function TagSelector({
  tag,
  selected,
  onToggle,
}: {
  tag: string;
  selected: boolean;
  onToggle: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onToggle}
      className={[
        'inline-flex items-center rounded-full px-3 py-1',
        'font-mono text-[11px] uppercase tracking-widest',
        'border border-border2 text-muted',
        'transition-colors',
        selected ? 'bg-[rgba(240,23,122,0.12)] border-pink text-pink' : '',
      ].join(' ')}
    >
      {tag}
    </button>
  );
}

