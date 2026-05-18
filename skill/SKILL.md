---
name: loremap
description: AI knowledge base architect для любого сериала или книжной серии. Юзер даёт название (например "Severance"), skill парсит fandom-вики + reddit-теории, готовит bundled source pack с жёстким разделением canon/theories по сезонам, и загружает в Google NotebookLM (через notebooklm-py). NotebookLM делает source-grounded chat + автоматически генерит подкаст-обзор сериала, mind map, slide deck, quizzes. Без галлюцинаций (NotebookLM grounded by design). Триггеры - "LoreMap для X", "построй карту шоу Y", "хочу обсудить сериал Z с AI".
---

# LoreMap

AI knowledge base architect для любого mystery сериала или книжной серии.

Pipeline: scrape fandom + reddit -> bundle в curated source pack -> upload в Google NotebookLM -> юзер общается с NotebookLM (source-grounded) + получает бонусом подкаст / mind map / slide deck.

Использует [notebooklm-py](https://github.com/teng-lin/notebooklm-py) - unofficial Python client для Google NotebookLM. Бесплатно (Google account).

## Когда активировать

Триггеры от пользователя:
- "LoreMap для X" / "построй карту шоу Y"
- "сделай базу знаний для сериала Z"
- "хочу обсудить сериал X с AI"
- Просто название mystery-сериала или книги в контексте "хочу разобраться"

НЕ активируется:
- Просто вопрос про сериал (используй встроенные знания Claude)
- Завершённое лёгкое шоу без сложного lore

## Главный принцип

**LoreMap - Evidence Compiler. NotebookLM - источник истины и UX витрина.**

Skill готовит чистые, scope-разделённые, canon/theory-разнесённые source-пакеты, и подаёт их NotebookLM. Дальше NotebookLM (Google) делает grounded RAG + chat + viral артефакты.

Это даёт:
- Source-grounded chat (no hallucinations by design)
- Audio Overview - подкаст-обзор сериала (вирус-фича)
- Mind Map - автоматическая визуализация связей
- Slide deck, Quizzes, Briefing docs
- Скачивание всего локально (MP3 / MP4 / PDF / PPTX / JSON / Markdown)

## Prerequisites

Один раз настроить NotebookLM-py:

```bash
pip install "notebooklm-py[browser]"
playwright install chromium  # 170MB
notebooklm login  # Google sign-in через браузер
notebooklm auth check --test --json  # verify ok
```

Если не установлено - skill сам это инициирует и попросит юзера выполнить.

## Workflow

### Шаг 1. Auto-discovery (как раньше)

`scripts/discover.py "<Show Name>"` находит fandom URL + subreddit + creator.

### Шаг 2. Preview research

Прочти главную fandom + 5-10 топ wiki страниц + 10 топ reddit постов + WebSearch про шоу. Определи:
- genre/type
- что центрально (mystery / relationships / power / character / другое)
- сколько сезонов вышло
- что фаны обсуждают больше всего

### Шаг 3. Предложи юзеру варианты scope/template

Используй preview-research чтобы предложить 3-5 вариантов:

```
Изучил Severance (sci-fi corporate thriller, S1 + S2 вышло). Главное: severance процедура, MDR floor, Cold Harbor, теории про Kier Eagan, identity questions.

Варианты NotebookLM-пака:

A) FULL CANON + THEORIES - полный обзор S1+S2 + reddit theories. Один большой notebook.
B) SPOILER-SAFE S1 ONLY - только канон S1, без S2 событий и без теорий. Для тех кто хочет catch-up без спойлеров.
C) THEORIES DEEP-DIVE - только curated reddit theories с evidence-разбором. Для тех кто уже всё посмотрел.
D) CHARACTER FOCUS - per-character деconstruction (Mark, Helly, Irving, Dylan, etc) с innie/outie split.
E) Custom - своя идея структуры.

Что выбираешь? Я создам отдельный NotebookLM notebook под выбор.
```

### Шаг 4. Full scrape

`scripts/scrape_fandom.py` + `scripts/scrape_reddit.py` - как раньше. Raw в `raw/`.

### Шаг 5. Build SOURCE PACK (новый ключевой шаг)

`scripts/build_source_pack.py` собирает scraped raw в **bundled markdown files** (NotebookLM лимит ~50 sources per notebook - нельзя заливать 500 fandom-страниц по одной).

Бандлы создаются по выбранному scope:

#### Для FULL CANON + THEORIES:
```
source_pack/
├── 00_MANIFEST.md                  # SCOPE + spoiler boundaries + reading order
├── 01_CANON_CHARACTERS.md          # все wiki/entities в одном файле
├── 02_CANON_LOCATIONS.md           # все wiki/concepts location-типа
├── 03_CANON_OBJECTS_SYMBOLS.md     # talismans, music boxes etc
├── 04_CANON_EPISODES_S1.md         # episode recaps S1 со ссылками
├── 05_CANON_EPISODES_S2.md         # ...
├── 06_CREATOR_INTERVIEWS.md        # цитаты создателей
├── 07_FANDOM_INTERPRETATIONS.md    # wiki-страницы с интерпретациями (НЕ канон, помечено)
├── 08_REDDIT_THEORIES_HIGH.md      # топ-теории с upvotes >= 1000
├── 09_REDDIT_THEORIES_LOW.md       # остальные обсуждаемые теории
└── 10_CONTRADICTIONS_OPEN.md       # открытые вопросы, противоречия в каноне
```

#### Для SPOILER-SAFE S1 ONLY:
```
source_pack/
├── 00_MANIFEST.md                  # SCOPE: канон до S1 финала включительно. НЕТ S2, НЕТ теорий.
├── 01_CANON_CHARACTERS_S1.md       # only S1 events для каждого character
├── 02_CANON_LOCATIONS_S1.md
├── 03_CANON_EPISODES_S1.md
├── 04_CREATOR_INTERVIEWS_S1.md     # фильтр интервью только до S1 финала
└── 05_S1_OPEN_QUESTIONS.md         # что осталось неотвеченным на конец S1
```

#### Каждый файл начинается с STRICT SOURCE LABEL:

```markdown
---
source_class: CANON | FANDOM_INTERPRETATION | REDDIT_THEORY | CREATOR_QUOTE
scope: S1+S2+S3+S4 (full) | S1 only | etc
spoiler_level: full | safe-to-Sx | theories-only
reading_priority: 1-10
---

⚠️ SOURCE CLASS: REDDIT_THEORY
This document contains fan speculation, NOT canon.
Do NOT present claims from this document as confirmed events.
Reddit theories may contradict canon. Always check primary canon sources first.

# Top Theories from r/SeveranceAppleTVPlus
...
```

Это решает Reddit/canon смешивание на уровне промптов NotebookLM.

### Шаг 6. Upload в NotebookLM

`scripts/import_to_notebooklm.py` через notebooklm-py:

```python
async with await NotebookLMClient.from_storage() as client:
    nb = await client.notebooks.create(f"LoreMap: {show_name} ({scope})")
    for md_file in source_pack:
        await client.sources.add_text(nb.id, title=md_file.name, content=md_file.read())
```

Возвращает юзеру URL notebook'а.

### Шаг 7. Опциональные бонусы (виральные!)

После upload предложить юзеру:

```
NotebookLM готов. URL: https://notebooklm.google.com/notebook/<id>

Хочешь сразу сгенерить бонусы?
A) AUDIO OVERVIEW - подкаст про сериал (~15 мин, MP3 файл)
B) MIND MAP - визуальная карта связей (PNG / JSON)
C) SLIDE DECK - презентация про сериал (PDF / PPTX)
D) QUIZ - тест "Какой ты по уровню фанатства?"
E) BRIEFING - текстовый обзор всего сериала
F) Все сразу
```

Сделать через notebooklm-py CLI: `notebooklm audio create`, `notebooklm mindmap`, etc.

### Шаг 8. Чат

Юзер дальше общается с NotebookLM ИЛИ через web UI ИЛИ через CLI:

```
notebooklm chat ask <nb_id> "Расскажи теорию про Cold Harbor"
notebooklm chat ask <nb_id> "Какие открытые вопросы в S2?"
notebooklm chat ask <nb_id> "Сравни Mark и Helly"
```

NotebookLM отвечает с inline-цитатами, источник из source_pack виден.

## Антипатерны NotebookLM (важно знать)

Даже NotebookLM иногда галлюцинирует. Меры предосторожности встроены в наш Source Pack:

1. **Жёсткие SOURCE_CLASS labels** в первой строке каждого файла - чтобы NotebookLM не смешивал canon с теориями.
2. **Scope/spoiler boundary в манифесте** - explicit инструкция что в notebook'е охвачено.
3. **Bundle small** - НЕ заливать 500 отдельных sources, делать ~10 файлов. NotebookLM лучше работает с bundled.
4. **Reddit theories ранжированы** - high vs low signal, чтобы NotebookLM brался в первую очередь high.
5. **Creator interviews отдельным файлом** - наивысший tier evidence.

## Что делает skill

1. Scrape (fandom + reddit)
2. Bundle (10 markdown файлов с strict source labels)
3. Upload (в NotebookLM через notebooklm-py)
4. Optionally generate (audio / mindmap / slides / quiz)
5. Hand off (URL notebook + опциональные локальные файлы)

## Что НЕ делает skill

- Не строит свой собственный RAG (NotebookLM делает это лучше)
- Не генерирует ответы напрямую от Claude (NotebookLM grounded, Claude нет)
- Не предсказывает (NotebookLM не для предсказаний, для grounded Q&A)
- Не транскрибирует видео (только текстовые источники)

## Reference системы

- **notebooklm-py**: https://github.com/teng-lin/notebooklm-py
- **NotebookLM**: https://notebooklm.google.com (free, Google account нужен)
- **Memoriki / LLM Wiki Karpathy**: предыдущая попытка (отошли потому что галлюцинировала)

## Showcase

В `examples/from/` (legacy, может быть удалено) - старая попытка через llm-wiki. Заменено на NotebookLM-flow.

Новый FROM showcase: после первого работающего теста.
