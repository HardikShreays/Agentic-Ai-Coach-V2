import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';

import { useAuthStore } from '../../store/useAuthStore';

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const user = useAuthStore((s) => s.user);
  const isLoading = useAuthStore((s) => s.isLoading);
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="acad-card min-h-[420px] flex items-center justify-center">
        <div className="text-muted font-mono text-[12px] uppercase tracking-widest">Loading account...</div>
      </div>
    );
  }

  if (!user) {
    const redirect = encodeURIComponent(`${location.pathname}${location.search}`);
    return <Navigate to={`/login?redirect=${redirect}`} replace />;
  }

  return <>{children}</>;
}
