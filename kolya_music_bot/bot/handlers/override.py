"""Manual override: reply «переложить в hiphop»."""

from __future__ import annotations

import logging
import re

from aiogram import Bot, F, Router
from aiogram.types import Message

from bot.config import Settings
from bot.genres import resolve_genre
from bot.handlers.upload import send_to_topic
from bot.services.metadata import meta_from_telegram
from bot.services.mover import plan_move
from bot.state import dedup, index

logger = logging.getLogger("kolya_music.handlers.override")
router = Router(name="override")

MOVE_RE = re.compile(
    r"^(?:переложить|положить|move)\s+(?:в|to)\s+(.+)$",
    re.IGNORECASE,
)


@router.message(F.reply_to_message, F.text)
async def on_text_override(message: Message, bot: Bot, settings: Settings) -> None:
    assert message.text is not None
    match = MOVE_RE.match(message.text.strip())
    if not match:
        return

    genre = resolve_genre(match.group(1))
    if not genre:
        await message.reply("Не знаю такую папку. /genres")
        return

    replied = message.reply_to_message
    assert replied is not None

    audio = replied.audio
    document = replied.document
    if not audio and not document:
        await message.reply("Reply должен быть на audio/document.")
        return

    if audio:
        meta = meta_from_telegram(
            file_name=audio.file_name,
            title=audio.title,
            performer=audio.performer,
            file_id=audio.file_id,
            file_unique_id=audio.file_unique_id,
        )
        file_id = audio.file_id
        is_audio = True
    else:
        assert document is not None
        meta = meta_from_telegram(
            file_name=document.file_name,
            file_id=document.file_id,
            file_unique_id=document.file_unique_id,
        )
        file_id = document.file_id
        is_audio = False

    plan = plan_move(
        genre_key=genre.key,
        topic_ids=settings.topic_ids,
        mode="manual",
        title=meta.title,
        artist=meta.artist,
        year=meta.year,
        reason="override",
    )

    if settings.music_group_id and plan.topic_id is not None:
        await send_to_topic(
            bot,
            group_id=settings.music_group_id,
            topic_id=plan.topic_id,
            file_id=file_id,
            is_audio=is_audio,
            caption=plan.caption,
        )

    dedup.remember(
        file_unique_id=meta.file_unique_id,
        location=plan.genre.title,
        title=meta.title,
        artist=meta.artist,
        year=meta.year,
    )
    index.add(meta, genre_key=genre.key, topic_key=genre.key)
    logger.info("override → %s title=%r", genre.key, meta.title)
    await message.reply(f"Переложено → {plan.genre.title}")
