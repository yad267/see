#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$HOME/Developer/Languages-on-site}"
UDID="${UDID:-00008130-00166C4C0221001C}"
HERE="$(cd "$(dirname "$0")" && pwd)"

cp -f "$HERE/EnglishOnSite/Views/PhrasalHubView.swift" "$ROOT/EnglishOnSite/Views/PhrasalHubView.swift"
cp -f "$HERE/EnglishOnSite/Views/TutorPairsView.swift" "$ROOT/EnglishOnSite/Views/TutorPairsView.swift"
cp -f "$HERE/EnglishOnSite/Resources/learning_phrasals_site_v1.json" "$ROOT/EnglishOnSite/Resources/learning_phrasals_site_v1.json"
cp -f "$HERE/EnglishOnSite/Resources/phrasals_bank_v1.json" "$ROOT/EnglishOnSite/Resources/phrasals_bank_v1.json"
cp -f "$HERE/EnglishOnSite/Resources/learning_words_v1.json" "$ROOT/EnglishOnSite/Resources/learning_words_v1.json"

# Keep STT fixes if present
for f in Services/TimedSpeechCapture.swift Views/AddMyPhraseView.swift Views/PhrasalSpeakPracticeRow.swift; do
  [[ -f "$HERE/EnglishOnSite/$f" ]] && cp -f "$HERE/EnglishOnSite/$f" "$ROOT/EnglishOnSite/$f" && echo "copied $f"
done

echo "--- verify ---"
python3 - <<PY
import json
from pathlib import Path
root=Path("$ROOT/EnglishOnSite/Resources")
w=json.loads((root/"learning_words_v1.json").read_text())["items"]
print("words", len(w), "with_ru", sum(1 for i in w if str(i.get("ru","")).strip()))
p=json.loads((root/"learning_phrasals_site_v1.json").read_text())["items"]
focus=("get","got","take","turn","ten","over")
print("site_phrasals", len(p), "focus", sum(1 for i in p if any(t in i["en"].lower().split() or t in i["en"].lower() for t in focus)))
PY
rg -n "TutorPairsView|GameKind|preferFocusPhrasals|case \.words" "$ROOT/EnglishOnSite/Views/PhrasalHubView.swift" "$ROOT/EnglishOnSite/Views/TutorPairsView.swift" | head -30

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
echo "OK: BUILD SUCCEEDED + install — Duolingo Фразовые/Слова + get/take/over + 300 words bank"
