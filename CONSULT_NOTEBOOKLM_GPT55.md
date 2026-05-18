# GPT-5.5: pivot LoreMap to NotebookLM-py?

_cost: $0.1071_

Короткий вердикт: **NotebookLM — отличный “viral UX/backend for grounded chat”, но плохой единственный фундамент для публичного LoreMap.** Я бы сделал pivot, но не “всё отдать NotebookLM”, а **NotebookLM-first MVP + свой Evidence Pack/ontology как страхующий слой**.

---

## 1) Лучше ли это, чем строить GraphRAG самим?

**Для MVP — да, лучше.**  
Потому что NotebookLM уже даёт то, что ты сам будешь строить месяцами:

- source-grounded Q&A;
- inline citations;
- нормальный UX;
- audio overview;
- mind map;
- slide deck;
- quizzes;
- ingest URL/text;
- меньше галлюцинаций из коробки.

Но есть важный нюанс: **NotebookLM не понимает твою epistemic ontology сам по себе.** Если ты зальёшь туда fandom + reddit как обычные источники, он всё равно может смешать:

- канон;
- фанатские теории;
- speculation;
- hallucinated wiki claims;
- in-universe POV;
- visions/dreams;
- “mentioned as present”.

То есть NotebookLM снижает галлюцинации, но не решает автоматически:

- canon vs theory;
- temporal scope;
- POV confusion;
- reliability hierarchy;
- spoiler boundaries;
- contradictory sources.

**Вывод:** NotebookLM лучше как grounded interaction layer, но перед ним нужен твой слой подготовки источников.

---

## 2) Риски unofficial Google API

Риск высокий.

`notebooklm-py` — это не официальный API, а Playwright automation поверх веба. Значит:

1. **Google может поменять DOM / endpoints** — библиотека сломается за день.
2. **Может появиться CAPTCHA / bot detection.**
3. **Логин Google через automation — токсичная зона доверия.**
4. **Может нарушать ToS.**
5. **Аккаунты могут получить rate-limit или soft-block.**
6. **Нельзя гарантировать работу публичному Reddit-аудиту.**

Для личного Claude Code skill — норм.  
Для viral public release — опасно, если ты обещаешь “работает стабильно”.

Правильная формулировка продукта:

> LoreMap generates a NotebookLM-ready source pack and can optionally automate NotebookLM import locally using an unofficial helper.

Не:

> LoreMap uses NotebookLM API.

Потому что API нет.

---

## 3) Free tier лимиты NotebookLM

Точные лимиты надо проверять live, потому что Google их меняет. Исторически порядок был примерно такой:

- около **100 notebooks** на free account;
- около **50 sources per notebook**;
- крупный лимит на размер source, примерно сотни тысяч слов;
- ограничение на chat queries/day;
- ограничение на Audio Overview generations/day;
- Plus/Workspace дают кратно больше.

Для casual fan use этого обычно хватит, если ты **не добавляешь 500 fandom pages как 500 sources**.

Главный практический лимит — **sources per notebook**. Поэтому тебе надо делать не “каждая страница = source”, а source bundling:

```text
01_CANON_EPISODES_S01.md
02_CANON_EPISODES_S02.md
03_CHARACTERS.md
04_ORGANIZATIONS.md
05_TIMELINE.md
06_OBJECTS_AND_SYMBOLS.md
07_UNRESOLVED_MYSTERIES.md
08_REDDIT_THEORIES_HIGH_SIGNAL.md
09_REDDIT_THEORIES_LOW_CONFIDENCE.md
10_CONTRADICTIONS_AND_RETCONS.md
```

И внутри каждого блока держать citations/URLs.

---

## 4) Public skill с Google login или local-only RAG?

Если выбирать бинарно:

- **Google login + NotebookLM**: лучше качество, хуже adoption/trust.
- **Local-only RAG**: лучше независимость, хуже ответы, больше галлюцинаций.

Я бы не заставлял всех логиниться в Google через скрипт. Это барьер и trust issue.

Лучший вариант:

### Mode A — Safe/public default

LoreMap генерирует:

- `LoreMap_SourcePack.zip`;
- Markdown sources;
- `manifest.json`;
- список URL;
- prompt-инструкции;
- “Import this into NotebookLM manually”.

Юзер сам открывает NotebookLM и добавляет sources. Никаких cookies, никакого Playwright login.

### Mode B — Power user automation

Опционально:

```bash
loremap notebooklm --import --local-browser-profile
```

С предупреждением:

> Uses unofficial local browser automation. Credentials are never collected. May break.

### Mode C — Local fallback

Минимальный local RAG/evidence search:

- BM25/vector local;
- цитаты;
- temporal filters;
- canon/theory separation;
- no generative claims without evidence.

Не надо строить “идеальный GraphRAG” сразу. Сделай **Evidence Store + structured source pack**.

---

## 5) Что exploit для виральности

Самые viral-фичи:

### 1. Audio Overview: “фан-подкаст про сериал”

Это самое сильное. Люди будут шарить:

> “Я сделал 18-минутный подкаст про все теории Severance S2.”

Но надо контролировать input. Иначе NotebookLM может озвучить мусорные Reddit-теории как серьёзные.

Сделай разные аудио-пакеты:

- `Canon Recap`;
- `Top 10 Theories`;
- `Unanswered Mysteries`;
- `Character Conspiracy Board`;
- `Before Season 3 Catch-up`;
- `Spoiler-free onboarding`.

### 2. Mind Map

Для mystery-сериалов это идеально:

- персонажи;
- организации;
- символы;
- локации;
- временные линии;
- unresolved clues.

Фанаты любят “conspiracy board”.

### 3. Quizzes

Менее viral, но хорошо для fandom engagement:

- “Are you an MDR-level Severance expert?”
- “Which theory do you believe?”
- “Canon or theory?”

### 4. Theory debate packs

Очень ценно:

```text
Theory: Gemma is partially alive
Evidence for:
Evidence against:
Contradictions:
Required assumptions:
Confidence:
Sources:
```

NotebookLM хорошо работает, если ты загружаешь уже структурированный debate pack.

### 5. Spoiler-mode notebooks

Отдельные notebooks:

- `Severance S1 only`;
- `Severance S1-S2`;
- `Full spoilers`;
- `Theories only`.

Это решает temporal compression.

---

## 6) Риск блокировки при 1000 фанатах

Да, риск есть.

Но зависит от модели использования.

### Если все используют свои Google accounts

Меньше риск централизованного бана, но:

- automation pattern может детектиться;
- library может сломаться;
- OAuth/session/captcha friction;
- разные регионы/аккаунты/Workspace policies.

### Если ты используешь один shared Google account

Не делай так. Почти гарантированный бан/rate-limit/security lock.

### Если ты распространяешь только source packs

Риск минимальный.

Поэтому публичный релиз должен быть:

> “Generate NotebookLM-ready LoreMap packs.”

А automation — experimental.

---

## 7) Три design choices first thing

### Choice 1: Source pack before NotebookLM

Не скармливай raw scraped pages напрямую. Делай промежуточный артефакт:

```json
{
  "series": "Severance",
  "scope": "S1-S2",
  "source_type": "canon/wiki/reddit/theory",
  "spoiler_level": "full",
  "claim_type": "event/relationship/theory/symbol/timeline",
  "confidence": "high/medium/low",
  "evidence_url": "...",
  "quote": "...",
  "episode_context": "S02E04",
  "temporal_validity": {
    "from": "S01E01",
    "to": "S02E10"
  }
}
```

Потом из этого генерируешь Markdown для NotebookLM.

То есть NotebookLM получает curated evidence, а не интернет-суп.

---

### Choice 2: Hard separation of canon and theories

Создавай отдельные sources:

```text
CANON_ONLY.md
FANDOM_WIKI_DERIVED.md
REDDIT_THEORIES.md
CONTRADICTIONS.md
UNVERIFIED_CLAIMS.md
```

И в каждом документе жирно писать инструкцию:

```text
SOURCE CLASS: REDDIT THEORY
This document contains fan speculation, not canon.
Do not present claims from this document as confirmed events.
```

NotebookLM не всегда идеально следует этому, но это сильно помогает.

Для фанатов это критично. Ошибка “theory stated as canon” убивает доверие.

---

### Choice 3: Temporal/spoiler scoped notebooks

Не один универсальный “Severance LoreMap”, а несколько:

```text
Severance LoreMap — S1 only
Severance LoreMap — S1-S2
Severance LoreMap — Full canon + theories
Severance LoreMap — Theories only
```

Так ты избегаешь:

- temporal compression;
- future spoilers;
- “recent” ambiguity;
- S4 event leaking into S2 discussion.

Каждый notebook должен иметь `SCOPE.md`:

```text
This notebook covers canon up to Season 2 Episode 10.
Events after this point must be treated as out of scope.
If a source mentions later information, label it as future/out-of-scope.
```

---

## 8) Vote: pivot или продолжать свой GraphRAG?

Мой vote:

# Pivot на NotebookLM-first, но не NotebookLM-only.

Конкретно:

### Не строй сейчас полный Neo4j GraphRAG.

Это overkill для раннего LoreMap. Ты утонешь в:

- entity resolution;
- temporal modeling;
- contradiction handling;
- vector retrieval;
- NLI validators;
- UI;
- citations;
- evals.

А фанаты всё равно будут судить по одному: “не врёт ли про канон?”

### Строй свой слой как Evidence Compiler

Твой настоящий moat не в chat engine.  
Твой moat — в **качественном lore ingestion/evidence normalization**:

- scraping;
- deduplication;
- source classification;
- canon/theory split;
- temporal scope;
- claim extraction;
- contradiction detection;
- source pack generation;
- NotebookLM export;
- local fallback.

### Architecture I would ship

```text
User enters: "Severance"

        |
        v

Discovery
- fandom wiki
- episode pages
- character pages
- subreddit high-signal threads
- official sources if available

        |
        v

Scraper
- raw HTML/text
- URLs
- timestamps
- thread metadata

        |
        v

Evidence Compiler
- canon/theory classification
- spoiler scope
- temporal labels
- claim extraction
- confidence labels
- contradictions
- citations

        |
        v

LoreMap Source Pack
- Markdown sources
- manifest.json
- URL list
- import instructions
- local searchable index

        |
        +----------------------+
        |                      |
        v                      v

NotebookLM Mode          Local Mode
- manual import          - keyword/BM25/vector
- optional automation    - citation-first answers
- audio overview         - no account needed
- mind map
- quizzes
```

---

## Hidden pitfalls you must not ignore

### 1. NotebookLM still can hallucinate

Меньше, но не ноль. Особенно если:

- sources conflict;
- Reddit theories verbose;
- wiki pages have speculation;
- character pages summarize future events;
- source labels are weak.

### 2. Fandom wiki is not pure canon

Fandom pages часто содержат:

- editor interpretation;
- chronology compression;
- offscreen assumptions;
- “it is implied”;
- production trivia mixed with plot.

Не относись к wiki как к ground truth. Лучше:

```text
official episode transcript/recap > official site > episode page > fandom wiki > reddit
```

### 3. Reddit theories are adversarial noise

Нужно ранжирование:

- upvotes;
- comments;
- author reputation;
- date;
- pre/post episode;
- debunked/not debunked;
- repeated across threads;
- evidence count.

### 4. “Mentioned” не значит “exists/present”

В claim schema нужно различать:

```text
APPEARS_ON_SCREEN
MENTIONED
IMPLIED
SEEN_IN_VISION
DREAMED
FLASHBACK
THEORIZED
CONFIRMED_BY_CREATOR
```

NotebookLM не сделает это сам без подготовки.

### 5. Нужно eval-set фанатских ловушек

Для каждого сериала держи `red_team_questions.md`:

```text
Q: Was X actually present in episode Y?
Expected: No, only mentioned.
Evidence: ...
```

Перед релизом прогоняешь через NotebookLM и local fallback.

---

## Итоговая рекомендация

**Да, используй NotebookLM.** Это даст тебе лучший UX и viral features почти бесплатно.

Но позиционируй LoreMap не как “бот на unofficial NotebookLM API”, а как:

> AI-generated, source-grounded lore research pack for NotebookLM and local exploration.

Главный продукт:

- не Playwright automation;
- не Google login;
- не GraphRAG;
- а **clean, temporally scoped, canon/theory-separated evidence pack**.

NotebookLM — витрина и усилитель.  
Твой Evidence Compiler — ядро.
