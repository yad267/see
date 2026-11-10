#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$HOME/Developer/Languages-on-site}"
UDID="${UDID:-00008130-00166C4C0221001C}"
HERE="$(cd "$(dirname "$0")" && pwd)"

cp -f "$HERE/EnglishOnSite/Views/HomeView.swift" "$ROOT/EnglishOnSite/Views/"
cp -f "$HERE/EnglishOnSite/Views/PhrasalHubView.swift" "$ROOT/EnglishOnSite/Views/"
cp -f "$HERE/EnglishOnSite/Views/TutorPairsView.swift" "$ROOT/EnglishOnSite/Views/" 2>/dev/null || true
cp -f "$HERE/EnglishOnSite/Views/RegularLanguageRequestView.swift" "$ROOT/EnglishOnSite/Views/" 2>/dev/null || true
cp -f "$HERE/EnglishOnSite/Services/SectionLessonStore.swift" "$ROOT/EnglishOnSite/Services/"
cp -f "$HERE/EnglishOnSite/Services/GeminiSiteCoachService.swift" "$ROOT/EnglishOnSite/Services/" 2>/dev/null || true
cp -f "$HERE/EnglishOnSite/Models/AppLearningMode.swift" "$ROOT/EnglishOnSite/Models/" 2>/dev/null || true
cp -f "$HERE/EnglishOnSite/Models/AppSettings.swift" "$ROOT/EnglishOnSite/Models/" 2>/dev/null || true
cp -f "$HERE/EnglishOnSite/Resources/lessons_onsite_sections_v1.json" "$ROOT/EnglishOnSite/Resources/"
cp -f "$HERE/EnglishOnSite/Resources/lessons_regular_sections_v1.json" "$ROOT/EnglishOnSite/Resources/"
cp -f "$HERE/EnglishOnSite.xcodeproj/project.pbxproj" "$ROOT/EnglishOnSite.xcodeproj/project.pbxproj"

# DO NOT modify ContentView tab set in this apply beyond pbxproj file refs already included.

cd "$ROOT"
rm -rf /tmp/EOSDerived
set +e
xcodebuild -project EnglishOnSite.xcodeproj -scheme EnglishOnSite \
  -destination "id=$UDID" -derivedDataPath /tmp/EOSDerived \
  clean build 2>&1 | tee /tmp/eos-build.log | grep -E 'error:|BUILD SUCCEEDED|BUILD FAILED'
XC=${PIPESTATUS[0]}
set -e
if ! grep -q 'BUILD SUCCEEDED' /tmp/eos-build.log; then
  echo FAIL; grep error: /tmp/eos-build.log | sort -u | head -40; exit 1
fi
APP=$(find /tmp/EOSDerived/Build/Products -name 'EnglishOnSite.app' -type d | head -1)
xcrun devicectl device install app --device "$UDID" "$APP"
echo "OK: Уроки Onsite|Regular sections + Фразовые Onsite|Regular Duolingo"
