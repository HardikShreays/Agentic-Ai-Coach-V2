import React from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';

import { useAuthStore } from '../../store/useAuthStore';

type Tab = {
  to: string;
  label: string;
  withNewBadge?: boolean;
};

const tabs: Tab[] = [
  { to: '/predict', label: 'PREDICT' },
  { to: '/roadmap', label: 'ROADMAP' },
  { to: '/coach', label: 'AI COACH', withNewBadge: true },
];

function TabItem({ to, label, withNewBadge }: Tab) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        [
          'flex items-center gap-2',
          'font-mono uppercase',
          'text-[11px] tracking-widest',
          'rounded-full',
          'px-4 py-2',
          'transition-shadow',
          isActive ? 'bg-pink text-white shadow-[0_0_22px_rgba(240,23,122,0.45)]' : 'text-muted',
        ].join(' ')
      }
    >
      {label}
      {withNewBadge ? (
        <span
          className="ml-1 inline-flex items-center justify-center rounded-full px-2 py-0.5 text-[9px] font-mono"
          style={{
            background: 'rgba(6,214,199,0.12)',
            border: '1px solid rgba(6,214,199,0.35)',
            color: '#06d6c7',
          }}
        >
          NEW
        </span>
      ) : null}
    </NavLink>
  );
}

export default function Navbar() {
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const authBusy = useAuthStore((s) => s.isLoading);
  const navigate = useNavigate();

  const onLogout = async () => {
    await logout();
    navigate('/', { replace: true });
  };

  return (
    <header
      className="sticky top-0 z-[50]"
      style={{
        backdropFilter: 'blur(20px)',
        background: 'rgba(14,8,24,0.65)',
      }}
    >
      <div className="max-w-6xl mx-auto px-4 py-3">
        <div className="flex items-center justify-between gap-4 flex-wrap">
          <Link to="/" className="flex items-center gap-3 no-underline text-inherit">
            <div className="font-mono uppercase tracking-[0.18em] text-[12px] text-text">ACADPIPELINE</div>
            <div
              className="rounded-full"
              style={{
                width: 8,
                height: 8,
                background: '#f0177a',
                boxShadow: '0 0 12px rgba(240,23,122,0.9)',
                animation: 'bounce 1.4s ease-in-out infinite',
              }}
            />
          </Link>

          {user ? (
            <div className="flex items-center gap-2 flex-wrap justify-end">
              <nav
                className="flex items-center gap-1 rounded-full border border-border2"
                style={{
                  background: 'rgba(255,255,255,0.04)',
                  borderColor: 'rgba(139,92,246,0.2)',
                  padding: 4,
                }}
              >
                {tabs.map((t) => (
                  <TabItem key={t.to} {...t} />
                ))}
              </nav>
              <button
                type="button"
                onClick={onLogout}
                disabled={authBusy}
                className="acad-btn acad-btn-ghost text-[10px] !py-2 !px-3 disabled:opacity-40"
              >
                Log out
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link
                to="/login"
                className="acad-btn acad-btn-ghost text-[10px] !py-2 !px-4 no-underline inline-flex items-center"
              >
                Sign in
              </Link>
              <Link
                to="/signup"
                className="acad-btn acad-btn-primary text-[10px] !py-2 !px-4 no-underline inline-flex items-center"
              >
                Sign up
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
