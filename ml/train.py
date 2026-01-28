import sys
import os
from pathlib import Path
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
sys.path.append(str(project_root))
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from src.utils import engagement_score, cognitive_load  

# Define paths
DATA_PATH = project_root / "data" / "student_burnout_synthetic.csv"
MODEL_DIR = project_root / "models"
MODEL_DIR.mkdir(exist_ok=True) # Create folder if it doesn't exist

# Load dataset
df = pd.read_csv(DATA_PATH)

# Load dataset
df = pd.read_csv("data/student_burnout_synthetic.csv")

# Feature engineering
df["engagement_score"] = df.apply(
    lambda x: engagement_score(
        x["study_hours"],
        x["class_attendance_rate"],
        x["assignment_deadline_missed"]
    ), axis=1
)

df["cognitive_load_score"] = df.apply(
    lambda x: cognitive_load(
        x["assignments_pending"],
        x["upcoming_deadline_load"]
    ), axis=1
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

X = df[features]
y = df["burnout_risk_label"]

# Encode labels
label_encoder = LabelEncoder()
y_enc = label_encoder.fit_transform(y)

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y_enc, test_size=0.2, stratify=y_enc, random_state=42
)

# Train model
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    random_state=42
)
model.fit(X_train, y_train)

# Evaluate
print(classification_report(y_test, model.predict(X_test)))

# Save artifacts
joblib.dump(model, MODEL_DIR / "burnout_model.pkl")
joblib.dump(scaler, MODEL_DIR / "scaler.pkl")
joblib.dump(label_encoder, MODEL_DIR / "label_encoder.pkl")

print("Model trained and saved successfully.")
