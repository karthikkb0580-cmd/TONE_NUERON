import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database.session import Base


class UsageEvent(Base):
    __tablename__ = "usage_events"

    __table_args__ = (
        Index(
            "ix_usage_user_created",
            "user_id",
            "created_at",
        ),
        CheckConstraint(
            "processing_time_ms >= 0",
            name="ck_usage_processing_time",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    feature: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    language: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    detected_tone: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    successful: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    processing_time_ms: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
