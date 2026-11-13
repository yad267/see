"""Inline keyboards: pick folder after search / uncertain classify."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.genres import SORTABLE_GENRES


def genre_pick_keyboard(track_ref: str, *, prefix: str = "move") -> InlineKeyboardMarkup:
    """
    prefix:
      move  — place uploaded/found track into topic
      confirm — confirm auto suggestion
    callback: {prefix}:{genre_key}:{track_ref}
    """
    rows: list[list[InlineKeyboardButton]] = []
    row: list[InlineKeyboardButton] = []
    for genre in SORTABLE_GENRES:
        row.append(
            InlineKeyboardButton(
                text=genre.title,
                callback_data=f"{prefix}:{genre.key}:{track_ref}"[:64],
            )
        )
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append(
        [
            InlineKeyboardButton(
                text="Inbox",
                callback_data=f"{prefix}:inbox:{track_ref}"[:64],
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def search_hit_keyboard(track_id: str) -> InlineKeyboardMarkup:
    """After search: auto-sort or pick folder manually."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Авто → жанр",
                    callback_data=f"searchauto:{track_id}"[:64],
                ),
                InlineKeyboardButton(
                    text="Выбрать папку",
                    callback_data=f"searchpick:{track_id}"[:64],
                ),
            ]
        ]
    )
