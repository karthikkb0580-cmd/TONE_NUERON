from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class FeedbackCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    message_id: UUID

    rating: int | None = Field(
        default=None,
        ge=1,
        le=5,
    )

    reaction: Literal["like", "dislike"] | None = None

    comment: str | None = Field(
        default=None,
        max_length=2000,
    )

    @model_validator(mode="after")
    def validate_feedback(self):
        if (
            self.rating is None
            and self.reaction is None
            and not self.comment
        ):
            raise ValueError("Feedback cannot be empty.")

        return self


class FeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    message_id: UUID
    rating: int | None
    reaction: str | None
    comment: str | None
    created_at: datetime
    updated_at: datetime
