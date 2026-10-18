"""Telegram handlers."""

from aiogram import Router

from bot.handlers.override import router as override_router
from bot.handlers.search import router as search_router
from bot.handlers.start import router as start_router
from bot.handlers.upload import router as upload_router


def setup_routers() -> Router:
    root = Router()
    root.include_router(start_router)
    root.include_router(upload_router)
    root.include_router(search_router)
    root.include_router(override_router)
    return root
