#!/usr/bin/env bash
# Bootstrap local «финучёт Коля» data dir on this Mac (NOT Коля Mac).
set -euo pipefail

ROOT="${FINUCHET_ROOT:-$HOME/Developer/finuchet-kolya}"
DATA="$ROOT/data"
mkdir -p "$DATA"
if [[ ! -f "$DATA/reminders.json" ]]; then
  cp "$(cd "$(dirname "$0")" && pwd)/reminders.sample.json" "$DATA/reminders.json"
  echo "Created $DATA/reminders.json"
else
  echo "Exists: $DATA/reminders.json (left untouched)"
fi

# Optional: My Machines worker so cloud/N8N can address «финучёт Коля» by machine name.
cat >"$ROOT/README.md" <<EOF
# финучёт Коля (local on this Mac)

- Data: \`$DATA/reminders.json\`
- Machine name for Cursor My Machines: \`finuchet-kolya\`
- Start worker (keep terminal open OR add LaunchAgent similar to zavod):

\`\`\`bash
agent worker start --name finuchet-kolya --worker-dir "$ROOT"
\`\`\`

Unfinished reminders (done=false) are reported by n8n workflow
\`finuchet-unfinished-report.json\` → Telegram «Коля ассистент».
EOF

echo "Ready: $ROOT"
echo "Optional worker: agent worker start --name finuchet-kolya --worker-dir \"$ROOT\""
