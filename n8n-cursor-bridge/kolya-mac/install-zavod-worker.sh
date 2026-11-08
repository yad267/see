#!/usr/bin/env bash
# Install / reload always-on «завод основной» worker on Коля Mac.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SCRIPT="$REPO_ROOT/n8n-cursor-bridge/kolya-mac/zavod-worker.sh"
PLIST_SRC="$REPO_ROOT/n8n-cursor-bridge/kolya-mac/com.yad26.zavod-osnovnoy.plist"
PLIST_DST="$HOME/Library/LaunchAgents/com.yad26.zavod-osnovnoy.plist"
LOG_DIR="$HOME/Library/Logs/zavod-osnovnoy"

chmod +x "$SCRIPT"
mkdir -p "$HOME/Library/LaunchAgents" "$LOG_DIR"

sed "s|REPLACE_HOME|$HOME|g" "$PLIST_SRC" >"$PLIST_DST"

launchctl bootout "gui/$(id -u)/com.yad26.zavod-osnovnoy" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST_DST"
launchctl enable "gui/$(id -u)/com.yad26.zavod-osnovnoy" 2>/dev/null || true
launchctl kickstart -k "gui/$(id -u)/com.yad26.zavod-osnovnoy"

echo "Installed: $PLIST_DST"
echo "Worker name: zavod-osnovnoy"
echo "Worker dir:  ${ZAVOD_WORKER_DIR:-$HOME/Developer/see}"
echo "Logs:        $LOG_DIR/"
echo "Check:       launchctl print gui/$(id -u)/com.yad26.zavod-osnovnoy | head"
echo "Tail log:    tail -f $LOG_DIR/worker.log"
