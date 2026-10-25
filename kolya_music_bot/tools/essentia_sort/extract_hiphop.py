#!/usr/bin/env python3
"""
Extract all Hip-Hop / Rap / Trap tracks from an entire music library
and COPY them into one destination folder, prefixing each filename with
its original folder name: "[Source_Folder] original_name.mp3".

- Never moves or deletes original files.
- Never modifies ID3 tags (preserves Rekordbox TIT2 markers).
- Avoids scanning the destination folder or previous sorted folders.
- Dedupes identical files by (size, clean_stem) so you don't get 5 copies
  if the same trackalready sat in multiple test folders.

Signals used:
  1) Folder path contains hip-hop / rap / trap markers
  2) ID3 Genre (TCON) or Title (TIT2) or Artist (TPE1) keywords
  3) Filename keywords + known hip-hop artist hints
  4) Optional: Essentia audio check (--with-essentia) for untagged tracks
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import shutil
import sys
from pathlib import Path

AUDIO_EXT = {".mp3", ".m4a", ".flac", ".wav", ".ogg", ".aac", ".aiff", ".aif"}

# Skip folders we created during tests so we only pull from the real library
DEFAULT_SKIP_DIRS = {
    "musicsorted",
    "музыка готово",
    "музыка готово 2",
    "музыка готово 3",
    "готово музыка",
    "проба_strip",
    "_to_review",
    "_review",
    "00 possible duplicates flat",
    "00 duplicates review",
    "00 genre sorted view",
    "00 genre sorte...refined",
    "предыдущие медиатеки",
    ".git",
    ".venv",
    "node_modules",
}

LEADING_BRACKET_RE = re.compile(r"^(?:\[[^\]]*\]\s*)+")

# Word-boundary / safe substring rules for hip-hop / rap / trap
HIPHOP_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"hip[\s_\-]?hop", re.I), "kw:hip-hop"),
    (re.compile(r"хип[\s_\-]?хоп", re.I), "kw:хип-хоп"),
    (re.compile(r"(?<![a-zа-я0-9])rap(?![a-zа-я0-9])", re.I), "kw:rap"),
    (re.compile(r"(?<![a-zа-я0-9])рэп(?![a-zа-я0-9])", re.I), "kw:рэп"),
    (re.compile(r"(?<![a-zа-я0-9])реп(?![a-zа-я0-9])", re.I), "kw:реп"),
    (re.compile(r"(?<![a-zа-я0-9])trap(?![a-zа-я0-9])", re.I), "kw:trap"),
    (re.compile(r"(?<![a-zа-я0-9])трэп(?![a-zа-я0-9])", re.I), "kw:трэп"),
    (re.compile(r"boom[\s_\-]?bap", re.I), "kw:boombap"),
    (re.compile(r"g[\s_\-]?funk", re.I), "kw:gfunk"),
    (re.compile(r"(?<![a-zа-я0-9])phonk(?![a-zа-я0-9])", re.I), "kw:phonk"),
    (re.compile(r"(?<![a-zа-я0-9])drill(?![a-zа-я0-9])", re.I), "kw:drill"),
    (re.compile(r"r\s*&\s*b|rnb", re.I), "kw:rnb"),
    (re.compile(r"old[\s_\-]?school\s+hip", re.I), "kw:oldschool"),
]

# Common RU / INT hip-hop artists frequently found in DJ libraries
HIPHOP_ARTISTS: tuple[str, ...] = (
    "eminem",
    "50 cent",
    "snoop dogg",
    "dr. dre",
    "dr dre",
    "kendrick lamar",
    "travis scott",
    "drake",
    "kanye west",
    "jay-z",
    "jay z",
    "nas",
    "2pac",
    "tupac",
    "notorious b.i.g",
    "biggie",
    "ice cube",
    "cypress hill",
    "wu-tang",
    "mobb deep",
    "dmx",
    "busta rhymes",
    "missy elliott",
    "timbaland",
    "outkast",
    "lil wayne",
    "future",
    "21 savage",
    "metro boomin",
    "asap rocky",
    "a$ap rocky",
    "playboi carti",
    "pop smoke",
    "central cee",
    "jack harlow",
    "cardi b",
    "nicki minaj",
    "megan thee stallion",
    "doja cat",
    "post malone",
    "tyga",
    "wiz khalifa",
    "mac miller",
    "logic",
    "j. cole",
    "j cole",
    "rick ross",
    "gucci mane",
    "migos",
    "lil baby",
    "da baby",
    "dababy",
    "gunna",
    "young thug",
    "lil uzi",
    "xxxtentacion",
    "juice wrld",
    "suicideboys",
    "$uicideboy$",
    "bones",
    "ghostemane",
    "city morgue",
    # RU / CIS rap & hip-hop
    "баста",
    "basta",
    "скриптонит",
    "scriptonite",
    "oxxxymiron",
    "оксимирон",
    "morgenshtern",
    "моргенштерн",
    "эндшпиль",
    "miyagi",
    "мияги",
    "каста",
    "kasta",
    "гуф",
    "guf",
    "centr",
    "ноггано",
    "смоки мо",
    "ак-47",
    "триагрутрика",
    "словетский",
    "рем дигга",
    "rem digga",
    "pharaoh",
    "фараон",
    "kizaru",
    "кизару",
    "obladaet",
    "обладает",
    "markul",
    "маркул",
    "лдпр",
    "allj",
    "элджей",
    "feduk",
    "федук",
    "big baby tape",
    "aikko",
    "rocket",
    "og buda",
    "mayot",
    "seeming",
    "платина",
    "lovv66",
    "macan",
    "макан",
    "instasamka",
    "инстасамка",
    "хаски",
    "saluki",
    "салуки",
    "104",
    "truwer",
    "масло черного тмина",
    "noize mc",
    "нойз мс",
    "децл",
    "лигалайз",
    "многоточие",
    "кacта",
    "тимати",
    "l'one",
    "мот",
)

# Negative guards: if it clearly says House/Techno remix, don't pull as pure hip-hop
# unless the user wants club edits too (controlled via --include-club-edits)
CLUB_EDIT_RE = re.compile(
    r"\b(tech\s*house|deep\s*house|melodic\s*house|melodic\s*techno|progressive\s*house|afro\s*house|club\s*mix|extended\s*mix|vip\s*mix)\b",
    re.I,
)


def sanitize(name: str, max_len: int = 80) -> str:
    name = name.strip() or "unknown"
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name)
    name = re.sub(r"\s+", " ", name).strip(" .")
    return (name[:max_len] or "unknown").rstrip(" .")


def strip_existing_brackets(filename: str) -> str:
    cleaned = LEADING_BRACKET_RE.sub("", filename, count=1).strip()
    return cleaned or filename


def source_folder_label(path: Path, src_root: Path) -> str:
    """
    Pick a meaningful folder name where the file lived.
    If parent is generic ('2', 'mp3', 'Music'), climb one level up.
    """
    parent = path.parent
    generic = {"music", "музыка", "mp3", "tracks", "new", "1", "2", "3", "0"}
    if parent != src_root and parent.name.strip().lower() in generic and parent.parent != src_root:
        label = f"{parent.parent.name}_{parent.name}"
    else:
        label = parent.name
    return sanitize(label, max_len=60)


def read_tags(path: Path) -> dict[str, str]:
    out = {"title": "", "artist": "", "genre": "", "album": "", "comment": ""}
    try:
        from mutagen import File as MutagenFile

        audio = MutagenFile(path, easy=True)
        if audio and audio.tags:
            for k in ("title", "artist", "genre", "album"):
                val = audio.tags.get(k)
                if val:
                    out[k] = " ".join(str(x) for x in val)
    except Exception:
        pass
    return out


def match_hiphop_metadata(
    path: Path,
    tags: dict[str, str],
    *,
    include_club_edits: bool,
) -> str | None:
    stem_clean = strip_existing_brackets(path.stem)
    folder_chain = " / ".join(path.parts[-3:])
    blob_genre = f"{tags['genre']} {folder_chain}"
    blob_all = f"{stem_clean} {tags['artist']} {tags['title']} {tags['genre']} {folder_chain}"

    if not include_club_edits and CLUB_EDIT_RE.search(blob_all):
        # Still allow if genre tag explicitly says hip-hop/rap
        if not any(p.search(tags["genre"]) for p, _ in HIPHOP_PATTERNS[:6]):
            return None

    # 1) Genre tag / folder name
    for pat, label in HIPHOP_PATTERNS:
        if pat.search(blob_genre):
            return f"genre/folder({label})"

    # 2) Title / filename / artist keywords
    for pat, label in HIPHOP_PATTERNS:
        if pat.search(blob_all):
            return f"text({label})"

    # 3) Known hip-hop artist in filename or artist/title tag
    low_check = f"{stem_clean} {tags['artist']} {tags['title']}".lower()
    for art in HIPHOP_ARTISTS:
        # match artist as whole token-ish
        if re.search(rf"(?<![a-zа-я0-9]){re.escape(art)}(?![a-zа-я0-9])", low_check):
            return f"artist({art})"

    return None


def unique_dest(directory: Path, filename: str) -> Path:
    cand = directory / filename
    if not cand.exists():
        return cand
    stem = Path(filename).stem
    ext = Path(filename).suffix
    for i in range(2, 10000):
        alt = directory / f"{stem}__{i}{ext}"
        if not alt.exists():
            return alt
    raise RuntimeError(f"Cannot find free name for {filename}")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Extract all Hip-Hop from library with [Source_Folder] prefix (COPY)"
    )
    ap.add_argument("--src", required=True, type=Path, help="Root library folder, e.g. ~/Music")
    ap.add_argument(
        "--dst",
        required=True,
        type=Path,
        help="Destination folder for Hip-Hop, e.g. ~/Music/ВЕСЬ ХИП-ХОП",
    )
    ap.add_argument(
        "--include-club-edits",
        action="store_true",
        help="Also include House/Tech-House remixes of hip-hop tracks (default: include!)",
    )
    ap.add_argument(
        "--strict-no-club",
        action="store_true",
        help="Exclude tracks that look like House/Techno club mixes",
    )
    ap.add_argument(
        "--with-essentia",
        action="store_true",
        help="Also run Essentia audio model on unmatched tracks (slow on 5000+ files)",
    )
    ap.add_argument("--models-dir", type=Path, default=Path(__file__).parent / "models")
    ap.add_argument("--min-conf", type=float, default=0.30)
    ap.add_argument("--dry-run", action="store_true", help="Only list matches, do not copy")
    ap.add_argument("--limit", type=int, default=0, help="Max matched files to copy (0 = all)")
    args = ap.parse_args()

    src = args.src.expanduser().resolve()
    dst = args.dst.expanduser().resolve()
    if not src.is_dir():
        print(f"ERROR: src not found: {src}", file=sys.stderr)
        return 1

    include_club = not args.strict_no_club

    essentia_predict = None
    if args.with_essentia:
        try:
            from fallback_sort import load_essentia

            essentia_predict = load_essentia(args.models_dir.expanduser().resolve())
        except Exception as exc:  # noqa: BLE001
            print(f"WARN: Essentia not loaded ({exc})", file=sys.stderr)

    if not args.dry_run:
        dst.mkdir(parents=True, exist_ok=True)

    seen_dedup: set[tuple[int, str]] = set()
    rows: list[dict[str, str]] = []
    scanned = 0
    matched = 0
    skipped_dup = 0

    for dirpath, dirnames, filenames in os.walk(src):
        current_dir = Path(dirpath).resolve()
        # Don't descend into dst or known generated folders
        dirnames[:] = [
            d
            for d in dirnames
            if d.lower().strip() not in DEFAULT_SKIP_DIRS
            and (current_dir / d).resolve() != dst
        ]
        if current_dir == dst or dst in current_dir.parents:
            continue

        for fname in sorted(filenames):
            fpath = current_dir / fname
            if fpath.suffix.lower() not in AUDIO_EXT:
                continue
            scanned += 1
            tags = read_tags(fpath)
            reason = match_hiphop_metadata(fpath, tags, include_club_edits=include_club)

            if not reason and essentia_predict is not None:
                try:
                    folder, conf, raw = essentia_predict(fpath)
                    if folder in {"Hip-Hop", "Trap"} and conf >= args.min_conf:
                        reason = f"essentia({raw}@{conf:.2f})"
                except Exception:
                    pass

            if not reason:
                continue

            # Dedup by (filesize, clean lowercase stem)
            clean_file = strip_existing_brackets(fname)
            try:
                fsize = fpath.stat().st_size
            except OSError:
                continue
            dedup_key = (fsize, Path(clean_file).stem.lower().strip())
            if dedup_key in seen_dedup:
                skipped_dup += 1
                continue
            seen_dedup.add(dedup_key)

            folder_tag = source_folder_label(fpath, src)
            new_name = f"[{folder_tag}] {clean_file}"
            target = unique_dest(dst, new_name) if not args.dry_run else (dst / new_name)

            if not args.dry_run:
                shutil.copy2(str(fpath), str(target))

            matched += 1
            print(f"[{matched}] {new_name}  <--  {reason}")
            rows.append(
                {
                    "new_name": target.name,
                    "source_folder": folder_tag,
                    "reason": reason,
                    "title_tag": tags["title"],
                    "artist_tag": tags["artist"],
                    "genre_tag": tags["genre"],
                    "original_path": str(fpath),
                }
            )

            if args.limit > 0 and matched >= args.limit:
                break
        if args.limit > 0 and matched >= args.limit:
            break

    report_dir = dst if not args.dry_run else src
    csv_path = (dst / "_hiphop_report.csv") if not args.dry_run else (Path("/tmp") / "_hiphop_report.csv")
    txt_path = (dst / "report.txt") if not args.dry_run else (Path("/tmp") / "hiphop_report.txt")

    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "new_name",
                "source_folder",
                "reason",
                "title_tag",
                "artist_tag",
                "genre_tag",
                "original_path",
            ],
        )
        w.writeheader()
        w.writerows(rows)

    txt_lines = [
        f"scanned={scanned} matched_hiphop={matched} skipped_duplicates={skipped_dup} mode={'DRY-RUN' if args.dry_run else 'COPY'}",
        f"src={src}",
        f"dst={dst}",
        "==================================================================",
        *[f"{r['new_name']}\t|\t{r['reason']}\t|\tTIT2={r['title_tag'][:60]}" for r in rows],
    ]
    txt_path.write_text("\n".join(txt_lines) + "\n", encoding="utf-8")

    print(
        f"\nDONE: scanned={scanned} matched={matched} dup_skipped={skipped_dup}\n"
        f"dst={dst}\nreport={txt_path}\ncsv={csv_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
