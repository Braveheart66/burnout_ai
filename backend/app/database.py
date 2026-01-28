import os
import psycopg2
import pandas as pd
import hashlib
from datetime import datetime

class BurnoutDatabase:
    def __init__(self):
        self.conn_url = os.getenv("DATABASE_URL")
        if not self.conn_url:
            raise RuntimeError("DATABASE_URL not set")

    def get_connection(self):
        return psycopg2.connect(self.conn_url)

    def setup_database(self):
        conn = self.get_connection()
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS individual_checkouts (
            id SERIAL PRIMARY KEY,
            user_id_hash TEXT NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            date DATE NOT NULL,
            department TEXT,
            study_hours REAL,
            sleep_hours REAL,
            screen_time_hours REAL,
            engagement_level REAL,
            assignment_deadline_missed INTEGER,
            assignments_pending INTEGER,
            upcoming_deadline_load INTEGER,
            self_reported_stress INTEGER,
            sentiment_score REAL,
            burnout_score INTEGER,
            risk_label TEXT,
            reflection_text TEXT,
            UNIQUE(user_id_hash, date)
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS department_aggregates (
            id SERIAL PRIMARY KEY,
            date DATE NOT NULL,
            department TEXT NOT NULL,
            avg_stress REAL,
            avg_sleep REAL,
            avg_workload REAL,
            avg_screen_time REAL,
            avg_sentiment REAL,
            risk_low_count INTEGER,
            risk_medium_count INTEGER,
            risk_high_count INTEGER,
            total_checkouts INTEGER,
            participation_rate REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(date, department)
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS organization_aggregates (
            id SERIAL PRIMARY KEY,
            date DATE NOT NULL,
            avg_stress REAL,
            avg_sleep REAL,
            avg_workload REAL,
            risk_low_pct REAL,
            risk_medium_pct REAL,
            risk_high_pct REAL,
            total_checkouts INTEGER,
            participation_rate REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(date)
        );
        """)

        conn.commit()
        conn.close()

    def hash_user(self, email: str) -> str:
        return hashlib.sha256(email.encode()).hexdigest()

    def save_checkout(self, email, dept, data, score, label, reflection=""):
        conn = self.get_connection()
        cur = conn.cursor()

        cur.execute("""
        INSERT INTO individual_checkouts (
            user_id_hash, timestamp, date, department,
            study_hours, sleep_hours, screen_time_hours,
            engagement_level, assignment_deadline_missed,
            assignments_pending, upcoming_deadline_load,
            self_reported_stress, sentiment_score,
            burnout_score, risk_label, reflection_text
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (user_id_hash, date) DO UPDATE SET
            burnout_score = EXCLUDED.burnout_score,
            risk_label = EXCLUDED.risk_label;
        """, (
            self.hash_user(email),
            datetime.now(),
            datetime.now().date(),
            dept,
            data["study_hours"],
            data["sleep_hours"],
            data["screen_time_hours"],
            data["engagement_level"],
            data["assignment_deadline_missed"],
            data["assignments_pending"],
            data["upcoming_deadline_load"],
            data["self_reported_stress"],
            data["sentiment_score"],
            score,
            label,
            reflection
        ))

        conn.commit()
        conn.close()

    def department_aggregates(self, start, end):
        conn = self.get_connection()
        df = pd.read_sql("""
        SELECT * FROM department_aggregates
        WHERE date BETWEEN %s AND %s
        """, conn, params=(start, end))
        conn.close()
        return df

    def org_aggregates(self, start, end):
        conn = self.get_connection()
        df = pd.read_sql("""
        SELECT * FROM organization_aggregates
        WHERE date BETWEEN %s AND %s
        """, conn, params=(start, end))
        conn.close()
        return df
