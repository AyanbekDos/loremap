# Mystery Template

Для шоу с центральной загадкой: FROM, Lost, Twin Peaks, Westworld, Severance, Yellowjackets, Dark, Stranger Things.

## Файлы которые строит Claude

```
wiki/synthesis/
├── mystery_graph.yaml          # Главный артефакт (см. MYSTERY_GRAPH_SCHEMA.md)
├── mystery_graph.md            # Mermaid визуализация для Obsidian
├── open_questions.md           # Список незакрытых вопросов с приоритетами
├── contradictions.md           # Канон-противоречия с цитатами
├── top_fan_theories.md         # Ранжированные топ-теории фанов
└── predictions/                # Опционально - locked теории если юзер просит
```

## Алгоритм

1. Прочитай wiki/entities/ + wiki/concepts/ для ключевых mystery-сущностей
2. Построй mystery_graph по схеме MYSTERY_GRAPH_SCHEMA.md
3. Сгенерируй open_questions.md - список загадок с tier (core_required / likely / may_remain / atmosphere_only)
4. Найди противоречия канон-утверждений в wiki через LLM-проход
5. Прочитай wiki/theories/ и составь топ-5 ранжированных fan_theory с canon_support

Дальше юзер общается:
- "Какая твоя главная теория по X?"
- "Что говорят фаны по Y?"
- "Какие противоречия закроет финал?"

При желании юзера - спавнь adversarial agent для разбора теорий (см. PREDICTION_SCHEMA.md).

## Sample показан в examples/from/
