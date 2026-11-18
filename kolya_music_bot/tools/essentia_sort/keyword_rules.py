"""Filename / title regex-ish keyword → genre (for rare remixes not in DBs)."""

from __future__ import annotations

import re

# Longer groups first conceptually; we scan in order.
KEYWORD_RULES: list[tuple[list[str], str]] = [
    (
        ["melodic house", "melodic techno", "melodic"],
        "Melodic",
    ),
    (
        ["deep house", "deep techno", "deep"],
        "Deep",
    ),
    (
        ["tech house", "minimal techno", "hard techno", "techno"],
        "Techno",
    ),
    (
        ["remix", "club mix", "club", "vocal mix", "radio mix", "extended mix", "mix"],
        "House",  # user asked House/Remix bucket → whitelist folder House
    ),
    (
        ["bassline", "uk garage", "speed garage", "fidget", "house"],
        "House",
    ),
    (
        ["hip hop", "hip-hop", "hiphop", "rap", "prod by", "prod.", "trap"],
        "Hip-Hop",
    ),
    (
        ["drum and bass", "drum & bass", "dnb", "d&b", "jungle"],
        "DnB",
    ),
    (
        ["trance", "psytrance", "psy-trance"],
        "Trance",
    ),
    (
        ["disco", "nu-disco", "funk"],
        "Disco",
    ),
    (
        ["ambient", "downtempo"],
        "Ambient",
    ),
]


def genre_from_text(*parts: str) -> str | None:
    blob = " ".join(p for p in parts if p).lower()
    blob = re.sub(r"[_\-\[\]\(\)]+", " ", blob)
    if not blob.strip():
        return None
    for keywords, folder in KEYWORD_RULES:
        for kw in keywords:
            if kw in blob:
                return folder
    return None
