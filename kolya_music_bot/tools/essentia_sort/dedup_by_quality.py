#!/usr/bin/env python3
"""
Deduplicate a sorted music folder by keeping the HIGHEST AUDIO QUALITY copy
and moving worse duplicates into a separate folder (e.g. "3_Дубликаты").

Also flags any unique track whose best available quality is below 320 kbps MP3
(or lossless), so the DJ knows which tracks have low bitrate.

Quality ranking (highest wins):
  1) Lossless: FLAC / WAV / AIFF / ALAC
  2) MP3 >= 315 kbps (i.e. 320 kbps CBR) or M4A/AAC >= 250 kbps
  3) Higher real bitrate (kbps)
  4) Higher sample rate (Hz)
  5) Larger file size (bytes)

Important:
  - Different remixes (e.g. Original Mix vs Club Remix) are NOT treated as
    duplicates of each other.
  - Preserves [Source_Folder] prefix and never touches ID3 tags.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

AUDIO_EXT = {".flac", ".wav", ".aiff", ".aif", ".m4a", ".mp3", ".ogg", ".aac"}
LOSSLESS_EXT = {".flac", ".wav", ".aiff", ".aif"}

LEADING_BRACKET_RE = re.compile(r"^(?:\[[^\]]*\]\s*)+")
COPY_SUFFIX_RE = re.compile(
    r"(?:\s*\(\d+\)|\s*__+\d+|\s+copy|\s+копия|\s*-\s*copy)+$",
    re.I,
)
JUNK_SITES_RE = re.compile(
    r"[\(\[\s]*(?:mp3name\.net|z1\.fm|zvukoff\.ru|muzofond|vmuz\d*|freshmp3\.net|promodj|зайцев\.нет|myzuka|hitmo|drivemusic)[\)\]\s]*",
    re.I,
)
KEY_BPM_TAIL_RE = re.compile(r"\b\d{1,2}[AB]\s+\d{2,3}\b", re.I)


@dataclass
class AudioInfo:
    path: Path
    subfolder: str
    ext: str
    is_lossless: bool
    bitrate_kbps: int
    sample_rate: int
    duration_sec: float
    size_bytes: int
    md5_head: str
    norm_key: str
    title_tag: str
    artist_tag: str

    @property
    def is_320_or_better(self) -> bool:
        if self.is_lossless:
            return True
        if self.ext == ".mp3" and self.bitrate_kbps >= 312:
            return True
        if self.ext in {".m4a", ".aac"} and self.bitrate_kbps >= 245:
            return True
        return False

    def quality_tuple(self) -> tuple[int, int, int, int, int]:
        lossless_rank = 2 if self.is_lossless else (1 if self.is_320_or_better else 0)
        return (
            lossless_rank,
            self.bitrate_kbps,
            self.sample_rate,
            self.size_bytes,
            -len(self.path.name),
        )

    def quality_label(self) -> str:
        fmt = self.ext.lstrip(".").upper()
        if self.is_lossless:
            return f"{fmt} LOSSLESS ({self.sample_rate}Hz, {self.size_bytes // (1024*1024)}MB)"
        return f"{fmt} {self.bitrate_kbps}kbps ({self.sample_rate}Hz, {round(self.size_bytes / (1024*1024), 1)}MB)"


def normalize_track_key(filename: str, artist_tag: str, title_tag: str) -> str:
    """
    Build a canonical key for 'same track & same version/remix'.
    Different remixes stay distinct; file copy suffixes like (1), __2, [Folder] are stripped.
    """
    stem = Path(filename).stem
    stem = LEADING_BRACKET_RE.sub("", stem).strip()
    stem = JUNK_SITES_RE.sub(" ", stem)
    stem = COPY_SUFFIX_RE.sub("", stem).strip()
    stem = KEY_BPM_TAIL_RE.sub(" ", stem)
    # Remove leading track numbers like "01 - " or "03. "
    stem = re.sub(r"^\d{1,3}[\s._\-]+", "", stem)
    stem = stem.lower()
    stem = re.sub(r"[_\-–—]+", " ", stem)
    stem = re.sub(r"[^\w\sа-яё]", " ", stem, flags=re.I)
    stem = re.sub(r"\s+", " ", stem).strip()
    if len(stem) >= 5:
        return stem
    fallback = f"{artist_tag} {title_tag}".lower()
    fallback = re.sub(r"\s+", " ", fallback).strip()
    return fallback or filename.lower()


def inspect_audio(path: Path, root: Path) -> AudioInfo:
    ext = path.suffix.lower()
    is_lossless = ext in LOSSLESS_EXT
    bitrate_kbps = 0
    sample_rate = 0
    duration_sec = 0.0
    title_tag = ""
    artist_tag = ""

    try:
        size_bytes = path.stat().st_size
    except OSError:
        size_bytes = 0

    # Fast hash of audio payload (first + middle + last 64KB) to catch byte-identical audio
    md5 = hashlib.md5()
    try:
        with path.open("rb") as f:
            if size_bytes <= 256 * 1024:
                md5.update(f.read())
            else:
                f.seek(size_bytes // 3)
                md5.update(f.read(65536))
                f.seek((size_bytes * 2) // 3)
                md5.update(f.read(65536))
    except OSError:
        pass
    md5_head = f"{size_bytes}:{md5.hexdigest()}"

    try:
        from mutagen import File as MutagenFile

        audio = MutagenFile(path)
        if audio is not None and getattr(audio, "info", None) is not None:
            info = audio.info
            br = int(getattr(info, "bitrate", 0) or 0)
            bitrate_kbps = round(br / 1000) if br > 1000 else br
            sample_rate = int(getattr(info, "sample_rate", 0) or 0)
            duration_sec = float(getattr(info, "length", 0.0) or 0.0)
            # Check Apple lossless
            codec = str(getattr(info, "codec", "") or "").lower()
            if "alac" in codec:
                is_lossless = True

        easy = MutagenFile(path, easy=True)
        if easy and easy.tags:
            artist_tag = " ".join(easy.tags.get("artist") or [])
            title_tag = " ".join(easy.tags.get("title") or [])
    except Exception:
        pass

    rel_parent = path.parent.relative_to(root) if path.parent != root else Path(".")
    norm_key = normalize_track_key(path.name, artist_tag, title_tag)

    return AudioInfo(
        path=path,
        subfolder=str(rel_parent),
        ext=ext,
        is_lossless=is_lossless,
        bitrate_kbps=bitrate_kbps,
        sample_rate=sample_rate,
        duration_sec=duration_sec,
        size_bytes=size_bytes,
        md5_head=md5_head,
        norm_key=norm_key,
        title_tag=title_tag,
        artist_tag=artist_tag,
    )


def unique_dest(directory: Path, filename: str) -> Path:
    cand = directory / filename
    if not cand.exists():
        return cand
    stem = Path(filename).stem
    ext = Path(filename).suffix
    for i in range(2, 10000):
        alt = directory / f"{stem}__dup{i}{ext}"
        if not alt.exists():
            return alt
    raise RuntimeError(f"Cannot find free name for {filename}")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Deduplicate folder keeping best audio quality (Lossless > 320kbps > lower)"
    )
    ap.add_argument(
        "--root",
        required=True,
        type=Path,
        help="Target folder, e.g. /Users/Sputnik/Music/ВЕСЬ ХИП-ХОП",
    )
    ap.add_argument(
        "--dup-folder-name",
        default="3_Дубликаты",
        help="Subfolder inside --root where worse duplicates are moved",
    )
    ap.add_argument(
        "--low-bitrate-folder-name",
        default="",
        help="Optional: move unique tracks <320kbps into this subfolder (default: keep in place, only report)",
    )
    ap.add_argument(
        "--apply",
        action="store_true",
        help="Actually move worse duplicates into 3_Дубликаты (default: dry-run report only)",
    )
    args = ap.parse_args()

    root = args.root.expanduser().resolve()
    if not root.is_dir():
        print(f"ERROR: root not found: {root}", file=sys.stderr)
        return 1

    dup_dir = root / args.dup_folder_name
    low_dir = (root / args.low_bitrate_folder_name) if args.low_bitrate_folder_name else None

    all_items: list[AudioInfo] = []
    for dirpath, dirnames, filenames in os.walk(root):
        cur = Path(dirpath).resolve()
        dirnames[:] = [
            d
            for d in dirnames
            if (cur / d).resolve() != dup_dir
            and (low_dir is None or (cur / d).resolve() != low_dir)
        ]
        if cur == dup_dir or (low_dir is not None and cur == low_dir):
            continue
        for fname in sorted(filenames):
            fpath = cur / fname
            if fpath.suffix.lower() not in AUDIO_EXT:
                continue
            all_items.append(inspect_audio(fpath, root))

    # Group by exact audio payload hash first, then by normalized track name
    by_key: dict[str, list[AudioInfo]] = {}
    hash_to_key: dict[str, str] = {}

    for item in all_items:
        key = hash_to_key.get(item.md5_head, item.norm_key)
        hash_to_key[item.md5_head] = key
        by_key.setdefault(key, []).append(item)

    kept_best: list[AudioInfo] = []
    moved_dups: list[tuple[AudioInfo, AudioInfo, str]] = []  # (loser, winner, reason)

    for key, group in by_key.items():
        if len(group) == 1:
            kept_best.append(group[0])
            continue
        # Sort descending by quality_tuple
        ranked = sorted(group, key=lambda x: x.quality_tuple(), reverse=True)
        winner = ranked[0]
        kept_best.append(winner)
        for loser in ranked[1:]:
            reason = f"kept [{winner.quality_label()}] {winner.path.name} > [{loser.quality_label()}]"
            moved_dups.append((loser, winner, reason))

    if args.apply and moved_dups:
        dup_dir.mkdir(parents=True, exist_ok=True)
        for loser, _winner, _reason in moved_dups:
            dest = unique_dest(dup_dir, loser.path.name)
            shutil.move(str(loser.path), str(dest))

    low_quality = [x for x in kept_best if not x.is_320_or_better]
    if args.apply and low_dir is not None and low_quality:
        low_dir.mkdir(parents=True, exist_ok=True)
        for item in low_quality:
            dest = unique_dest(low_dir, item.path.name)
            shutil.move(str(item.path), str(dest))

    # Write detailed quality & dedup report
    report_txt = root / "report_quality.txt"
    report_csv = root / "_quality_report.csv"

    lossless_cnt = sum(1 for x in kept_best if x.is_lossless)
    hq_320_cnt = sum(1 for x in kept_best if (not x.is_lossless and x.is_320_or_better))
    low_cnt = len(low_quality)

    lines = [
        f"MODE: {'APPLY (dups moved)' if args.apply else 'DRY-RUN (nothing moved yet)'}",
        f"ROOT: {root}",
        f"TOTAL SCANNED: {len(all_items)}",
        f"UNIQUE KEPT: {len(kept_best)}  (Lossless={lossless_cnt}, 320kbps={hq_320_cnt}, <320kbps={low_cnt})",
        f"DUPLICATES FOUND: {len(moved_dups)} -> {dup_dir.name}/",
        "",
        "=== 1. DUPLICATES (WORSE COPY -> 3_Дубликаты) ===",
    ]
    if not moved_dups:
        lines.append("  (дубликатов не обнаружено)")
    else:
        for i, (loser, winner, _) in enumerate(moved_dups, 1):
            lines.append(
                f"  {i}) УБРАТЬ В ДУБЛИ: {loser.subfolder}/{loser.path.name} [{loser.quality_label()}]\n"
                f"     ОСТАВИТЬ ЛУЧШИЙ: {winner.subfolder}/{winner.path.name} [{winner.quality_label()}]"
            )

    lines.append("")
    lines.append("=== 2. ТРЕКИ НИЖЕ 320 KBPS (УНИКАЛЬНЫЕ, ЛУЧШЕЙ ВЕРСИИ НА ДИСКЕ НЕТ) ===")
    if not low_quality:
        lines.append("  (все уникальные треки 320 kbps или Lossless!)")
    else:
        for i, item in enumerate(sorted(low_quality, key=lambda x: x.bitrate_kbps), 1):
            lines.append(f"  {i}) [{item.quality_label()}] {item.subfolder}/{item.path.name}")

    report_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with report_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "status",
                "subfolder",
                "filename",
                "format",
                "bitrate_kbps",
                "sample_rate",
                "size_mb",
                "is_320_or_better",
                "winner_if_dup",
            ],
        )
        w.writeheader()
        for x in kept_best:
            w.writerow(
                {
                    "status": "KEPT_BEST",
                    "subfolder": x.subfolder,
                    "filename": x.path.name,
                    "format": "LOSSLESS" if x.is_lossless else x.ext.lstrip(".").upper(),
                    "bitrate_kbps": x.bitrate_kbps,
                    "sample_rate": x.sample_rate,
                    "size_mb": round(x.size_bytes / (1024 * 1024), 2),
                    "is_320_or_better": x.is_320_or_better,
                    "winner_if_dup": "",
                }
            )
        for loser, winner, _ in moved_dups:
            w.writerow(
                {
                    "status": "MOVED_TO_DUPLICATES" if args.apply else "DUP_CANDIDATE",
                    "subfolder": loser.subfolder,
                    "filename": loser.path.name,
                    "format": "LOSSLESS" if loser.is_lossless else loser.ext.lstrip(".").upper(),
                    "bitrate_kbps": loser.bitrate_kbps,
                    "sample_rate": loser.sample_rate,
                    "size_mb": round(loser.size_bytes / (1024 * 1024), 2),
                    "is_320_or_better": loser.is_320_or_better,
                    "winner_if_dup": f"{winner.path.name} ({winner.quality_label()})",
                }
            )

    print("\n".join(lines[:35]))
    print(f"\nReport saved: {report_txt}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
