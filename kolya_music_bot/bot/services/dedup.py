"""In-memory dedup by Telegram file_unique_id (+ soft filename key)."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

logger = logging.getLogger("kolya_music.dedup")


@dataclass
class DedupStore:
    by_unique_id: dict[str, str] = field(default_factory=dict)
    by_soft_key: dict[str, str] = field(default_factory=dict)

    @staticmethod
    def soft_key(title: str, artist: str, year: int | None) -> str:
        return "|".join(
            [
                (artist or "").strip().lower(),
                (title or "").strip().lower(),
                str(year or ""),
            ]
        )

    def seen(
        self,
        *,
        file_unique_id: str,
        title: str = "",
        artist: str = "",
        year: int | None = None,
    ) -> str | None:
        """Return existing location label if duplicate, else None."""
        if file_unique_id and file_unique_id in self.by_unique_id:
            return self.by_unique_id[file_unique_id]
        key = self.soft_key(title, artist, year)
        if key != "||" and key in self.by_soft_key:
            return self.by_soft_key[key]
        return None

    def remember(
        self,
        *,
        file_unique_id: str,
        location: str,
        title: str = "",
        artist: str = "",
        year: int | None = None,
    ) -> None:
        if file_unique_id:
            self.by_unique_id[file_unique_id] = location
        key = self.soft_key(title, artist, year)
        if key != "||":
            self.by_soft_key[key] = location
        logger.info("dedup remember unique=%s location=%s", file_unique_id or "-", location)
