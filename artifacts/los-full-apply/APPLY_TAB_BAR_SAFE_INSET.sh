#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="${1:-$HOME/Developer/Languages-on-site}"
cp -f "$HERE/EnglishOnSite/Views/TutorPairsView.swift" "$ROOT/EnglishOnSite/Views/TutorPairsView.swift"
cp -f "$HERE/EnglishOnSite/Views/PhrasalHubView.swift" "$ROOT/EnglishOnSite/Views/PhrasalHubView.swift"
cp -f "$HERE/EnglishOnSite/Views/HomeView.swift" "$ROOT/EnglishOnSite/Views/HomeView.swift"
echo "DONE tab-bar safe inset → TutorPairsView / PhrasalHubView / HomeView"
