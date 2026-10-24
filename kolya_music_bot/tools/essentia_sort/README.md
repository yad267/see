# Essentia sort (Mac) — жанр по звуку + исходная папка в имени

Бесплатно. Оригиналы по умолчанию **не трогает** (COPY).

Результат:
```
Music/MusicSorted/
  House/[0 OGON] track.mp3
  Techno/[Deepweekend] other.mp3
  Unknown/[...] ...
```

## 1. Python venv

```bash
cd ~/see/kolya_music_bot/tools/essentia_sort   # или путь к репо
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install essentia-tensorflow numpy
# НЕ ставь пакет essentia в этот же venv
```

## 2. Модели (Discogs)

Создай `models/` и скачай с https://essentia.upf.edu/models.html :

- `discogs-effnet-bs64-1.pb` (Discogs-EffNet embeddings)
- `genre_discogs400-discogs-effnet-1.pb` (Genre Discogs400)
- `genre_discogs400-discogs-effnet-1.json` (классы/labels, желательно)

Положи файлы в:
```
tools/essentia_sort/models/
```

## 3. Тест на 20 файлах (COPY)

```bash
mkdir -p ~/Music/MusicSorted
python sort_by_genre.py \
  --src ~/Music/ТУТ_ТВОЯ_ПРОБНАЯ_ПАПКА \
  --dst ~/Music/MusicSorted \
  --models-dir ./models \
  --limit 20
```

Проверь `~/Music/MusicSorted` и `_essentia_report.csv`.

## 4. Больше файлов

Убери `--limit 20`. Пока без `--move`.

Когда устраивает результат:
```bash
python sort_by_genre.py --src ... --dst ~/Music/MusicSorted --models-dir ./models --move
```

## Жанровые папки (whitelist)

House, Deep, Melodic, Techno, Hip-Hop, Disco, Trance, DnB, Ambient, Trap, Bass, Other, Unknown  

Сырые Discogs-стили схлопываются в `genre_map.py` (правишь там).
