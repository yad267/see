# Kolya Music Bot

Личный музыкальный архив в **закрытой форум-группе** (только invite-link).

## Что делает бот

1. **`/setup`** — сам создаёт топики-жанры и запоминает их id  
2. Кидаешь трек → раскладывает по папке (или Inbox + кнопки)  
3. **`/find`** — отдельный поиск (жанр / название / год) → авто или руками в папку  

## Что делаешь ты (минимум)

1. [@BotFather](https://t.me/BotFather) → `/newbot` → скопируй токен  
2. Создай **private** группу → включи **Topics**  
3. Добавь бота **админом** (нужно право **Manage Topics**)  
4. На машине:

```bash
cd kolya_music_bot
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# впиши BOT_TOKEN=...
python -m bot.main
```

5. В группе напиши **`/setup`** — бот создаст Inbox, Hip-Hop, House, Techno, Disco/Funk, Other  
6. Кинь тестовый hip-hop трек  

Всё. `MUSIC_GROUP_ID` и `TOPIC_*` вручную собирать не нужно — пишет в `data/topics.json`.

## Команды

| Команда | Зачем |
|---------|--------|
| `/setup` | Создать папки в группе (один раз) |
| `/start` | Справка |
| `/genres` | Список папок |
| `/find hiphop` | Поиск |
| `переложить в hiphop` | Reply на трек — ручной перенос |

## Тесты без Telegram

```bash
pytest -q
```

## Важно

- Группа закрытая — чтобы не светить архив наружу  
- Чужие музыкальные каналы бот сам по интернету не ищет; только whitelist, если добавишь  
- Это не RentKolyaBot и не завод шортов  
