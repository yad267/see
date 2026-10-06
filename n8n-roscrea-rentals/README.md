# Roscrea Housing Hunter v2 — оценка GPT + наша лучшая версия

## Справедливая оценка предложения ChatGPT

### Что у GPT правильно (берём)
| Идея | Оценка | Решение |
|---|---|---|
| Не полагаться на 5-мин бот | ✅ | polling **1–2 мин** + Daft email instant |
| Daft + MyHome как ядро | ✅ | обязательно |
| Только новые + dedupe | ✅ | ID/URL в staticData + Sheet |
| Богатый Telegram-алерт | ✅ | NEW PROPERTY + время + возраст |
| Радиус вокруг Roscrea | ✅ | Roscrea + Templemore/Birr/Moneygall/Shinrone/Nenagh |
| Facebook важен, но сложно | ✅ | Phase 2, не обещать “все группы” |
| Спросить budget / radius / chat_id | ✅ | Config |

### Что у GPT слабо / раздуто
| Идея | Оценка | Почему |
|---|---|---|
| Сразу 10+ источников | ⚠️ | половина даст шум и ломается |
| Rent.ie / Property.ie | ⚠️ | вторичны, мало уникального vs Daft |
| Reddit / community forums | ❌ сейчас | почти нет оперативных объявлений Roscrea |
| Google/Bing как realtime | ❌ | минуты/часы задержки, не “23 sec ago” |
| Facebook Marketplace “обязательно” в v1 | ❌ | баны, логин, закрытые группы |
| “нормальная система” без MVP | ⚠️ | лучше ядро → расширение |

**Вердикт:** направление верное, но GPT продаёт “идеальную систему”.  
Нам нужна **боевая v2**: скорость + покрытие + минимум хрупкости.

---

## Наша улучшенная архитектура (v2)

### Priority 1 — must have (уже собираем)
1. Daft Roscrea + nearby towns  
2. MyHome Roscrea  
3. Daft Email Alerts → IMAP instant  
4. Verify listing still AVAILABLE  
5. Dedupe DB  
6. Telegram urgent format  

### Priority 2 — next
- Local agents: Sherry FitzGerald Fogarty / REA Seamus Browne pages  
- Public FB groups via manual join + approved scrapers/Apify later  

### Priority 3 — later / optional
- Rent.ie / Property.ie  
- Google Alerts as backup, не как realtime  

### Не делаем в v1/v2
- обещание мониторинга всех закрытых FB-групп  
- автоотправка enquiry без твоего/ассистента контроля  

---

## Фильтры v2 (по умолчанию)
- Location: **Roscrea + 20–30 km towns**
- Type: rent / to let
- Beds: **>= 2**
- Price: без лимита (пока не задашь)
- Only NEW + LIVE

Nearby towns:
`Roscrea, Templemore, Birr, Moneygall, Shinrone, Nenagh, Cloughjordan`

---

## Файлы
- `roscrea-realtime-hunt.json` — быстрый multi-source polling + verify  
- `roscrea-email-instant.json` — мгновенные Daft emails  
- `roscrea-rental-alerts.json` — тот же realtime (alias)

## Telegram формат v2
```
🚨 NEW PROPERTY

🏠 2 Bed House
📍 Roscrea, Co. Tipperary
💶 €370 per week (~€1603/mo)
🕐 detected: 10:42:17
🟢 NEW — just now
📡 daft-roscrea
✅ LIVE verified

🔗 https://www.daft.ie/...

ACTION:
1) Open
2) Call if phone visible
3) Else Enquire NOW
```

## Что нужно от тебя (чтобы дожать)
1. max budget (€/month) или `без лимита`  
2. радиус: `10 / 20 / 30` км  
3. Telegram chat id  
