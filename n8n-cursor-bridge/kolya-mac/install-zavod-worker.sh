#!/usr/bin/env bash
# Install / reload always-on «завод основной» worker on Коля Mac.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SCRIPT="$REPO_ROOT/n8n-cursor-bridge/kolya-mac/zavod-worker.sh"
PLIST_SRC="$REPO_ROOT/n8n-cursor-bridge/kolya-mac/com.yad26.zavod-osnovnoy.plist"
PLIST_DST="$HOME/Library/LaunchAgents/com.yad26.zavod-osnovnoy.plist"
LOG_DIR="$HOME/Library/Logs/zavod-osnovnoy"

# Prefer explicit env, else this checkout, else common paths on Kolya.
if [[ -z "${ZAVOD_WORKER_DIR:-}" ]]; then
  if [[ -d "$REPO_ROOT/.git" ]]; then
    ZAVOD_WORKER_DIR="$REPO_ROOT"
  elif [[ -d "$HOME/see/.git" ]]; then
    ZAVOD_WORKER_DIR="$HOME/see"
  elif [[ -d "$HOME/Developer/see/.git" ]]; then
    ZAVOD_WORKER_DIR="$HOME/Developer/see"
  else
    ZAVOD_WORKER_DIR="$REPO_ROOT"
  fi
fi
export ZAVOD_WORKER_DIR

chmod +x "$SCRIPT"
mkdir -p "$HOME/Library/LaunchAgents" "$LOG_DIR"

sed -e "s|REPLACE_HOME|$HOME|g" \
    -e "s|REPLACE_WORKER_DIR|$ZAVOD_WORKER_DIR|g" \
    "$PLIST_SRC" >"$PLIST_DST"

launchctl bootout "gui/$(id -u)/com.yad26.zavod-osnovnoy" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST_DST"
launchctl enable "gui/$(id -u)/com.yad26.zavod-osnovnoy" 2>/dev/null || true
launchctl kickstart -k "gui/$(id -u)/com.yad26.zavod-osnovnoy"

echo "Installed: $PLIST_DST"
echo "Worker name: zavod-osnovnoy"
echo "Worker dir:  $ZAVOD_WORKER_DIR"
echo "Logs:        $LOG_DIR/"
echo "Check:       launchctl print gui/$(id -u)/com.yad26.zavod-osnovnoy | head"
echo "Tail log:    tail -f $LOG_DIR/worker.log"
