"""Lightweight genre classifier (filename / title keywords). LLM hook later."""

from __future__ import annotations

import re

from bot.genres import SORTABLE_GENRES
from bot.models import ClassifyResult, TrackMeta

# keyword → genre_key (longer / more specific first via sorting by length)
KEYWORD_MAP: tuple[tuple[str, str], ...] = tuple(
    sorted(
        (
            ("hip-hop", "hiphop"),
            ("hip hop", "hiphop"),
            ("hiphop", "hiphop"),
            ("trap", "hiphop"),
            ("rap", "hiphop"),
            ("рэп", "hiphop"),
            ("хип-хоп", "hiphop"),
            ("хипхоп", "hiphop"),
            ("deep house", "house"),
            ("tech house", "house"),
            ("house", "house"),
            ("хаус", "house"),
            ("techno", "techno"),
            ("текно", "techno"),
            ("техно", "techno"),
            ("nu-disco", "disco"),
            ("disco", "disco"),
            ("funk", "disco"),
            ("диско", "disco"),
            ("фанк", "disco"),
        ),
        key=lambda item: len(item[0]),
        reverse=True,
    )
)


def _blob(meta: TrackMeta) -> str:
    parts = [meta.title, meta.artist, meta.filename, meta.genre_hint or ""]
    return " ".join(p for p in parts if p).lower()


def classify_track(meta: TrackMeta, *, threshold: float = 0.55) -> ClassifyResult:
    text = _blob(meta)
    if not text.strip():
        return ClassifyResult("inbox", 0.0, "empty metadata")

    for keyword, genre_key in KEYWORD_MAP:
        if re.search(rf"(?<!\w){re.escape(keyword)}(?!\w)", text) or keyword in text:
            # Strong hit if keyword sits in title/filename explicitly.
            confidence = 0.9 if keyword in f"{meta.title} {meta.filename}".lower() else 0.7
            if confidence < threshold:
                return ClassifyResult("inbox", confidence, f"low confidence for {genre_key}")
            return ClassifyResult(genre_key, confidence, f"keyword:{keyword}")

    # No keyword → Inbox for human decision (not silent Other).
    return ClassifyResult("inbox", 0.2, "no genre keywords")


def classify_or_inbox(meta: TrackMeta, *, threshold: float = 0.55) -> ClassifyResult:
    result = classify_track(meta, threshold=threshold)
    if result.confidence < threshold and result.genre_key != "inbox":
        return ClassifyResult("inbox", result.confidence, result.reason + "; below threshold")
    return result


def known_sortable_keys() -> tuple[str, ...]:
    return tuple(g.key for g in SORTABLE_GENRES)
