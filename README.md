# LoreMap

> Назови сериал - LoreMap соберёт fan-вики + reddit-теории, упакует в bundled source pack, и зальёт в Google NotebookLM. Получаешь grounded AI чат + автоматический подкаст-обзор + mind map бесплатно.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## TL;DR

```
You: "LoreMap для Severance"
LoreMap: scrapes Severance fandom + reddit -> builds 10-file source pack -> 
         creates NotebookLM notebook -> gives you URL + audio overview podcast
You:    chats with NotebookLM (free) about the show. No hallucinations.
```

## Что делает

Skill для Claude Code который:

1. **Auto-discovery** - находит fandom wiki + subreddit по названию сериала
2. **Scrape** - забирает все wiki-страницы + топ-теории с reddit
3. **Bundle** - упаковывает в ~10 markdown файлов с жёсткими SOURCE_CLASS labels (canon vs theory vs creator quote)
4. **Upload** - заливает в Google NotebookLM через [notebooklm-py](https://github.com/teng-lin/notebooklm-py)
5. **Generate bonuses** - опционально автоматически делает Audio Overview (подкаст про сериал!), Mind Map, Slide deck, Quizzes
6. **Hand off** - даёт юзеру URL notebook'а, дальше юзер общается с NotebookLM (web UI или CLI)

## Почему через NotebookLM

NotebookLM от Google **source-grounded by design**:
- Каждый ответ имеет inline-цитаты на источники
- Не галлюцинирует (отказывается отвечать если нет evidence)
- Уже отполированный UX от Google
- Бесплатно (Google account)

Это решает фанатскую проблему: "AI несёт чушь про мой любимый сериал".

LoreMap добавляет ключевое: **правильную подготовку sources** с жёстким разделением канона и фанатских теорий, чтобы NotebookLM не смешивал.

## Установка

```bash
# 1. Клонировать
git clone https://github.com/AyanbekDos/loremap.git ~/projects/loremap

# 2. Установить как Claude Code skill
mkdir -p ~/.claude/skills/
cp -r ~/projects/loremap/skill ~/.claude/skills/loremap

# 3. Python deps для scraping + bundle
cd ~/projects/loremap
python3 -m venv .venv
source .venv/bin/activate
pip install httpx beautifulsoup4 lxml pyyaml markdownify tenacity

# 4. notebooklm-py для NotebookLM API
pip install "notebooklm-py[browser]"
playwright install chromium
notebooklm login   # Google sign-in через браузер (одноразово)
notebooklm auth check --test --json  # verify
```

После - в Claude Code пишешь `"LoreMap для <название>"`.

## Архитектура

```
USER: "LoreMap для Severance"
          |
          v
Claude Code skill
          |
          +--> discover.py: fandom URL + subreddit
          |
          +--> scrape_fandom.py + scrape_reddit.py: raw/ directory
          |
          +--> build_source_pack.py: 10 curated markdown files с
          |     - SOURCE_CLASS: CANON | FANDOM_INTERPRETATION | REDDIT_THEORY | CREATOR_QUOTE
          |     - spoiler_level scope
          |     - bundled (NotebookLM лимит ~50 sources)
          |
          +--> import_to_notebooklm.py: upload в Google NotebookLM
          |
          +--> ОПЦИОНАЛЬНО: trigger Audio Overview / Mind Map / Slide Deck / Quiz
          |
          v
USER: chats with NotebookLM (web UI) или 'notebooklm chat ask <id> "вопрос"'
```

## Source Pack структура

LoreMap НЕ заливает 500 fandom-страниц по одной (NotebookLM лимит ~50 sources). Вместо этого:

```
source_pack/
├── 00_MANIFEST.md                  # scope + reading priority + AI instructions
├── 01_CANON_CHARACTERS.md          # все wiki/entities в одном bundle
├── 02_CANON_LOCATIONS_AND_OBJECTS.md
├── 03_CANON_EPISODES_S1.md
├── 04_CANON_EPISODES_S2.md
├── 05_CANON_EPISODES_S3.md         # ... per-season
├── 07_REDDIT_THEORIES_HIGH.md      # score >= 1000, помечено как FAN SPECULATION
├── 08_REDDIT_THEORIES_LOW.md       # score 100-1000
├── 09_CREATOR_INTERVIEWS.md        # высший trust tier
```

Каждый файл начинается с жёсткой инструкции:

```markdown
⚠️ SOURCE CLASS: REDDIT_THEORY
This document contains fan speculation, NOT canon.
Do NOT present claims from this document as confirmed events.
```

NotebookLM это видит и не смешивает.

## Опциональные scopes для разных юзеров

- `--scope full` - всё + теории + интерпретации
- `--scope s1-only` - только канон S1 (spoiler-safe для catch-up)
- `--scope s1-s2` - канон до S2
- `--scope theories-only` - только curated теории (для тех кто всё посмотрел)
- `--scope characters` - per-character деconstruction

## Виральные бонусы от NotebookLM

После upload skill может автоматически triggerнуть:

1. **Audio Overview** - 15-минутный AI-podcast про сериал. MP3 файл. Самая viral фича.
2. **Mind Map** - визуальная карта связей. PNG / interactive JSON.
3. **Slide Deck** - презентация по канону. PDF / PPTX.
4. **Quiz** - "Какой ты по уровню фанатства?". JSON / HTML.
5. **Briefing Doc** - текстовый обзор всего сериала.

Все скачиваются локально.

## Что НЕ делает LoreMap

- Не строит собственный RAG (NotebookLM делает это лучше)
- Не генерирует predictions / theories напрямую (NotebookLM grounded - не предсказывает, а отвечает по источникам)
- Не транскрибирует видео (только текстовые источники)
- Не использует платные API (только Google account, Claude Code подписка юзера, бесплатно)

## Риск: unofficial NotebookLM API

[notebooklm-py](https://github.com/teng-lin/notebooklm-py) - unofficial Python client. Google может изменить эндпоинты в любой момент. Если notebooklm-py перестанет работать - skill сломается, нужно будет обновление.

LoreMap считает это приемлемым риском - выигрыш в качестве (grounded UX + автоматический podcast) того стоит.

## Лицензия

MIT. Используй, форкай, продавай. Не хранит полные субтитры/расшифровки шоу - только публичные fan-wiki + Reddit.

## Authors

Концепт: [Aianbek Dossumbayev](https://github.com/AyanbekDos)
Implementation: Claude Code (Claude Opus 4.7)

Использует:
- [notebooklm-py](https://github.com/teng-lin/notebooklm-py) by Teng Lin - unofficial NotebookLM client
- [NotebookLM](https://notebooklm.google.com) by Google - source-grounded AI knowledge base
- [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) by Karpathy - концептуальная основа (но архитектурно отошли)
