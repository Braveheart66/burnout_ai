import psycopg2
import pandas as pd
from datetime import datetime
import hashlib
import streamlit as st
from typing import Dict, List, Optional

class BurnoutDatabase:
    def __init__(self):
        # Initialize connection using Streamlit secrets
        self.init_connection()
        self.setup_database()
    
    def init_connection(self):
        """Connect to Supabase/Postgres using Streamlit Secrets"""
        try:
            # Looks for [db_url] in .streamlit/secrets.toml
            self.conn_url = st.secrets["db_url"]
        except FileNotFoundError:
            st.error("🚨 Database secret not found! Did you set up .streamlit/secrets.toml?")
            st.stop()
        except KeyError:
            st.error("🚨 'db_url' not found in secrets.toml")
            st.stop()

    def get_connection(self):
        """Create a new connection object"""
        return psycopg2.connect(self.conn_url)
    
    def setup_database(self):
        """Initialize database with PostgreSQL schema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Individual checkouts
        cursor.execute("""
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
        
        # Department Aggregates
        cursor.execute("""
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
        
        # Organization Aggregates
        cursor.execute("""
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
        
    def hash_user_id(self, email: str) -> str:
        """One-way hash for user privacy"""
        return hashlib.sha256(email.encode()).hexdigest()
    
    def save_individual_checkout(self, user_email: str, department: str, data: Dict, score: int, label: str, reflection: str = "") -> bool:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            user_hash = self.hash_user_id(user_email)
            today = datetime.now().date()
            timestamp = datetime.now()
            
            # Postgres UPSERT syntax
            cursor.execute("""
                INSERT INTO individual_checkouts (
                    user_id_hash, timestamp, date, department,
                    study_hours, sleep_hours, screen_time_hours,
                    engagement_level, assignment_deadline_missed,
                    assignments_pending, upcoming_deadline_load,
                    self_reported_stress, sentiment_score,
                    burnout_score, risk_label, reflection_text
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id_hash, date) DO UPDATE SET
                    timestamp = EXCLUDED.timestamp,
                    study_hours = EXCLUDED.study_hours,
                    burnout_score = EXCLUDED.burnout_score,
                    risk_label = EXCLUDED.risk_label;
            """, (
                user_hash, timestamp, today, department,
                data['study_hours'], data['sleep_hours'], data['screen_time_hours'],
                data['engagement_level'], data['assignment_deadline_missed'],
                data['assignments_pending'], data['upcoming_deadline_load'],
                data['self_reported_stress'], data['sentiment_score'],
                score, label, reflection
            ))
            conn.commit()
            conn.close()
            
            # Update aggregates immediately
            self.update_aggregates(today)
            return True
        except Exception as e:
            st.error(f"Database Error: {e}")
            return False
            
    def get_user_history(self, user_email: str, days: int = 30) -> pd.DataFrame:
        conn = self.get_connection()
        user_hash = self.hash_user_id(user_email)
        
        # Postgres date math syntax
        query = """
            SELECT date, burnout_score, risk_label, 
                   self_reported_stress, sleep_hours, sentiment_score
            FROM individual_checkouts
            WHERE user_id_hash = %s
            AND date >= CURRENT_DATE - INTERVAL '%s days'
            ORDER BY date DESC
        """
        # Note: Params must be passed as a tuple
        df = pd.read_sql_query(query, conn, params=(user_hash, days))
        conn.close()
        return df

    def update_aggregates(self, date: datetime.date):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Aggregation Query
        # Note: 'HAVING COUNT(*) >= 1' ensures data shows immediately for testing
        query = """
            SELECT department,
                   AVG(self_reported_stress) as avg_stress,
                   AVG(sleep_hours) as avg_sleep,
                   AVG(study_hours) as avg_workload,
                   AVG(screen_time_hours) as avg_screen_time,
                   AVG(sentiment_score) as avg_sentiment,
                   SUM(CASE WHEN risk_label = 'Low' THEN 1 ELSE 0 END) as risk_low,
                   SUM(CASE WHEN risk_label = 'Medium' THEN 1 ELSE 0 END) as risk_medium,
                   SUM(CASE WHEN risk_label = 'High' THEN 1 ELSE 0 END) as risk_high,
                   COUNT(*) as total
            FROM individual_checkouts
            WHERE date = %s
            GROUP BY department
            HAVING COUNT(*) >= 1
        """
        
        df = pd.read_sql_query(query, conn, params=(date,))
        
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT INTO department_aggregates (
                    date, department, avg_stress, avg_sleep, avg_workload,
                    avg_screen_time, avg_sentiment,
                    risk_low_count, risk_medium_count, risk_high_count,
                    total_checkouts, participation_rate
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (date, department) DO UPDATE SET
                    avg_stress = EXCLUDED.avg_stress,
                    total_checkouts = EXCLUDED.total_checkouts;
            """, (
                date, row['department'],
                float(row['avg_stress']), float(row['avg_sleep']),
                float(row['avg_workload']), float(row['avg_screen_time']),
                float(row['avg_sentiment']),
                int(row['risk_low']), int(row['risk_medium']), int(row['risk_high']),
                int(row['total']), 0.80
            ))
            
        # Update Organization Globals
        cursor.execute("""
            INSERT INTO organization_aggregates (
                date, avg_stress, avg_sleep, avg_workload,
                risk_low_pct, risk_medium_pct, risk_high_pct,
                total_checkouts, participation_rate
            )
            SELECT 
                date, AVG(avg_stress), AVG(avg_sleep), AVG(avg_workload),
                SUM(risk_low_count) * 1.0 / SUM(total_checkouts),
                SUM(risk_medium_count) * 1.0 / SUM(total_checkouts),
                SUM(risk_high_count) * 1.0 / SUM(total_checkouts),
                SUM(total_checkouts), AVG(participation_rate)
            FROM department_aggregates
            WHERE date = %s
            GROUP BY date
            ON CONFLICT (date) DO UPDATE SET
                avg_stress = EXCLUDED.avg_stress,
                total_checkouts = EXCLUDED.total_checkouts;
        """, (date,))
        
        conn.commit()
        conn.close()

    def get_department_aggregates(self, start_date, end_date, departments=None) -> pd.DataFrame:
        conn = self.get_connection()
        query = """
            SELECT date, department,
                   avg_stress, avg_sleep, avg_workload, avg_screen_time,
                   risk_low_count, risk_medium_count, risk_high_count,
                   total_checkouts, participation_rate,
                   CAST(risk_low_count AS REAL) / NULLIF(total_checkouts, 0) as risk_low_pct,
                   CAST(risk_medium_count AS REAL) / NULLIF(total_checkouts, 0) as risk_medium_pct,
                   CAST(risk_high_count AS REAL) / NULLIF(total_checkouts, 0) as risk_high_pct
            FROM department_aggregates
            WHERE date BETWEEN %s AND %s
        """
        params = [start_date, end_date]
        
        if departments:
            # Postgres syntax for array checking
            query += " AND department = ANY(%s)"
            params.append(departments)
            
        query += " ORDER BY date, department"
        
        df = pd.read_sql_query(query, conn, params=tuple(params))
        conn.close()
        return df

    def get_organization_aggregates(self, start_date, end_date) -> pd.DataFrame:
        conn = self.get_connection()
        query = """
            SELECT date, avg_stress, avg_sleep, avg_workload,
                   risk_low_pct, risk_medium_pct, risk_high_pct,
                   total_checkouts, participation_rate
            FROM organization_aggregates
            WHERE date BETWEEN %s AND %s
            ORDER BY date
        """
        df = pd.read_sql_query(query, conn, params=(start_date, end_date))
        conn.close()
        return df