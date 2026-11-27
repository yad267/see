"""Whitelist-only Telegram channel indexer (stub for next iteration).

Bot may index audio only from SOURCE_CHANNEL_IDS — personal / invite sources.
No global crawl of Telegram music channels.
"""

from __future__ import annotations

import logging

from bot.models import TrackMeta
from bot.services.metadata import meta_from_telegram
from bot.services.search_index import TrackIndex

logger = logging.getLogger("kolya_music.channel_index")


def is_allowed_source(chat_id: int, allowed: frozenset[int]) -> bool:
    if not allowed:
        return False
    return chat_id in allowed


def index_channel_audio(
    index: TrackIndex,
    *,
    chat_id: int,
    allowed: frozenset[int],
    file_name: str | None,
    title: str | None,
    performer: str | None,
    file_id: str,
    file_unique_id: str,
    genre_hint: str | None = None,
) -> TrackMeta | None:
    if not is_allowed_source(chat_id, allowed):
        logger.info("skip channel %s — not in whitelist", chat_id)
        return None

    meta = meta_from_telegram(
        file_name=file_name,
        title=title,
        performer=performer,
        file_id=file_id,
        file_unique_id=file_unique_id,
        source="tg_channel",
        source_chat_id=chat_id,
    )
    meta.genre_hint = genre_hint
    index.add(meta, genre_key=genre_hint)
    return meta
