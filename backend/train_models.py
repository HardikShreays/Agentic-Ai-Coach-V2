from __future__ import annotations

import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression


DATA_PATH = Path(__file__).resolve().parent / "data" / "StudentPerformanceFactors.csv"
MODELS_DIR = Path(__file__).resolve().parent / "models" / "ml_models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

LINEAR_MODEL_PATH = MODELS_DIR / "linear_regression.pkl"
KMEANS_MODEL_PATH = MODELS_DIR / "kmeans.pkl"


def _ordinal_map(val) -> float:
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return 2.0
    s = str(val).strip().lower()
    if "low" in s:
        return 1.0
    if "med" in s:
        return 2.0
    if "high" in s:
        return 3.0
    # If already numeric (1/2/3) or unknown, try cast
    try:
        x = float(val)
        return float(x)
    except Exception:
        return 2.0


def _binary_map_yes_no(val) -> float:
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return 0.0
    s = str(val).strip().lower()
    if s in {"1", "true", "yes", "y"} or "yes" in s:
        return 1.0
    return 0.0


def _engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    # Must match ml_engine._compute_engineered_features exactly (order matters for X)
    study_effort = df["Hours_Studied"] * (df["Attendance"] / 100.0)
    attendance_score = df["Attendance"] / 100.0
    support_system = (df["Parental_Involvement"] + df["Access_to_Resources"] + df["Motivation_Level"]) / 3.0
    optimal_sleep = ((df["Sleep_Hours"] >= 6) & (df["Sleep_Hours"] <= 9)).astype(float)
    high_intensity = (df["Hours_Studied"] > 30).astype(float)
    risk_factor = (
        (df["Attendance"] < 75).astype(int)
        + (df["Hours_Studied"] < 10).astype(int)
        + (df["Motivation_Level"] == 1).astype(int)
    ).astype(float)

    return pd.DataFrame(
        {
            "study_effort": study_effort.astype(float),
            "attendance_score": attendance_score.astype(float),
            "support_system": support_system.astype(float),
            "optimal_sleep": optimal_sleep.astype(float),
            "high_intensity": high_intensity.astype(float),
            "risk_factor": risk_factor.astype(float),
        }
    )


def _fallback_synthetic_dataset(n_rows: int = 6607, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    hours_studied = rng.uniform(0, 44, size=n_rows)
    attendance = rng.uniform(60, 100, size=n_rows)
    previous_scores = rng.uniform(50, 100, size=n_rows)
    sleep_hours = rng.uniform(4, 10, size=n_rows)
    tutoring_sessions = rng.uniform(0, 8, size=n_rows)

    parental_involvement = rng.integers(1, 4, size=n_rows)
    access_to_resources = rng.integers(1, 4, size=n_rows)
    motivation_level = rng.integers(1, 4, size=n_rows)
    internet_access = rng.integers(0, 2, size=n_rows)

    df = pd.DataFrame(
        {
            "Hours_Studied": hours_studied,
            "Attendance": attendance,
            "Previous_Scores": previous_scores,
            "Sleep_Hours": sleep_hours,
            "Tutoring_Sessions": tutoring_sessions,
            "Parental_Involvement": parental_involvement,
            "Access_to_Resources": access_to_resources,
            "Motivation_Level": motivation_level,
            "Internet_Access": internet_access,
        }
    )

    # Use your fallback formula to generate target (with small noise).
    feats = _engineer_features(df)
    study_effort = feats["study_effort"]
    attendance_score = feats["attendance_score"]
    support_system = feats["support_system"]
    optimal_sleep = feats["optimal_sleep"].round().astype(int)
    risk_factor = feats["risk_factor"].round().astype(int)

    score = (
        40
        + (study_effort * 0.38)
        + (df["Previous_Scores"] * 0.35)
        + (attendance_score * 8)
        + (support_system * 3.2)
        + (optimal_sleep * 2.1)
        + (df["Tutoring_Sessions"] * 0.9)
        + (df["Internet_Access"] * 1.4)
        - (risk_factor * 3.5)
    )
    score = np.clip(score, 40, 100)
    noise = rng.normal(0, 2.0, size=n_rows)
    df["Exam_Score"] = np.clip(score + noise, 0, 100)
    return df


def load_or_create_dataset() -> pd.DataFrame:
    if DATA_PATH.exists():
        df = pd.read_csv(DATA_PATH)
        # Basic sanity check: if dataset is empty or missing target, use synthetic fallback.
        if df.empty or "Exam_Score" not in df.columns:
            return _fallback_synthetic_dataset()

        # Normalize column names (case-insensitive) to expected schema.
        cols = {c.lower().strip(): c for c in df.columns}

        def pick(*names: str) -> str:
            for n in names:
                key = n.lower().strip()
                if key in cols:
                    return cols[key]
            raise KeyError(f"Missing required column: {names[0]}")

        df_norm = pd.DataFrame(
            {
                "Hours_Studied": df[pick("Hours_Studied", "Hours Studied", "HoursStudied")],
                "Attendance": df[pick("Attendance")],
                "Previous_Scores": df[pick("Previous_Scores", "Previous Scores", "PreviousScores")],
                "Sleep_Hours": df[pick("Sleep_Hours", "Sleep Hours", "SleepHours")],
                "Tutoring_Sessions": df[pick("Tutoring_Sessions", "Tutoring Sessions", "TutoringSessions")],
                "Parental_Involvement": df[pick("Parental_Involvement", "Parental Involvement", "ParentalInvolvement")],
                "Access_to_Resources": df[pick("Access_to_Resources", "Access to Resources", "AccessResources")],
                "Motivation_Level": df[pick("Motivation_Level", "Motivation Level", "MotivationLevel")],
                "Internet_Access": df[pick("Internet_Access", "Internet Access", "InternetAccess")],
                "Exam_Score": df[pick("Exam_Score", "Exam Score", "ExamScore")],
            }
        )

        # Encode categorical features (ordinal/binary) exactly as mapping expects.
        df_norm["Parental_Involvement"] = df_norm["Parental_Involvement"].apply(_ordinal_map)
        df_norm["Access_to_Resources"] = df_norm["Access_to_Resources"].apply(_ordinal_map)
        df_norm["Motivation_Level"] = df_norm["Motivation_Level"].apply(_ordinal_map)
        df_norm["Internet_Access"] = df_norm["Internet_Access"].apply(_binary_map_yes_no)

        return df_norm

    return _fallback_synthetic_dataset()


def main() -> None:
    df = load_or_create_dataset()

    X = _engineer_features(df).astype(float).values
    y = df["Exam_Score"].astype(float).values

    # Train Linear Regression on engineered features
    lr = LinearRegression()
    lr.fit(X, y)

    # Train KMeans on feature matrix
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    kmeans.fit(X)

    # Sort cluster indices by mean Exam_Score
    clusters = kmeans.labels_
    means = {c: float(np.mean(y[clusters == c])) for c in sorted(set(clusters))}
    sorted_old = sorted(means.keys(), key=lambda c: means[c])  # low -> high

    # Map to desired output order: 0=struggling, 1=average, 2=high-performer
    cluster_mapping = {int(sorted_old[0]): 0, int(sorted_old[1]): 1, int(sorted_old[2]): 2}

    with open(LINEAR_MODEL_PATH, "wb") as f:
        pickle.dump(lr, f)

    with open(KMEANS_MODEL_PATH, "wb") as f:
        pickle.dump({"model": kmeans, "cluster_mapping": cluster_mapping}, f)

    print(f"Saved models to: {MODELS_DIR}")


if __name__ == "__main__":
    main()

