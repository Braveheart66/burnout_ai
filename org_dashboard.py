import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# FIX IMPORT: Use the new src folder
from src.database import BurnoutDatabase

# Page config
st.set_page_config(
    page_title="Organizational Wellbeing Dashboard",
    layout="wide",
    page_icon="📊"
)

# Custom CSS - Dark Mode (Matches app_daily.py)
st.markdown("""
    <style>
    /* Main background */
    .stApp {
        background-color: #000000;
    }
    
    /* Text defaults */
    .stMarkdown, .stText, h1, h2, h3, p, span {
        color: #ffffff !important;
    }
    
    /* Header */
    .dashboard-header {
        background: #111111;
        padding: 2rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2rem;
        border: 1px solid #333;
        text-align: center;
    }
    .dashboard-title {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #00C6FF 0%, #0072FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* KPI Cards */
    .kpi-card {
        background: #121212;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        text-align: center;
        border: 1px solid #333;
    }
    .kpi-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #ffffff;
    }
    .kpi-label {
        font-size: 0.9rem;
        color: #a0aec0 !important;
        margin-top: 0.5rem;
    }
    
    /* Alert Boxes */
    .alert-box {
        background: #2a1212;
        border-left: 4px solid #f56565;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #fff;
    }
    .success-box {
        background: #0f291e;
        border-left: 4px solid #48bb78;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #fff;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #111111;
        border-right: 1px solid #333;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize database
db = BurnoutDatabase()

# Helper Functions
def generate_sample_org_data():
    """Generate sample organizational data (aggregate only) - FALLBACK ONLY"""
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    departments = ['Engineering', 'Marketing', 'Sales', 'Operations', 'HR', 'Finance']
    org_data = []
    
    for dept in departments:
        for date in dates:
            base_stress = {'Engineering': 6.5, 'Marketing': 5.5, 'Sales': 7.0, 'Operations': 5.0, 'HR': 4.5, 'Finance': 6.0}[dept]
            
            if date.day > 25: stress_factor = 1.3
            elif date.day < 5: stress_factor = 1.2
            else: stress_factor = 1.0
            
            avg_stress = base_stress * stress_factor + np.random.normal(0, 0.5)
            avg_sleep = 7.0 - (avg_stress - 5) * 0.3 + np.random.normal(0, 0.3)
            avg_workload = 6.5 + (avg_stress - 5) * 0.5 + np.random.normal(0, 0.5)
            
            if avg_stress < 5: risk_low, risk_med, risk_high = 0.7, 0.25, 0.05
            elif avg_stress < 7: risk_low, risk_med, risk_high = 0.4, 0.45, 0.15
            else: risk_low, risk_med, risk_high = 0.2, 0.35, 0.45
            
            org_data.append({
                'date': date,
                'department': dept,
                'avg_stress': max(1, min(10, avg_stress)),
                'avg_sleep': max(4, min(9, avg_sleep)),
                'avg_workload': max(4, min(12, avg_workload)),
                'participation_rate': np.random.uniform(0.7, 0.95),
                'risk_low_pct': risk_low,
                'risk_medium_pct': risk_med,
                'risk_high_pct': risk_high,
                'checkouts_today': np.random.randint(15, 50)
            })
    return pd.DataFrame(org_data)

def load_org_data_from_database(start_date, end_date, departments=None):
    try:
        df = db.get_department_aggregates(start_date, end_date, departments)
        if len(df) == 0:
            st.warning("📊 No real data available yet. Showing sample data for demonstration.")
            return generate_sample_org_data()
        df['checkouts_today'] = df['total_checkouts']
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return generate_sample_org_data()

# --- MAIN APP LOGIC ---

today = datetime.now()

# Sidebar Filters
st.sidebar.header("🔍 Filters")
date_range = st.sidebar.date_input(
    "Date Range",
    value=(today - timedelta(days=30), today),
    max_value=today
)

# Load Data
temp_df = load_org_data_from_database(
    start_date=pd.to_datetime(date_range[0]).date(),
    end_date=pd.to_datetime(date_range[1]).date()
)

# --------------------------------------------------------------------------------
# FIX: Convert 'date' column to datetime objects immediately
# This prevents the "TypeError: Cannot compare Timestamp with datetime.date" crash
# --------------------------------------------------------------------------------
if not temp_df.empty:
    temp_df['date'] = pd.to_datetime(temp_df['date'])

# Department Filter (Fixed duplicates)
selected_depts = st.sidebar.multiselect(
    "Departments",
    options=temp_df['department'].unique(),
    default=temp_df['department'].unique(),
    key="org_dept_filter_primary"
)

# Apply Filters
df = temp_df[temp_df['department'].isin(selected_depts)]
df_filtered = df # Alias for clarity

# Subsets for metrics
df_today = df_filtered[df_filtered['date'] == df_filtered['date'].max()]
df_week = df_filtered[df_filtered['date'] >= pd.to_datetime(today - timedelta(days=7))]

# Header
st.markdown("""
    <div class="dashboard-header">
        <div class="dashboard-title">📊 Organizational Wellbeing Dashboard</div>
        <p>Aggregate insights • No individual tracking • Privacy-first analytics</p>
    </div>
""", unsafe_allow_html=True)

# Key metrics row
st.subheader("📈 Organization-Wide Metrics (Last 7 Days)")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
    participation = df_week['participation_rate'].mean()
    st.markdown(f'<div class="kpi-value">{participation:.0%}</div>', unsafe_allow_html=True)
    st.markdown('<div class="kpi-label">Participation Rate</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
    avg_stress = df_week['avg_stress'].mean()
    st.markdown(f'<div class="kpi-value">{avg_stress:.1f}/10</div>', unsafe_allow_html=True)
    st.markdown('<div class="kpi-label">Avg Stress Level</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
    avg_sleep = df_week['avg_sleep'].mean()
    color = "#48bb78" if avg_sleep >= 7 else "#ecc94b" if avg_sleep >= 6 else "#f56565"
    st.markdown(f'<div class="kpi-value" style="color: {color}">{avg_sleep:.1f}h</div>', unsafe_allow_html=True)
    st.markdown('<div class="kpi-label">Avg Sleep</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
    high_risk = df_week['risk_high_pct'].mean()
    st.markdown(f'<div class="kpi-value">{high_risk:.0%}</div>', unsafe_allow_html=True)
    st.markdown('<div class="kpi-label">High Risk %</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col5:
    st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
    total_checkouts = df_week['checkouts_today'].sum()
    st.markdown(f'<div class="kpi-value">{int(total_checkouts)}</div>', unsafe_allow_html=True)
    st.markdown('<div class="kpi-label">Total Checkouts</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Alerts section
st.subheader("⚠️ Alerts & Recommendations")

if avg_stress > 7.5:
    st.markdown("""
    <div class="alert-box">
        <strong>🚨 Elevated Stress Detected</strong><br>
        Organization-wide stress levels are high. Consider reviewing deadlines and resource allocation.
    </div>
    """, unsafe_allow_html=True)

if avg_sleep < 6.5:
    st.markdown("""
    <div class="alert-box">
        <strong>😴 Sleep Deficit Alert</strong><br>
        Average sleep is below healthy levels. Consider promoting flexible hours and reducing late meetings.
    </div>
    """, unsafe_allow_html=True)

if high_risk > 0.3:
    st.markdown("""
    <div class="alert-box">
        <strong>📊 High-Risk Population Alert</strong><br>
        Over 30% of employees showing high burnout risk. Immediate workload redistribution recommended.
    </div>
    """, unsafe_allow_html=True)

if avg_stress < 5 and avg_sleep > 7:
    st.markdown("""
    <div class="success-box">
        <strong>✅ Positive Wellbeing Trend</strong><br>
        Organizational health indicators are good! Current practices are working well.
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Department comparison
st.subheader("🏢 Department Comparison")

col1, col2 = st.columns(2)

with col1:
    # Stress by department
    dept_stress = df_filtered.groupby('department')['avg_stress'].mean().sort_values(ascending=False)
    fig_dept_stress = px.bar(
        x=dept_stress.values,
        y=dept_stress.index,
        orientation='h',
        title="Average Stress by Department",
        labels={'x': 'Stress Level', 'y': 'Department'},
        color=dept_stress.values,
        color_continuous_scale='RdYlGn_r'
    )
    # Applied dark template
    fig_dept_stress.update_layout(showlegend=False, height=400, template="plotly_dark")
    st.plotly_chart(fig_dept_stress, use_container_width=True)

with col2:
    # Risk distribution by department
    dept_risk = df_filtered.groupby('department')[['risk_low_pct', 'risk_medium_pct', 'risk_high_pct']].mean()
    fig_dept_risk = go.Figure()
    fig_dept_risk.add_trace(go.Bar(name='Low Risk', x=dept_risk.index, y=dept_risk['risk_low_pct'], marker_color='#48bb78'))
    fig_dept_risk.add_trace(go.Bar(name='Medium Risk', x=dept_risk.index, y=dept_risk['risk_medium_pct'], marker_color='#ecc94b'))
    fig_dept_risk.add_trace(go.Bar(name='High Risk', x=dept_risk.index, y=dept_risk['risk_high_pct'], marker_color='#f56565'))
    # Applied dark template
    fig_dept_risk.update_layout(barmode='stack', title='Risk Distribution by Department', yaxis_title='Proportion', height=400, template="plotly_dark")
    st.plotly_chart(fig_dept_risk, use_container_width=True)

# Time trends
st.subheader("📅 Trends Over Time")

col1, col2 = st.columns(2)

with col1:
    # Stress trend
    daily_stress = df_filtered.groupby('date')['avg_stress'].mean().reset_index()
    fig_stress_trend = px.line(
        daily_stress,
        x='date',
        y='avg_stress',
        title='Average Stress Trend',
        labels={'avg_stress': 'Stress Level', 'date': 'Date'}
    )
    fig_stress_trend.add_hline(y=7, line_dash="dash", line_color="#f56565", annotation_text="High Threshold")
    fig_stress_trend.add_hline(y=5, line_dash="dash", line_color="#48bb78", annotation_text="Healthy Level")
    # Applied dark template
    fig_stress_trend.update_layout(template="plotly_dark")
    st.plotly_chart(fig_stress_trend, use_container_width=True)

with col2:
    # Participation trend
    daily_participation = df_filtered.groupby('date')['participation_rate'].mean().reset_index()
    fig_participation = px.line(
        daily_participation,
        x='date',
        y='participation_rate',
        title='Daily Checkout Participation Rate',
        labels={'participation_rate': 'Participation %', 'date': 'Date'}
    )
    # Applied dark template
    fig_participation.update_layout(yaxis=dict(range=[0, 1]), template="plotly_dark")
    st.plotly_chart(fig_participation, use_container_width=True)

# --- WORKLOAD ANALYSIS SECTION ---
st.subheader("💼 Workload Analysis")

col1, col2 = st.columns(2)

with col1:
    # Workload vs Sleep
    fig_scatter = px.scatter(
        df_filtered,
        x='avg_workload',
        y='avg_sleep',
        color='avg_stress',
        size='checkouts_today',
        hover_data=['department'],
        title='Workload vs Sleep (colored by stress)',
        labels={
            'avg_workload': 'Average Work Hours',
            'avg_sleep': 'Average Sleep Hours',
            'avg_stress': 'Stress'
        },
        color_continuous_scale='RdYlGn_r'
    )
    fig_scatter.update_layout(template="plotly_dark")
    st.plotly_chart(fig_scatter, use_container_width=True)

with col2:
    # Day of week pattern
    # Ensure correct day ordering
    df_filtered['day_of_week'] = pd.to_datetime(df_filtered['date']).dt.day_name()
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    # Reindex to force order, fillna to handle missing days
    weekly_pattern = df_filtered.groupby('day_of_week')['avg_stress'].mean().reindex(day_order).fillna(0)

    fig_weekly = px.bar(
        x=weekly_pattern.index,
        y=weekly_pattern.values,
        title='Stress Pattern by Day of Week',
        labels={'x': 'Day', 'y': 'Average Stress'},
        color=weekly_pattern.values,
        color_continuous_scale='RdYlGn_r'
    )
    fig_weekly.update_layout(template="plotly_dark")
    st.plotly_chart(fig_weekly, use_container_width=True)

# Footer
st.markdown("---")
st.info("""
**🔒 Privacy Note**: This dashboard shows only aggregated, anonymized data. 
Individual responses are never accessible to management.
""")