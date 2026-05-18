# llm-wiki-theory-engine

AI-методология которая берёт любой mystery-сериал или книжную серию и строит из неё knowledge base + генерирует обоснованные теории + предсказания финала.

Полностью внутри Claude Code. Без внешних API ключей.

## Когда активировать

Триггеры от пользователя:
- "сделай теории для сериала X" / "проанализируй сериал Y"
- "построй карту сериала Z"
- "предскажи финал сериала / книги"
- "разбери mystery шоу X"
- Просто название mystery-сериала или книжной серии: "Severance", "Yellowjackets", "Stormlight Archive"

НЕ активируется когда:
- Просто вопрос про сериал (используй встроенные знания Claude)
- Запрос на одну конкретную теорию без построения базы
- Это не mystery / не имеет фан-вики

## ВАЖНО: пользователь даёт ТОЛЬКО название

Юзер не должен искать fandom URL или subreddit. Только название сериала / книги. Ты сам auto-discovery (см. Шаг 1 ниже).

## База

Skill использует архитектуру memoriki (LLM Wiki Karpathy + status-tagging):

```
{project-dir}/
├── raw/                 Сырые источники (immutable)
│   ├── fandom/          Wiki pages
│   └── reddit/          Top theories
├── wiki/                Нормализованная база (Claude владеет)
│   ├── entities/        Персонажи
│   ├── concepts/        Места, объекты, символы
│   ├── episodes/        Эпизоды/главы
│   ├── theories/        Фан-теории
│   └── synthesis/       Сводки + наши теории
│       ├── mystery_graph.yaml
│       ├── open_mysteries.md
│       └── predictions/
└── CLAUDE.md            Правила вики для будущих сессий
```

КАЖДАЯ страница имеет frontmatter с `status: canon | fan_theory | speculation`. Без этого Claude мешает канон с теориями.

## Workflow

### Шаг 1. Инициализация проекта

Пользователь даёт ТОЛЬКО НАЗВАНИЕ сериала / книжной серии. Например "Severance", "FROM", "Stormlight Archive".

ТЫ автоматически находишь:
- fandom URL
- subreddit
- создателя

#### Auto-discovery fandom

Пробуй URL-варианты от названия (lowercase, no spaces, remove articles):

```
https://<slug>.fandom.com/api.php
```

Slug candidates:
1. `<name_lowercase_no_spaces>` (severance -> severance)
2. `<name_with_dashes>` (the-last-of-us -> the-last-of-us)
3. `<name_no_the>` (the-from -> from)
4. `<show_acronym>` (a-song-of-ice-and-fire -> asoiaf)
5. `<name>-tv` или `<name>tv` (если 1-3 не сработали)

Тестируй HTTP GET на каждый - если 200 OK с MediaWiki JSON, нашёл.

Если не нашёл - WebSearch "<show name> fandom wiki" чтобы получить URL вручную, либо спроси юзера.

#### Auto-discovery subreddit

Patterns для пробы (используй reddit JSON `https://www.reddit.com/r/<sub>/about.json`):
1. `r/<name_no_spaces>` (Severance -> SeveranceAppleTVPlus, FROM -> FromTVEpix, ASOIAF -> asoiaf)
2. `r/<show_acronym>` 
3. `r/<name>TV` или `r/<name>Show`
4. `r/<name>FX` / `r/<name>HBO` / `r/<name>AppleTVPlus` / `r/<name>MGM` (по платформе)

Тестируй каждый - проверь что subreddit_subscribers >= 1000 и contains "theor" в last 50 posts (чтобы убедиться mystery-фокус).

Если не нашёл - WebSearch "<show name> reddit theories" или спроси юзера.

#### Auto-discovery creator

Просто Perplexity / WebSearch "<show name> creator showrunner". Кладёшь в CLAUDE.md проекта.

#### Создай папку проекта

`~/projects/<show-slug>-theories/` (или предложенный путь).

Скопируй скрипты:
```bash
cp ~/.claude/skills/llm-wiki-theory-engine/scripts/* <project>/scripts/
cp ~/.claude/skills/llm-wiki-theory-engine/references/CLAUDE_TEMPLATE.md <project>/CLAUDE.md
```

Запусти:
```bash
python scripts/scrape_fandom.py --api <api-url> --output raw/fandom/
python scripts/scrape_reddit.py --subreddit <name> --output raw/reddit/
```

### Шаг 2. Нормализация

```bash
python scripts/normalize.py --raw raw/ --wiki wiki/
```

Скрипт перекладывает по доменам с status тегами + конвертирует `/wiki/X` ссылки в `[[X]]`.

### Шаг 3. Mystery graph (Claude делает это сам)

НЕ через API. Ты (Claude в сессии Code) читаешь wiki/entities/ + wiki/concepts/ для ключевых mystery-сущностей и пишешь YAML в `wiki/synthesis/mystery_graph.yaml` по схеме из `references/MYSTERY_GRAPH_SCHEMA.md`.

Включи: ключевые персонажи-загадки (антагонисты), необъяснённые объекты/символы, локации с тайной природой. Edges = canon-evidence связи между узлами.

### Шаг 4. Theory generation (ты, Claude)

Когда пользователь спрашивает "построй теорию про X" / "предскажи финал":

1. Прочитай `wiki/entities/<X>.md` + связанные `wiki/concepts/`
2. Прочитай 3-5 топовых `wiki/theories/*.md` касающихся X
3. Используй схему из `references/PREDICTION_SCHEMA.md`:
   - Тезис (1-2 предложения)
   - 5-8 аргументов канона с ссылками на эпизоды
   - 2-3 контраргумента
   - Что объясняет (закрываемые open_questions из mystery_graph)
   - Что НЕ объясняет
   - Альтернативные объяснения
   - Scoring по 5 осям (canon_support, contradiction_count, explanatory_power, simplicity, creator_plausibility)

5. ADVERSARIAL REVIEW: спавн `Agent` tool с `subagent_type=general-purpose`:
   ```
   prompt: "Ты adversarial-критик литературной теории. Перед тобой канон [...] и теория [...]. Найди дыры: какие канон-факты игнорируются, какие логические скачки, какая альтернатива сильнее. Скорректируй scoring. Verdict: hold/revise/reject."
   ```

6. Финальный синтез: что выживает после критики, что пересмотрено, что отброшено.

7. Сохрани в `wiki/synthesis/predictions/<mystery>-<YYYY-MM-DD>.md` с YAML frontmatter (model: claude-opus, status: speculation, scoring before/after).

### Шаг 5. Validation (опционально, для незавершённых сериалов)

После релиза новой серии:
- Скрап обновлённой fandom + reddit (resume mode)
- Прочитать новые episode wiki pages
- Для каждой prediction в `wiki/synthesis/predictions/`: оценить HIT/PARTIAL/MISS по validation_rule
- Append в `wiki/synthesis/predictions/_ledger.md`

## Принципы

1. **Status tagging критичен**: canon vs fan_theory vs speculation. Без этого LLM мешает в кашу.
2. **Adversarial review обязателен**: спавн отдельного agent с противоположной задачей.
3. **Locked predictions**: git commit hash в frontmatter каждой prediction.
4. **Не выдумывай canon**: только то что есть в источниках. Если уверенности нет - status: speculation, не canon.

## Anti-patterns

См. `references/ANTI_PATTERNS.md`:
- AP-001 Temporal compression (события прошлых сезонов как "недавние")
- AP-002 Hallucination POV confusion (видения как реальность)
- AP-003 Scene boundary contamination
- AP-004 "Mentioned" trated as "present"

Каждое prediction проверяй на эти anti-patterns.

## Showcase (пример)

Полный кейс на FROM (MGM+/Epix, John Griffin) в `examples/from/`:
- 238 fandom pages
- 200 reddit theories
- 17-node mystery_graph
- Sample prediction Boy in White с verdict "revise" после adversarial review

Когда пользователь не знает с чего начать - покажи FROM example.

## Reddit-friendly выход

Финальный продукт для viral-поста:
- Mystery graph как mermaid diagram
- Топ-5 predictions для самых популярных mysteries сериала
- Adversarial reviews показывают что LLM не просто пересказывает Reddit
- Локированный git hash = "predict now, validate after finale"

## Что НЕ делает skill

- Не транскрибирует видео (легально/технически сложно)
- Не парсит YouTube разборщиков (требует whisper + yt-dlp setup)
- Не предсказывает СЛЕДУЮЩУЮ серию (только финал и долгосрочные mysteries)
- Не работает на завершённых сериях без mystery элемента
