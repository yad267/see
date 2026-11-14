#!/usr/bin/env bash
# Install / reload always-on Languages-on-site worker on Kolya Mac (survives reboot).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="${1:-${LOS_WORKER_DIR:-$HOME/Developer/Languages-on-site}}"
LABEL="com.yad267.languages-on-site.worker"
PLIST_SRC="$SCRIPT_DIR/com.yad267.languages-on-site.worker.plist"
PLIST_DST="$HOME/Library/LaunchAgents/${LABEL}.plist"
WRAPPER_DST="$ROOT/macos/languages-on-site-worker.sh"
LOG_DIR="$HOME/Library/Logs/languages-on-site"

if [[ ! -d "$ROOT" ]]; then
  echo "ERROR: project dir missing: $ROOT"
  echo "Pass path: bash install-languages-on-site-worker.sh /path/to/Languages-on-site"
  exit 1
fi

mkdir -p "$HOME/Library/LaunchAgents" "$LOG_DIR" "$ROOT/macos"
cp -f "$SCRIPT_DIR/languages-on-site-worker.sh" "$WRAPPER_DST"
chmod +x "$WRAPPER_DST"

sed -e "s|REPLACE_HOME|$HOME|g" \
    -e "s|REPLACE_WORKER_DIR|$ROOT|g" \
    -e "s|REPLACE_SCRIPT|$WRAPPER_DST|g" \
    "$PLIST_SRC" >"$PLIST_DST"

# Soft-reset hung workers before bootstrap
pkill -f "cursor-agent.*worker" 2>/dev/null || true
pkill -f "agent worker" 2>/dev/null || true
rm -f "$HOME/.local/share/cursor-agent/worker.lock" 2>/dev/null || true

launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
launchctl unload "$PLIST_DST" 2>/dev/null || true
if launchctl bootstrap "gui/$(id -u)" "$PLIST_DST" 2>/dev/null; then
  :
else
  launchctl load -w "$PLIST_DST"
fi
launchctl enable "gui/$(id -u)/$LABEL" 2>/dev/null || true
launchctl kickstart -k "gui/$(id -u)/$LABEL" 2>/dev/null || true

echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) install-languages-on-site-worker: plist=$PLIST_DST wrapper=$WRAPPER_DST" >>"$LOG_DIR/worker.log"

echo "Installed: $PLIST_DST"
echo "Wrapper:   $WRAPPER_DST"
echo "Worker:    Languages-on-site"
echo "Dir:       $ROOT"
echo "Logs:      $LOG_DIR/worker.log"
echo "Check:     launchctl print gui/$(id -u)/$LABEL | head -40"
echo "Tail:      tail -f $LOG_DIR/worker.log"
