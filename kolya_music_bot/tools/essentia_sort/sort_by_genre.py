#!/usr/bin/env python3
"""
Sort music files by Essentia Discogs genre (audio) into folders.
Embeds the original parent folder name into the filename.

Default = COPY (originals untouched). Use --move only after a test run.

Example:
  python sort_by_genre.py \\
    --src ~/Music/Picard-work \\
    --dst ~/Music/MusicSorted \\
    --models-dir ./models \\
    --limit 20
"""

from __future__ import annotations

import argparse
import csv
import re
import shutil
import sys
from pathlib import Path

from genre_map import map_genre

AUDIO_EXT = {".mp3", ".m4a", ".flac", ".wav", ".ogg", ".aac", ".aiff", ".aif"}


def sanitize(name: str, max_len: int = 80) -> str:
    name = name.strip() or "unknown"
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name)
    name = re.sub(r"\s+", " ", name).strip(" .")
    return (name[:max_len] or "unknown").rstrip(" .")


def load_classifier(models_dir: Path):
    try:
        from essentia.standard import (
            MonoLoader,
            TensorflowPredict2D,
            TensorflowPredictEffnetDiscogs,
        )
    except ImportError as exc:
        raise SystemExit(
            "Install: pip install essentia-tensorflow\n"
            "Do NOT also install plain 'essentia' in the same venv.\n"
            f"Import error: {exc}"
        ) from exc

    emb = models_dir / "discogs-effnet-bs64-1.pb"
    gen = models_dir / "genre_discogs400-discogs-effnet-1.pb"
    meta = models_dir / "genre_discogs400-discogs-effnet-1.json"
    for p in (emb, gen):
        if not p.exists():
            raise SystemExit(
                f"Missing model: {p}\n"
                "Download from https://essentia.upf.edu/models.html "
                "(Discogs-EffNet + Genre Discogs400)."
            )

    labels: list[str] = []
    if meta.exists():
        import json

        data = json.loads(meta.read_text(encoding="utf-8"))
        # common keys in Essentia model metadata
        labels = (
            data.get("classes")
            or data.get("labels")
            or data.get("genre")
            or []
        )
        if isinstance(labels, dict):
            labels = list(labels.values())

    embedding_model = TensorflowPredictEffnetDiscogs(
        graphFilename=str(emb),
        output="PartitionedCall:1",
    )
    genre_model = TensorflowPredict2D(
        graphFilename=str(gen),
        input="serving_default_model_Placeholder",
        output="PartitionedCall:0",
    )

    def predict(path: Path) -> tuple[str, float, str]:
        audio = MonoLoader(filename=str(path), sampleRate=16000, resampleQuality=4)()
        embeddings = embedding_model(audio)
        preds = genre_model(embeddings)
        # preds shape: (patches, classes) or (classes,)
        import numpy as np

        arr = np.array(preds)
        if arr.ndim == 2:
            scores = arr.mean(axis=0)
        else:
            scores = arr
        idx = int(scores.argmax())
        conf = float(scores[idx])
        raw = labels[idx] if labels and idx < len(labels) else f"class_{idx}"
        folder = map_genre(str(raw))
        return folder, conf, str(raw)

    return predict


def iter_audio(src: Path) -> list[Path]:
    files = [p for p in src.rglob("*") if p.is_file() and p.suffix.lower() in AUDIO_EXT]
    files.sort()
    return files


def unique_dest(path: Path) -> Path:
    if not path.exists():
        return path
    stem, ext, parent = path.stem, path.suffix, path.parent
    for i in range(2, 1000):
        candidate = parent / f"{stem}__{i}{ext}"
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Cannot find free name for {path}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Essentia genre sort with source-folder in filename")
    ap.add_argument("--src", required=True, type=Path, help="Folder with music (scanned recursively)")
    ap.add_argument("--dst", required=True, type=Path, help="Output root, e.g. ~/Music/MusicSorted")
    ap.add_argument("--models-dir", type=Path, default=Path(__file__).parent / "models")
    ap.add_argument("--limit", type=int, default=0, help="Process only first N files (0 = all)")
    ap.add_argument("--move", action="store_true", help="MOVE instead of copy (default: copy)")
    ap.add_argument("--min-conf", type=float, default=0.15, help="Below → Unknown")
    ap.add_argument("--report", type=Path, default=None, help="CSV report path")
    args = ap.parse_args()

    src = args.src.expanduser().resolve()
    dst = args.dst.expanduser().resolve()
    if not src.is_dir():
        raise SystemExit(f"Source not found: {src}")

    predict = load_classifier(args.models_dir.expanduser().resolve())
    files = iter_audio(src)
    if args.limit and args.limit > 0:
        files = files[: args.limit]

    dst.mkdir(parents=True, exist_ok=True)
    report_path = args.report or (dst / "_essentia_report.csv")
    rows: list[dict[str, str]] = []

    print(f"src={src}\ndst={dst}\nfiles={len(files)}\nmode={'MOVE' if args.move else 'COPY'}")

    for i, path in enumerate(files, 1):
        try:
            folder, conf, raw = predict(path)
        except Exception as exc:  # noqa: BLE001 — keep batch going
            folder, conf, raw = "Unknown", 0.0, f"ERROR:{exc}"
            print(f"[{i}/{len(files)}] FAIL {path.name}: {exc}", file=sys.stderr)
        if conf < args.min_conf and not str(raw).startswith("ERROR:"):
            folder = "Unknown"

        source_folder = sanitize(path.parent.name)
        new_name = f"[{source_folder}] {path.name}"
        new_name = sanitize(new_name, max_len=180)
        # keep extension from original
        if not new_name.lower().endswith(path.suffix.lower()):
            new_name = f"{Path(new_name).stem}{path.suffix}"

        target_dir = dst / folder
        target_dir.mkdir(parents=True, exist_ok=True)
        target = unique_dest(target_dir / new_name)

        if args.move:
            shutil.move(str(path), str(target))
        else:
            shutil.copy2(str(path), str(target))

        print(f"[{i}/{len(files)}] {folder} ({conf:.2f}) ← {raw}")
        print(f"    {path.name}")
        print(f" →  {target.relative_to(dst)}")

        rows.append(
            {
                "src": str(path),
                "dst": str(target),
                "genre_folder": folder,
                "raw_label": raw,
                "confidence": f"{conf:.4f}",
                "source_folder": source_folder,
            }
        )

    with report_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["src", "dst", "genre_folder", "raw_label", "confidence", "source_folder"],
        )
        w.writeheader()
        w.writerows(rows)

    print(f"\nDone. Report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
