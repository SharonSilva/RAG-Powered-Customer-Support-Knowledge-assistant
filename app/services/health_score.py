from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import QueryLog, GapRecommendation
from app.services.impact_analytics import get_summary

ANSWER_RATE_WEIGHT = 0.5
FEEDBACK_WEIGHT = 0.3
GAP_CLOSURE_WEIGHT = 0.2


def _feedback_score(db: Session) -> tuple[float, str]:
    up = db.query(func.count(QueryLog.id)).filter(QueryLog.feedback == "up").scalar() or 0
    down = db.query(func.count(QueryLog.id)).filter(QueryLog.feedback == "down").scalar() or 0
    total_feedback = up + down

    if total_feedback == 0:
        return 100.0, "no feedback data yet — defaulted to neutral"

    score = round((up / total_feedback) * 100, 1)
    return score, f"based on {total_feedback} feedback submissions"


def _gap_closure_score(db: Session) -> tuple[float, str]:
    approved = db.query(func.count(GapRecommendation.id)).filter(GapRecommendation.status == "approved").scalar() or 0
    rejected = db.query(func.count(GapRecommendation.id)).filter(GapRecommendation.status == "rejected").scalar() or 0
    reviewed = approved + rejected

    if reviewed == 0:
        return 100.0, "no reviewed recommendations yet — defaulted to neutral"

    score = round((approved / reviewed) * 100, 1)
    return score, f"based on {reviewed} reviewed recommendations"


def compute_health_score(db: Session) -> dict:
    summary = get_summary(db)
    answer_rate = 100 - summary["fallback_rate_percent"]

    feedback_score, feedback_note = _feedback_score(db)
    gap_closure_score, gap_closure_note = _gap_closure_score(db)

    overall_score = round(
        (answer_rate * ANSWER_RATE_WEIGHT)
        + (feedback_score * FEEDBACK_WEIGHT)
        + (gap_closure_score * GAP_CLOSURE_WEIGHT),
        1,
    )

    return {
        "knowledge_health_score": overall_score,
        "breakdown": {
            "answer_rate": {"value": answer_rate, "weight": ANSWER_RATE_WEIGHT},
            "feedback_score": {"value": feedback_score, "weight": FEEDBACK_WEIGHT, "note": feedback_note},
            "gap_closure_score": {"value": gap_closure_score, "weight": GAP_CLOSURE_WEIGHT, "note": gap_closure_note},
        },
    }
