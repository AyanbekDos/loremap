# Schema для mystery graph

Граф ключевых mystery-узлов сериала и canon-связей между ними. Foundation для всех predictions.

Сохраняется в `wiki/synthesis/mystery_graph.yaml` + рендерится в `mystery_graph.md` с mermaid-визуализацией.

## YAML структура

```yaml
nodes:
  - id: <snake_case_id>
    name: <Pretty Display Name>
    type: entity | concept | event
    canon_summary: "1-2 предложения чистого канона - без спекуляций"
    priority: core_required | likely_supported | may_remain_ambiguous | atmosphere_only
    open_questions:
      - "Конкретный неотвеченный вопрос 1"
      - "Конкретный неотвеченный вопрос 2"
    related_sources:
      - wiki/entities/X.md
      - wiki/concepts/Y.md

edges:
  - from: <node-id-1>
    to: <node-id-2>
    relation: "guards | opens | requires | is_part_of | opposes | created_from | has_knowledge_of | manipulates | depends_on"
    evidence_type: canon_explicit | canon_inferred
    evidence_quote: "цитата или описание канон-сцены"
    episode_ref: "SXEY или chapter X"
```

## Priority уровни

- **core_required**: финал ОБЯЗАН ответить (главные антагонисты, ключевые тайны мира)
- **likely_supported**: вероятно закроет (объекты с явной mystery нагрузкой)
- **may_remain_ambiguous**: возможно оставит (детали, мелкие символы)
- **atmosphere_only**: вряд ли (декоративные элементы)

## Как Claude строит граф

Когда skill активирован и normalize отработал:

1. Прочитай wiki/entities/ + wiki/concepts/ - выдели kandidates для узлов:
   - Антагонисты с тайной природой
   - Необъяснённые объекты/символы
   - Локации с тайной природой
   - События происхождения (origin events)
   - Главные герои с тайной связью

2. Для каждого узла напиши canon_summary - ТОЛЬКО факты из wiki, без спекуляций.

3. Определи priority по логике: связан ли узел с центральной интригой сериала.

4. Извлеки open_questions: для каждого узла какие открытые вопросы должны быть закрыты в финале.

5. Edges - связи между узлами с canon-evidence:
   - canon_explicit: прямо показано/сказано в сериале
   - canon_inferred: вытекает из нескольких сцен
   - НЕ canon_speculation - спекуляций в графе быть не должно

6. Густой граф: минимум 30 edges чтобы каждый узел был с другими связан.

## Mermaid визуализация

В mystery_graph.md:

```markdown
## Связи

\`\`\`mermaid
graph LR
  boy_in_white-->|guides|tabitha
  boy_in_white-->|has_knowledge_of|bottle_trees
  man_in_yellow-->|may_control|township
  ...
\`\`\`
```

## Пример (FROM)

См. examples/from/wiki/synthesis/mystery_graph.yaml - 17 узлов, 49 связей.
