"""Shared domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(slots=True)
class TrackMeta:
    title: str
    artist: str = ""
    year: int | None = None
    filename: str = ""
    file_unique_id: str = ""
    file_id: str = ""
    source: str = "upload"  # upload | tg_channel | open
    source_chat_id: int | None = None
    genre_hint: str | None = None


@dataclass(slots=True)
class ClassifyResult:
    genre_key: str
    confidence: float
    reason: str


@dataclass(slots=True)
class IndexedTrack:
    track_id: str
    meta: TrackMeta
    genre_key: str | None = None
    topic_key: str | None = None
    indexed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
