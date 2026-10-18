"""Unit tests for classifier + searcher (no Telegram token needed)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bot.genres import resolve_genre
from bot.models import TrackMeta
from bot.services.classify import classify_or_inbox
from bot.services.dedup import DedupStore
from bot.services.metadata import meta_from_telegram
from bot.services.mover import plan_move
from bot.services.search_index import TrackIndex, parse_search_query


def test_resolve_hiphop():
    g = resolve_genre("хип-хоп")
    assert g is not None and g.key == "hiphop"


def test_classify_hiphop_filename():
    meta = meta_from_telegram(
        file_name="Nas - N.Y. State of Mind (hip-hop 1994).mp3",
        file_unique_id="u1",
    )
    assert meta.year == 1994
    result = classify_or_inbox(meta)
    assert result.genre_key == "hiphop"
    assert result.confidence >= 0.55


def test_classify_uncertain_goes_inbox():
    meta = TrackMeta(title="Ambient Drift", filename="Ambient Drift.flac")
    result = classify_or_inbox(meta)
    assert result.genre_key == "inbox"


def test_parse_search_genre_year_and_title():
    q = parse_search_query("hiphop eminem 2002-2005")
    assert q.genre_key == "hiphop"
    assert q.text.lower() == "eminem"
    assert q.year_from == 2002 and q.year_to == 2005


def test_index_search_by_genre_title_year():
    idx = TrackIndex()
    a = TrackMeta(title="Lose Yourself", artist="Eminem", year=2002, file_unique_id="a")
    b = TrackMeta(title="One More Time", artist="Daft Punk", year=2000, file_unique_id="b")
    idx.add(a, genre_key="hiphop", topic_key="hiphop")
    idx.add(b, genre_key="house", topic_key="house")

    hits = idx.search(parse_search_query("hiphop"))
    assert len(hits) == 1 and hits[0].meta.title == "Lose Yourself"

    hits = idx.search(parse_search_query("lose yourself"))
    assert len(hits) == 1

    hits = idx.search(parse_search_query("2002"))
    assert len(hits) == 1 and hits[0].meta.artist == "Eminem"


def test_dedup_and_move_plan():
    store = DedupStore()
    assert store.seen(file_unique_id="x") is None
    store.remember(file_unique_id="x", location="Hip-Hop", title="T", artist="A", year=2001)
    assert store.seen(file_unique_id="x") == "Hip-Hop"

    plan = plan_move(
        genre_key="hiphop",
        topic_ids={"hiphop": 42},
        mode="manual",
        title="T",
        artist="A",
        year=2001,
    )
    assert plan.topic_id == 42
    assert plan.genre.key == "hiphop"
