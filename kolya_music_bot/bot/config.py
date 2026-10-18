"""Runtime config from environment."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

from bot.genres import GENRE_BY_KEY


@dataclass(frozen=True, slots=True)
class Settings:
    bot_token: str
    music_group_id: int
    topic_ids: dict[str, int]
    classify_threshold: float
    source_channel_ids: frozenset[int]


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
