# Power Template

Для шоу где центральна борьба за власть, политика: Game of Thrones, Succession, House of Cards, Mr. Robot, Better Call Saul, Industry, Borgia, Yellowstone.

## Файлы которые строит Claude

```
wiki/synthesis/
├── throne_history.md           # Кто и когда у власти, хронология переходов
├── power_pyramid_by_season.yaml # Иерархия силы по сезонам
├── key_battles.md              # Ключевые битвы / коnflicts / executive moves
├── political_factions.yaml     # Группы и их идеологии
├── leverage_map.md             # Кто у кого имеет рычаг (информация, связи, ресурсы)
├── geographical_map.md         # Территории / зоны влияния
└── decision_consequences.md    # Ключевые решения и их последствия
```

## YAML power_pyramid_by_season

```yaml
season: 3
power_holders:
  - rank: 1
    name: Tywin Lannister
    role: Hand of the King
    sources_of_power: [house Lannister wealth, military command, royal grandfather]
    weaknesses: [lack of true control over Joffrey]
  - rank: 2
    name: Joffrey Baratheon
    role: King
    sources_of_power: [throne, royal title]
    weaknesses: [puppet of Tywin, hated]
  - rank: 3
    name: Cersei Lannister
    role: Queen Mother
    ...
```

## Алгоритм

1. Прочитай wiki/episodes/ - для каждого выдели "кто сейчас у власти"
2. Постройchronological throne_history.md
3. Найди ключевые power moves (избирания, перевороты, убийства претендентов)
4. Прочитай wiki/concepts/ для locations - построй geographical_map с зонами влияния
5. Для каждой фракции - power_pyramid

Юзер общается:
- "Кто реально правил в Westeros в сезоне 5?"
- "Какие решения изменили баланс силы больше всего?"
- "Если бы X выиграл битву Y - как бы изменилась карта?"
- "Кто самый эффективный политик во всём сериале?"
