# Character Arcs Template

Для шоу где центральны психологические трансформации героев: Breaking Bad, Better Call Saul, The Sopranos, BoJack Horseman, Mad Men, Fleabag, Mr. Robot.

## Файлы которые строит Claude

```
wiki/synthesis/
├── character_arcs/
│   ├── walter_white.md          # Per-character arc map
│   ├── jesse_pinkman.md
│   └── ...
├── moral_compass_shifts.md      # Кто куда сдвинулся в моральном спектре
├── key_decisions_ledger.md      # Решения которые изменили арки
├── transformation_timeline.md   # Сравнительная timeline всех арок
└── psychological_themes.md      # Какие психотемы шоу прорабатывает (вина, тревога, амбиции)
```

## Per-character arc структура

```yaml
character: Walter White
display_name: Walter White ("Heisenberg")

baseline_season_1:
  identity: High school chemistry teacher
  primary_drive: Family security + dying with dignity
  moral_position: Lawful neutral
  key_fears: Dying penniless, family in poverty
  self_image: Mediocre but decent

inflection_points:
  - season: 1
    episode: 1 (Pilot)
    event: Diagnosed terminal cancer
    decision: Synthesize meth to leave money
    moral_shift: Towards selfish-utilitarian justification

  - season: 1
    episode: 6
    event: Strangling Krazy-8
    decision: Kill rather than free
    moral_shift: Crossed first violence threshold

  - season: 2
    episode: 12
    event: Let Jane die (passive)
    decision: Withhold help
    moral_shift: Now actively callous to deaths
  ...

ending_season_5:
  identity: Heisenberg
  primary_drive: Empire / legacy / pride
  moral_position: Chaotic evil with self-justification
  key_fears: Being forgotten, being seen as weak
  self_image: I AM the danger

trajectory_summary: "Family-man chemist → cancer-driven meth cook → power-drunk crime lord. Each death he caused removed empathy. By S5 he admits 'I did it for me'."

closest_parallels: [Michael Corleone (Godfather), Macbeth, Tony Soprano]
```

## Алгоритм

1. Прочитай wiki/entities/ - выдели main characters (>=5 эпизодов экранного времени)
2. Для каждого пройди по wiki/episodes/ - извлеки decisions/events влияющие на персонажа
3. Построй per-character файл по схеме выше
4. transformation_timeline - таблица где X = сезон, Y = персонажи, ячейки = их moral_compass position
5. psychological_themes.md - какие общие темы шоу исследует через всех arc-ов

Юзер общается:
- "Покажи трансформацию X через все сезоны"
- "Какое решение X было моральной точкой невозврата?"
- "Сравни Walter и Jesse - кто пал ниже?"
- "Какие персонажи остались моральной opora всему шоу?"
- "Кто из главных героев максимально похож на меня?"
