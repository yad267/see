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
        "<b>Один раз настроить:</b>\n"
        "1) Создай private-группу, включи Topics\n"
        "2) Добавь бота админом (с правом Manage Topics)\n"
        "3) В группе напиши /setup — бот сам создаст папки-жанры\n\n"
        "• Кинь audio/document → разложу по топику\n"
        "• /find — поиск (жанр / название / год)\n"
        "• Reply: «переложить в hiphop»\n\n"
        "Группа только по invite-link."
    )
    await message.answer(text)


@router.message(Command("genres"))
async def cmd_genres(message: Message) -> None:
    lines = ["Папки (топики):"]
    for g in GENRES:
        lines.append(f"• {g.title} — ключ `{g.key}`")
    await message.answer("\n".join(lines))
