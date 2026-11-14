#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$HOME/Developer/Languages-on-site}"
UDID="${UDID:-00008130-00166C4C0221001C}"
HERE="$(cd "$(dirname "$0")" && pwd)"

cp -f "$HERE/EnglishOnSite/Resources/onsite_cefr_pack_v1.json" "$ROOT/EnglishOnSite/Resources/"
cp -f "$HERE/EnglishOnSite/Resources/SitePhraseBank.json" "$ROOT/EnglishOnSite/Resources/"
cp -f "$HERE/EnglishOnSite/Resources/lessons_onsite_sections_v1.json" "$ROOT/EnglishOnSite/Resources/"
[[ -f "$HERE/EnglishOnSite/Resources/learning_sentences_v1.json" ]] && cp -f "$HERE/EnglishOnSite/Resources/learning_sentences_v1.json" "$ROOT/EnglishOnSite/Resources/"

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
echo "OK: site command phrases (go get / bring / cut / give me)"
