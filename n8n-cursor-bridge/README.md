# Multi-router: cloud / Telegram → Languages on site · завод основной · финучёт Коля

Не ломает существующий мост `telegram-cursor-bridge.json` (Languages on site).
Новый workflow `multi-router-bridge.json` добавляет маршрутизацию **по имени цели** и вход из **любого cloud-чата**.

## Архитектура

```
Any cloud Cursor chat ──POST──► N8N /webhook/cloud-chat-router ─┐
Telegram (existing bot) ──────► N8N Telegram Trigger ─────────────┼─► route by name
                                                                  ▼
                         ┌─ languages-on-site → My Machine «Languages-on-site»
                         ├─ завод основной    → My Machine «zavod-osnovnoy» (Коля Mac, always-on)
                         └─ финучёт Коля      → My Machine «finuchet-kolya» (this Mac, local data)
                                                                  ▼
                                              poll Cursor Agents API → reply Telegram
```

Таблица маршрутов: `routes.json`.

## 1) Коля Mac — постоянный «завод основной»

```bash
cd ~/Developer/see   # или путь к клону этого репо
bash n8n-cursor-bridge/kolya-mac/install-zavod-worker.sh
tail -f ~/Library/Logs/zavod-osnovnoy/worker.log
```

Это ставит **LaunchAgent** `com.yad26.zavod-osnovnoy` (RunAtLoad + KeepAlive):
цикл `agent worker start --name zavod-osnovnoy` — не one-off скрипт.

Worker должен быть онлайн, иначе Create Agent на `zavod-osnovnoy` некуда посадить.

## 2) this Mac — финучёт Коля (локально)

```bash
bash n8n-cursor-bridge/this-mac/finuchet/install-finuchet-local.sh
# optional persistent machine:
agent worker start --name finuchet-kolya --worker-dir ~/Developer/finuchet-kolya
```

Данные: `~/Developer/finuchet-kolya/data/reminders.json` (`done: false` = незакрыто).

Отчёт незакрытых → Telegram «Коля ассистент»: импорт `finuchet-unfinished-report.json`.

## 3) N8N (https://n8n.yad26ai.uk)

1. Import **`multi-router-bridge.json`** (новый workflow; старый Languages bridge можно оставить Inactive, если оба слушают один Telegram webhook — активен должен быть только один Telegram Trigger на бота).
2. Credentials как раньше: Telegram API + HTTP Basic (Cursor API key, password empty).
3. Environment variables (Settings → Variables):

| Variable | Meaning |
|----------|---------|
| `TELEGRAM_ALLOWED_CHAT_ID` | whitelist chat |
| `TELEGRAM_BOT_TOKEN` | bot token |
| `CURSOR_MACHINE_NAME` / `_EOS` | `Languages-on-site` |
| `CURSOR_REPO_URL` / `_EOS` | Languages-on-site git HTTPS |
| `CURSOR_MACHINE_NAME_ZAVOD` | `zavod-osnovnoy` |
| `CURSOR_REPO_URL_ZAVOD` | repo для завода (часто `https://github.com/yad267/see.git`) |
| `CURSOR_MACHINE_NAME_FINUCHET` | `finuchet-kolya` |
| `CURSOR_REPO_URL_FINUCHET` | repo/path для финучёта |
| `DEFAULT_ROUTE` | `languages-on-site` если имя цели не указано |
| `CLOUD_ROUTER_SECRET` | shared secret for cloud webhook |
| `KOLYA_ASSISTANT_CHAT_ID` | куда слать отчёт незакрытых |
| `FINUCHET_REMINDERS_URL` | HTTPS URL JSON reminders (tunnel/hosting) |

4. Activate workflow.
5. Telegram webhook (если ещё не стоит):

```
https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://n8n.yad26ai.uk/webhook/telegram-cursor-bridge-webhook
```

Cloud ingress path: `https://n8n.yad26ai.uk/webhook/cloud-chat-router`  
(см. `prompts/CLOUD-CHAT-INVOKE.md`).

## Как дергать

### Из Telegram
Первая строка / префикс = имя цели:

- `завод основной: поправь по скрину …` (+ photo)
- `languages on site: STATUS OK`
- `финучёт: напомни оплатить …`

### Из любого cloud Cursor чата
Агент делает `POST` на `cloud-chat-router` с `target`, `text`, опционально `image_base64`, `reply_chat_id`.
Результат уходит в Telegram (как у текущего моста). Cursor API webhooks для обратной доставки в cloud-чат пока нет — канал ответа = Telegram.

### Прямой Create Agent (без N8N)
Cloud chat с Cursor API key:

```json
{
  "prompt": { "text": "…", "images": [] },
  "name": "завод основной",
  "env": { "type": "machine", "name": "zavod-osnovnoy" },
  "repos": [{ "url": "https://github.com/yad267/see.git" }],
  "mode": "agent"
}
```

Предпочтительный путь для единообразия — через N8N router.

## Что ещё заполнить вручную

- [ ] Cursor Personal API key в n8n Basic Auth
- [ ] Telegram bot token + allowed chat id
- [ ] `CLOUD_ROUTER_SECRET`
- [ ] `CURSOR_REPO_URL_*` если отличаются от дефолтов
- [ ] На Коле: установлен LaunchAgent, worker online
- [ ] На this Mac: `reminders.json` + опционально worker `finuchet-kolya`
- [ ] `FINUCHET_REMINDERS_URL` (доступный с n8n HTTPS к JSON) + `KOLYA_ASSISTANT_CHAT_ID`
- [ ] В n8n: только один active Telegram Trigger на бота

## Файлы

| Path | Role |
|------|------|
| `telegram-cursor-bridge.json` | исходный Languages-only мост (сохранён) |
| `multi-router-bridge.json` | Telegram + cloud webhook + route by name |
| `routes.json` | канон имён/алиасов/машин |
| `finuchet-unfinished-report.json` | периодический отчёт незакрытых |
| `kolya-mac/*` | always-on worker завод |
| `this-mac/finuchet/*` | локальный финучёт |
| `prompts/CLOUD-CHAT-INVOKE.md` | примеры вызова |
