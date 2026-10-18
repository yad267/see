"""Process-wide stores (v1: memory; later sqlite)."""

from __future__ import annotations

from bot.services.dedup import DedupStore
from bot.services.search_index import TrackIndex

dedup = DedupStore()
index = TrackIndex()

# Temporary map short ref → pending file payload for callbacks
pending_files: dict[str, dict] = {}
