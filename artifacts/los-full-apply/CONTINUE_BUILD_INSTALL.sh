#!/bin/bash
# Continue after worker+apply already succeeded (skip rg crash).
set -euo pipefail
ROOT="${1:-$HOME/Developer/Languages-on-site}"
UDID="${UDID:-00008130-00166C4C0221001C}"
cd "$ROOT"
echo "voiceES proof:"
grep -nE 'voiceES|WXhpeBU9aWHzJYNLQaSr' EnglishOnSite/Services/ElevenLabsConfig.swift | head -5 || true
rm -rf /tmp/EOSDerived
set +e
xcodebuild -project EnglishOnSite.xcodeproj -scheme EnglishOnSite \
  -destination "id=$UDID" \
  -derivedDataPath /tmp/EOSDerived \
  clean build 2>&1 | tee /tmp/eos-build.log | tail -80
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
echo "Autostart:"
launchctl print "gui/$(id -u)/com.yad267.languages-on-site.worker" 2>/dev/null | head -15 || true
pgrep -fl 'agent worker' || true
