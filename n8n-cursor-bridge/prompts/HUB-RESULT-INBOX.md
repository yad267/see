# Hub Result Inbox — отчёты бота → хаб Cursor

## Почему хаб не видел Telegram

`cloud-chat-router` / multi-router создаёт Cursor agent **ключом n8n** и шлёт итог только в Telegram (`TG: Send Result`).  
Этот хаб (`bc-01a13043…`) — **другой** API principal: `batch-fetch` не видит n8n-агентов, а исходящие сообщения бота в Telegram **не приходят** в Cursor chat.

`callbackUrl` / `replyMode` уже были в payload, но **ноды callback не было** — результат всегда только в TG.

## Что добавлено

1. **Store Hub Result** — кладёт последние 30 отчётов в `workflow staticData.hubInbox`.
2. **GET** `https://n8n.yad26ai.uk/webhook/hub-result-inbox?limit=5` — хаб читает inbox (без токена бота).
3. Опционально **POST callbackUrl**, если в ingress передан `callback_url`.
4. Ingress принимает `hub_agent_id` (на будущее).
5. Fix: `Extract IDs` → Wait параллельно с Ack (не через ответ Telegram); Create Agent **POST**; парсинг `agent.id` / `run.id`.

## Импорт на n8n.yad26ai.uk

Переимпортировать/обновить workflow из `n8n-cursor-bridge/multi-router-bridge.json`, Active ON.  
Старый LOS-only Trigger на том же боте — снять Publish (один Trigger).

## Проверка

```bash
curl -sS "https://n8n.yad26ai.uk/webhook/hub-result-inbox?limit=3"
```

После любой задачи через router/Telegram — `items[0].text` должен совпасть с сообщением бота.

Хаб после `accepted:true` поллит этот URL и цитирует `text` пользователю.
