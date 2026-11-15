#!/usr/bin/env bash
# Always-on Cursor worker for Languages-on-site on Kolya Mac.
# launchd KeepAlive + this loop: if the worker exits, log and restart.
set -u

NAME="${CURSOR_MACHINE_NAME_LOS:-Languages-on-site}"
DIR="${LOS_WORKER_DIR:-$HOME/Developer/Languages-on-site}"
LOG_DIR="${LOS_LOG_DIR:-$HOME/Library/Logs/languages-on-site}"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/worker.log"

export PATH="$HOME/.local/bin:/usr/local/bin:/opt/homebrew/bin:$PATH"

echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) start name=$NAME dir=$DIR" >>"$LOG"

if [[ ! -d "$DIR" ]]; then
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) ERROR: worker dir missing: $DIR — edit LOS_WORKER_DIR or install project at ~/Developer/Languages-on-site" >>"$LOG"
  exit 1
fi

run_worker() {
  # Clear stale lock so relaunch can bind
  rm -f "$HOME/.local/share/cursor-agent/worker.lock" 2>/dev/null || true
  if command -v agent >/dev/null 2>&1; then
    agent worker start --name "$NAME" --worker-dir "$DIR"
    return $?
  fi
  if command -v cursor-agent >/dev/null 2>&1; then
    cursor-agent worker start --name "$NAME" --worker-dir "$DIR"
    return $?
  fi
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) ERROR: neither 'agent' nor 'cursor-agent' in PATH — install Cursor CLI agent" >>"$LOG"
  return 127
}

while true; do
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) launching worker…" >>"$LOG"
  set +e
  run_worker >>"$LOG" 2>&1
  code=$?
  set -e
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) worker exited code=$code — restart in 5s" >>"$LOG"
  sleep 5
done
