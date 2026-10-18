""" /start /genres help """

from __future__ import annotations

import logging

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from bot.genres import GENRES

logger = logging.getLogger("kolya_music.handlers.start")
router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    logger.info("/start from user=%s chat=%s", message.from_user.id if message.from_user else None, message.chat.id)
    text = (
        "Kolya Music Bot — личный архив в закрытой форум-группе.\n\n"
        "• Кинь audio/document в группу → разложу по топику-жанру\n"
        "• Не уверен → Inbox + кнопки\n"
        "• /find — отдельный поисковик (жанр / название / год)\n"
        "• После поиска: авто в папку или выбрать руками\n"
        "• Reply: «переложить в hiphop»\n\n"
        "Группа только по invite-link. Чужие каналы — только твой whitelist."
    )
    await message.answer(text)


@router.message(Command("genres"))
async def cmd_genres(message: Message) -> None:
    lines = ["Папки (топики):"]
    for g in GENRES:
        lines.append(f"• {g.title} — ключ `{g.key}`")
    await message.answer("\n".join(lines))
