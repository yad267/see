#!/usr/bin/env python3
"""
Multi-fallback music sorter for rare remixes / bootlegs not in official DBs.

Order:
  1) MusicBrainz (identity + tags) — often empty for rare edits
  2) Essentia audio genre (optional, if models present)
  3) Regex/keywords on filename + ID3 (+ artist overrides)
  4) else → _To_Review

Default: COPY (safe). Writes report.txt + CSV.

Example:
  python fallback_sort.py \\
    --src "/Users/Sputnik/Music/МУЗЫКА ПРОБА" \\
    --dst "/Users/Sputnik/Music/МУЗЫКА ГОТОВО 2" \\
    --models-dir ./models \\
    --limit 20
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from artist_overrides import override_for_artist
from genre_map import map_genre
from keyword_rules import genre_from_text

AUDIO_EXT = {".mp3", ".m4a", ".flac", ".wav", ".ogg", ".aac", ".aiff", ".aif"}
USER_AGENT = "KolyaMusicFallbackSort/1.0 (local; personal library)"
REVIEW_DIR = "_To_Review"


@dataclass
class TrackMeta:
    path: Path
    artist: str = ""
    title: str = ""
    id3_genre: str = ""
    year: str = ""


def sanitize(name: str, max_len: int = 80) -> str:
    name = name.strip() or "unknown"
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name)
    name = re.sub(r"\s+", " ", name).strip(" .")
    return (name[:max_len] or "unknown").rstrip(" .")


def unique_dest(path: Path) -> Path:
    if not path.exists():
        return path
    stem, ext, parent = path.stem, path.suffix, path.parent
    for i in range(2, 1000):
        candidate = parent / f"{stem}__{i}{ext}"
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"no free name for {path}")


def parse_filename(path: Path) -> tuple[str, str]:
    stem = path.stem
    # strip leading [folder] marker if re-processing
    stem = re.sub(r"^\[[^\]]+\]\s*", "", stem)
    for sep in (" - ", " — ", " – "):
        if sep in stem:
            left, right = stem.split(sep, 1)
            return left.strip(), right.strip()
    return "", stem.strip()


def read_id3(path: Path) -> TrackMeta:
    artist, title = parse_filename(path)
    genre = ""
    year = ""
    try:
        from mutagen import File as MutagenFile

        audio = MutagenFile(path, easy=True)
        if audio and audio.tags:
            artist = (audio.tags.get("artist") or [artist])[0] or artist
            title = (audio.tags.get("title") or [title])[0] or title
            genre = (audio.tags.get("genre") or [""])[0] or ""
            date = (audio.tags.get("date") or audio.tags.get("year") or [""])[0]
            year = str(date)[:4] if date else ""
    except Exception:
        pass
    return TrackMeta(path=path, artist=str(artist), title=str(title), id3_genre=str(genre), year=year)


def mb_search(artist: str, title: str) -> tuple[str | None, str]:
    """Return (mapped_folder or None, raw note). Soft-fail on network/404."""
    if not title and not artist:
        return None, "mb:skip_empty"
    q_parts = []
    if artist:
        q_parts.append(f'artist:"{artist}"')
    if title:
        q_parts.append(f'recording:"{title}"')
    query = " AND ".join(q_parts)
    url = (
        "https://musicbrainz.org/ws/2/recording/?query="
        + urllib.parse.quote(query)
        + "&fmt=json&limit=1"
    )
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:  # noqa: BLE001
        return None, f"mb:error:{exc}"
    recs = data.get("recordings") or []
    if not recs:
        return None, "mb:not_found"
    rec = recs[0]
    tags = rec.get("tags") or []
    tag_names = [t.get("name", "") for t in sorted(tags, key=lambda x: -int(x.get("count") or 0))]
    # also try release-group genres if present later — keep simple
    for name in tag_names:
        mapped = map_genre(name)
        if mapped not in {"Other", "Unknown"}:
            return mapped, f"mb:tag:{name}"
    if tag_names:
        return map_genre(tag_names[0]), f"mb:tag:{tag_names[0]}"
    return None, "mb:found_no_tags"


def load_essentia(models_dir: Path):
    from essentia.standard import (  # type: ignore
        MonoLoader,
        TensorflowPredict2D,
        TensorflowPredictEffnetDiscogs,
    )

    emb = models_dir / "discogs-effnet-bs64-1.pb"
    gen = models_dir / "genre_discogs400-discogs-effnet-1.pb"
    meta = models_dir / "genre_discogs400-discogs-effnet-1.json"
    if not emb.exists() or not gen.exists():
        return None

    labels: list[str] = []
    if meta.exists():
        data = json.loads(meta.read_text(encoding="utf-8"))
        labels = data.get("classes") or data.get("labels") or data.get("genre") or []
        if isinstance(labels, dict):
            labels = list(labels.values())

    embedding_model = TensorflowPredictEffnetDiscogs(
        graphFilename=str(emb), output="PartitionedCall:1"
    )
    genre_model = TensorflowPredict2D(
        graphFilename=str(gen),
        input="serving_default_model_Placeholder",
        output="PartitionedCall:0",
    )

    def predict(path: Path) -> tuple[str | None, float, str]:
        import numpy as np

        audio = MonoLoader(filename=str(path), sampleRate=16000, resampleQuality=4)()
        embeddings = embedding_model(audio)
        preds = genre_model(embeddings)
        arr = np.array(preds)
        scores = arr.mean(axis=0) if arr.ndim == 2 else arr
        idx = int(scores.argmax())
        conf = float(scores[idx])
        raw = labels[idx] if labels and idx < len(labels) else f"class_{idx}"
        folder = map_genre(str(raw))
        return folder, conf, str(raw)

    return predict


def decide(
    meta: TrackMeta,
    *,
    essentia_predict,
    min_conf: float,
    use_mb: bool,
) -> tuple[str, str]:
    """Return (folder, reason)."""
    # 0) artist hard override
    ov = override_for_artist(meta.artist) or override_for_artist(meta.path.stem)
    if ov:
        return ov, f"artist_override:{meta.artist or meta.path.stem}"

    # melodic beats deep if both hinted in text
    text_hint = genre_from_text(meta.artist, meta.title, meta.path.name, meta.id3_genre)

    # 1) MusicBrainz
    if use_mb:
        mb_folder, mb_note = mb_search(meta.artist, meta.title)
        time.sleep(1.1)  # polite MB rate limit
        if mb_folder and mb_folder not in {"Other", "Unknown"}:
            # prefer Melodic if filename says melodic
            if text_hint == "Melodic" and mb_folder == "Deep":
                return "Melodic", f"{mb_note}+keyword_melodic"
            return mb_folder, mb_note

    # 2) Essentia audio
    if essentia_predict is not None:
        try:
            folder, conf, raw = essentia_predict(meta.path)
            if conf >= min_conf and folder not in {"Unknown"}:
                if text_hint == "Melodic" and folder == "Deep":
                    return "Melodic", f"essentia:{raw}@{conf:.2f}+keyword_melodic"
                return folder, f"essentia:{raw}@{conf:.2f}"
            ess_note = f"essentia_low:{raw}@{conf:.2f}"
        except Exception as exc:  # noqa: BLE001
            ess_note = f"essentia_err:{exc}"
    else:
        ess_note = "essentia:off"

    # 3) Regex / keywords / id3 genre
    if text_hint:
        return text_hint, f"regex:{text_hint}|{ess_note}"
    if meta.id3_genre:
        mapped = map_genre(meta.id3_genre)
        if mapped not in {"Other", "Unknown"}:
            return mapped, f"id3:{meta.id3_genre}|{ess_note}"

    # 4) review
    return REVIEW_DIR, f"review|{ess_note}"


def write_report_txt(path: Path, auto_rows: list[str], review_rows: list[str]) -> None:
    lines = [
        "AUTO-CLASSIFIED",
        "===============",
        *auto_rows,
        "",
        "TO REVIEW (_To_Review)",
        "======================",
        *review_rows,
        "",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Fallback sorter: MB → Essentia → regex → _To_Review")
    ap.add_argument("--src", required=True, type=Path)
    ap.add_argument("--dst", required=True, type=Path)
    ap.add_argument("--models-dir", type=Path, default=Path(__file__).parent / "models")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--move", action="store_true")
    ap.add_argument("--min-conf", type=float, default=0.35)
    ap.add_argument("--no-mb", action="store_true", help="Skip MusicBrainz (offline / faster)")
    ap.add_argument("--no-essentia", action="store_true")
    args = ap.parse_args()

    src = args.src.expanduser().resolve()
    dst = args.dst.expanduser().resolve()
    if not src.is_dir():
        raise SystemExit(f"src missing: {src}")
    dst.mkdir(parents=True, exist_ok=True)

    essentia_predict = None
    if not args.no_essentia:
        try:
            essentia_predict = load_essentia(args.models_dir.expanduser().resolve())
        except Exception as exc:  # noqa: BLE001
            print(f"Essentia unavailable ({exc}); continuing MB+regex", file=sys.stderr)

    files = sorted(
        p for p in src.rglob("*") if p.is_file() and p.suffix.lower() in AUDIO_EXT
    )
    if args.limit > 0:
        files = files[: args.limit]

    auto_lines: list[str] = []
    review_lines: list[str] = []
    csv_rows: list[dict[str, str]] = []

    print(f"src={src}\ndst={dst}\nfiles={len(files)}\nmode={'MOVE' if args.move else 'COPY'}")

    for i, path in enumerate(files, 1):
        meta = read_id3(path)
        folder, reason = decide(
            meta,
            essentia_predict=essentia_predict,
            min_conf=args.min_conf,
            use_mb=not args.no_mb,
        )
        source_folder = sanitize(path.parent.name)
        new_name = f"[{source_folder}] {path.name}"
        if not new_name.lower().endswith(path.suffix.lower()):
            new_name = f"{Path(sanitize(new_name, 180)).stem}{path.suffix}"
        target_dir = dst / folder
        target_dir.mkdir(parents=True, exist_ok=True)
        target = unique_dest(target_dir / new_name)

        if args.move:
            shutil.move(str(path), str(target))
        else:
            shutil.copy2(str(path), str(target))

        line = f"{folder}\t{meta.artist} - {meta.title or path.name}\t{reason}\t{path.name}"
        print(f"[{i}/{len(files)}] {line}")
        if folder == REVIEW_DIR:
            review_lines.append(line)
        else:
            auto_lines.append(line)

        csv_rows.append(
            {
                "src": str(path),
                "dst": str(target),
                "folder": folder,
                "reason": reason,
                "artist": meta.artist,
                "title": meta.title,
            }
        )

    report_txt = dst / "report.txt"
    report_csv = dst / "_fallback_report.csv"
    write_report_txt(report_txt, auto_lines, review_lines)
    with report_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["src", "dst", "folder", "reason", "artist", "title"])
        w.writeheader()
        w.writerows(csv_rows)

    print(f"\nDone. report.txt={report_txt}\ncsv={report_csv}")
    print(f"auto={len(auto_lines)} review={len(review_lines)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
