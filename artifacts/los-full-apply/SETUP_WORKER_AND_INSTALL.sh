#!/bin/bash
# Run ON Kolya MacBook (second machine) with Languages-on-site checkout.
set -euo pipefail

ROOT="${1:-$HOME/Developer/Languages-on-site}"
UDID="${UDID:-00008130-00166C4C0221001C}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLIST_SRC="$SCRIPT_DIR/macos/com.yad267.languages-on-site.worker.plist"
PLIST_DST="$HOME/Library/LaunchAgents/com.yad267.languages-on-site.worker.plist"
LABEL="com.yad267.languages-on-site.worker"

echo "== 1) Reset hung cursor-agent workers =="
pkill -f "cursor-agent.*worker" || true
pkill -f "agent worker" || true
sleep 1
rm -f "$HOME/.local/share/cursor-agent/worker.lock" || true
rm -f /tmp/cursor-agent-worker*.lock 2>/dev/null || true

echo "== 2) Install launchd KeepAlive for Languages-on-site =="
mkdir -p "$HOME/Library/LaunchAgents"
# Rewrite WorkingDirectory to this user's home Developer path in a temp plist
python3 - <<PY
from pathlib import Path
import os
src = Path("$PLIST_SRC")
dst = Path("$PLIST_DST")
text = src.read_text()
home = os.path.expanduser("~")
# Ensure WorkingDirectory is user home (plist template uses /Users/Shared)
text = text.replace("/Users/Shared", home)
dst.write_text(text)
print("wrote", dst)
PY

launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
launchctl unload "$PLIST_DST" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST_DST" 2>/dev/null || launchctl load -w "$PLIST_DST"
launchctl enable "gui/$(id -u)/$LABEL" 2>/dev/null || true
launchctl kickstart -k "gui/$(id -u)/$LABEL" 2>/dev/null || true

export PATH="$HOME/.local/bin:/usr/local/bin:/opt/homebrew/bin:$PATH"
# Also start once in background if launchd did not attach yet
if ! pgrep -fl "agent worker" >/dev/null 2>&1; then
  nohup agent worker start --name "Languages-on-site" --worker-dir "$ROOT" \
    >/tmp/languages-on-site-worker.manual.log 2>&1 &
  echo "manual worker pid $!"
  sleep 2
fi
pgrep -fl "agent worker" || pgrep -fl "cursor-agent" || echo "WARN: worker process not visible yet"

echo "== 3) Apply los-full-apply pack =="
if [[ ! -d "$ROOT/EnglishOnSite" ]]; then
  echo "ERROR: missing $ROOT/EnglishOnSite"
  exit 1
fi
rsync -a "$SCRIPT_DIR/EnglishOnSite/" "$ROOT/EnglishOnSite/"
cp -f "$SCRIPT_DIR/EnglishOnSite.xcodeproj/project.pbxproj" "$ROOT/EnglishOnSite.xcodeproj/project.pbxproj"
echo "voiceES proof:"
rg -n 'voiceES|WXhpeBU9aWHzJYNLQaSr' "$ROOT/EnglishOnSite/Services/ElevenLabsConfig.swift" | head -5

echo "== 4) Clean + xcodebuild + install UDID=$UDID =="
cd "$ROOT"
rm -rf /tmp/EOSDerived
set +e
xcodebuild -project EnglishOnSite.xcodeproj -scheme EnglishOnSite \
  -destination "id=$UDID" \
  -derivedDataPath /tmp/EOSDerived \
  clean build 2>&1 | tee /tmp/eos-build.log | tail -60
BUILD_RC=${PIPESTATUS[0]}
set -e
APP=$(find /tmp/EOSDerived/Build/Products -name 'EnglishOnSite.app' -type d 2>/dev/null | head -1 || true)
echo "BUILD_RC=$BUILD_RC APP=$APP"
if [[ -z "${APP:-}" || "$BUILD_RC" -ne 0 ]]; then
  echo "INSTALL: FAIL (build)"
  rg -n "error:|BUILD FAILED|failed with" /tmp/eos-build.log | tail -40 || true
  exit 1
fi
set +e
xcrun devicectl device install app --device "$UDID" "$APP" 2>&1 | tee /tmp/eos-install.log
INST_RC=${PIPESTATUS[0]}
set -e
if [[ "$INST_RC" -eq 0 ]]; then
  echo "INSTALL: OK"
else
  echo "INSTALL: FAIL"
  tail -40 /tmp/eos-install.log || true
  exit 1
fi

echo "== 5) Autostart check =="
launchctl print "gui/$(id -u)/$LABEL" 2>/dev/null | head -20 || launchctl list | rg -i "languages-on-site|cursor-agent" || true
echo "DONE worker+autostart+install"
