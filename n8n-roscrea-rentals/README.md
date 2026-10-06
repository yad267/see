# Roscrea Rental Alerts (Daft → n8n → Telegram)

Бот для быстрой ловли аренды в **Roscrea, Co. Tipperary**.

## Зачем
В Tipperary/Roscrea объявлений мало, но хорошие уходят быстро.  
Ассистент должен получить Telegram и сразу писать/звонить.

## Что делает
1. Каждые **5 минут** проверяет Daft:
   - `https://www.daft.ie/property-for-rent/roscrea-tipperary`
   - плюс Tipperary county, где в адресе есть `Roscrea`
2. Сравнивает с уже виденными `listing id`
3. Новые → в Telegram в формате **CALL/ENQUIRE NOW**
4. Пишет строку в Google Sheet (опционально, для дедупа/статуса)

## Важно про телефон
На Daft номер часто **не в открытом JSON**.  
Поэтому в алерте:
- если телефона нет → `Send Daft enquiry NOW`
- ассистент открывает ссылку и действует сразу

## Установка
1. Import `roscrea-rental-alerts.json` в n8n
2. Нода **Config**:
   - `telegramChatId`
   - `maxMonthlyEuro` (например 1500; `0` = без лимита)
   - `minBeds` (например 1; `0` = без фильтра)
3. Подключи Telegram credentials
4. (Опционально) Google Sheets credentials + Sheet ID
5. Active ON
6. На Daft дополнительно включи Saved Search Email Alerts по Roscrea

## Сообщение ассистенту
```
🚨 ROSCREA RENTAL — ACT NOW

📍 Limerick Rd, Roscrea
💶 €370 / week · 2 Bed · House
👤 Claudia (PRIVATE)

🔗 https://www.daft.ie/for-rent/...

Action:
1) Open link
2) Call if phone visible
3) Else send enquiry immediately

Script:
Hi, I’m interested in the Roscrea rental on Daft.
Is it still available for viewing this week?
```

## Рекомендация
Держи этот polling-бот + email alerts Daft параллельно.  
Email иногда быстрее, polling страхует.
