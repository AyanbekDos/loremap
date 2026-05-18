---
name: loremap
description: AI knowledge base architect для любого сериала или книжной серии. Юзер даёт название (например "Severance"), skill изучает шоу, понимает его жанр и фишки, и ПРЕДЛАГАЕТ 3-4 варианта структуры базы знаний (mystery graph / family tree / power map / character arcs / custom). Юзер выбирает или предлагает свой. Skill строит Obsidian-compatible mind map в выбранном формате. Потом юзер общается с AI про сериал, обсуждает теории, ищет связи. Триггеры - "LoreMap для X", "построй карту шоу Y", "хочу обсудить сериал Z с AI".
---

# LoreMap

AI архитектор knowledge base для любого сериала или книжной серии. Адаптивный: разные шоу = разные структуры.

Полностью внутри Claude Code. Без внешних API ключей.

## Когда активировать

Триггеры от пользователя:
- "LoreMap для X" / "построй карту шоу Y"
- "сделай базу знаний для сериала Z"
- "хочу обсудить сериал X с AI"
- Просто название сериала / книги в контексте "хочу разобраться"

НЕ активируется:
- Просто вопрос про сериал (используй встроенные знания Claude)
- Завершённое лёгкое шоу без сложного lore

## Главный принцип

**НЕ один-размер-всем.** Разные сериалы требуют разной структуры:

- FROM (mystery horror) → mystery graph + загадки + теории
- Game of Thrones (политика+отношения) → family trees + альянсы + power map + кто кого предал по сезонам
- Breaking Bad (трансформация героев) → character arc maps + moral compass shift + key decisions
- Lost (mystery+character) → mystery graph + flashback timeline
- The Office (workplace) → org chart + interpersonal heatmap + recurring jokes
- Sopranos (mob) → crime family tree + hits + power transitions
- Foundation (sci-fi) → empire timeline + tech tree + factions
- Yellowjackets (двойная timeline) → past vs present + character evolution

Skill сначала ИЗУЧАЕТ шоу + ПРЕДЛАГАЕТ варианты + юзер выбирает.

## Workflow

### Шаг 1. Юзер даёт название

Юзер: "LoreMap для Game of Thrones"

### Шаг 2. AUTO-DISCOVERY

Запустить `scripts/discover.py "<Show Name>"` чтобы найти:
- fandom URL (api.php)
- subreddit
- creator

Если не нашёл - WebSearch fallback или спросить юзера.

### Шаг 3. PREVIEW RESEARCH (КЛЮЧЕВОЙ НОВЫЙ ШАГ)

Ты (Claude) делаешь МАЛЕНЬКИЙ research до полного скрапа:

1. Фетчишь главную страницу fandom + 5-10 топ wiki страниц (через scrape_fandom.py --limit 10)
2. Фетчишь топ-10 постов с subreddit (через scrape_reddit.py --posts-limit 10)
3. WebSearch: "<show name> review themes genre"
4. Если есть Perplexity skill - perplexity_ask "Что характерно для шоу <X>? Какие у фанов главные обсуждения?"

На основе этой preview определи:

- **Genre/type**: mystery / drama / political / horror / sci-fi / workplace / crime / fantasy / heist / anthology / комбинация
- **Что центрально**: загадки? отношения? сила? трансформация? технологии? мифология?
- **Структура шоу**: один таймлайн или несколько? Закрытое или ongoing? Большой ансамбль или малый кор?
- **Что фаны обсуждают больше всего**: топ-теории, топ-character analysis, топ-references к канон-событиям

### Шаг 4. ПРЕДЛОЖЕНИЕ 3-4 ВАРИАНТА БАЗЫ + КАСТОМ

На основе preview предложи юзеру СПИСОК ВАРИАНТОВ структуры. Каждый со своим обоснованием почему подходит этому шоу.

ПРИМЕР для GoT:

```
Изучил Game of Thrones (HBO 2011-2019, fantasy/political drama, fandom 16k+ страниц, r/asoiaf 800k subscribers). 

Главное в нём: политика, война за престол, семейные интриги, мифология Westeros, незакрытые тайны (R+L=J, Azor Ahai).

ПРЕДЛАГАЮ ВАРИАНТЫ БАЗЫ:

A) Family Tree + Alliance Map - дома Westeros, родственные связи, кто с кем в союзе, кто кого предал по сезонам. Подходит если интересуют отношения и политика.

B) Power Dynamics - кто сидел на престоле, ключевые битвы, переходы власти, geopolitical map континента. Подходит если интересует борьба за власть.

C) Mystery Focus - Azor Ahai, prophecies, R+L=J, Бран как Three-Eyed Raven, происхождение White Walkers. Подходит если хочешь обсуждать загадки.

D) Character Arcs - психологическая трансформация ключевых героев по сезонам (Daenerys, Jaime, Sansa, Theon). Подходит если интересует human drama.

E) Combo - все 4 в одной базе. Дольше строить (~30 мин vs 10 мин), но полная картина.

F) Custom - опиши свою идею структуры. Я построю под неё. Например: "карта всех смертей и причин", "trace boys' army через все семь сезонов".

Что выбираешь? Можешь комбинировать (типа A+C) или предложить F.
```

### Шаг 5. ПОЛНЫЙ SCRAPE

После выбора:
1. `scripts/scrape_fandom.py --api <api-url> --output raw/fandom/` (все страницы)
2. `scripts/scrape_reddit.py --subreddit <name> --output raw/reddit/<sub>/`
3. `scripts/normalize.py --raw raw/ --wiki wiki/`

### Шаг 6. СТРОЙКА ПО ВЫБРАННОМУ ШАБЛОНУ

В зависимости от выбора применяешь соответствующий template (см. `references/templates/`):

- A (Relationships) → `references/templates/RELATIONSHIPS_TEMPLATE.md` - строй family_tree.yaml, alliances_by_season.yaml, betrayals_ledger.md
- B (Power) → `references/templates/POWER_TEMPLATE.md` - throne_history.md, key_battles.md, geo_map.md
- C (Mystery) → `references/templates/MYSTERY_TEMPLATE.md` - mystery_graph.yaml (как в FROM showcase), open_questions.md
- D (Character) → `references/templates/CHARACTER_TEMPLATE.md` - per-character arc map с moral_compass / key_decisions / transformations
- E (Combo) → все из A+B+C+D
- F (Custom) → юзер описал, Claude строит инпровизирует под этот запрос

Все файлы - markdown с YAML frontmatter, [[wiki-links]], готовые для Obsidian.

### Шаг 7. ОБСУЖДЕНИЕ

Дальше юзер общается с тобой про шоу:

- "Расскажи про этого персонажа"
- "Где упоминается этот символ?"
- "Обсудим теорию из reddit-поста [link]"
- "Что бы изменилось если бы X не умер?"
- "Какие противоречия в каноне?"
- "Сравни как Daenerys трансформировалась по сезонам"
- "Что значил этот эпизод тематически?"
- "Хочу написать фанфик - кто из персонажей естественно подойдёт под сюжет где Y?"
- "Кому я могу помочь в этом сериале как пользователь?"

Для каждого запроса используй wiki/ как контекст. Если нужны теории - можешь спавнить general-purpose agent для adversarial review (опционально).

## Anti-patterns (необязательно но полезно знать)

См. `references/ANTI_PATTERNS.md`:
- AP-001 Temporal compression (события из старых сезонов как "недавние")
- AP-002 Hallucination POV (видения как реальность)
- AP-003 Scene boundary contamination
- AP-004 "Mentioned" treated as "present"
- AP-005 Single-key fallacy
- AP-006 Creator-lied escape hatch
- AP-007 Reddit selection bias
- AP-008 Verbose validation rules

Применяй когда строишь теории или анализируешь канон.

## Принципы

1. **Сначала research, потом скрап**. Полный скрап 500+ страниц дорог. Preview-research 10-20 страниц = $0 (Claude в сессии). Решай структуру до больших затрат.
2. **Предлагай варианты, не диктуй**. Юзер сам решает что ему интересно.
3. **Custom-option всегда**. Креативные фанаты придумают такое о чём ты не подумал.
4. **Obsidian-ready output**. Markdown + frontmatter + [[wiki-links]]. Юзер открывает базу в Obsidian для визуального исследования.
5. **Chat-first после стройки**. База - это foundation для разговоров, не финальный продукт.

## Showcase: FROM

В `examples/from/` лежит готовый пример Mystery-template на FROM (MGM+):
- 17-узловой mystery graph (Boy in White, Man in Yellow, Township, Children и тд)
- 49 canon-evidence связей
- Sample theory generation про Boy in White с adversarial review

## Что НЕ делает skill

- Не предсказывает (это побочно если юзер захочет, не центрально)
- Не транскрибирует видео (только текст из wiki + reddit)
- Не работает на шоу без fan-wiki
- Не сохраняет полные субтитры (легально-юридический риск)
