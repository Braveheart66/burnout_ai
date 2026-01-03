import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)

# CONFIGURATION
NUM_USERS = 50
NUM_DAYS = 60
START_DATE = datetime(2025, 9, 1)

rows = []

for user in range(1, NUM_USERS + 1):
    base_stress = np.random.randint(2, 5)

    for day in range(NUM_DAYS):
        date = START_DATE + timedelta(days=day)

        # Stress evolves slowly (time-series behavior)
        stress = np.clip(
            base_stress + np.random.choice([-1, 0, 1], p=[0.2, 0.6, 0.2]),
            1, 10
        )
        base_stress = stress

        # Burnout logic
        if stress <= 3:
            label = "Low"
            sentiment = np.random.uniform(0.4, 0.8)
        elif stress <= 6:
            label = "Medium"
            sentiment = np.random.uniform(-0.1, 0.3)
        else:
            label = "High"
            sentiment = np.random.uniform(-0.8, -0.2)

        study_hours = np.clip(np.random.normal(6 - stress * 0.3, 1.2), 0, 12)
        sleep_hours = np.clip(np.random.normal(7.5 - stress * 0.35, 1), 3, 9)
        screen_time = np.clip(np.random.normal(7 + stress * 0.4, 2), 1, 14)
        attendance = np.clip(np.random.normal(0.9 - stress * 0.05, 0.08), 0, 1)

        rows.append({
            "user_id": f"U_{user:03}",
            "date": date.strftime("%Y-%m-%d"),
            "study_hours": round(study_hours, 1),
            "screen_time_hours": round(screen_time, 1),
            "sleep_hours": round(sleep_hours, 1),
            "class_attendance_rate": round(attendance, 2),
            "assignment_deadline_missed": int(stress > 6),
            "assignments_pending": np.random.randint(0, 5),
            "upcoming_deadline_load": np.random.randint(0, 5),
            "self_reported_stress": stress,
            "sentiment_score": round(sentiment, 2),
            "burnout_risk_label": label
        })

df = pd.DataFrame(rows)
df.to_csv("student_burnout_synthetic.csv", index=False)

print(f"Dataset generated successfully with {len(df)} rows.")
