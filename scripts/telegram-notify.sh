#!/usr/bin/env bash
# Send short status/result/error to Telegram chat 217250285.
# 1) Prefer TELEGRAM_BOT_TOKEN + Bot API
# 2) Fallback: n8n webhook hub-telegram-notify
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG="${TELEGRAM_CONFIG_FILE:-$ROOT/.telegram-config}"
N8N_NOTIFY_URL="${N8N_TELEGRAM_NOTIFY_URL:-https://n8n.yad26ai.uk/webhook/hub-telegram-notify}"

if [[ -f "$CONFIG" ]]; then
  while IFS= read -r line || [[ -n "$line" ]]; do
    case "$line" in
      ''|\#*) continue ;;
      *=*)
        key="${line%%=*}"; val="${line#*=}"
        if [[ -z "${!key:-}" ]]; then export "$key=$val"; fi
        ;;
    esac
  done < "$CONFIG"
fi

TOKEN="${TELEGRAM_BOT_TOKEN:-}"
CHAT_ID="${TELEGRAM_CHAT_ID:-217250285}"
KIND="${1:-status}"
shift || true
TEXT="${*:-}"
[[ -n "$TEXT" ]] || TEXT="$(cat 2>/dev/null || true)"
[[ -n "$TEXT" ]] || { echo "telegram-notify: empty message" >&2; exit 2; }

case "$KIND" in
  result|ok|success) PREFIX="✅ RESULT" ;;
  error|fail|failed) PREFIX="❌ ERROR" ;;
  *) PREFIX="ℹ️ STATUS" ;;
esac
BODY=$(printf '%s · Languages on site\n%s' "$PREFIX" "$TEXT")
BODY="${BODY:0:3500}"

if [[ -n "$TOKEN" ]]; then
  RESP="$(curl -sS --max-time 20 -X POST \
    "https://api.telegram.org/bot${TOKEN}/sendMessage" \
    --data-urlencode "chat_id=${CHAT_ID}" \
    --data-urlencode "text=${BODY}" \
    --data-urlencode "disable_web_page_preview=true")"
  echo "$RESP"
  echo "$RESP" | grep -q '"ok":true' || { echo "telegram-notify: bot API failed" >&2; exit 1; }
  exit 0
fi

PAYLOAD=$(CHAT_ID="$CHAT_ID" BODY="$BODY" python3 - <<'PY'
import json, os
print(json.dumps({"chat_id": os.environ["CHAT_ID"], "text": os.environ["BODY"]}, ensure_ascii=False))
PY
)
RESP="$(curl -sS --max-time 30 -X POST "$N8N_NOTIFY_URL" \
  -H 'Content-Type: application/json' \
  -d "$PAYLOAD")"
echo "$RESP"
if echo "$RESP" | grep -q '"ok":\s*true'; then
  exit 0
fi
echo "telegram-notify: n8n fallback failed — activate Hub Telegram Notify webhook on n8n" >&2
exit 1
