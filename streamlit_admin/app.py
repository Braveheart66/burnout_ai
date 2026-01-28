# ============================================================
# streamlit_admin/app.py
# Daily Checkout (ADMIN / INTERNAL STREAMLIT)
# ============================================================

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import requests

# ============================================================
# CONFIG
# ============================================================

API_BASE = "https://your-render-url"   # <-- CHANGE THIS
CHECKOUT_ENDPOINT = f"{API_BASE}/checkout"
HISTORY_ENDPOINT = f"{API_BASE}/user/history"

# ============================================================
# SESSION STATE
# ============================================================

if "checkout_count" not in st.session_state:
    st.session_state.checkout_count = 0
if "last_checkout" not in st.session_state:
    st.session_state.last_checkout = None
if "user_email" not in st.session_state:
    st.session_state.user_email = "demo_user@company.com"
if "user_department" not in st.session_state:
    st.session_state.user_department = "Engineering"

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Daily Checkout",
    layout="centered",
    initial_sidebar_state="collapsed",
    page_icon="🌙"
)

# ============================================================
# CSS (UNCHANGED — FULL AESTHETICS PRESERVED)
# ============================================================

st.markdown("""
<style>
.stApp { background-color: #000000; }

.stMarkdown, .stText, h1, h2, h3, p {
    color: #ffffff !important;
}

.checkout-header {
    text-align: center;
    padding: 2rem 0;
    margin-bottom: 2rem;
    background: #111111;
    border-radius: 16px;
    border: 1px solid #333;
}

.checkout-title {
    font-size: 3.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #00C6FF 0%, #0072FF 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.checkout-subtitle {
    font-size: 1.2rem;
    color: #e0e0e0;
}

.anonymous-badge {
    background: #1a1a1a;
    color: #48bb78;
    border: 1px solid #48bb78;
    padding: 0.4rem 1rem;
    border-radius: 25px;
    font-weight: 600;
}

.section-card {
    background: #121212;
    border-radius: 16px;
    padding: 1.75rem;
    margin: 1.25rem 0;
    border: 1px solid #333;
}

.quick-question {
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
}

.stButton > button {
    background: linear-gradient(135deg, #00C6FF 0%, #0072FF 100%);
    color: white;
    font-weight: 700;
    font-size: 1.1rem;
    padding: 0.75rem 2rem;
    border-radius: 12px;
    border: none;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================

st.markdown(f"""
<div class="checkout-header">
    <div class="checkout-title">🌙 Daily Checkout</div>
    <div class="checkout-subtitle">Take 2 minutes to reflect on your day</div>
    <div class="time-display">📅 {datetime.now().strftime("%A, %B %d, %Y • %I:%M %p")}</div>
</div>
""", unsafe_allow_html=True)

st.markdown(
    '<div style="text-align:center;"><span class="anonymous-badge">🔒 100% Anonymous</span></div>',
    unsafe_allow_html=True
)

st.markdown("---")

# ============================================================
# MOOD CHECK
# ============================================================

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<p class="quick-question">💭 How are you feeling right now?</p>', unsafe_allow_html=True)

mood_map = {
    "😫 Overwhelmed": -1.0,
    "😟 Stressed": -0.5,
    "😐 Neutral": 0.0,
    "🙂 Good": 0.5,
    "😊 Great": 1.0
}

mood_label = st.radio(
    "Mood",
    options=list(mood_map.keys()),
    horizontal=True,
    label_visibility="collapsed"
)

sentiment_score = mood_map[mood_label]
st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# WORKLOAD
# ============================================================

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<p class="quick-question">📊 Today’s Workload</p>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    study_hours = st.slider("⏰ Work Hours", 0.0, 14.0, 6.0, 0.5)
    assignments_pending = st.slider("📝 Tasks Pending", 0, 10, 3)

with col2:
    screen_time = st.slider("📱 Screen Time", 1.0, 16.0, 8.0, 0.5)
    upcoming_deadlines = st.slider("📅 Deadlines This Week", 0, 10, 2)

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# WELLNESS
# ============================================================

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<p class="quick-question">💚 Wellness Check</p>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    sleep_hours = st.slider("😴 Sleep (hours)", 3.0, 12.0, 7.0, 0.5)
    stress_level = st.select_slider("🧘 Stress Level", options=list(range(1, 11)), value=5)

with col2:
    engagement = st.slider("🎯 Engagement Level", 0.0, 1.0, 0.8, 0.05)
    missed_deadline = st.checkbox("⏰ Missed a deadline today")

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# REFLECTION
# ============================================================

st.markdown('<div class="section-card">', unsafe_allow_html=True)
reflection = st.text_area(
    "Reflection",
    placeholder="What went well? What was challenging?",
    height=120,
    label_visibility="collapsed"
)
st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# SUBMIT
# ============================================================

if st.button("✅ Complete Daily Checkout", use_container_width=True):
    payload = {
        "user_email": st.session_state.user_email,
        "department": st.session_state.user_department,
        "study_hours": study_hours,
        "sleep_hours": sleep_hours,
        "screen_time_hours": screen_time,
        "engagement_level": engagement,
        "assignment_deadline_missed": int(missed_deadline),
        "assignments_pending": assignments_pending,
        "upcoming_deadline_load": upcoming_deadlines,
        "self_reported_stress": stress_level,
        "sentiment_score": sentiment_score,
        "reflection": reflection
    }

    with st.spinner("Processing checkout..."):
        res = requests.post(CHECKOUT_ENDPOINT, json=payload)

    if res.status_code == 200:
        data = res.json()
        score = data["burnout_score"]
        label = data["risk_label"]

        st.success("✅ Checkout complete!")
        st.session_state.checkout_count += 1

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            gauge={"axis": {"range": [0, 100]}}
        ))
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.error("❌ API Error. Please check backend.")

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.caption("""
🔒 Privacy Guarantee: Only anonymized aggregates are visible to leadership.  
💚 This tool supports awareness — not surveillance.
""")
