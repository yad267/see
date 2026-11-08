#!/usr/bin/env bash
# Persistent always-on Cursor My Machines worker for «завод основной» on Коля Mac.
# KeepAlive loop: if the worker exits, restart after a short delay.
set -u

NAME="${CURSOR_MACHINE_NAME_ZAVOD:-zavod-osnovnoy}"
DIR="${ZAVOD_WORKER_DIR:-$HOME/Developer/see}"
LOG_DIR="${ZAVOD_LOG_DIR:-$HOME/Library/Logs/zavod-osnovnoy}"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/worker.log"

export PATH="$HOME/.local/bin:/usr/local/bin:/opt/homebrew/bin:$PATH"

echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) start name=$NAME dir=$DIR" >>"$LOG"

if [[ ! -d "$DIR" ]]; then
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) ERROR: worker dir missing: $DIR" >>"$LOG"
  exit 1
fi

# Prefer `agent` CLI (Cursor), fall back to documented aliases if present.
run_worker() {
  if command -v agent >/dev/null 2>&1; then
    agent worker start --name "$NAME" --worker-dir "$DIR"
    return $?
  fi
  if command -v cursor-agent >/dev/null 2>&1; then
    cursor-agent worker start --name "$NAME" --worker-dir "$DIR"
    return $?
  fi
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) ERROR: neither 'agent' nor 'cursor-agent' in PATH" >>"$LOG"
  return 127
}

while true; do
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) launching worker…" >>"$LOG"
  run_worker >>"$LOG" 2>&1
  code=$?
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) worker exited code=$code — restart in 5s" >>"$LOG"
  sleep 5
done
