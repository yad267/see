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

echo "== 2) Install launchd KeepAlive + watchdog for Languages-on-site =="
bash "$SCRIPT_DIR/macos/install-languages-on-site-worker.sh" "$ROOT"
export PATH="$HOME/.local/bin:/usr/local/bin:/opt/homebrew/bin:$PATH"
sleep 2
pgrep -fl "agent worker|languages-on-site-worker|cursor-agent" || echo "WARN: worker process not visible yet — check ~/Library/Logs/languages-on-site/worker.log"

echo "== 3) Apply los-full-apply pack =="
if [[ ! -d "$ROOT/EnglishOnSite" ]]; then
  echo "ERROR: missing $ROOT/EnglishOnSite"
  exit 1
fi
rsync -a "$SCRIPT_DIR/EnglishOnSite/" "$ROOT/EnglishOnSite/"
cp -f "$SCRIPT_DIR/EnglishOnSite.xcodeproj/project.pbxproj" "$ROOT/EnglishOnSite.xcodeproj/project.pbxproj"
echo "voiceES proof:"
grep -nE 'voiceES|WXhpeBU9aWHzJYNLQaSr' "$ROOT/EnglishOnSite/Services/ElevenLabsConfig.swift" | head -5 || true

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
  grep -nE 'error:|BUILD FAILED|failed with' /tmp/eos-build.log | tail -40 || true
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
launchctl print "gui/$(id -u)/$LABEL" 2>/dev/null | head -20 || launchctl list | grep -iE 'languages-on-site|cursor-agent' || true
echo "DONE worker+autostart+install"
