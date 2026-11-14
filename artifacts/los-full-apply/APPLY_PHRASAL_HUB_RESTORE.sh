#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$HOME/Developer/Languages-on-site}"
UDID="${UDID:-00008130-00166C4C0221001C}"
HERE="$(cd "$(dirname "$0")" && pwd)"

cp -f "$HERE/EnglishOnSite/Views/PhrasalHubView.swift" "$ROOT/EnglishOnSite/Views/PhrasalHubView.swift"
# Keep STT fixes if present in pack
for f in \
  Services/TimedSpeechCapture.swift \
  Views/AddMyPhraseView.swift \
  Views/PhrasalSpeakPracticeRow.swift
 do
  if [[ -f "$HERE/EnglishOnSite/$f" ]]; then
    cp -f "$HERE/EnglishOnSite/$f" "$ROOT/EnglishOnSite/$f"
    echo "copied $f"
  fi
 done

grep -n 'TutorPhrasalSearchView\|Погнал\|Инструменты' "$ROOT/EnglishOnSite/Views/PhrasalHubView.swift" | head -20

cd "$ROOT"
rm -rf /tmp/EOSDerived
set +e
xcodebuild -project EnglishOnSite.xcodeproj -scheme EnglishOnSite \
  -destination "id=$UDID" -derivedDataPath /tmp/EOSDerived \
  clean build 2>&1 | tee /tmp/eos-build.log | grep -E 'error:|BUILD SUCCEEDED|BUILD FAILED'
XC=${PIPESTATUS[0]}
set -e
if ! grep -q 'BUILD SUCCEEDED' /tmp/eos-build.log; then
  echo "FAIL: build (exit=$XC)"
  grep -E 'error:' /tmp/eos-build.log | sort -u | head -40
  exit 1
fi
APP=$(find /tmp/EOSDerived/Build/Products -name 'EnglishOnSite.app' -type d | head -1)
xcrun devicectl device install app --device "$UDID" "$APP"
echo "OK: BUILD SUCCEEDED + install — Фразовые Duolingo-стиль возвращены"
