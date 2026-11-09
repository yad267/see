#!/bin/bash
set -euo pipefail
ROOT="${1:-$HOME/Developer/Languages-on-site}"
UDID="00008130-00166C4C0221001C"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "Applying to $ROOT"
rsync -a "$SCRIPT_DIR/EnglishOnSite/" "$ROOT/EnglishOnSite/"
cp -f "$SCRIPT_DIR/EnglishOnSite.xcodeproj/project.pbxproj" "$ROOT/EnglishOnSite.xcodeproj/project.pbxproj"
cd "$ROOT"
echo "voiceES:"; rg -n 'voiceES' EnglishOnSite/Services/ElevenLabsConfig.swift | head -3
echo "Clean build..."
xcodebuild -project EnglishOnSite.xcodeproj -scheme EnglishOnSite \
  -destination "id=$UDID" \
  -derivedDataPath /tmp/EOSDerived \
  clean build | tee /tmp/eos-build.log | tail -40
APP=$(find /tmp/EOSDerived/Build/Products -name 'EnglishOnSite.app' -type d | head -1)
echo "APP=$APP"
if [[ -z "$APP" ]]; then echo "BUILD FAIL: no .app"; exit 1; fi
echo "Installing..."
xcrun devicectl device install app --device "$UDID" "$APP"
echo "INSTALL_OK"
