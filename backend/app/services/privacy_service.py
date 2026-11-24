from sqlalchemy import select, func
from sqlalchemy.orm import Session

from backend.app.models.user import UserPreferences
from backend.app.models.conversation import Conversation
from backend.app.models.message import Message
from backend.app.models.feedback import Feedback
from backend.app.models.device import Device
from backend.app.models.usage import UsageEvent

from backend.app.schemas.privacy import PrivacySummary


def get_privacy_summary(db: Session, user_id):

    preferences = db.scalar(
        select(UserPreferences).where(
            UserPreferences.user_id == user_id
        )
    )

    def count(model):
        return db.scalar(
            select(func.count()).select_from(model).where(
                model.user_id == user_id
            )
        ) or 0

    messages = db.scalar(
        select(func.count())
        .select_from(Message)
        .join(
            Conversation,
            Message.conversation_id == Conversation.id
        )
        .where(Conversation.user_id == user_id)
    ) or 0

    return PrivacySummary(
        conversation_history_enabled=(
            preferences.conversation_history
            if preferences else False
        ),
        analytics_enabled=(
            preferences.analytics_enabled
            if preferences else False
        ),
        total_conversations=count(Conversation),
        total_messages=messages,
        total_feedback=count(Feedback),
        registered_devices=count(Device),
        analytics_events=count(UsageEvent),
    )
