#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$HOME/Developer/Languages-on-site}"
UDID="${UDID:-00008130-00166C4C0221001C}"
HERE="$(cd "$(dirname "$0")" && pwd)"
test -d "$ROOT/EnglishOnSite" || { echo "FAIL: missing $ROOT/EnglishOnSite"; exit 1; }

rsync -a "$HERE/EnglishOnSite/" "$ROOT/EnglishOnSite/"
for f in \
  Services/TimedSpeechCapture.swift \
  Views/AddMyPhraseView.swift \
  Views/PhrasalSpeakPracticeRow.swift
 do
  cp -f "$HERE/EnglishOnSite/$f" "$ROOT/EnglishOnSite/$f"
  echo "copied $f"
 done

# Proof: no forced on-device STT
grep -n 'requiresOnDeviceRecognition' "$ROOT/EnglishOnSite/Services/TimedSpeechCapture.swift" | head -5
grep -n 'Слушаю… говори\|▶ Слушать\|prefer server STT\|requiresOnDeviceRecognition = false' \
  "$ROOT/EnglishOnSite/Views/AddMyPhraseView.swift" \
  "$ROOT/EnglishOnSite/Views/PhrasalSpeakPracticeRow.swift" \
  "$ROOT/EnglishOnSite/Services/TimedSpeechCapture.swift" | head -20

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
echo "OK: BUILD SUCCEEDED + install (STT live transcript + TTS handoff)"
