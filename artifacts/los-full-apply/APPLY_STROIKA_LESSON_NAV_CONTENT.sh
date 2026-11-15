#!/usr/bin/env bash
# Fix: Стройка lesson tap bounced to menu + cloned "We need this on site…" dialogues.
# Copies fixed HomeView (destination NavigationLink → PlayerView) + unique section JSON.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="${1:-$HOME/Developer/Languages-on-site}"

echo "DST=$ROOT"
test -d "$ROOT/EnglishOnSite" || { echo "missing EnglishOnSite under $ROOT"; exit 1; }

mkdir -p "$ROOT/EnglishOnSite/Views" "$ROOT/EnglishOnSite/Resources" "$ROOT/EnglishOnSite/Services"

cp -f "$HERE/EnglishOnSite/Views/HomeView.swift" "$ROOT/EnglishOnSite/Views/HomeView.swift"
cp -f "$HERE/EnglishOnSite/Services/SectionLessonStore.swift" "$ROOT/EnglishOnSite/Services/SectionLessonStore.swift"
cp -f "$HERE/EnglishOnSite/Resources/lessons_onsite_sections_v1.json" "$ROOT/EnglishOnSite/Resources/lessons_onsite_sections_v1.json"
cp -f "$HERE/EnglishOnSite/Resources/lessons_regular_sections_v1.json" "$ROOT/EnglishOnSite/Resources/lessons_regular_sections_v1.json"

python3 - "$ROOT" <<'PY'
import json, sys
from pathlib import Path
root = Path(sys.argv[1])
onsite = json.loads((root / "EnglishOnSite/Resources/lessons_onsite_sections_v1.json").read_text())
sec = next(s for s in onsite["sections"] if s["id"] == "construction")
lessons = {x["id"]: x for x in onsite["lessons"]}
ids = sec["lesson_ids"]
sigs = []
missing = []
for i in ids:
    L = lessons.get(i)
    if not L:
        missing.append(i)
        continue
    sigs.append(tuple(ln.get("en") for ln in L.get("lines") or []))
assert not missing, f"missing lessons: {missing}"
assert len(set(sigs)) == len(sigs), f"cloned dialogues still present: unique={len(set(sigs))} of {len(sigs)}"
firsts = [lessons[i]["lines"][0]["en"] for i in ids]
assert "We need this on site for construction." not in firsts, "old clone stub still in pack"
print(f"OK construction {len(ids)} lessons, {len(set(sigs))} unique dialogues")
print("sample:", firsts[0], "|", firsts[1] if len(firsts) > 1 else "")
PY

# Ensure JSON is in the Xcode resources copy phase if pbxproj lists resources explicitly
if [[ -f "$ROOT/EnglishOnSite.xcodeproj/project.pbxproj" ]]; then
  if ! grep -q 'lessons_onsite_sections_v1.json' "$ROOT/EnglishOnSite.xcodeproj/project.pbxproj"; then
    echo "WARN: lessons_onsite_sections_v1.json not referenced in pbxproj — add to Resources if bundle misses it"
  else
    echo "OK pbxproj references lessons_onsite_sections_v1.json"
  fi
fi

echo "DONE — rebuild/install Language on Site on device"
