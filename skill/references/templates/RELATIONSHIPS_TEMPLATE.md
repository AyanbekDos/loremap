# Relationships Template

Для шоу где центральны отношения, семьи, союзы: Game of Thrones, Succession, The Sopranos, The Crown, Yellowstone, Downton Abbey, Friends.

## Файлы которые строит Claude

```
wiki/synthesis/
├── family_trees.yaml           # Семейные деревья (генеалогия)
├── family_trees.md             # Mermaid визуализация
├── alliances_by_season.yaml    # Кто с кем в союзе по сезонам
├── alliances_evolution.md      # Mermaid timeline альянсов
├── betrayals_ledger.md         # Кто кого предал, контекст, последствия
├── romantic_history.md         # Романтические связи между персонажами
├── power_struggles.md          # Кто за что борется, мотивации
└── relationship_heatmap.md     # Таблица силы связи между всеми pair-ами
```

## YAML schema family_trees

```yaml
houses:
  - house_id: stark
    name: House Stark
    motto: "Winter is Coming"
    seat: Winterfell
    members:
      - id: ned_stark
        name: Eddard Stark
        status: deceased
        died_season: 1
        died_episode: 9
        children: [robb, sansa, arya, bran, rickon, jon (acknowledged)]
        spouse: catelyn_tully
      - ...
    allies_seasons:
      - season: 1
        allied_with: [house_tully, house_baratheon (Robert)]
      - season: 4
        allied_with: []
        status: scattered_after_red_wedding
```

## YAML schema alliances_by_season

```yaml
season: 1
date_in_show: ~ 298 AC
alliances:
  - parties: [stark, baratheon (Robert)]
    nature: friendship + king's hand
    status: active
  - parties: [lannister (Cersei), baratheon]
    nature: marriage of convenience
    status: deteriorating
  ...
betrayals_this_season:
  - betrayer: littlefinger
    victim: ned_stark
    episode: 7
    consequence: ned_arrested
```

## Алгоритм

1. Прочитай wiki/entities/ - выдели всех major characters + их family relations из infobox + body
2. Построй family_trees.yaml
3. Прочитай wiki/episodes/ - для каждого сезона выдели союзы и предательства
4. alliances_by_season.yaml + betrayals_ledger.md
5. relationship_heatmap - 2D таблица всех ↔ всех с score 0-10 (-10 enemy ... +10 closest)

Дальше юзер общается:
- "Покажи как менялось отношение X к Y по сезонам"
- "Кто кого предал больше всего?"
- "Какие альянсы пережили все сезоны?"
- "Если бы X не умер - какие альянсы изменились бы?"
