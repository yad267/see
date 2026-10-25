#!/usr/bin/env bash
# Download Essentia Discogs-EffNet + Genre Discogs400 models into ./models
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p models
cd models

# Official model hosting (Essentia / MTG). URLs may redirect; if 404, take links from:
# https://essentia.upf.edu/models.html
BASE="https://essentia.upf.edu/models/feature-extractors/discogs-effnet"
GENRE="https://essentia.upf.edu/models/classification-heads/genre_discogs400"

curl -fL -o discogs-effnet-bs64-1.pb \
  "${BASE}/discogs-effnet-bs64-1.pb" || true
curl -fL -o genre_discogs400-discogs-effnet-1.pb \
  "${GENRE}/genre_discogs400-discogs-effnet-1.pb" || true
curl -fL -o genre_discogs400-discogs-effnet-1.json \
  "${GENRE}/genre_discogs400-discogs-effnet-1.json" || true

ls -la
echo "If any file missing/HTML, download manually from essentia.upf.edu/models.html into ./models/"
