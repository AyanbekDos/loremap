# Schema для prediction-теории

Каждая prediction сохраняется как markdown с YAML frontmatter в `wiki/synthesis/predictions/<mystery-slug>-<YYYY-MM-DD>.md`.

## Frontmatter

```yaml
---
title: "Prediction: <Что предсказываем>"
type: prediction
status: speculation
mystery: <mystery-id из mystery_graph.yaml>
created: YYYY-MM-DD
updated: YYYY-MM-DD
model: claude-opus (in-session, no API)
critic: general-purpose-agent (in-session adversarial subagent)
git_commit_hash: <hash на момент создания>
sources:
  - "[[Entity Name]]"
  - "[[Concept Name]]"
  - wiki/theories/relevant-theory.md
  - raw/interviews/research-file.md
scoring_initial:
  canon_support: X/10
  contradiction_count: X
  explanatory_power: X/10
  simplicity: X/10
  creator_plausibility: X/10
scoring_after_review:
  canon_support: X/10
  contradiction_count: X
  explanatory_power: X/10
  simplicity: X/10
  creator_plausibility: X/10
verdict: hold | revise | reject
---
```

## Тело документа

```markdown
# <Mystery>

## ШАГ 1. Prediction (Claude в сессии)

### Тезис

1-2 предложения. Прямая гипотеза.

### Аргументы канона

1. **Прямая ссылка на эпизод/событие** (с цитатой если есть). Объяснение почему этот факт поддерживает тезис.
2. ...

5-8 аргументов минимум.

### Контраргументы

1. Что в каноне противоречит тезису.
2. Какие открытые вопросы тезис НЕ закрывает.

### Что объясняет (закрываемые открытые вопросы из mystery_graph)

- Open question 1 (из узла X mystery_graph)
- Open question 2
- ...

### Что НЕ объясняет

- ...

### Альтернативные объяснения

1. **Alt name**: 1-2 предложения. Чем сильнее/слабее основного.
2. ...

### Initial Scoring (моя оценка)

- canon_support: X/10 (сколько канон-фактов подтверждают)
- contradiction_count: X (целое число противоречий)
- explanatory_power: X/10 (сколько open questions закрывает)
- simplicity: X/10 (Оккам)
- creator_plausibility: X/10 (в стиле создателя)

## ШАГ 2. Adversarial review (general-purpose subagent)

Спавн через Agent tool с задачей:

```
"Ты adversarial-критик литературной теории mystery-сериала <NAME>. Перед тобой канон [контекст из wiki/entities/concepts/episodes] и prediction-теория [текст шага 1]. 

Твоя задача найти ДЫРЫ:
1. Какие канон-факты теория ИГНОРИРУЕТ или искажает? Минимум 3 пункта с цитатой канона.
2. Где автор делает логический скачок? Минимум 2 пункта.
3. Какие альтернативные объяснения он недооценил? Минимум 1.
4. Скорректируй scoring.
5. Verdict: hold / revise / reject.

Не хвалить. Только критика. Маркдаун, чётко по структуре."
```

Вставь полный ответ критика сюда.

## ШАГ 3. Финальный синтез

**Что выживает после критики:**
- ...

**Что критик справедливо понизил:**
- ...

**Альтернатива критика сильнее или слабее:**
- ...

**Финальный verdict:** hold / revise / reject

## Меточные данные для будущей валидации

После выхода новых серий проверять:
- [Проверяемый факт 1]
- [Проверяемый факт 2]

При подтверждении/опровержении обновлять scoring выше + добавлять запись в `wiki/synthesis/predictions/_ledger.md`.
```

## Правила

1. **Все факты канона ОБЯЗАНЫ иметь ссылку на источник** (эпизод/глава/интервью). Без источника - не используй.
2. **status: speculation для prediction** ВСЕГДА. Даже если уверен на 90%.
3. **Adversarial review обязателен** перед сохранением. Без него файл недействителен.
4. **Git commit hash в frontmatter** на момент создания - для locked predictions.
5. **Применяй anti-patterns checks** перед сохранением (см. ANTI_PATTERNS.md):
   - AP-001: не сжимай разные сезоны в "недавнее"
   - AP-002: галлюцинации/видения = НЕ canon-факты
   - AP-003: не путай сцены
   - AP-004: "mentioned" не значит "present"
