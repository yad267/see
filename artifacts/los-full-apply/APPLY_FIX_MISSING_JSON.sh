#!/usr/bin/env bash
# Fix: pbxproj references regular_cefr_pack_v1.json / onsite packs but prior scripts skipped them.
set -euo pipefail
ROOT="${1:-$HOME/Developer/Languages-on-site}"
UDID="${UDID:-00008130-00166C4C0221001C}"
HERE="$(cd "$(dirname "$0")" && pwd)"

mkdir -p "$ROOT/EnglishOnSite/Resources" \
         "$ROOT/EnglishOnSite/Views" \
         "$ROOT/EnglishOnSite/Services" \
         "$ROOT/EnglishOnSite/Models"

# All JSON resources from pack (covers regular_cefr_pack_v1.json etc.)
if [[ -d "$HERE/EnglishOnSite/Resources" ]]; then
  cp -f "$HERE/EnglishOnSite/Resources/"*.json "$ROOT/EnglishOnSite/Resources/" || true
fi

# Swift needed by Home / Phrasal / CEFR / sections
for f in \
  Views/HomeView.swift \
  Views/PhrasalHubView.swift \
  Views/TutorPairsView.swift \
  Views/RegularLanguageRequestView.swift \
  Views/RegularLanguageMenuView.swift \
  Views/OnSiteMenuView.swift \
  Views/LibraryView.swift \
  Views/ReviewSessionView.swift \
  Services/SectionLessonStore.swift \
  Services/RegularCEFRStore.swift \
  Services/OnSiteCEFRStore.swift \
  Services/PhrasalUsageExamplesStore.swift \
  Services/GeminiSiteCoachService.swift \
  Models/AppLearningMode.swift \
  Models/AppSettings.swift \
  Models/CEFRLevel.swift
 do
  [[ -f "$HERE/EnglishOnSite/$f" ]] && cp -f "$HERE/EnglishOnSite/$f" "$ROOT/EnglishOnSite/$f" && echo "copied $f"
 done
test -f "$ROOT/EnglishOnSite/Services/PhrasalUsageExamplesStore.swift" || { echo "MISSING PhrasalUsageExamplesStore.swift"; exit 1; }
test -f "$ROOT/EnglishOnSite/Resources/phrasal_usage_examples_v1.json" || { echo "MISSING phrasal_usage_examples_v1.json"; exit 1; }

# Ensure ReviewSession «Нет»/«Да» always speak EN even if an older local copy wins.
if [[ -f "$ROOT/EnglishOnSite/Views/ReviewSessionView.swift" ]]; then
  if ! grep -q 'speakEN(item.en)' "$ROOT/EnglishOnSite/Views/ReviewSessionView.swift" 2>/dev/null \
     && ! grep -q 'speakEN(items\[index\]' "$ROOT/EnglishOnSite/Views/ReviewSessionView.swift" 2>/dev/null; then
    echo "WARN: ReviewSessionView missing speakEN on grade — pack copy should have fixed it"
  else
    echo "OK ReviewSessionView TTS wired"
  fi
fi
test -f "$ROOT/EnglishOnSite/Models/CEFRLevel.swift" || { echo "MISSING CEFRLevel.swift"; exit 1; }
test -f "$ROOT/EnglishOnSite/Services/OnSiteCEFRStore.swift" || { echo "MISSING OnSiteCEFRStore.swift"; exit 1; }
test -f "$ROOT/EnglishOnSite/Services/RegularCEFRStore.swift" || { echo "MISSING RegularCEFRStore.swift"; exit 1; }

[[ -f "$HERE/EnglishOnSite.xcodeproj/project.pbxproj" ]] && \
  cp -f "$HERE/EnglishOnSite.xcodeproj/project.pbxproj" "$ROOT/EnglishOnSite.xcodeproj/project.pbxproj"

echo "--- verify required JSON ---"
for j in regular_cefr_pack_v1.json onsite_cefr_pack_v1.json \
         lessons_onsite_sections_v1.json lessons_regular_sections_v1.json \
         phrasals_bank_v1.json phrasal_usage_examples_v1.json; do
  if [[ -f "$ROOT/EnglishOnSite/Resources/$j" ]]; then
    echo "OK $j ($(wc -c < "$ROOT/EnglishOnSite/Resources/$j") bytes)"
  else
    echo "MISSING $j"
    exit 1
  fi
done

echo "--- verify unique section dialogues ---"
python3 - <<'PY' "$ROOT"
import json, hashlib, sys
from pathlib import Path
root = Path(sys.argv[1]) / "EnglishOnSite" / "Resources"
for name, track in [("lessons_onsite_sections_v1.json","onsite"),("lessons_regular_sections_v1.json","regular")]:
    pack = json.loads((root/name).read_text())
    by = {L["id"]: L for L in pack["lessons"]}
    for sec in pack["sections"]:
        prefix = f"{track}-{sec['id']}-"
        lids = [i for i in sec["lesson_ids"] if i.startswith(prefix) and i[len(prefix):].isdigit()]
        hashes = [hashlib.md5(json.dumps(by[i]["lines"], sort_keys=True).encode()).hexdigest() for i in lids]
        if len(set(hashes)) != len(hashes):
            raise SystemExit(f"NON-UNIQUE dialogues in {track}/{sec['id']}")
        print(f"OK {track}/{sec['id']} {len(hashes)} unique")
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
echo "OK: BUILD SUCCEEDED + install (missing JSON fixed)"
