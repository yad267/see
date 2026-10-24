"""Map Discogs-400 style labels → short folder whitelist."""

from __future__ import annotations

# Longer / more specific keys first (matched as substring, lowercased).
RULES: list[tuple[str, str]] = [
    ("melodic house", "Melodic"),
    ("melodic techno", "Melodic"),
    ("deep house", "Deep"),
    ("deep techno", "Deep"),
    ("tech house", "Techno"),
    ("minimal techno", "Techno"),
    ("hard techno", "Techno"),
    ("electro house", "House"),
    ("progressive house", "House"),
    ("future house", "House"),
    ("garage house", "House"),
    ("acid house", "House"),
    ("tribal house", "House"),
    ("euro house", "House"),
    ("italo house", "House"),
    ("ghetto house", "House"),
    ("hip house", "House"),
    ("club house", "House"),
    ("nu-disco", "Disco"),
    ("nu disco", "Disco"),
    ("italo-disco", "Disco"),
    ("euro-disco", "Disco"),
    ("drum n bass", "DnB"),
    ("drum and bass", "DnB"),
    ("jungle", "DnB"),
    ("dark trap", "Trap"),
    ("hip hop", "Hip-Hop"),
    ("hip-hop", "Hip-Hop"),
    ("boom bap", "Hip-Hop"),
    ("horrorcore", "Hip-Hop"),
    ("psy-trance", "Trance"),
    ("psy trance", "Trance"),
    ("progressive trance", "Trance"),
    ("hard trance", "Trance"),
    ("tech trance", "Trance"),
    ("goa trance", "Trance"),
    ("dark ambient", "Ambient"),
    ("dub techno", "Techno"),
    ("techno", "Techno"),
    ("house", "House"),
    ("trance", "Trance"),
    ("disco", "Disco"),
    ("funk", "Disco"),
    ("trap", "Trap"),
    ("dubstep", "Bass"),
    ("uk garage", "House"),
    ("ambient", "Ambient"),
    ("downtempo", "Ambient"),
    ("rap", "Hip-Hop"),
    ("phonk", "Trap"),
]


def map_genre(raw_label: str) -> str:
    text = (raw_label or "").strip().lower().replace("_", " ")
    if not text:
        return "Unknown"
    # Discogs labels often look like "Electronic---Deep House"
    text = text.replace("---", " ").replace("/", " ")
    for needle, folder in RULES:
        if needle in text:
            return folder
    return "Other"
