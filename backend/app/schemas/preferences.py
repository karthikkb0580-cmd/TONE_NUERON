from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class PreferencesUpdate(BaseModel):
    preferred_language: str | None = Field(
        default=None, min_length=2, max_length=20
    )
    communication_style: Literal[
        "professional", "friendly", "casual",
        "formal", "empathetic", "concise"
    ] | None = None

    theme: Literal["light", "dark", "system"] | None = None
    mascot_enabled: bool | None = None
    notifications_enabled: bool | None = None
    grammar_correction: bool | None = None
    tone_detection: bool | None = None
    reply_suggestions: bool | None = None
    conversation_history: bool | None = None


class PreferencesResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    preferred_language: str = "en"
    communication_style: str = "professional"
    theme: str = "system"
    mascot_enabled: bool = True
    notifications_enabled: bool = True
    grammar_correction: bool = True
    tone_detection: bool = True
    reply_suggestions: bool = True
    conversation_history: bool = False
