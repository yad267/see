"""Hard artist → folder overrides (beats weak audio/DB guesses)."""

from __future__ import annotations

# lowercase artist substring → folder
ARTIST_OVERRIDES: list[tuple[str, str]] = [
    ("monolink", "Melodic"),
    ("tale of us", "Melodic"),
    ("anyma", "Melodic"),
    ("afterlife", "Melodic"),
    ("dom dolla", "House"),
    ("fisher", "House"),
    ("chris lake", "House"),
    ("john summit", "House"),
    ("james hype", "House"),
]


def override_for_artist(artist: str) -> str | None:
    a = (artist or "").strip().lower()
    if not a:
        return None
    for needle, folder in ARTIST_OVERRIDES:
        if needle in a:
            return folder
    return None
