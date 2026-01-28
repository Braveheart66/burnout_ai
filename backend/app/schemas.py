from pydantic import BaseModel
from typing import Optional

class CheckoutRequest(BaseModel):
    email: str
    department: str
    study_hours: float
    sleep_hours: float
    screen_time_hours: float
    engagement_level: float
    assignment_deadline_missed: int
    assignments_pending: int
    upcoming_deadline_load: int
    self_reported_stress: int
    sentiment_score: float
    reflection: Optional[str] = ""

class CheckoutResponse(BaseModel):
    score: int
    label: str
