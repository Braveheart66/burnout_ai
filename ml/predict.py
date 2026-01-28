import joblib, pandas as pd
from pathlib import Path
from ml.utils import engagement_score, cognitive_load

BASE = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE / "backend" / "models"

model = joblib.load(MODEL_DIR / "burnout_model.pkl")
scaler = joblib.load(MODEL_DIR / "scaler.pkl")
encoder = joblib.load(MODEL_DIR / "label_encoder.pkl")

def predict_burnout(data):
    df = pd.DataFrame([data])
    df["engagement_score"] = engagement_score(
        df.study_hours[0],
        df.engagement_level[0],
        df.assignment_deadline_missed[0]
    )
    df["cognitive_load_score"] = cognitive_load(
        df.assignments_pending[0],
        df.upcoming_deadline_load[0]
    )

    X = scaler.transform(df[[
        "study_hours","screen_time_hours","sleep_hours",
        "self_reported_stress","sentiment_score",
        "engagement_score","cognitive_load_score"
    ]])

    proba = model.predict_proba(X)[0]
    idx = proba.argmax()
    label = encoder.inverse_transform([idx])[0]
    score = int(proba[idx] * 100)
    return score, label
