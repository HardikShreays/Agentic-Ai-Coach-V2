import React from 'react';
import { Route, Routes, useLocation } from 'react-router-dom';
import { useEffect } from 'react';

import Navbar from './components/layout/Navbar';
import AmbientOrbs from './components/layout/AmbientOrbs';
import ProtectedRoute from './components/auth/ProtectedRoute';
import PredictPage from './pages/PredictPage';
import RoadmapPage from './pages/RoadmapPage';
import CoachPage from './pages/CoachPage';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import { useAuthStore } from './store/useAuthStore';

function NoiseOverlay() {
  return (
    <svg
      className="pointer-events-none fixed inset-0 w-full h-full"
      style={{ opacity: 0.28, zIndex: 9999 }}
      viewBox="0 0 500 500"
      preserveAspectRatio="none"
    >
      <filter id="noiseFilter">
        <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="4" stitchTiles="stitch" />
      </filter>
      <rect width="500" height="500" filter="url(#noiseFilter)" opacity="1" />
    </svg>
  );
}

export default function App() {
  const location = useLocation();
  const refreshMe = useAuthStore((s) => s.refreshMe);

  useEffect(() => {
    refreshMe();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="min-h-full">
      <NoiseOverlay />
      <AmbientOrbs />
      <Navbar />

      <main className="relative z-10 max-w-6xl mx-auto px-4 pb-16 pt-6">
        <div key={location.pathname} className="animate-fadeUp">
          <Routes location={location}>
            <Route path="/" element={<LandingPage />} />
            <Route
              path="/predict"
              element={
                <ProtectedRoute>
                  <PredictPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/roadmap"
              element={
                <ProtectedRoute>
                  <RoadmapPage />
                </ProtectedRoute>
              }
            />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={<SignupPage />} />
            <Route
              path="/coach"
              element={
                <ProtectedRoute>
                  <CoachPage />
                </ProtectedRoute>
              }
            />
          </Routes>
        </div>
      </main>
    </div>
  );
}

