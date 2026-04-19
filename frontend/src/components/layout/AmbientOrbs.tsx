import React from 'react';

export default function AmbientOrbs() {
  return (
    <>
      {/* Orb 1: pink, top-left offset */}
      <div
        className="orb-drift"
        style={{
          position: 'fixed',
          width: 500,
          height: 500,
          top: '-150px',
          left: '-150px',
          background: 'radial-gradient(circle at 30% 30%, rgba(240,23,122,1) 0%, rgba(255,255,255,0) 60%)',
          opacity: 0.15,
          filter: 'blur(30px)',
          pointerEvents: 'none',
          zIndex: 1,
          animationDuration: '12s',
        }}
      />

      {/* Orb 2: purple, bottom-right offset, reverse drift */}
      <div
        className="orb-drift"
        style={{
          position: 'fixed',
          width: 400,
          height: 400,
          right: '-100px',
          bottom: '-100px',
          background: 'radial-gradient(circle at 40% 40%, rgba(139,92,246,1) 0%, rgba(255,255,255,0) 60%)',
          opacity: 0.17,
          filter: 'blur(30px)',
          pointerEvents: 'none',
          zIndex: 1,
          animationDuration: '10s',
          animationDirection: 'reverse',
        }}
      />

      {/* Orb 3: cyan, centered, delayed drift */}
      <div
        className="orb-drift"
        style={{
          position: 'fixed',
          width: 250,
          height: 250,
          left: '50%',
          top: '50%',
          transform: 'translate(-50%, -50%)',
          background: 'radial-gradient(circle at 30% 30%, rgba(6,214,199,1) 0%, rgba(255,255,255,0) 60%)',
          opacity: 0.05,
          filter: 'blur(30px)',
          pointerEvents: 'none',
          zIndex: 1,
          animationDuration: '14s',
          animationDelay: '3000ms',
        }}
      />
    </>
  );
}

