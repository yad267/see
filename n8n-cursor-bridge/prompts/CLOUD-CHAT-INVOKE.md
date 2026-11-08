# Как вызвать из любого cloud Cursor чата

N8N принимает JSON на webhook (после импорта `multi-router-bridge.json` и Active):

`POST https://n8n.yad26ai.uk/webhook/cloud-chat-router`

## Пример: завод основной + скрин

```bash
curl -sS -X POST "https://n8n.yad26ai.uk/webhook/cloud-chat-router" \
  -H "Content-Type: application/json" \
  -H "x-router-secret: $CLOUD_ROUTER_SECRET" \
  -d '{
    "target": "завод основной",
    "text": "Поправь вот это и вот это по скрину",
    "image_base64": "<BASE64_JPEG>",
    "image_mime": "image/jpeg",
    "reply_chat_id": "'"$TELEGRAM_ALLOWED_CHAT_ID"'",
    "reply_mode": "telegram"
  }'
```

## Пример: Languages on Site

```json
{
  "target": "languages on site",
  "text": "Ответь одной строкой: STATUS OK",
  "reply_mode": "telegram",
  "reply_chat_id": "<TELEGRAM_ALLOWED_CHAT_ID>"
}
```

## Пример: финучёт Коля

```json
{
  "target": "финучёт Коля",
  "text": "Добавь напоминание: оплатить страховку завтра",
  "reply_mode": "telegram"
}
```

Из Cursor-чата: попроси агента `POST` на этот webhook (секрет только из env/Secrets, не в чат).
Ответ выполнения приходит в Telegram (тот же whitelist chat), как у существующего моста.
