from datetime import datetime, timezone

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.user import User, UserPreferences
from backend.app.models.user_profile import UserProfile
from backend.app.models.conversation import Conversation
from backend.app.models.message import Message
from backend.app.models.feedback import Feedback
from backend.app.models.device import Device
from backend.app.models.usage import UsageEvent


def serialize(instance, fields):

    if instance is None:
        return None

    return jsonable_encoder({
        field: getattr(instance, field)
        for field in fields
    })


def export_user_data(db: Session, user_id):

    user = db.get(User, user_id)

    preferences = db.scalar(
        select(UserPreferences).where(
            UserPreferences.user_id == user_id
        )
    )

    profile = db.get(UserProfile, user_id)

    conversations = db.scalars(
        select(Conversation).where(
            Conversation.user_id == user_id
        )
    ).all()

    messages = db.scalars(
        select(Message)
        .join(
            Conversation,
            Message.conversation_id == Conversation.id
        )
        .where(Conversation.user_id == user_id)
        .order_by(Message.created_at)
    ).all()

    feedback = db.scalars(
        select(Feedback).where(
            Feedback.user_id == user_id
        )
    ).all()

    devices = db.scalars(
        select(Device).where(
            Device.user_id == user_id
        )
    ).all()

    analytics = db.scalars(
        select(UsageEvent).where(
            UsageEvent.user_id == user_id
        )
    ).all()

    return {
        "export_version": "1.0",

        "exported_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "account": serialize(user, [
            "id",
            "email",
            "username",
            "is_verified",
            "is_active",
            "created_at",
        ]),

        "profile": serialize(profile, [
            "display_name",
            "bio",
            "avatar_url",
        ]),

        "preferences": serialize(preferences, [
            "country_code",
            "language_code",
            "neuro_avatar",
            "communication_style",
            "theme",
            "mascot_enabled",
            "notifications_enabled",
            "grammar_correction",
            "tone_detection",
            "reply_suggestions",
            "conversation_history",
            "analytics_enabled",
        ]),

        "conversations": [
            serialize(item, [
                "id",
                "title",
                "created_at",
                "updated_at",
            ])
            for item in conversations
        ],

        "messages": [
            serialize(item, [
                "id",
                "conversation_id",
                "role",
                "content",
                "language",
                "created_at",
            ])
            for item in messages
        ],

        "feedback": [
            serialize(item, [
                "id",
                "message_id",
                "rating",
                "reaction",
                "comment",
                "created_at",
                "updated_at",
            ])
            for item in feedback
        ],

        "devices": [
            serialize(item, [
                "id",
                "installation_id",
                "device_name",
                "operating_system",
                "app_version",
                "mascot_enabled",
                "clipboard_enabled",
                "selected_text_enabled",
                "created_at",
                "last_active_at",
            ])
            for item in devices
        ],

        "analytics": [
            serialize(item, [
                "id",
                "feature",
                "language",
                "detected_tone",
                "successful",
                "processing_time_ms",
                "created_at",
            ])
            for item in analytics
        ],
    }
