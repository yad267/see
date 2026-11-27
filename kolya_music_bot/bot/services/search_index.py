"""Separate music searcher: genre / title / year over a personal index."""

from __future__ import annotations

import logging
import re
import uuid
from dataclasses import dataclass, field

from bot.models import IndexedTrack, TrackMeta

logger = logging.getLogger("kolya_music.search")

YEAR_RANGE_RE = re.compile(r"^(?P<a>(?:19|20)\d{2})\s*[-–—]\s*(?P<b>(?:19|20)\d{2})$")
YEAR_RE = re.compile(r"^(?:19|20)\d{2}$")


@dataclass
class SearchQuery:
    text: str = ""
    genre_key: str | None = None
    year: int | None = None
    year_from: int | None = None
    year_to: int | None = None


def parse_search_query(raw: str) -> SearchQuery:
    """
    Parse free text like:
      hiphop
      lose yourself
      2010
      hiphop 2018
      eminem 2002-2005
    """
    from bot.genres import resolve_genre

    tokens = raw.strip().split()
    genre_key = None
    year = None
    year_from = None
    year_to = None
    text_parts: list[str] = []

    for token in tokens:
        lower = token.lower()
        range_match = YEAR_RANGE_RE.match(token)
        if range_match:
            year_from = int(range_match.group("a"))
            year_to = int(range_match.group("b"))
            if year_from > year_to:
                year_from, year_to = year_to, year_from
            continue
        if YEAR_RE.match(token):
            year = int(token)
            continue
        genre = resolve_genre(lower)
        if genre and genre.key != "inbox" and genre_key is None:
            genre_key = genre.key
            continue
        text_parts.append(token)

    return SearchQuery(
        text=" ".join(text_parts).strip(),
        genre_key=genre_key,
        year=year,
        year_from=year_from,
        year_to=year_to,
    )


@dataclass
class TrackIndex:
    """Personal index: uploads + whitelist channel posts (no global TG crawl)."""

    tracks: dict[str, IndexedTrack] = field(default_factory=dict)

    def add(
        self,
        meta: TrackMeta,
        *,
        genre_key: str | None = None,
        topic_key: str | None = None,
        track_id: str | None = None,
    ) -> IndexedTrack:
        tid = track_id or meta.file_unique_id or uuid.uuid4().hex
        item = IndexedTrack(
            track_id=tid,
            meta=meta,
            genre_key=genre_key,
            topic_key=topic_key,
        )
        self.tracks[tid] = item
        logger.info(
            "index add id=%s title=%r artist=%r year=%s genre=%s",
            tid,
            meta.title,
            meta.artist,
            meta.year,
            genre_key,
        )
        return item

    def update_topic(self, track_id: str, topic_key: str, genre_key: str | None = None) -> None:
        item = self.tracks.get(track_id)
        if not item:
            return
        item.topic_key = topic_key
        if genre_key:
            item.genre_key = genre_key

    def search(self, query: SearchQuery, *, limit: int = 10) -> list[IndexedTrack]:
        needle = query.text.lower().strip()
        results: list[IndexedTrack] = []

        for item in self.tracks.values():
            meta = item.meta
            if query.genre_key and (item.genre_key or "") != query.genre_key:
                # Also allow genre_hint on meta
                if (meta.genre_hint or "") != query.genre_key:
                    continue

            if query.year is not None:
                if meta.year != query.year:
                    continue
            if query.year_from is not None or query.year_to is not None:
                if meta.year is None:
                    continue
                lo = query.year_from or 0
                hi = query.year_to or 9999
                if not (lo <= meta.year <= hi):
                    continue

            if needle:
                hay = " ".join(
                    [
                        meta.title,
                        meta.artist,
                        meta.filename,
                    ]
                ).lower()
                if needle not in hay:
                    continue

            results.append(item)
            if len(results) >= limit:
                break

        logger.info(
            "search q=%r genre=%s year=%s hits=%d",
            query.text,
            query.genre_key,
            query.year or f"{query.year_from}-{query.year_to}",
            len(results),
        )
        return results
