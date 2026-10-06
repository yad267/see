# Roscrea Housing Hunter — полная логика

Цель: в Telegram приходит **только реально доступное жильё по Roscrea**, максимально быстро.

## Что считается “доступным”
Объявление проходит в TG только если:
1. Найдено на источнике сейчас
2. В тексте/адресе есть **Roscrea** (или страница Roscrea)
3. Это аренда (rent / to let / sharing)
4. Страница объявления ещё **PUBLISHED / live**
5. Этого `id/url` ещё не было в памяти бота

Иначе — молчит.

## Источники (реальное время)
| Источник | Как |
|---|---|
| Daft Roscrea rent | polling каждые **2 мин** |
| Daft Tipperary (фильтр Roscrea) | polling |
| Daft Roscrea houses/apartments | polling |
| Daft sharing Roscrea | polling |
| MyHome Roscrea house/apartment | polling |
| Daft Email Alerts | **IMAP мгновенно** (самый быстрый канал) |

Facebook Marketplace официально нестабилен для бота — не используем как основу.

## Поток от и до
```
новые объявления
   ↓
сбор с Daft/MyHome + письмо Daft
   ↓
нормализация (id, title, price, url, seller)
   ↓
фильтр: Roscrea + rent + budget/beds
   ↓
verify live (страница объявления)
   ↓
dedupe (staticData / Sheet)
   ↓
Telegram RENTALS-URGENT
   ↓
ассистент звонит / enquiry < 2 мин
```

## Файлы
1. `roscrea-realtime-hunt.json` — быстрый polling + verify + Telegram  
2. `roscrea-email-instant.json` — Daft email → Telegram  
3. Этот README

Импортируй **оба** workflow. Вместе = быстрее всего.

## Настройка за 10 минут
1. Создай Telegram-чат `RENTALS-URGENT` (ты + ассистент)
2. Создай Telegram-бота, возьми chat id
3. На Daft:
   - Saved Search: Roscrea rent
   - Email Alerts ON
   - Письма на отдельный Gmail
4. Import обоих JSON в n8n
5. В **Config** впиши:
   - `telegramChatId`
   - `maxMonthlyEuro` (0 = без лимита)
   - `minBeds`
6. В email-workflow подключи IMAP Gmail
7. Active ON на обоих
8. Test Workflow вручную

## Что приходит в Telegram
```
🚨 ROSCREA LIVE RENTAL

📍 Limerick Rd, Roscrea
💶 €370 per week (~€1603/mo) · 2 Bed · House
👤 Claudia
🟢 Status: AVAILABLE NOW
📡 Source: daft

🔗 https://www.daft.ie/for-rent/...

ACTION NOW:
1) Open link
2) Call if phone visible
3) Else Enquire immediately

Script:
Hi, I'm interested in the Roscrea rental on Daft.
Is it still available for a viewing this week?
```

## Чтобы было “очень быстро”
- polling = **2 минуты**
- email alerts Daft = почти сразу
- ассистент с включёнными уведомлениями
- не раздувать фильтры на весь Tipperary без слова Roscrea

## Антиспам
- один `listing id` = одно сообщение
- снятые/expired не отправляются
- повторная публикация того же id не спамит
