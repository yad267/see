# Задача: регистрация → Workflow + Sputnik (два персонажа)

**Статус:** пользователь сейчас регистрируется по ссылкам ниже.  
**После регистрации:** вшить credentials/URL/ключи в n8n Workflow — во все нужные места, в т.ч. где делаются ролики (Odds 003/005/005b и связанные).  
**Возможно:** те же ссылки/ключи подойдут и для Sputnik Stoica — проверить и при необходимости переиспользовать.  
**Sputnik Stoica (отдельное требование):** в сценариях с двумя ролями (например начальник ↔ собеседник, жена ↔ муж) — **два разных человека / два голоса / два персонажа**, диалог друг с другом, **не один** голос на обе роли.

## Ссылки на повторную регистрацию (источник: `odds-history-registration-sites.md` + AcoustID)

### Обязательно / мини-порядок Odds
1. Pixabay register: https://pixabay.com/accounts/register/
2. Pixabay API docs (ключ → `PIXABAY_API_KEY`): https://pixabay.com/api/docs/
3. Wikimedia Commons CreateAccount: https://commons.wikimedia.org/wiki/Special:CreateAccount
4. Archive.org signup: https://archive.org/account/signup
5. Boosty: https://boosty.to
6. David Rumsey (закладки/скачивание): https://www.davidrumsey.com
7. Library of Congress maps: https://www.loc.gov/maps/

### Уже есть — только проверить логин (не «зарегистрировать снова»)
- Pexels API: https://www.pexels.com/api/
- Google Drive: https://drive.google.com
- Google Sheets: https://sheets.google.com
- ElevenLabs: https://elevenlabs.io
- json2video: https://json2video.com
- n8n: https://n8n.yad26ai.uk
- YouTube Studio: https://studio.youtube.com

### Опционально / без обязательной регистрации
- NASA: https://images.nasa.gov
- Telegram API (если нужен): https://my.telegram.org
- VK: https://vk.com
- RuTube: https://rutube.ru
- SunCalc: https://www.suncalc.org
- КиберЛенинка: https://cyberleninka.ru
- Wikipedia: https://ru.wikipedia.org
- Gallica: https://gallica.bnf.fr
- Europeana: https://www.europeana.eu
- Commons root: https://commons.wikimedia.org

### Music Bot (не Odds, но явная регистрация приложения)
- AcoustID new application: https://acoustid.org/new-application

## Следующие шаги после регистрации
1. Получить от пользователя подтверждение / ключи (через secrets n8n, не в чат).
2. Прописать в Workflow Odds (003 short / 005 long / 005b cover / Asset Resolve) — Pixabay и прочие источники.
3. Проверить переиспользование тех же credentials для Sputnik Stoica.
4. Sputnik: доработать сценарист/озвучку под **два персонажа / два голоса** в диалоговых сценах.

## Новые сток-видео источники (НЕ в старом списке) — фильтр завода

Критерии: без водяных знаков на финальном файле; коммерция; автоскачивание через **официальный API** или стабильные download URL из API (не scrape).

### Подходят под пайплайн (официальный API)
| Сайт | URL | Signup | Лицензия | Автодоступ | Sputnik диалоги |
|---|---|---|---|---|---|
| Coverr | https://coverr.co/ | Да, для API: https://coverr.co/ + https://coverr.co/developers | Coverr License (коммерция OK; на Free/Demo API — attribution Coverr) | Да: REST `api.coverr.co`, поле `urls.mp4_download` | Слабо: B-roll «meeting/talk», не два актёра с репликами |
| Magnific (ex-Freepik/Videvo) | https://www.magnific.com/videos | Да + **платный** план для Stock API | Magnific/Freepik license; free на сайте часто с attribution | Да API, но stock download лимиты на платных планах | Слабо то же |
| Vecteezy API | https://www.vecteezy.com/developers | Да | Free licence: attribution + бюджет ≤$1k; Pro — коммерция без attribution | Free tier: preview **с watermark** → для завода **не** (грязный IP) | Слабо |

### Не для автозавода (нет официального API / только scrape / WM / attribution-ловушки)
- Mixkit https://mixkit.co/ — Mixkit Stock Video Free License (проверять Free vs Restricted); **нет** public API
- Dareful https://dareful.com/ — CC BY 4.0; нет API
- Videezy https://www.videezy.com/ — часто attribution/WM на free; нет public API
- Vidsplay https://www.vidsplay.com/ — credit required; нет API

### Уже в вашем списке (для сравнения, не «новые»)
Pexels License + API · Pixabay Content License + API · NASA Image/Video Library API · Commons/Archive per-file
