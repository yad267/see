#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="${1:-$HOME/Developer/Languages-on-site}"
cp -f "$HERE/EnglishOnSite/Views/SiteTutorView.swift" "$ROOT/EnglishOnSite/Views/SiteTutorView.swift"
cp -f "$HERE/EnglishOnSite/Views/PhrasalHubView.swift" "$ROOT/EnglishOnSite/Views/PhrasalHubView.swift"
rg -n 'pairsHub|«Пары»|Пары' "$ROOT/EnglishOnSite/Views/SiteTutorView.swift" | head -10
echo "DONE repeater Пары → PhrasalHubView(embedded)"
