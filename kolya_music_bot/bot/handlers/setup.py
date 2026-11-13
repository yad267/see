""" /setup — create genre topics in the invite-only forum group."""

from __future__ import annotations

import logging

from aiogram import Bot, Router
from aiogram.enums import ChatMemberStatus, ChatType
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import Message

from bot.config import Settings
from bot.genres import GENRES
from bot.topic_store import save_topics

logger = logging.getLogger("kolya_music.handlers.setup")
router = Router(name="setup")

# Visual markers for forum topic list (optional icons via emoji)
TOPIC_EMOJI = {
    "inbox": "📥",
    "hiphop": "🎤",
    "house": "🏠",
    "techno": "⚙️",
    "disco": "🕺",
    "other": "🎵",
}


async def _is_group_admin(bot: Bot, chat_id: int, user_id: int) -> bool:
    member = await bot.get_chat_member(chat_id, user_id)
    return member.status in {
        ChatMemberStatus.CREATOR,
        ChatMemberStatus.ADMINISTRATOR,
    }


@router.message(Command("setup"))
async def cmd_setup(message: Message, bot: Bot, settings: Settings) -> None:
    """
    Run inside the closed forum group after the bot is admin.

    Creates missing genre topics and saves ids to data/topics.json.
    """
    chat = message.chat
    if chat.type not in {ChatType.GROUP, ChatType.SUPERGROUP}:
        await message.answer(
            "Команду /setup нужно отправить <b>внутри закрытой форум-группы</b>, "
            "не в личке.\n\n"
            "1) Создай private-группу с Topics\n"
            "2) Добавь бота админом\n"
            "3) Напиши в группе: /setup"
        )
        return

    if not message.from_user:
        return

    if not await _is_group_admin(bot, chat.id, message.from_user.id):
        await message.answer("Только админ группы может запускать /setup.")
        return

    # Ensure we know forum mode; if topics disabled, Telegram will error on create.
    try:
        full = await bot.get_chat(chat.id)
        is_forum = bool(getattr(full, "is_forum", False))
    except TelegramBadRequest:
        is_forum = False

    if not is_forum:
        await message.answer(
            "В этой группе не включены Topics (темы).\n"
            "Настройки группы → Topics → On, потом снова /setup."
        )
        return

    created: list[str] = []
    reused: list[str] = []
    errors: list[str] = []

    # Reuse already known topic ids; create the rest
    for genre in GENRES:
        if genre.key in settings.topic_ids:
            reused.append(f"{TOPIC_EMOJI.get(genre.key, '')} {genre.title} → {settings.topic_ids[genre.key]}")
            continue
        name = f"{TOPIC_EMOJI.get(genre.key, '')} {genre.title}".strip()
        try:
            topic = await bot.create_forum_topic(chat_id=chat.id, name=name)
            settings.topic_ids[genre.key] = topic.message_thread_id
            created.append(f"{name} → {topic.message_thread_id}")
            logger.info("created topic %s thread=%s", genre.key, topic.message_thread_id)
        except TelegramBadRequest as exc:
            errors.append(f"{genre.title}: {exc.message}")
            logger.exception("create topic failed key=%s", genre.key)

    settings.music_group_id = chat.id
    path = save_topics(settings.music_group_id, dict(settings.topic_ids))

    lines = [
        "✅ Setup группы",
        f"group id: <code>{chat.id}</code>",
        f"сохранено: <code>{path}</code>",
        "",
    ]
    if created:
        lines.append("<b>Созданы топики:</b>")
        lines.extend(f"• {x}" for x in created)
        lines.append("")
    if reused:
        lines.append("<b>Уже были в конфиге:</b>")
        lines.extend(f"• {x}" for x in reused)
        lines.append("")
    if errors:
        lines.append("<b>Ошибки:</b>")
        lines.extend(f"• {x}" for x in errors)
        lines.append("")
        lines.append(
            "Если ошибка про права — дай боту право "
            "<i>Manage Topics</i> / управление темами."
        )
    else:
        lines.append("Дальше можно кидать треки. Старт теста: Hip-Hop.")

    await message.answer("\n".join(lines))
