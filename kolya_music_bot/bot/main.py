"""Entry point: python -m bot.main"""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path
from typing import Any, Awaitable, Callable

# Allow `python -m bot.main` from kolya_music_bot/
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aiogram import BaseMiddleware, Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import TelegramObject

from bot.config import Settings, load_settings
from bot.handlers import setup_routers


class SettingsMiddleware(BaseMiddleware):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        data["settings"] = self.settings
        return await handler(event, data)


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        stream=sys.stdout,
    )


async def run() -> None:
    setup_logging()
    settings = load_settings(require_token=True)
    log = logging.getLogger("kolya_music")
    log.info(
        "starting Kolya Music Bot group_id=%s topics=%s sources=%s",
        settings.music_group_id,
        settings.topic_ids,
        list(settings.source_channel_ids),
    )

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.update.middleware(SettingsMiddleware(settings))
    dp.include_router(setup_routers())
    await dp.start_polling(bot)


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
