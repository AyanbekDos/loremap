# llm-wiki-theory-engine

AI-методология для построения "карты mystery-сериала или книжной серии" через llm-wiki архитектуру + ensemble theories с adversarial review. Всё внутри Claude Code, без внешних API.

## Что делает

Берёт любой mystery-сериал или книжную серию и:

1. Парсит fandom wiki + reddit топ-теории + создатель-интервью
2. Раскладывает в structured wiki со status-тегами (canon | fan_theory | speculation)
3. Строит mystery_graph с canon-evidence связями между узлами
4. По запросу генерирует obоснованные теории про любую загадку
5. Adversarial review через subagent ловит дыры
6. Сохраняет locked predictions с git commit hash

После релиза новых серий validate-режим отмечает HIT/MISS predictions.

## Активация

В Claude Code:

```
"Активируй llm-wiki-theory-engine для https://from.fandom.com и r/FromTVEpix"
```

или

```
"Построй theory engine для сериала Severance используя его fan wiki и r/SeveranceAppleTVPlus"
```

Skill инициализирует папку проекта, скрапит источники, нормализует, строит граф. Дальше юзер общается:

```
"Расскажи теорию про Boy in White"
"Предскажи финал сериала"
"Какие открытые вопросы остались?"
"Где противоречия в каноне?"
```

## Архитектура памяти (memoriki / Karpathy LLM Wiki)

```
project/
├── raw/                Immutable источники
│   ├── fandom/         MediaWiki API scrap
│   └── reddit/         JSON API scrap
├── wiki/               Claude нормализует и владеет
│   ├── entities/       Персонажи
│   ├── concepts/       Места, объекты, символы
│   ├── episodes/       Эпизоды / главы
│   ├── theories/       Фан-теории (status: fan_theory)
│   └── synthesis/      Сводки + наши predictions
│       ├── mystery_graph.yaml
│       └── predictions/
└── CLAUDE.md           Правила для будущих сессий
```

## Файлы skill-а

- `SKILL.md` - инструкции для Claude Code (главный файл активации)
- `scripts/scrape_fandom.py` - универсальный MediaWiki API scraper
- `scripts/scrape_reddit.py` - универсальный subreddit top-posts scraper
- `scripts/normalize.py` - нормализация raw -> wiki по доменам с auto-classification
- `references/MYSTERY_GRAPH_SCHEMA.md` - схема mystery graph
- `references/PREDICTION_SCHEMA.md` - схема prediction-теории с adversarial review
- `references/ANTI_PATTERNS.md` - 8 anti-patterns LLM моделей которые надо предотвращать
- `references/CLAUDE_TEMPLATE.md` - шаблон CLAUDE.md для проекта юзера
- `examples/from/` - полный showcase на сериале FROM (MGM+/Epix)

## Showcase: FROM

В `examples/from/` лежит работающий пример:

- 17-узловой mystery_graph (Boy in White, Man in Yellow, Township, Children, Bottle Trees, Faraway, Talismans, Symbol, Creatures, Music Box, Lighthouse, Victor, Tabitha, Miranda, Fatima baby, Boyd, Jade) с 49 canon-evidence связями
- Sample prediction "Boy in White" с adversarial review GPT (раньше использовали external API, теперь общая методология)
- Observed anti-patterns AP-001 до AP-008 (реально пойманные ошибки на FROM)

## Anti-patterns которые методология предотвращает

- AP-001 Temporal compression: события из старых сезонов как "недавние"
- AP-002 Hallucination POV confusion: видения как реальность
- AP-003 Scene boundary contamination: механические окна ломают сцены
- AP-004 Mentioned vs present: упоминание считается присутствием
- AP-005 Single-key fallacy: теория всё одним ключом объясняет
- AP-006 Creator-lied escape hatch
- AP-007 Reddit selection bias
- AP-008 Verbose validation rules

## Зачем нужно

Mystery-сериалы (FROM, Severance, Yellowjackets, Twin Peaks, Lost) и незавершённые книжные серии (ASOIAF, Stormlight) имеют огромные фанатские теории. Но фаны не систематизируют. Эта методология систематизирует + добавляет AI-prediction с локальным adversarial review.

Reddit фанаты любого шоу могут за вечер построить ИИ-карту своего сериала и получить обоснованные predictions.

## Лицензия

Личный исследовательский проект. Не хранит полные субтитры/расшифровки шоу. Использует только публично доступные fan wiki + Reddit.
