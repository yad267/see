# Kolya Music Bot

Личный музыкальный архив в **закрытой форум-группе Telegram** (только invite-link).

Не связан с RentKolyaBot и заводом шортов.

## Идея

Два модуля:

1. **Поисковик** (`/find`) — жанр / название / год по личному индексу.
2. **Раскладка** — после загрузки или поиска трек уходит в топик-«папку» **авто** или **вручную**.

## Топики v1

| Топик | Ключ |
|--------|------|
| Inbox | `inbox` |
| Hip-Hop | `hiphop` |
| House | `house` |
| Techno | `techno` |
| Disco / Funk | `disco` |
| Other | `other` |

## Быстрый старт

```bash
cd kolya_music_bot
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# заполнить BOT_TOKEN, MUSIC_GROUP_ID, TOPIC_*
python -m bot.main
```

### Настройка Telegram

1. Создать **закрытую** группу → включить Topics.
2. Создать топики как в таблице выше.
3. Добавить бота админом (сообщения + управление темами по необходимости).
4. Узнать `message_thread_id` каждого топика (переслать пост из топика боту-утилите или посмотреть в update) → прописать в `.env`.
5. Группа только по пригласительной ссылке.

### Команды

- `/start` — справка
- `/genres` — список папок
- `/find hiphop` / `/find lose yourself` / `/find 2010`
- Reply на трек: `переложить в hiphop`

### Поток

```
upload или /find
    → кандидаты / классификация
    → авто в топик  ИЛИ  кнопки «Выбрать папку»
    → Hip-Hop / House / … / Inbox
```

Индекс источников: твои загрузки + опциональный **whitelist** `SOURCE_CHANNEL_IDS` (без обхода всего Telegram).

## Тесты без токена

```bash
cd kolya_music_bot
pytest -q
```

## Дальше

- sqlite вместо памяти
- LLM-классификатор при низкой уверенности
- индексатор whitelist-каналов
- open sources (Jamendo) как отдельный провайдер поиска
