import React, { useState } from 'react';
import { Sparkles } from 'lucide-react';

import { useSessionStore } from '../store/useSessionStore';
import { predictScore } from '../api/client';

import Card from '../components/ui/Card';
import PredictForm from '../components/predict/PredictForm';
import ScoreRing from '../components/predict/ScoreRing';
import FactorBars from '../components/predict/FactorBars';
import RiskBadges from '../components/predict/RiskBadges';
import ClusterPill from '../components/predict/ClusterPill';
import type { PredictRequest } from '../types';

export default function PredictPage() {
  const predictResult = useSessionStore((s) => s.predictResult);
  const setPredictResult = useSessionStore((s) => s.setPredictResult);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onRun = async (payload: PredictRequest) => {
    setLoading(true);
    setError(null);
    try {
      const res = await predictScore(payload);
      setPredictResult(res);
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Prediction failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-2 gap-6 max-[660px]:grid-cols-1">
      <div className="flex flex-col gap-4">
        <PredictForm loading={loading} onRun={onRun} />
        {error ? (
          <div className="text-pink font-mono text-[12px] mt-2">{error}</div>
        ) : null}
      </div>

      <div className="flex flex-col gap-6">
        {!predictResult ? (
          <div className="acad-card flex flex-col items-center justify-center min-h-[380px] gap-3">
            <div
              className="rounded-full border border-border2"
              style={{
                width: 60,
                height: 60,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 0 30px rgba(240,23,122,0.25)',
              }}
            >
              <Sparkles size={26} color="#f0177a" />
            </div>
            <div className="text-text font-syne font-bold" style={{ fontSize: 18 }}>
              Run prediction to see your score
            </div>
            <div className="text-muted font-sans text-[13px] text-center">
              Accurate, data-driven guidance based on your study and environment factors.
            </div>
          </div>
        ) : (
          <>
            <Card title="Score Ring">
              <ScoreRing
                score={predictResult.score}
                grade={predictResult.grade}
                gradeLabel={predictResult.gradeLabel}
              />
            </Card>
            <Card title="Factor Impact">
              <FactorBars factors={predictResult.factors} />
            </Card>
            <Card title="Risk Profile">
              <RiskBadges risks={predictResult.risks} />
            </Card>
            <Card title="Peer Cluster">
              <ClusterPill
                cluster={predictResult.cluster}
                label={predictResult.clusterLabel}
                description={predictResult.clusterDescription}
              />
            </Card>
          </>
        )}
      </div>
    </div>
  );
}

