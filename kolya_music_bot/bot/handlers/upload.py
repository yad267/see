"""Accept audio/document → classify → move (or Inbox + ask)."""

from __future__ import annotations

import logging
import uuid

from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery, Message

from bot.config import Settings
from bot.keyboards import genre_pick_keyboard
from bot.services.classify import classify_or_inbox
from bot.services.metadata import meta_from_telegram
from bot.services.mover import plan_move
from bot.state import dedup, index, pending_files

logger = logging.getLogger("kolya_music.handlers.upload")
router = Router(name="upload")


async def send_to_topic(
    bot: Bot,
    *,
    group_id: int,
    topic_id: int | None,
    file_id: str,
    is_audio: bool,
    caption: str,
) -> None:
    kwargs: dict = {"chat_id": group_id, "caption": caption}
    if topic_id is not None:
        kwargs["message_thread_id"] = topic_id
    if is_audio:
        await bot.send_audio(audio=file_id, **kwargs)
    else:
        await bot.send_document(document=file_id, **kwargs)


@router.message(F.audio | F.document)
async def on_media(message: Message, bot: Bot, settings: Settings) -> None:
    audio = message.audio
    document = message.document

    if audio:
        file_name = audio.file_name or f"{audio.title or 'track'}.mp3"
        meta = meta_from_telegram(
            file_name=file_name,
            title=audio.title,
            performer=audio.performer,
            file_id=audio.file_id,
            file_unique_id=audio.file_unique_id,
            source="upload",
            source_chat_id=message.chat.id,
        )
        is_audio = True
        file_id = audio.file_id
    else:
        assert document is not None
        name = (document.file_name or "").lower()
        mime = (document.mime_type or "").lower()
        if not (
            name.endswith((".mp3", ".m4a", ".flac", ".wav", ".ogg", ".aac"))
            or mime.startswith("audio/")
        ):
            return
        meta = meta_from_telegram(
            file_name=document.file_name,
            file_id=document.file_id,
            file_unique_id=document.file_unique_id,
            source="upload",
            source_chat_id=message.chat.id,
        )
        is_audio = False
        file_id = document.file_id

    existing = dedup.seen(
        file_unique_id=meta.file_unique_id,
        title=meta.title,
        artist=meta.artist,
        year=meta.year,
    )
    if existing:
        logger.info("duplicate skipped → %s", existing)
        await message.reply(f"Уже есть: {existing}")
        return

    result = classify_or_inbox(meta, threshold=settings.classify_threshold)
    logger.info(
        "classify title=%r → %s (%.2f) %s",
        meta.title,
        result.genre_key,
        result.confidence,
        result.reason,
    )

    track_ref = uuid.uuid4().hex[:12]
    pending_files[track_ref] = {
        "file_id": file_id,
        "is_audio": is_audio,
        "meta": meta,
    }
    indexed = index.add(meta, genre_key=result.genre_key if result.genre_key != "inbox" else None)
    pending_files[track_ref]["track_id"] = indexed.track_id

    if result.genre_key == "inbox" or result.confidence < settings.classify_threshold:
        await message.reply(
            f"Не уверен ({result.reason}). Куда положить?\n"
            f"{meta.artist + ' — ' if meta.artist else ''}{meta.title}"
            + (f" ({meta.year})" if meta.year else ""),
            reply_markup=genre_pick_keyboard(track_ref, prefix="move"),
        )
        plan = plan_move(
            genre_key="inbox",
            topic_ids=settings.topic_ids,
            mode="auto",
            title=meta.title,
            artist=meta.artist,
            year=meta.year,
            reason="needs review",
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
                location="Inbox",
                title=meta.title,
                artist=meta.artist,
                year=meta.year,
            )
        return

    plan = plan_move(
        genre_key=result.genre_key,
        topic_ids=settings.topic_ids,
        mode="auto",
        title=meta.title,
        artist=meta.artist,
        year=meta.year,
        reason=f"{result.confidence:.2f}",
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
        index.update_topic(indexed.track_id, plan.genre.key, plan.genre.key)
        await message.reply(
            f"→ {plan.genre.title} ({result.confidence:.2f})\nМожно переложить кнопкой:",
            reply_markup=genre_pick_keyboard(track_ref, prefix="move"),
        )
    else:
        await message.reply(
            f"Класс: {plan.genre.title} ({result.confidence:.2f}), "
            "но MUSIC_GROUP_ID / TOPIC_* ещё не заданы. Выбери папку:",
            reply_markup=genre_pick_keyboard(track_ref, prefix="move"),
        )


@router.callback_query(F.data.startswith("move:"))
async def on_move_callback(query: CallbackQuery, bot: Bot, settings: Settings) -> None:
    assert query.data is not None
    _, genre_key, track_ref = query.data.split(":", 2)
    pending = pending_files.get(track_ref)
    if not pending:
        await query.answer("Сессия устарела — кинь трек ещё раз", show_alert=True)
        return

    meta = pending["meta"]
    plan = plan_move(
        genre_key=genre_key,
        topic_ids=settings.topic_ids,
        mode="manual",
        title=meta.title,
        artist=meta.artist,
        year=meta.year,
        reason="manual",
    )
    if settings.music_group_id and plan.topic_id is not None:
        await send_to_topic(
            bot,
            group_id=settings.music_group_id,
            topic_id=plan.topic_id,
            file_id=pending["file_id"],
            is_audio=pending["is_audio"],
            caption=plan.caption,
        )
    dedup.remember(
        file_unique_id=meta.file_unique_id,
        location=plan.genre.title,
        title=meta.title,
        artist=meta.artist,
        year=meta.year,
    )
    track_id = pending.get("track_id")
    if track_id:
        index.update_topic(track_id, plan.genre.key, plan.genre.key)

    logger.info("manual move → %s title=%r", plan.genre.key, meta.title)
    await query.answer(f"В {plan.genre.title}")
    if query.message:
        await query.message.edit_text(f"Переложено → {plan.genre.title}")
