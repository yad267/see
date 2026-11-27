"""Runtime config from environment + optional data/topics.json."""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

from bot.genres import GENRE_BY_KEY
from bot.topic_store import load_topics


@dataclass(slots=True)
class Settings:
    """Mutable: /setup can fill music_group_id and topic_ids at runtime."""

    bot_token: str
    music_group_id: int = 0
    topic_ids: dict[str, int] = field(default_factory=dict)
    classify_threshold: float = 0.55
    source_channel_ids: frozenset[int] = field(default_factory=frozenset)


def _optional_int(name: str, default: int | None = None) -> int | None:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    return int(raw)


def load_settings(*, require_token: bool = True) -> Settings:
    load_dotenv()

    token = os.getenv("BOT_TOKEN", "").strip()
    if require_token and not token:
        raise RuntimeError("Missing required env var: BOT_TOKEN")

    group_raw = os.getenv("MUSIC_GROUP_ID", "0").strip() or "0"
    music_group_id = int(group_raw)

    topic_env = {
        "inbox": "TOPIC_INBOX",
        "hiphop": "TOPIC_HIPHOP",
        "house": "TOPIC_HOUSE",
        "techno": "TOPIC_TECHNO",
        "disco": "TOPIC_DISCO",
        "other": "TOPIC_OTHER",
    }
    topic_ids: dict[str, int] = {}
    for key, env_name in topic_env.items():
        if key not in GENRE_BY_KEY:
            continue
        value = _optional_int(env_name)
        if value is not None:
            topic_ids[key] = value

    # File from /setup wins for missing keys / empty group
    stored_group, stored_topics = load_topics()
    if not music_group_id and stored_group:
        music_group_id = stored_group
    for key, tid in stored_topics.items():
        topic_ids.setdefault(key, tid)

    threshold = float(os.getenv("CLASSIFY_THRESHOLD", "0.55"))

    channels_raw = os.getenv("SOURCE_CHANNEL_IDS", "").strip()
    source_ids: set[int] = set()
    if channels_raw:
        for part in channels_raw.split(","):
            part = part.strip()
            if part:
                source_ids.add(int(part))

    return Settings(
        bot_token=token or "test-token",
        music_group_id=music_group_id,
        topic_ids=topic_ids,
        classify_threshold=threshold,
        source_channel_ids=frozenset(source_ids),
    )
