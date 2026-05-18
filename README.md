# LoreMap

> Назови сериал - получи AI-архитектора который изучит шоу, предложит варианты структуры базы знаний, построит Obsidian-карту и станет твоим собеседником по этому миру.

[![Skills.sh](https://img.shields.io/badge/skills.sh-installable-blue)](https://skills.sh)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## TL;DR

Юзер в Claude Code пишет:

```
"LoreMap для Severance"
```

Skill сначала ИЗУЧАЕТ шоу (preview-research): тип жанра, что центрально, что фаны обсуждают. Потом ПРЕДЛАГАЕТ 3-5 вариантов структуры базы:

```
Изучил Severance (Apple TV+, sci-fi corporate thriller). Главное: разделение сознания, MDR floor, мифология Lumon, теории про Cold Harbor.

Варианты базы:

A) Mystery focus - Cold Harbor, файлы рефинеров, мифология Кир Игана
B) Character split-arc - innie vs outie динамика per character
C) Lumon corporate map - иерархия, история компании, отделы
D) Theme analysis - капитализм, идентичность, контроль через дисциплину
E) Combo
F) Custom - своя идея структуры

Что выбираешь?
```

Юзер выбирает (включая свой кастомный запрос). Skill строит Obsidian-compatible mind map. Дальше юзер ОБЩАЕТСЯ с Claude который видит всю базу: задаёт вопросы, обсуждает теории, исследует связи.

## Установка

```bash
git clone https://github.com/AyanbekDos/loremap.git ~/projects/loremap
mkdir -p ~/.claude/skills/
cp -r ~/projects/loremap/skill ~/.claude/skills/loremap

cd ~/projects/loremap
python3 -m venv .venv
source .venv/bin/activate
pip install httpx beautifulsoup4 lxml pyyaml markdownify tenacity
```

После - в Claude Code пишешь `"LoreMap для <название>"` и идёшь по conversation flow.

## Главный принцип: НЕ один-размер-всем

Разные сериалы требуют разной структуры базы:

| Шоу | Подходящая структура |
|-----|---------------------|
| FROM, Lost, Twin Peaks | Mystery graph + theories + open questions |
| Game of Thrones, Succession | Family tree + alliances + betrayals + power map |
| Breaking Bad, BoJack | Character arc maps + moral compass shifts |
| The Office, Friends | Relationship heatmap + recurring jokes |
| The Sopranos, The Wire | Crime family tree + power transitions |
| Severance, Westworld | Mystery + corporate map + character split-arcs |
| Foundation, The Expanse | Timeline + factions + tech tree |
| Yellowjackets, Dark | Past-vs-present + character evolution |

И кастомные запросы которые мы ещё не предсказали - "карта всех смертей с поэтикой", "музыкальный гид по сезонам", "анализ еды в Sopranos".

## Архитектура

```
project/
├── raw/                       Источники (immutable)
│   ├── fandom/                MediaWiki API scrape
│   └── reddit/                Top theories + discussions
├── wiki/                      Claude нормализует и владеет
│   ├── entities/              Персонажи
│   ├── concepts/              Места, объекты, символы
│   ├── episodes/              Эпизоды / главы
│   ├── theories/              Фан-теории (status: fan_theory)
│   └── synthesis/             Сводки + специфичные под выбранный template
│       ├── mystery_graph.yaml    (если Mystery template)
│       ├── family_trees.yaml     (если Relationships template)
│       ├── character_arcs/       (если Character template)
│       └── ...
└── CLAUDE.md                  Правила для сессий
```

Каждая страница с `status: canon | fan_theory | speculation`. Без status LLM мешает в кашу. Markdown + frontmatter + `[[wiki-links]]` - готово для Obsidian.

## Templates встроенные

В `skill/references/templates/`:

- `MYSTERY_TEMPLATE.md` - для шоу с центральной загадкой
- `RELATIONSHIPS_TEMPLATE.md` - семьи, союзы, предательства
- `POWER_TEMPLATE.md` - политика, борьба за престол
- `CHARACTER_TEMPLATE.md` - психологические трансформации
- `CUSTOM_TEMPLATE.md` - принципы построения произвольной базы

Claude выбирает template based на user choice + adapts под конкретное шоу.

## Что внутри skill

- `SKILL.md` - инструкции активации для Claude Code (главный файл)
- `scripts/discover.py` - автопоиск fandom + subreddit по названию
- `scripts/scrape_fandom.py` - универсальный MediaWiki API scraper
- `scripts/scrape_reddit.py` - универсальный subreddit top-posts
- `scripts/normalize.py` - raw → wiki auto-classification
- `references/` - schemas + templates + anti-patterns
- `examples/from/` - showcase на сериале FROM

## После стройки - chat с Claude

Юзер общается:
- "Расскажи про этого персонажа"
- "Где упоминается этот символ?"
- "Обсудим теорию из reddit-поста [link]"
- "Что бы изменилось если бы X не умер?"
- "Какие противоречия в каноне?"
- "Сравни как Daenerys трансформировалась по сезонам"
- "Хочу написать фанфик - кто из персонажей подойдёт под сюжет где Y?"

Claude видит всю базу через wiki + при желании спавнит subagent для adversarial-разбора теорий.

## Anti-patterns которые методология предотвращает

LLM регулярно ошибается на mystery-контенте. LoreMap включает 8 проверенных anti-patterns:

| ID | Проблема |
|----|----------|
| AP-001 | Temporal compression - события из S1 как "current" в S4 |
| AP-002 | Hallucination POV confusion - видения как реальность |
| AP-003 | Scene boundary contamination |
| AP-004 | "Mentioned" treated as "present" |
| AP-005 | Single-key fallacy |
| AP-006 | "Creator-lied" escape hatch |
| AP-007 | Reddit selection bias |
| AP-008 | Verbose validation rules |

## Лицензия

MIT. Используй, форкай, продавай. Не хранит полные субтитры/расшифровки шоу - только публичные fan-wiki + Reddit.

## Authors

Концепт: [Aianbek Dossumbayev](https://github.com/AyanbekDos)
Implementation: совместно с Claude Code (Claude Opus 4.7)

Архитектура на основе:
- [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) by Andrej Karpathy
- [memoriki](https://github.com/AyanbekDos/memoriki) (предыдущий проект)
