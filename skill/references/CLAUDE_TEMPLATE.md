# {{PROJECT_NAME}} - llm-wiki theories project

AI-карта сериала / книжной серии "{{SHOW_NAME}}". База знаний с status-тегами + mystery graph + locked predictions с adversarial review.

Сгенерировано через skill `llm-wiki-theory-engine`.

## Структура

```
raw/                Источники (immutable)
  fandom/           Fandom wiki pages (~XX страниц)
  reddit/           Reddit top theories (~XX постов)
wiki/               LLM-владение
  entities/         Персонажи
  concepts/         Места, объекты, символы, монстры
  episodes/         Эпизоды / главы
  theories/         Фан-теории (status: fan_theory)
  synthesis/        Сводки + наши predictions
    mystery_graph.yaml
    mystery_graph.md
    open_mysteries.md
    predictions/    Locked predictions со scoring
CLAUDE.md           Этот файл - правила для сессий
```

## Frontmatter правила

КАЖДАЯ страница имеет:

```yaml
---
status: canon | fan_theory | speculation
source: fandom | reddit | interview
source_url: <URL>
---
```

`status: canon` - факт показан/сказан в шоу/интервью
`status: fan_theory` - популярная фан-гипотеза
`status: speculation` - наша или единичная догадка

## Operations

**Build mystery graph** (один раз после нормализации):
Прочитай wiki/entities/ + wiki/concepts/, собери ключевые mystery-узлы, напиши YAML в wiki/synthesis/mystery_graph.yaml по схеме `~/.claude/skills/llm-wiki-theory-engine/references/MYSTERY_GRAPH_SCHEMA.md`.

**Generate theory** для конкретной mystery:
Используй схему `~/.claude/skills/llm-wiki-theory-engine/references/PREDICTION_SCHEMA.md`. 3 шага: prediction -> adversarial review (через Agent subagent_type=general-purpose) -> финальный synthesis. Сохрани в `wiki/synthesis/predictions/<mystery>-<YYYY-MM-DD>.md`.

**Update after new release** (для незавершённых сериалов):
1. Скрап fandom + reddit с --resume
2. Прочитай новые episode pages, пометь канон
3. Для каждой prediction в `wiki/synthesis/predictions/` - оцени HIT/PARTIAL/MISS, запиши в `_ledger.md`

## Anti-patterns

Перед каждой генерацией проверяй себя по `~/.claude/skills/llm-wiki-theory-engine/references/ANTI_PATTERNS.md`:
- AP-001 Temporal compression
- AP-002 Hallucination POV
- AP-003 Scene boundary
- AP-004 Mentioned vs present
- AP-005-008 Theory-level

## Showcase ссылка

Полный пример llm-wiki-theory-engine на сериале FROM в `~/.claude/skills/llm-wiki-theory-engine/examples/from/`.
