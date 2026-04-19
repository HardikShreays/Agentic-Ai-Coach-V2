import React from 'react';

export default function Card({
  title,
  children,
  className = '',
}: {
  title?: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <section className={`acad-card ${className}`.trim()}>
      {title ? <div className="acad-card-title">{title}</div> : null}
      {children}
    </section>
  );
}

