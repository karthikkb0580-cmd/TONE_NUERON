from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import Date, cast, delete, func, select
from sqlalchemy.orm import Session

from backend.app.models.usage import UsageEvent
from backend.app.models.user import User, UserPreferences


ALLOWED_FEATURES = {
    "analyze",
    "tone",
    "sentiment",
    "emotion",
    "rewrite",
    "grammar",
    "translate",
    "suggest_reply",
    "summarize",
    "expand",
    "coach",
    "toxicity",
}


def record_usage(
    db: Session,
    user_id: UUID,
    feature: str,
    language: str | None = None,
    detected_tone: str | None = None,
    successful: bool = True,
    processing_time_ms: int = 0,
):
    if feature not in ALLOWED_FEATURES:
        raise ValueError("Unsupported analytics feature.")

    if processing_time_ms < 0:
        raise ValueError("Invalid processing time.")

    db.execute(
        select(User.id)
        .where(User.id == user_id)
        .with_for_update()
    )

    preferences = db.scalar(
        select(UserPreferences)
        .where(UserPreferences.user_id == user_id)
        .execution_options(populate_existing=True)
    )

    if preferences is None or not preferences.analytics_enabled:
        return None

    event = UsageEvent(
        user_id=user_id,
        feature=feature,
        language=language,
        detected_tone=detected_tone,
        successful=successful,
        processing_time_ms=processing_time_ms,
    )

    db.add(event)
    db.flush()

    return event


def get_summary(
    db: Session,
    user_id: UUID,
    days: int,
):
    today = datetime.now(timezone.utc).date()

    first_day = today - timedelta(days=days - 1)

    start = datetime.combine(
        first_day,
        datetime.min.time(),
        tzinfo=timezone.utc,
    )

    conditions = (
        UsageEvent.user_id == user_id,
        UsageEvent.created_at >= start,
    )

    total = db.scalar(
        select(func.count())
        .select_from(UsageEvent)
        .where(*conditions)
    ) or 0

    successful = db.scalar(
        select(func.count())
        .select_from(UsageEvent)
        .where(
            *conditions,
            UsageEvent.successful.is_(True),
        )
    ) or 0

    average_time = db.scalar(
        select(func.avg(UsageEvent.processing_time_ms))
        .where(*conditions)
    ) or 0

    def distribution(column):
        rows = db.execute(
            select(
                column,
                func.count().label("count"),
            )
            .where(
                *conditions,
                column.is_not(None),
            )
            .group_by(column)
            .order_by(func.count().desc(), column)
        ).all()

        return [
            {"name": name, "count": count}
            for name, count in rows
        ]

    day_column = cast(
        func.timezone("UTC", UsageEvent.created_at),
        Date,
    )

    daily_rows = db.execute(
        select(day_column, func.count())
        .where(*conditions)
        .group_by(day_column)
        .order_by(day_column)
    ).all()

    daily_counts = dict(daily_rows)

    daily_usage = [
        {
            "date": (first_day + timedelta(days=i)).isoformat(),
            "count": daily_counts.get(
                first_day + timedelta(days=i),
                0,
            ),
        }
        for i in range(days)
    ]

    return {
        "period_days": days,
        "total_requests": total,
        "successful_requests": successful,
        "failed_requests": total - successful,
        "success_rate": round(
            successful / total * 100, 2
        ) if total else 0.0,
        "average_processing_time_ms": round(
            float(average_time), 2
        ),
        "features": distribution(UsageEvent.feature),
        "languages": distribution(UsageEvent.language),
        "tones": distribution(UsageEvent.detected_tone),
        "daily_usage": daily_usage,
    }


def clear_analytics(
    db: Session,
    user_id: UUID,
):
    db.execute(
        select(User.id)
        .where(User.id == user_id)
        .with_for_update()
    )

    db.execute(
        delete(UsageEvent).where(
            UsageEvent.user_id == user_id
        )
    )

    db.commit()
