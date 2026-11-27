"""Separate searcher: /find then auto or manual folder placement."""

from __future__ import annotations

import logging

from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import CallbackQuery, Message

from bot.config import Settings
from bot.handlers.upload import send_to_topic
from bot.keyboards import genre_pick_keyboard, search_hit_keyboard
from bot.services.classify import classify_or_inbox
from bot.services.mover import plan_move
from bot.services.search_index import parse_search_query
from bot.state import dedup, index, pending_files

logger = logging.getLogger("kolya_music.handlers.search")
router = Router(name="search")


def _format_hit(item) -> str:
    meta = item.meta
    line = f"• {meta.artist + ' — ' if meta.artist else ''}{meta.title}"
    if meta.year:
        line += f" ({meta.year})"
    if item.genre_key:
        line += f" [{item.genre_key}]"
    line += f"\n  id:`{item.track_id[:12]}`"
    return line


@router.message(Command("find"))
async def cmd_find(message: Message, command: CommandObject) -> None:
    """
    /find hiphop
    /find lose yourself
    /find 2010
    /find hiphop 2018
    """
    raw = (command.args or "").strip()
    if not raw:
        await message.answer(
            "Поисковик (отдельно от раскладки):\n"
            "<code>/find hiphop</code>\n"
            "<code>/find lose yourself</code>\n"
            "<code>/find 2010</code>\n"
            "<code>/find eminem 2002-2005</code>\n\n"
            "Потом: авто в папку или выбрать руками.",
        )
        return

    query = parse_search_query(raw)
    hits = index.search(query, limit=8)
    logger.info("/find raw=%r hits=%d", raw, len(hits))

    if not hits:
        await message.answer("Ничего не нашёл в личном индексе. Кинь треки или пополни whitelist.")
        return

    await message.answer(f"Нашёл {len(hits)}:\n\n" + "\n".join(_format_hit(h) for h in hits))
    top = hits[0]
    pending_files[top.track_id[:12]] = {
        "file_id": top.meta.file_id,
        "is_audio": True,
        "meta": top.meta,
        "track_id": top.track_id,
    }
    await message.answer(
        f"Топ-результат: {top.meta.title}\nАвто в жанр или выбрать папку?",
        reply_markup=search_hit_keyboard(top.track_id[:12]),
    )


@router.callback_query(F.data.startswith("searchauto:"))
async def on_search_auto(query: CallbackQuery, bot: Bot, settings: Settings) -> None:
    assert query.data is not None
    track_ref = query.data.split(":", 1)[1]
    pending = pending_files.get(track_ref)
    if not pending or not pending.get("file_id"):
        await query.answer("Нет file_id — только метаданные в индексе", show_alert=True)
        return

    meta = pending["meta"]
    result = classify_or_inbox(meta, threshold=settings.classify_threshold)
    genre_key = result.genre_key if result.genre_key != "inbox" else "inbox"
    plan = plan_move(
        genre_key=genre_key,
        topic_ids=settings.topic_ids,
        mode="auto",
        title=meta.title,
        artist=meta.artist,
        year=meta.year,
        reason="search-auto",
    )

    if settings.music_group_id and plan.topic_id is not None and pending["file_id"]:
        await send_to_topic(
            bot,
            group_id=settings.music_group_id,
            topic_id=plan.topic_id,
            file_id=pending["file_id"],
            is_audio=pending.get("is_audio", True),
            caption=plan.caption,
        )
        dedup.remember(
            file_unique_id=meta.file_unique_id,
            location=plan.genre.title,
            title=meta.title,
            artist=meta.artist,
            year=meta.year,
        )
        if pending.get("track_id"):
            index.update_topic(pending["track_id"], plan.genre.key, plan.genre.key)

    await query.answer(f"→ {plan.genre.title}")
    if query.message:
        await query.message.edit_text(f"Поиск → авто: {plan.genre.title}")


@router.callback_query(F.data.startswith("searchpick:"))
async def on_search_pick(query: CallbackQuery) -> None:
    assert query.data is not None
    track_ref = query.data.split(":", 1)[1]
    if track_ref not in pending_files:
        await query.answer("Сессия устарела", show_alert=True)
        return
    await query.answer()
    if query.message:
        await query.message.edit_text(
            "Выбери папку (топик):",
            reply_markup=genre_pick_keyboard(track_ref, prefix="move"),
        )
