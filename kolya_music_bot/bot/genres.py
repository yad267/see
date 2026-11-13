"""Genre catalog for forum topics (v1)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Genre:
    key: str
    title: str
    aliases: tuple[str, ...]


# Inbox is a bucket, not a musical genre — still addressable as a "folder".
GENRES: tuple[Genre, ...] = (
    Genre("inbox", "Inbox", ("inbox", "инбокс", "неразобранное")),
    Genre(
        "hiphop",
        "Hip-Hop",
        ("hiphop", "hip-hop", "hip hop", "rap", "рэп", "хипхоп", "хип-хоп"),
    ),
    Genre(
        "house",
        "House",
        ("house", "deep house", "tech house", "хаус"),
    ),
    Genre(
        "techno",
        "Techno",
        ("techno", "текно", "техно"),
    ),
    Genre(
        "disco",
        "Disco / Funk",
        ("disco", "nu-disco", "funk", "диско", "фанк"),
    ),
    Genre(
        "other",
        "Other",
        ("other", "другое", "misc"),
    ),
)

GENRE_BY_KEY: dict[str, Genre] = {g.key: g for g in GENRES}
SORTABLE_GENRES: tuple[Genre, ...] = tuple(g for g in GENRES if g.key != "inbox")


def resolve_genre(text: str) -> Genre | None:
    """Map free text / button payload to a Genre."""
    needle = " ".join(text.strip().lower().replace("_", " ").split())
    if not needle:
        return None
    for genre in GENRES:
        if needle == genre.key or needle == genre.title.lower():
            return genre
        if needle in genre.aliases:
            return genre
    for genre in GENRES:
        for alias in genre.aliases:
            if alias in needle or needle in alias:
                return genre
    return None
