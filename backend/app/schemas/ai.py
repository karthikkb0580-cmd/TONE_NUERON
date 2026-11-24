from typing import Literal

from pydantic import BaseModel, Field, ConfigDict


AIFeature = Literal[
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
]


class AIRequest(BaseModel):

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    text: str = Field(
        min_length=1,
        max_length=20000,
    )

    language: str | None = Field(
        default=None,
        min_length=2,
        max_length=20,
    )

    target_language: str | None = Field(
        default=None,
        min_length=2,
        max_length=20,
    )

    target_tone: Literal[
        "professional",
        "friendly",
        "casual",
        "formal",
        "empathetic",
        "concise",
        "confident",
        "polite",
    ] | None = None

    context: str | None = Field(
        default=None,
        max_length=5000,
    )


class MLRequest(AIRequest):

    feature: AIFeature


class AIResponse(BaseModel):

    model_config = ConfigDict(extra="forbid")

    feature: AIFeature

    output: str | None = Field(
        default=None,
        max_length=40000,
    )

    detected_language: str | None = Field(
        default=None,
        max_length=20,
    )

    detected_tone: str | None = Field(
        default=None,
        max_length=50,
    )

    sentiment: str | None = Field(
        default=None,
        max_length=50,
    )

    emotion: str | None = Field(
        default=None,
        max_length=50,
    )

    confidence: float | None = Field(
        default=None,
        ge=0,
        le=1,
    )

    toxicity_score: float | None = Field(
        default=None,
        ge=0,
        le=1,
    )

    suggestions: list[str] = Field(
        default_factory=list,
        max_length=20,
    )

    model_name: str = Field(
        min_length=1,
        max_length=100,
    )

    processing_time_ms: int = Field(
        default=0,
        ge=0,
    )
