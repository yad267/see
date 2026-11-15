#!/usr/bin/env bash
# 15 common phrasals per get/take/put/turn/look/come/over + verb/page sub-menu (5/page).
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="${1:-$HOME/Developer/Languages-on-site}"
echo "DST=$ROOT"
test -d "$ROOT/EnglishOnSite" || { echo "missing EnglishOnSite"; exit 1; }

mkdir -p "$ROOT/EnglishOnSite/Views" "$ROOT/EnglishOnSite/Resources"
cp -f "$HERE/EnglishOnSite/Views/PhrasalHubView.swift" "$ROOT/EnglishOnSite/Views/PhrasalHubView.swift"
cp -f "$HERE/EnglishOnSite/Resources/phrasals_bank_v1.json" "$ROOT/EnglishOnSite/Resources/phrasals_bank_v1.json"
cp -f "$HERE/EnglishOnSite/Resources/phrasals_general_v1.json" "$ROOT/EnglishOnSite/Resources/phrasals_general_v1.json"

python3 - "$ROOT" <<'PY'
import json, sys
from pathlib import Path
from collections import Counter
root = Path(sys.argv[1]) / "EnglishOnSite" / "Resources"
verbs = ["get","take","put","turn","look","come","over"]
for name in ["phrasals_bank_v1.json","phrasals_general_v1.json"]:
    p = root / name
    d = json.loads(p.read_text())
    items = d["phrasals"]
    def count(v):
        n=0
        for it in items:
            en=it["en"].lower().split()
            r=(it.get("root") or "").lower()
            if v=="over":
                if r=="over" or (en and en[-1]=="over"): n+=1
            elif r==v or (en and en[0]==v): n+=1
        return n
    counts={v:count(v) for v in verbs}
    bad={v:n for v,n in counts.items() if n<15}
    print(name, "total", len(items), counts)
    assert not bad, f"need ≥15 each: {bad}"
print("OK phrasal counts ≥15")
PY

if [[ -f "$ROOT/EnglishOnSite.xcodeproj/project.pbxproj" ]]; then
  if ! grep -q 'phrasals_general_v1.json' "$ROOT/EnglishOnSite.xcodeproj/project.pbxproj"; then
    echo "WARN: add phrasals_general_v1.json to Xcode Resources if Regular track empty"
  fi
fi
echo "DONE — rebuild Language on Site"
