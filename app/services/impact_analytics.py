from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Integer

from app.models import QueryLog


def get_summary(db: Session) -> dict:
    total = db.query(func.count(QueryLog.id)).scalar() or 0
    answered = db.query(func.count(QueryLog.id)).filter(QueryLog.answered == True).scalar() or 0  # noqa: E712
    fallback = total - answered

    fallback_rate = round((fallback / total) * 100, 1) if total > 0 else 0.0

    return {
        "total_queries": total,
        "answered": answered,
        "fallback": fallback,
        "fallback_rate_percent": fallback_rate,
    }


def get_daily_trend(db: Session) -> list[dict]:
    day_expr = func.date_trunc("day", QueryLog.created_at)

    rows = (
        db.query(
            day_expr.label("day"),
            func.count(QueryLog.id).label("total"),
            func.sum(cast(QueryLog.answered, Integer)).label("answered"),
        )
        .group_by(day_expr)
        .order_by(day_expr)
        .all()
    )

    trend = []
    for row in rows:
        total = row.total
        answered = row.answered or 0
        fallback = total - answered
        fallback_rate = round((fallback / total) * 100, 1) if total > 0 else 0.0

        trend.append({
            "date": row.day.date().isoformat(),
            "total_queries": total,
            "answered": answered,
            "fallback": fallback,
            "fallback_rate_percent": fallback_rate,
        })

    return trend
