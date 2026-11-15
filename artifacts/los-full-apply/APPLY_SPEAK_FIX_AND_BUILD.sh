#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$HOME/Developer/Languages-on-site}"
UDID="${UDID:-00008130-00166C4C0221001C}"
HERE="$(cd "$(dirname "$0")" && pwd)"
test -d "$ROOT/EnglishOnSite" || { echo "FAIL: missing $ROOT/EnglishOnSite"; exit 1; }

# Force overwrite views/services that cause missing-type errors
rsync -a "$HERE/EnglishOnSite/" "$ROOT/EnglishOnSite/"
# Explicit critical copies
for f in \
  Services/GeminiSiteCoachService.swift \
  Services/PhraseSimilarity.swift \
  Views/TutorTalkView.swift \
  Views/TutorSpeakDrillView.swift \
  Views/RoleplayLoopView.swift
 do
  cp -f "$HERE/EnglishOnSite/$f" "$ROOT/EnglishOnSite/$f"
  echo "copied $f"
 done

# Proof SpeakCorrection present on Mac tree
grep -n 'struct SpeakCorrection' "$ROOT/EnglishOnSite/Services/GeminiSiteCoachService.swift" | head -3
# Proof Mac TutorTalk no longer refs missing types
if grep -nE 'RussianSlideResult|SessionCorrectionRow|SessionSummaryPayload|SessionSummaryView' \
  "$ROOT/EnglishOnSite/Views/TutorTalkView.swift" \
  "$ROOT/EnglishOnSite/Views/TutorSpeakDrillView.swift" \
  "$ROOT/EnglishOnSite/Views/RoleplayLoopView.swift"; then
  echo "FAIL: Mac views still reference missing session types"
  exit 1
fi
echo "views_clean_ok"

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
echo "OK: BUILD SUCCEEDED + install"
