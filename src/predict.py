import joblib
import pandas as pd
from pathlib import Path
from src.utils import engagement_score, cognitive_load

# Setup paths
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "models"

# Load artifacts
model = joblib.load(MODEL_DIR / "burnout_model.pkl")
scaler = joblib.load(MODEL_DIR / "scaler.pkl")
label_encoder = joblib.load(MODEL_DIR / "label_encoder.pkl")

def predict_burnout(input_data: dict):
    """
    Predict burnout risk.
    Output is workload sustainability risk, NOT diagnosis.
    """

    df = pd.DataFrame([input_data])

    # Clamp unsafe ranges
    df["assignments_pending"] = min(df["assignments_pending"][0], 5)
    df["upcoming_deadline_load"] = min(df["upcoming_deadline_load"][0], 5)

    df["engagement_score"] = engagement_score(
        df["study_hours"][0],
        df["engagement_level"][0],
        df["assignment_deadline_missed"][0]
    )

    df["cognitive_load_score"] = cognitive_load(
        df["assignments_pending"][0],
        df["upcoming_deadline_load"][0]
    )

    features = [
        "study_hours",
        "screen_time_hours",
        "sleep_hours",
        "self_reported_stress",
        "sentiment_score",
        "engagement_score",
        "cognitive_load_score"
    ]

    X = scaler.transform(df[features])
    proba = model.predict_proba(X)[0]

    # Get the index of the highest probability
    label_index = proba.argmax()
    label = label_encoder.inverse_transform([label_index])[0]
    
    # FIX: Get the probability specifically for the predicted class
    # This fixes the bug where "High" risk used "Medium" probability
    confidence = proba[label_index]

    # Calculate Score
    if label == "Low":
        # Low Risk: Score between 0-40
        score = int(confidence * 40)
    elif label == "Medium":
        # Medium Risk: Score between 40-70
        score = int(40 + confidence * 30)
    else:
        # High Risk: Score between 70-100
        # Previously proba[2] was wrong because 'High' is index 0
        score = int(70 + confidence * 30)

    score = max(0, min(100, score))
    return score, label