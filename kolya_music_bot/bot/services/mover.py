"""Place a found/uploaded track into a forum topic ('folder')."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from bot.genres import GENRE_BY_KEY, Genre

logger = logging.getLogger("kolya_music.mover")


@dataclass(frozen=True, slots=True)
class MovePlan:
    genre: Genre
    topic_id: int | None
    mode: str  # auto | manual
    caption: str


def plan_move(
    *,
    genre_key: str,
    topic_ids: dict[str, int],
    mode: str,
    title: str,
    artist: str = "",
    year: int | None = None,
    reason: str = "",
) -> MovePlan:
    genre = GENRE_BY_KEY.get(genre_key) or GENRE_BY_KEY["inbox"]
    topic_id = topic_ids.get(genre.key)
    bits = [genre.title]
    if artist:
        bits.append(artist)
    bits.append(title)
    if year:
        bits.append(str(year))
    if reason:
        bits.append(f"({reason})")
    caption = " · ".join(bits)
    logger.info(
        "move plan mode=%s genre=%s topic_id=%s title=%r",
        mode,
        genre.key,
        topic_id,
        title,
    )
    return MovePlan(genre=genre, topic_id=topic_id, mode=mode, caption=caption)
