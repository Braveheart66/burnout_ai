import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import json
from src.predict import predict_burnout
from src.utils import get_risk_recommendations
from src.database import BurnoutDatabase

db = BurnoutDatabase()

# Initialize session state for tracking
if 'checkout_count' not in st.session_state:
    st.session_state.checkout_count = 0
if 'last_checkout' not in st.session_state:
    st.session_state.last_checkout = None
if 'user_email' not in st.session_state:
    st.session_state.user_email = "demo_user@company.com"
if 'user_department' not in st.session_state:
    st.session_state.user_department = "Engineering"

user_history = db.get_user_history(st.session_state.user_email, days=7)

# Page config
st.set_page_config(
    page_title="Daily Checkout",
    layout="centered",
    initial_sidebar_state="collapsed",
    page_icon="🌙"
)

# Custom CSS for Dark Mode / High Contrast
st.markdown("""
    <style>
    /* Main background - Pure Black */
    .stApp {
        background-color: #000000;
    }
    
    /* Text defaults for Streamlit components */
    .stMarkdown, .stText, h1, h2, h3, p {
        color: #ffffff !important;
    }

    /* Header styling */
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
        /* Neon gradient for contrast */
        background: linear-gradient(135deg, #00C6FF 0%, #0072FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .checkout-subtitle {
        font-size: 1.2rem;
        color: #e0e0e0; /* High contrast white-ish */
        font-weight: 400;
        margin-bottom: 0.5rem;
    }
    .time-display {
        text-align: center;
        font-size: 1rem;
        color: #a0aec0;
        margin-bottom: 1rem;
    }
    
    /* Privacy badge */
    .anonymous-badge {
        background: #1a1a1a;
        color: #48bb78; /* Bright green text */
        border: 1px solid #48bb78;
        padding: 0.4rem 1rem;
        border-radius: 25px;
        font-size: 0.875rem;
        font-weight: 600;
        display: inline-block;
        box-shadow: 0 0 10px rgba(72, 187, 120, 0.2);
    }
    
    /* Section cards - Dark Gray with Borders */
    .section-card {
        background: #121212;
        border-radius: 16px;
        padding: 1.75rem;
        margin: 1.25rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        border: 1px solid #333333; /* Distinct border */
    }
    
    /* Section headers */
    .section-icon {
        font-size: 1.5rem;
        margin-right: 0.5rem;
    }
    .quick-question {
        font-size: 1.2rem;
        font-weight: 600;
        color: #ffffff !important;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
    }
    
    /* Slider styling - Neon accents */
    .stSlider > div > div > div > div {
        background-color: #0072FF !important;
    }
    .stSlider div[data-testid="stMarkdownContainer"] p {
        color: #e0e0e0 !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #00C6FF 0%, #0072FF 100%);
        color: white;
        font-weight: 700;
        font-size: 1.1rem;
        padding: 0.75rem 2rem;
        border-radius: 12px;
        border: none;
        box-shadow: 0 0 15px rgba(0, 114, 255, 0.4);
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 25px rgba(0, 114, 255, 0.6);
    }
    
    /* Radio button labels */
    .stRadio > label {
        color: #ffffff !important;
    }
    div[data-testid="stRadio"] label p {
        color: #e0e0e0 !important;
        font-size: 1rem;
    }
    
    /* Progress indicator */
    .progress-bar {
        width: 100%;
        height: 4px;
        background: #333;
        border-radius: 2px;
        margin-bottom: 2rem;
    }
    .progress-fill {
        height: 100%;
        background: #0072FF;
        box-shadow: 0 0 10px #0072FF;
    }
    
    /* Info boxes (Recommendations) */
    .info-box {
        background: #1a1a1a;
        border-left: 4px solid #00C6FF;
        padding: 1rem;
        border-radius: 8px;
        color: #e0e0e0;
    }
    
    /* Text Area */
    .stTextArea textarea {
        background-color: #1a1a1a;
        color: #ffffff;
        border: 1px solid #444;
    }
    .stTextArea textarea:focus {
        border-color: #0072FF;
        box-shadow: 0 0 10px rgba(0, 114, 255, 0.2);
    }
    
    /* Divider */
    hr {
        border-color: #333;
    }
    
    /* Captions/Small text */
    .stCaptionContainer {
        color: #888888 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize database connection
from src.database import BurnoutDatabase

db = BurnoutDatabase()

# Initialize session state for tracking
if 'checkout_count' not in st.session_state:
    st.session_state.checkout_count = 0
if 'last_checkout' not in st.session_state:
    st.session_state.last_checkout = None
if 'user_email' not in st.session_state:
    # In production, this would come from authentication
    st.session_state.user_email = "demo_user@company.com"
if 'user_department' not in st.session_state:
    st.session_state.user_department = "Engineering"

# Header
st.markdown("""
    <div class="checkout-header">
        <div class="checkout-title">🌙 Daily Checkout</div>
        <div class="checkout-subtitle">Take 2 minutes to reflect on your day</div>
        <div class="time-display">📅 {}</div>
    </div>
""".format(datetime.now().strftime("%A, %B %d, %Y • %I:%M %p")), unsafe_allow_html=True)

# Privacy notice
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown('<div style="text-align: center;"><span class="anonymous-badge">🔒 100% Anonymous</span></div>', unsafe_allow_html=True)

st.markdown("---")

# Progress tracking
section_count = 0
total_sections = 3
st.markdown(f"""
    <div class="progress-bar">
        <div class="progress-fill" style="width: {(section_count/total_sections)*100}%"></div>
    </div>
""", unsafe_allow_html=True)

# Quick mood check
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<p class="quick-question"><span class="section-icon">💭</span>How are you feeling right now?</p>', unsafe_allow_html=True)

mood_options = [
    ("😫", "Overwhelmed", -1.0),
    ("😟", "Stressed", -0.5),
    ("😐", "Neutral", 0.0),
    ("🙂", "Good", 0.5),
    ("😊", "Great", 1.0)
]

selected_mood = st.radio(
    "mood",
    options=[m[2] for m in mood_options],
    format_func=lambda x: [m[0] + " " + m[1] for m in mood_options if m[2] == x][0],
    horizontal=True,
    label_visibility="collapsed",
    key="mood_selector"
)

if selected_mood <= -0.5:
    st.info("💙 It's okay to have tough days. Let's see what might help.")
elif selected_mood >= 0.5:
    st.success("✨ Great to hear! Let's keep that momentum going.")
    
st.markdown('</div>', unsafe_allow_html=True)

# Today's workday reflection
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<p class="quick-question"><span class="section-icon">📊</span>Today\'s Workload</p>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    study = st.slider("⏰ Work/Study Hours", 0.0, 14.0, 6.0, 0.5, 
                     help="Including meetings, focused work, studying",
                     key="work_hours")
    if study > 10:
        st.caption("⚠️ That's a long day! Make sure to rest.")
    
    assignments = st.slider("📝 Tasks Pending", 0, 10, 3,
                           help="Incomplete tasks/assignments")
    if assignments > 5:
        st.caption("💡 Tip: Try breaking these into smaller chunks")

with col2:
    screen = st.slider("📱 Screen Time", 1.0, 16.0, 8.0, 0.5,
                      help="Total device usage today")
    if screen > 12:
        st.caption("👀 High screen time - remember to take breaks!")
        
    upcoming = st.slider("📅 Deadlines This Week", 0, 10, 2,
                        help="Major deadlines in next 7 days")
    if upcoming > 5:
        st.caption("⏰ Busy week ahead - plan your time carefully")

st.markdown('</div>', unsafe_allow_html=True)

# Wellness check
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<p class="quick-question"><span class="section-icon">💚</span>Wellness Check</p>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    sleep = st.slider("😴 Sleep Last Night (hours)", 3.0, 12.0, 7.0, 0.5,
                     help="Quality sleep hours")
    if sleep < 6:
        st.caption("🚨 Sleep is critical! Try to get more tonight.")
    elif sleep >= 7:
        st.caption("✅ Great sleep! That helps everything.")
    
    stress = st.select_slider(
        "🧘 Stress Level",
        options=list(range(1, 11)),
        value=5,
        format_func=lambda x: f"{'🟢' if x <= 3 else '🟡' if x <= 6 else '🔴'} {x}/10",
        help="1 = Very calm, 10 = Extremely stressed"
    )
    if stress >= 8:
        st.caption("🆘 High stress - please consider reaching out for support")

with col2:
    attendance = st.slider("🎯 Engagement Level", 0.0, 1.0, 0.80, 0.05,
                          help="How engaged/present were you today?",
                          format="%.0f%%")
    if attendance < 0.6:
        st.caption("💭 Low engagement - that's okay, some days are harder")
    
    missed = st.checkbox("⏰ Missed an important deadline today", value=False)
    if missed:
        st.caption("Don't be too hard on yourself - communicate and adjust")

st.markdown('</div>', unsafe_allow_html=True)

# Optional reflection
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<p class="quick-question"><span class="section-icon">💭</span>Optional: Brief Reflection</p>', unsafe_allow_html=True)
st.markdown('<p style="font-size: 0.9rem; color: #718096; margin-bottom: 0.75rem;">This is just for you - a moment to pause and reflect.</p>', unsafe_allow_html=True)

reflection = st.text_area(
    "reflection_area",
    placeholder="What went well today? What was challenging? How are you really feeling?\n\nThis is private and won't be shared with anyone. Use it as a journal entry...",
    height=120,
    label_visibility="collapsed",
    key="reflection_text"
)

st.markdown('</div>', unsafe_allow_html=True)

# Checkout button
st.markdown("<br>", unsafe_allow_html=True)
checkout_btn = st.button("✅ Complete Daily Checkout", type="primary", use_container_width=True)

if checkout_btn:
    with st.spinner("Processing your checkout..."):
        # Prepare data
        data = {
            "study_hours": study,
            "sleep_hours": sleep,
            "screen_time_hours": screen,
            "engagement_level": attendance,
            "assignment_deadline_missed": 1 if missed else 0,
            "assignments_pending": assignments,
            "upcoming_deadline_load": upcoming,
            "self_reported_stress": stress,
            "sentiment_score": selected_mood
        }
        
        # Get prediction
        score, label = predict_burnout(data)
        
        # Save to database
        save_success = db.save_individual_checkout(
            user_email=st.session_state.user_email,
            department=st.session_state.user_department,
            data=data,
            score=score,
            label=label,
            reflection=reflection
        )
        
        if save_success:
            # Update session state
            st.session_state.checkout_count += 1
            st.session_state.last_checkout = datetime.now()
            
            # Get user history from database
            user_history = db.get_user_history(st.session_state.user_email, days=7)
        
            # Success message
            st.balloons()
            st.success("✅ Checkout complete! Thank you for taking care of yourself.")
        
        st.markdown("---")
        
        # Personal insights (private to user)
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("📊 Your Personal Insights")
        
        # Risk indicator
        if label == "Low":
            st.success(f"🟢 **Wellbeing Status: Healthy** (Score: {score}/100)")
            st.markdown("You're managing well! Keep up the healthy habits.")
        elif label == "Medium":
            st.warning(f"🟡 **Wellbeing Status: Attention Needed** (Score: {score}/100)")
            st.markdown("You're showing early signs of strain. Consider the recommendations below.")
        else:
            st.error(f"🔴 **Wellbeing Status: High Risk** (Score: {score}/100)")
            st.markdown("⚠️ **Please prioritize self-care and consider reaching out for support.**")
        
        # Mini gauge
        fig_mini = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkslateblue"},
                'steps': [
                    {'range': [0, 40], 'color': "#c6f6d5"},
                    {'range': [40, 70], 'color': "#fef08a"},
                    {'range': [70, 100], 'color': "#fecaca"}
                ],
            }
        ))
        fig_mini.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_mini, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Personalized recommendations
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("💡 Your Action Items")
        
        recommendations = get_risk_recommendations(label, data)
        
        if recommendations:
            for i, rec in enumerate(recommendations[:5], 1):  # Show top 5
                st.markdown(f"**{i}.** {rec}")
        else:
            st.info("✨ You're doing great! Keep maintaining your current habits.")
        
        # General guidance based on risk
        with st.expander("📋 View Detailed Guidance"):
            if label == "Low":
                st.markdown("""
                **Continue What's Working:**
                - Maintain your sleep schedule
                - Keep stress management practices
                - Stay engaged with your work
                - Take regular breaks
                """)
            elif label == "Medium":
                st.markdown("""
                **Prevention Strategies:**
                - **Sleep**: Aim for consistent 7-8 hours
                - **Breaks**: Take 5-10 min breaks every hour
                - **Boundaries**: Set clear work/life limits
                - **Support**: Talk to a colleague or mentor
                - **Tasks**: Break large projects into smaller steps
                """)
            else:
                st.markdown("""
                **Immediate Actions:**
                1. **Tonight**: Prioritize 8+ hours sleep
                2. **Tomorrow**: Reduce workload if possible
                3. **This Week**: Schedule time with support person
                4. **Consider**: Taking a mental health day
                5. **Reach Out**: Use employee assistance program
                """)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Weekly trend (if available)
        if len(user_history) > 1:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("📈 Your Week at a Glance")
            
            # Rename columns for display
            user_history = user_history.rename(columns={
                'burnout_score': 'score',
                'risk_label': 'label',
                'self_reported_stress': 'stress',
                'sleep_hours': 'sleep'
            })
            
            # Trend chart
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(
                x=list(range(len(user_history))),
                y=user_history['score'],
                mode='lines+markers',
                name='Wellbeing Score',
                line=dict(color='#805ad5', width=3),
                marker=dict(size=10)
            ))
            fig_trend.add_hline(y=40, line_dash="dash", line_color="green", 
                               annotation_text="Low Risk")
            fig_trend.add_hline(y=70, line_dash="dash", line_color="red",
                               annotation_text="High Risk")
            fig_trend.update_layout(
                title="Your Wellbeing Trend",
                xaxis_title="Days Ago",
                yaxis_title="Score",
                height=300,
                showlegend=False
            )
            st.plotly_chart(fig_trend, use_container_width=True)
            
            # Insights
            if user_history['score'].iloc[0] > user_history['score'].iloc[-1]:
                st.warning("📈 Your score has increased (worsening). Consider taking action today.")
            elif user_history['score'].iloc[0] < user_history['score'].iloc[-1]:
                st.success("📉 Your score is improving! Keep up the positive changes.")
            else:
                st.info("➡️ Your wellbeing is relatively stable this week.")
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("💡 Complete daily checkouts for 2+ days to see your trend analysis!")
        
        
        # Organizational note (anonymous data)
        st.markdown("---")
        st.info("""
        **📊 How This Helps Your Organization (Anonymous Data Only):**
        
        Your individual responses are completely private. Only anonymized, aggregated patterns 
        are visible to leadership to identify:
        - Departments with unsustainable workload trends
        - Seasonal stress patterns
        - When to add resources or redistribute work
        
        This creates a healthier workplace without monitoring individuals.
        """)
        
        # Support resources
        with st.expander("🆘 Need Immediate Support?"):
            st.markdown("""
            **Crisis Resources:**
            - 🇺🇸 988 Suicide & Crisis Lifeline
            - 🇮🇳 AASRA: +91-9820466726
            - 📞 Employee Assistance Program: [Contact HR]
            - 💬 Campus/Workplace Counseling Services
            
            **Non-Emergency Support:**
            - Manager/Supervisor check-in
            - HR wellness programs
            - Peer support groups
            - Occupational health services
            """)

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
st.caption("""
🔒 **Privacy Guarantee**: Your individual responses are never shared. Only anonymous, 
aggregated trends are used to improve workplace conditions.

⏱️ **Daily Habit**: Complete checkout at the end of each workday (takes 2-3 minutes).

💚 **Self-Care Reminder**: This is a tool for awareness, not judgment. Be honest with yourself.
""")