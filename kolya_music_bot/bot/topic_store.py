"""Persist forum topic ids so /setup survives restart."""

from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger("kolya_music.topic_store")

DEFAULT_PATH = Path(__file__).resolve().parents[1] / "data" / "topics.json"


def load_topics(path: Path = DEFAULT_PATH) -> tuple[int, dict[str, int]]:
    if not path.exists():
        return 0, {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("cannot read %s: %s", path, exc)
        return 0, {}
    group_id = int(raw.get("music_group_id") or 0)
    topics = {str(k): int(v) for k, v in (raw.get("topic_ids") or {}).items()}
    return group_id, topics


def save_topics(
    music_group_id: int,
    topic_ids: dict[str, int],
    path: Path = DEFAULT_PATH,
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "music_group_id": music_group_id,
        "topic_ids": topic_ids,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    logger.info("saved topics → %s group=%s", path, music_group_id)
    return path
