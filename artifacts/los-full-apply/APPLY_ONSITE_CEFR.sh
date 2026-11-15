#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$HOME/Developer/Languages-on-site}"
UDID="${UDID:-00008130-00166C4C0221001C}"
HERE="$(cd "$(dirname "$0")" && pwd)"

cp -f "$HERE/EnglishOnSite/Views/OnSiteMenuView.swift" "$ROOT/EnglishOnSite/Views/OnSiteMenuView.swift"
cp -f "$HERE/EnglishOnSite/Views/HomeView.swift" "$ROOT/EnglishOnSite/Views/HomeView.swift"
cp -f "$HERE/EnglishOnSite/Services/OnSiteCEFRStore.swift" "$ROOT/EnglishOnSite/Services/OnSiteCEFRStore.swift"
cp -f "$HERE/EnglishOnSite/Resources/onsite_cefr_pack_v1.json" "$ROOT/EnglishOnSite/Resources/onsite_cefr_pack_v1.json"
cp -f "$HERE/EnglishOnSite.xcodeproj/project.pbxproj" "$ROOT/EnglishOnSite.xcodeproj/project.pbxproj"

echo "--- verify ---"
rg -n 'On site|OnSiteMenuView|CEFRLevel' "$ROOT/EnglishOnSite/Views/HomeView.swift" "$ROOT/EnglishOnSite/Views/OnSiteMenuView.swift" | head -20
python3 - <<PY
import json
from pathlib import Path
from collections import Counter
items=json.loads(Path("$ROOT/EnglishOnSite/Resources/onsite_cefr_pack_v1.json").read_text())["items"]
print("items",len(items), Counter(i["cefr"] for i in items))
PY

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
echo "OK: BUILD SUCCEEDED + install — On site CEFR menu A1–C2"
