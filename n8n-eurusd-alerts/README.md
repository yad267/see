# EURUSD Spike + News Alerts (n8n → Telegram)

Бот для ловли ситуаций: **новость / резкий импульс по EURUSD → возможен отскок**.

## Сейчас по рынку (05.10.2026)
Тренд по EURUSD **вниз** (давление на евро: France debt/politics + сильный USD).  
Отскоки возможны как **коррекция в нисходящем тренде**, не как гарантия разворота.

## Что умеет
1. High-impact новости **USD/EUR** (за ~30 мин до и сразу после)
2. Детектор **spike** (если есть Twelve Data API key): движение > X пунктов за N минут
3. Алерт в Telegram с коротким bias

## Что нужно
1. n8n
2. Telegram bot token + chat id
3. (Желательно) бесплатный ключ [Twelve Data](https://twelvedata.com/) для цены EUR/USD

Без Twelve Data будут работать **только news-алерты**.  
Со spike-детектором — то, что тебе нужно для отскока.

## Установка
1. Import `eurusd-spike-alerts.json` в n8n
2. Нода **Config**:
   - `telegramChatId`
   - `spikePips` (по умолчанию `35`)
   - `spikeMinutes` (по умолчанию `5`)
   - `twelveDataApiKey` (если есть)
3. Credentials Telegram в нодах Send Telegram
4. Active = ON
5. Test workflow вручную

## Рекомендуемые пороги для отскока
- M1–M5: `30–40` pips за `3–5` минут
- После CPI/NFP/FOMC: не входи в первую минуту вслепую, жди алерт spike + свою свечную модель

## Важно
Это **алерты**, не автоторговля и не сигнал “100% купи/продай”.
