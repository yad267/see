# YouTube Thumbnail Factory

Полуавтомат: тема ролика → 3 концепции превью → Telegram.

Ориентир стиля: яркие бизнес-превью (Hartmann / Ситников).

## Поток
1. Пишешь боту: `Превью: <тема ролика>`
2. n8n через AI делает 3 варианта
3. В Telegram приходит:
   - текст на обложке
   - сцена
   - English image prompt
   - почему кликнут
4. Ты выбираешь лучший и собираешь в Canva/Photoshop за 10–20 мин

## Файлы
- `thumbnail-factory.json` — n8n workflow
- `PROMPT.md` — master prompt для AI

## Установка
1. Import JSON в n8n
2. Подключи Telegram bot + OpenAI/Gemini credentials
3. В Config впиши `telegramChatId`
4. Active ON

## Пример сообщения боту
```text
Превью: Как выйти на 10к евро в месяц в Европе
```

## Апгрейд v2
- автогенерация картинки (Flux/OpenAI Images)
- кнопки ✅/❌ в Telegram
- сохранение в Google Drive
- связка с заводом шортов
