"""Extract title / artist / year from Telegram payload + optional ID3."""

from __future__ import annotations

import re
from pathlib import Path

from bot.models import TrackMeta

YEAR_RE = re.compile(r"(?:(?:19|20)\d{2})")
PARENS_YEAR_RE = re.compile(r"[\(\[\{]\s*((?:19|20)\d{2})\s*[\)\]\}]")


def _year_from_text(text: str) -> int | None:
    if not text:
        return None
    m = PARENS_YEAR_RE.search(text)
    if m:
        return int(m.group(1))
    years = YEAR_RE.findall(text)
    if not years:
        return None
    # Prefer the last year-looking token (common in filenames).
    return int(years[-1])


def _split_artist_title(stem: str) -> tuple[str, str]:
    for sep in (" - ", " — ", " – "):
        if sep in stem:
            left, right = stem.split(sep, 1)
            return left.strip(), right.strip()
    return "", stem.strip()


def meta_from_telegram(
    *,
    file_name: str | None,
    title: str | None = None,
    performer: str | None = None,
    file_id: str = "",
    file_unique_id: str = "",
    source: str = "upload",
    source_chat_id: int | None = None,
) -> TrackMeta:
    filename = file_name or ""
    stem = Path(filename).stem if filename else ""
    artist = (performer or "").strip()
    track_title = (title or "").strip()

    if not track_title and stem:
        parsed_artist, parsed_title = _split_artist_title(stem)
        track_title = parsed_title or stem
        if not artist:
            artist = parsed_artist
    if not track_title:
        track_title = "unknown"

    year = _year_from_text(f"{track_title} {artist} {stem}")
    return TrackMeta(
        title=track_title,
        artist=artist,
        year=year,
        filename=filename,
        file_unique_id=file_unique_id,
        file_id=file_id,
        source=source,
        source_chat_id=source_chat_id,
    )


def enrich_from_id3(meta: TrackMeta, file_path: str | Path) -> TrackMeta:
    """Best-effort ID3 read; safe if mutagen missing or file unreadable."""
    try:
        from mutagen import File as MutagenFile
    except ImportError:
        return meta

    audio = MutagenFile(file_path, easy=True)
    if not audio or not getattr(audio, "tags", None):
        return meta

    tags = audio.tags
    title = (tags.get("title") or [None])[0]
    artist = (tags.get("artist") or [None])[0]
    date = (tags.get("date") or tags.get("year") or [None])[0]

    if title and meta.title in {"", "unknown"}:
        meta.title = str(title)
    if artist and not meta.artist:
        meta.artist = str(artist)
    if date and meta.year is None:
        meta.year = _year_from_text(str(date))
    return meta
