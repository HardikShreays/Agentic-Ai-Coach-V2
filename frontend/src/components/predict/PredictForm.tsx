import React, { useMemo, useState } from 'react';

import Button from '../ui/Button';
import Card from '../ui/Card';
import RangeSlider from '../ui/RangeSlider';

type PredictPayload = {
  hoursStudied: number;
  attendance: number;
  previousScores: number;
  sleepHours: number;
  tutoringSessions: number;
  parentalInvolvement: number;
  accessToResources: number;
  motivationLevel: number;
  internetAccess: number;
};

export default function PredictForm({
  loading,
  onRun,
}: {
  loading: boolean;
  onRun: (p: PredictPayload) => void | Promise<void>;
}) {
  const [hoursStudied, setHoursStudied] = useState(20);
  const [attendance, setAttendance] = useState(80);
  const [previousScores, setPreviousScores] = useState(72);
  const [sleepHours, setSleepHours] = useState(7);
  const [tutoringSessions, setTutoringSessions] = useState(2);

  const [parentalInvolvement, setParentalInvolvement] = useState(2);
  const [accessToResources, setAccessToResources] = useState(2);
  const [motivationLevel, setMotivationLevel] = useState(2);
  const [internetAccess, setInternetAccess] = useState(1);

  const payload: PredictPayload = useMemo(
    () => ({
      hoursStudied,
      attendance,
      previousScores,
      sleepHours,
      tutoringSessions,
      parentalInvolvement,
      accessToResources,
      motivationLevel,
      internetAccess,
    }),
    [
      hoursStudied,
      attendance,
      previousScores,
      sleepHours,
      tutoringSessions,
      parentalInvolvement,
      accessToResources,
      motivationLevel,
      internetAccess,
    ],
  );

  return (
    <div className="flex flex-col gap-4">
      <Card title="Academic Factors">
        <div className="flex flex-col gap-4">
          <RangeSlider
            id="hours_studied"
            label="Hours Studied / Week"
            min={0}
            max={44}
            step={1}
            value={hoursStudied}
            onChange={setHoursStudied}
            suffix="h"
          />
          <RangeSlider
            id="attendance"
            label="Attendance (%)"
            min={60}
            max={100}
            step={1}
            value={attendance}
            onChange={setAttendance}
            suffix="%"
          />
          <RangeSlider
            id="previous_scores"
            label="Previous Score"
            min={50}
            max={100}
            step={1}
            value={previousScores}
            onChange={setPreviousScores}
          />
          <RangeSlider
            id="sleep_hours"
            label="Sleep Hours / Night"
            min={4}
            max={10}
            step={0.5}
            value={sleepHours}
            onChange={setSleepHours}
            suffix="h"
          />
          <RangeSlider
            id="tutoring_sessions"
            label="Tutoring Sessions / Month"
            min={0}
            max={8}
            step={1}
            value={tutoringSessions}
            onChange={setTutoringSessions}
          />
        </div>
      </Card>

      <Card title="Environment">
        <div className="flex flex-col gap-4">
          <div>
            <div className="text-muted font-mono text-[10px] uppercase tracking-widest mb-2">
              Parental Involvement
            </div>
            <select
              className="acad-select"
              value={parentalInvolvement}
              onChange={(e) => setParentalInvolvement(Number(e.target.value))}
            >
              <option value={1}>Low (1)</option>
              <option value={2}>Medium (2)</option>
              <option value={3}>High (3)</option>
            </select>
          </div>

          <div>
            <div className="text-muted font-mono text-[10px] uppercase tracking-widest mb-2">
              Access to Resources
            </div>
            <select
              className="acad-select"
              value={accessToResources}
              onChange={(e) => setAccessToResources(Number(e.target.value))}
            >
              <option value={1}>Low (1)</option>
              <option value={2}>Medium (2)</option>
              <option value={3}>High (3)</option>
            </select>
          </div>

          <div>
            <div className="text-muted font-mono text-[10px] uppercase tracking-widest mb-2">
              Motivation Level
            </div>
            <select
              className="acad-select"
              value={motivationLevel}
              onChange={(e) => setMotivationLevel(Number(e.target.value))}
            >
              <option value={1}>Low (1)</option>
              <option value={2}>Medium (2)</option>
              <option value={3}>High (3)</option>
            </select>
          </div>

          <div>
            <div className="text-muted font-mono text-[10px] uppercase tracking-widest mb-2">
              Internet Access
            </div>
            <select
              className="acad-select"
              value={internetAccess}
              onChange={(e) => setInternetAccess(Number(e.target.value))}
            >
              <option value={1}>Yes (1)</option>
              <option value={0}>No (0)</option>
            </select>
          </div>
        </div>
      </Card>

      <Button variant="primary" disabled={loading} onClick={() => onRun(payload)} className="w-full mt-1">
        ⚙ Run Prediction
      </Button>
    </div>
  );
}

