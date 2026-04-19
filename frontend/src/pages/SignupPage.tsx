import React, { useEffect, useState } from 'react';
import { useNavigate, Link, useSearchParams } from 'react-router-dom';

import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { useAuthStore } from '../store/useAuthStore';
import { safeRedirectPath } from '../utils/redirect';

export default function SignupPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const user = useAuthStore((s) => s.user);
  const authBusy = useAuthStore((s) => s.isLoading);
  const signup = useAuthStore((s) => s.signup);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);

  const afterAuthPath = safeRedirectPath(searchParams.get('redirect'));

  useEffect(() => {
    if (!authBusy && user) {
      navigate(afterAuthPath, { replace: true });
    }
  }, [authBusy, user, afterAuthPath, navigate]);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      await signup(email.trim(), password);
      navigate(afterAuthPath, { replace: true });
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Signup failed');
    }
  };

  return (
    <div className="max-w-xl mx-auto">
      <div className="mb-6">
        <div className="font-syne font-bold text-[22px] text-text" style={{ color: '#ede9f8' }}>
          Create your account
        </div>
        <div className="text-muted text-[13px] mt-2">Get personalized coach context that follows you.</div>
      </div>

      <Card title="Signup">
        <form onSubmit={onSubmit} className="flex flex-col gap-4">
          <div>
            <div className="text-muted font-mono text-[10px] uppercase tracking-widest mb-2">Email</div>
            <input
              className="acad-input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              type="email"
              autoComplete="email"
              required
            />
          </div>

          <div>
            <div className="text-muted font-mono text-[10px] uppercase tracking-widest mb-2">Password</div>
            <input
              className="acad-input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="At least 8 characters"
              type="password"
              autoComplete="new-password"
              required
            />
          </div>

          {error ? <div className="text-pink font-mono text-[12px]">{error}</div> : null}

          <Button variant="primary" disabled={authBusy} type="submit" className="w-full">
            {authBusy ? 'Creating...' : 'Create Account'}
          </Button>

          <div className="text-muted text-[13px] text-center mt-2">
            Already have an account?{' '}
            <Link to={`/login?redirect=${encodeURIComponent(afterAuthPath)}`} style={{ color: '#f0177a', textDecoration: 'none' }}>
              Sign in
            </Link>
          </div>
        </form>
      </Card>
    </div>
  );
}

