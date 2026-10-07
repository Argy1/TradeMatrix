"""The shape of one scored headline (docs/03), used twice: as the JSON schema sent to Gemini
and as the check on what comes back. The schema steers the model; the check is what we trust.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

MAX_REASON_CHARS = 140

EventType = Literal[
    "regulation", "hack", "listing", "etf", "macro", "partnership", "technical", "market", "other"
]  # fmt: skip


@dataclass(frozen=True, slots=True)
class ToScore:
    """What is sent for one headline: id, title, source and time. Never any user data."""

    id: int
    source: str
    title: str
    published_at: datetime


class HeadlineSentiment(BaseModel):
    id: int
    assets: list[str]
    score: float = Field(ge=-1, le=1)  # -1 very bearish for price ... +1 very bullish
    confidence: float = Field(ge=0, le=1)  # how clear the price impact is
    event_type: EventType
    reason: str

    @field_validator("reason")
    @classmethod
    def short_plain_reason(cls, value: str) -> str:
        # A reason that runs long is cut, not rejected: the score is still usable.
        return " ".join(value.split())[:MAX_REASON_CHARS]


class SentimentBatch(BaseModel):
    items: list[HeadlineSentiment]


def response_schema(symbols: Sequence[str]) -> dict:
    """JSON schema for the reply, with `assets` limited to the coins we support right now."""
    schema = SentimentBatch.model_json_schema()
    item = schema["$defs"]["HeadlineSentiment"]["properties"]
    item["assets"]["items"] = {"type": "string", "enum": list(symbols)}
    item["reason"]["maxLength"] = MAX_REASON_CHARS
    return schema
