import React from 'react';

export default function Button({
  variant,
  children,
  disabled,
  onClick,
  className = '',
  type = 'button',
}: {
  variant: 'primary' | 'ghost';
  children: React.ReactNode;
  disabled?: boolean;
  onClick?: () => void;
  className?: string;
  type?: 'button' | 'submit';
}) {
  const base = 'acad-btn';
  const v = variant === 'primary' ? 'acad-btn-primary' : 'acad-btn-ghost';
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${base} ${v} ${className}`.trim()}
    >
      {children}
    </button>
  );
}

