# Apply on Mac (Languages-on-site)

Branch: `cursor/phrasal-tools-trainer-0d96` (from `main`)

## What this adds
1. **ElevenLabs ES LatAm** — same pipeline as EN (key/model/cache). Factory voice `Q4cwyRtDSxeo5Pq77ptz` (Ricardo, Latin American). Not Castilian. Override in Settings → «ID голоса ES (LatAm)». AVSpeech fallback `es-MX`.
2. **phrasal_tools.json** — 100 tool-context sentences, 10 sections × 10.
3. **UI** — Фразовые → Инструменты (section pick) + Тренажёр. Buttons: Проговорить (TTS→STT→word match), В тренажёр, Добавить свою (RU→Gemini→EN).

## Apply
```bash
cd ~/Developer/Languages-on-site   # or worker checkout
git fetch origin main
git checkout -B cursor/phrasal-tools-trainer-0d96 origin/main
git am /path/to/0001-phrasal-tools-latam-es.patch
# OR copy files from Services/ Views/ Models/ Resources/ and replace project.pbxproj
git push -u origin cursor/phrasal-tools-trainer-0d96
```

Do not change bundle id / PRODUCT_NAME / remotes / API keys.
