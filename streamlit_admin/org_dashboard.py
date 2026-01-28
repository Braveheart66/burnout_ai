# ============================================================
# streamlit_admin/org_dashboard.py
# Organizational Wellbeing Dashboard (ADMIN VIEW)
# ============================================================

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests

# ============================================================
# CONFIG
# ============================================================

API_BASE = "https://your-render-url"   # 🔴 CHANGE THIS
DEPT_ENDPOINT = f"{API_BASE}/dept/aggregates"
ORG_ENDPOINT = f"{API_BASE}/org/aggregates"

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Organizational Wellbeing Dashboard",
    layout="wide",
    page_icon="📊"
)

# ============================================================
# CSS — FULL ORIGINAL AESTHETICS PRESERVED
# ============================================================

st.markdown("""
<style>
.stApp {
    background-color: #000000;
}

.stMarkdown, .stText, h1, h2, h3, p, span {
    color: #ffffff !important;
}

.dashboard-header {
    background: #111111;
    padding: 2rem;
    border-radius: 16px;
    margin-bottom: 2rem;
    border: 1px solid #333;
    text-align: center;
}

.dashboard-title {
    font-size: 2.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #00C6FF 0%, #0072FF 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.kpi-card {
    background: #121212;
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    border: 1px solid #333;
}

.kpi-value {
    font-size: 2.5rem;
    font-weight: 700;
}

.kpi-label {
    font-size: 0.9rem;
    color: #a0aec0 !important;
}

.alert-box {
    background: #2a1212;
    border-left: 4px solid #f56565;
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
}

.success-box {
    background: #0f291e;
    border-left: 4px solid #48bb78;
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
}

section[data-testid="stSidebar"] {
    background-color: #111111;
    border-right: 1px solid #333;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATA LOADING HELPERS
# ============================================================

def load_department_data(start_date, end_date):
    try:
        r = requests.get(
            DEPT_ENDPOINT,
            params={"start": start_date, "end": end_date},
            timeout=10
        )
        r.raise_for_status()
        return pd.DataFrame(r.json())
    except Exception:
        return pd.DataFrame()

def load_org_data(start_date, end_date):
    try:
        r = requests.get(
            ORG_ENDPOINT,
            params={"start": start_date, "end": end_date},
            timeout=10
        )
        r.raise_for_status()
        return pd.DataFrame(r.json())
    except Exception:
        return pd.DataFrame()

def generate_fallback_data():
    dates = pd.date_range(end=datetime.now(), periods=30)
    depts = ["Engineering", "Marketing", "Sales", "Operations", "HR", "Finance"]
    rows = []

    for d in dates:
        for dept in depts:
            stress = np.random.uniform(4, 8)
            rows.append({
                "date": d,
                "department": dept,
                "avg_stress": stress,
                "avg_sleep": np.clip(8 - (stress - 5) * 0.4, 4, 9),
                "avg_workload": np.clip(6 + (stress - 5) * 0.5, 4, 12),
                "risk_low_pct": max(0, 1 - stress / 10),
                "risk_medium_pct": 0.3,
                "risk_high_pct": stress / 10,
                "participation_rate": np.random.uniform(0.7, 0.95),
                "total_checkouts": np.random.randint(20, 60)
            })

    return pd.DataFrame(rows)

# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("🔍 Filters")

today = datetime.now().date()
date_range = st.sidebar.date_input(
    "Date Range",
    value=(today - timedelta(days=30), today),
    max_value=today
)

start_date, end_date = date_range

# ============================================================
# LOAD DATA
# ============================================================

df = load_department_data(start_date, end_date)

if df.empty:
    st.warning("📊 No live data available — showing demo data.")
    df = generate_fallback_data()

df["date"] = pd.to_datetime(df["date"])

# ============================================================
# DEPARTMENT FILTER
# ============================================================

selected_depts = st.sidebar.multiselect(
    "Departments",
    options=sorted(df["department"].unique()),
    default=sorted(df["department"].unique())
)

df = df[df["department"].isin(selected_depts)]

# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="dashboard-header">
    <div class="dashboard-title">📊 Organizational Wellbeing Dashboard</div>
    <p>Aggregate insights • Privacy-first • No individual tracking</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# KPIs (LAST 7 DAYS)
# ============================================================

df_week = df[df["date"] >= df["date"].max() - pd.Timedelta(days=7)]

col1, col2, col3, col4, col5 = st.columns(5)

def kpi(card_col, value, label):
    with card_col:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{value}</div>
            <div class="kpi-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

kpi(col1, f"{df_week['participation_rate'].mean():.0%}", "Participation")
kpi(col2, f"{df_week['avg_stress'].mean():.1f}/10", "Avg Stress")
kpi(col3, f"{df_week['avg_sleep'].mean():.1f}h", "Avg Sleep")
kpi(col4, f"{df_week['risk_high_pct'].mean():.0%}", "High Risk %")
kpi(col5, int(df_week["total_checkouts"].sum()), "Total Checkouts")

# ============================================================
# ALERTS
# ============================================================

st.subheader("⚠️ Alerts & Insights")

if df_week["avg_stress"].mean() > 7.5:
    st.markdown("""
    <div class="alert-box">
        🚨 <strong>Elevated Stress Detected</strong><br>
        Organization-wide stress levels are critically high.
    </div>
    """, unsafe_allow_html=True)

if df_week["avg_sleep"].mean() < 6.5:
    st.markdown("""
    <div class="alert-box">
        😴 <strong>Sleep Deficit Warning</strong><br>
        Average sleep below healthy range.
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# DEPARTMENT COMPARISON
# ============================================================

st.subheader("🏢 Department Comparison")

col1, col2 = st.columns(2)

with col1:
    fig = px.bar(
        df.groupby("department")["avg_stress"].mean().sort_values(),
        orientation="h",
        title="Average Stress by Department",
        color_continuous_scale="RdYlGn_r"
    )
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    dept_risk = df.groupby("department")[["risk_low_pct", "risk_medium_pct", "risk_high_pct"]].mean()
    fig = go.Figure()
    fig.add_bar(name="Low", x=dept_risk.index, y=dept_risk["risk_low_pct"])
    fig.add_bar(name="Medium", x=dept_risk.index, y=dept_risk["risk_medium_pct"])
    fig.add_bar(name="High", x=dept_risk.index, y=dept_risk["risk_high_pct"])
    fig.update_layout(barmode="stack", template="plotly_dark", title="Risk Distribution")
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# TRENDS
# ============================================================

st.subheader("📈 Trends Over Time")

col1, col2 = st.columns(2)

with col1:
    stress_trend = df.groupby("date")["avg_stress"].mean().reset_index()
    fig = px.line(stress_trend, x="date", y="avg_stress", title="Stress Trend")
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    participation_trend = df.groupby("date")["participation_rate"].mean().reset_index()
    fig = px.line(participation_trend, x="date", y="participation_rate", title="Participation Trend")
    fig.update_layout(template="plotly_dark", yaxis=dict(range=[0, 1]))
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# WORKLOAD ANALYSIS
# ============================================================

st.subheader("💼 Workload vs Sleep")

fig = px.scatter(
    df,
    x="avg_workload",
    y="avg_sleep",
    color="avg_stress",
    size="total_checkouts",
    hover_data=["department"],
    color_continuous_scale="RdYlGn_r"
)
fig.update_layout(template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.info("""
🔒 **Privacy Guarantee**  
Only aggregated, anonymized metrics are displayed.  
No individual-level data is ever accessible.
""")
