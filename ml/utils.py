def engagement_score(study_hours, engagement_level, missed_deadline):
    """
    Engagement score (0–10)
    Higher = better engagement
    """
    # Optimal study range around 5 hours
    study_component = 1 - abs(study_hours - 5) / 6
    study_component = max(0, min(1, study_component))

    engagement_component = engagement_level
    deadline_penalty = 0.3 if missed_deadline else 0

    score = (0.4 * study_component + 0.6 * engagement_component - deadline_penalty) * 10
    return max(0, min(10, score))


def cognitive_load(assignments_pending, upcoming_deadline_load):
    """
    Cognitive load score (0–10)
    Higher = more mental load
    """
    assignments_norm = min(assignments_pending / 5, 1)
    deadlines_norm = min(upcoming_deadline_load / 5, 1)

    load = (0.6 * assignments_norm + 0.4 * deadlines_norm) * 10
    return min(10, load)


def get_risk_recommendations(label, data):
    """
    Rule-based, ethical recommendations
    """
    recs = []

    if data["sleep_hours"] < 6:
        recs.append("😴 Sleep is critically low. Aim for 7–9 hours tonight.")

    if data["screen_time_hours"] > 10:
        recs.append("📱 High screen time detected. Reduce screen exposure before bed.")

    if data["self_reported_stress"] >= 8:
        recs.append("🧘 High stress detected. Consider breathing exercises or talking to someone.")

    if data["assignments_pending"] >= 4:
        recs.append("📝 Break pending tasks into smaller steps.")

    if data["engagement_level"] < 0.6:
        recs.append("🎯 Low engagement today. Reflect on blockers or distractions.")

    if label == "High":
        recs.append("🆘 Consider reaching out to a trusted person or support service.")

    return recs
