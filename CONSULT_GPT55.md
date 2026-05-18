# GPT-5.5 consultation

_cost: $0.1251_

Надёжная AI-память для lore должна быть не «LLM, который всё понял», а **evidence-first система**, где LLM — библиотекарь/индексатор, а не автор канона.

Коротко: я бы строил **гибрид: immutable evidence store + structured claim store + knowledge graph + scene-level RAG**. Vector DB сам по себе не спасёт.

---

## 1. Архитектура памяти для canon-точности

### Не Vector DB как источник истины

Vector DB хорош для поиска похожих сцен:

> “Найди все сцены, где Марк говорит о Джемме.”

Но он плох как canonical memory, потому что embeddings не хранят:

- epistemic status: канон / теория / слух / сон / видение;
- temporal scope: S2E4 vs S4E1;
- source priority;
- точные ссылки на утверждения;
- distinction между “mentioned” и “present”.

### Я бы сделал 4 слоя

#### Layer 1: Immutable Evidence Store

Сырьё, которое нельзя переписывать:

```text
source_id: from_s04e05_subtitles
type: episode_transcript
series: FROM
season: 4
episode: 5
timestamp_start: 00:31:12
timestamp_end: 00:31:55
text: "..."
```

Сюда входят:

- SRT/субтитры;
- episode transcripts;
- официальные синопсисы;
- fandom wiki pages;
- Reddit posts;
- интервью шоураннеров;
- companion books;
- screenshots/vision descriptions, если есть multimodal extraction.

Важно: **source tiering**.

```text
Tier 0: episode itself / transcript / subtitles
Tier 1: official recap / creator interview
Tier 2: licensed companion / official site
Tier 3: fandom wiki
Tier 4: reddit / fan theory
```

#### Layer 2: Scene/Event Index

Не просто chunks по 500 токенов, а **scene-level units**:

```json
{
  "scene_id": "from_s04e05_scene_17",
  "location": "Sheriff Station",
  "time_in_episode": ["00:31:12", "00:34:02"],
  "characters_on_screen": ["Jade", "Boyd"],
  "characters_mentioned": ["Tabitha"],
  "mode": "subjective_vision",
  "pov_character": "Jade",
  "evidence": ["from_s04e05_subtitles:00:31:12-00:34:02"]
}
```

Ключевое: **mode/modality**.

Примеры enum:

```text
objective_scene
dream
vision
hallucination
flashback
story_told_by_character
rumor
theory
ambiguous
```

Это прямо лечит ошибку вида:

> Jade видел лес → Boyd физически был в лесу.

Правильная запись:

```json
{
  "claim": "Jade experiences a vision of the forest while at the Sheriff Station.",
  "modality": "vision",
  "physical_location": "Sheriff Station",
  "perceived_location": "forest",
  "not_claimed": ["Boyd is physically in the forest"]
}
```

#### Layer 3: Structured Claim Store

Каждый факт — отдельный claim с citation.

```json
{
  "claim_id": "c_91823",
  "subject": "Jade",
  "predicate": "experiences_vision_of",
  "object": "forest",
  "canonicality": "canon",
  "epistemic_status": "observed_in_episode",
  "modality": "vision",
  "valid_during": {
    "season": 4,
    "episode": 5
  },
  "source_refs": [
    {
      "source_id": "from_s04e05_transcript",
      "span": "00:31:12-00:34:02",
      "quote": "..."
    }
  ],
  "confidence": 0.92
}
```

Не надо хранить “Jade понял правду о городе” как факт. Это interpretation/theory.

#### Layer 4: Knowledge Graph

Neo4j / ArangoDB / RDF/Wikibase-style graph нужен для связей:

```text
(Character)-[:APPEARS_IN {presence:on_screen}]->(Scene)
(Character)-[:MENTIONED_IN]->(Scene)
(Character)-[:RELATED_TO {type:"sister"}]->(Character)
(Event)-[:OCCURS_IN]->(Episode)
(Theory)-[:SUPPORTED_BY]->(Claim)
(Theory)-[:CONTRADICTED_BY]->(Claim)
```

Но KG должен ссылаться на claim/evidence. Иначе это просто ещё одна hallucination database.

Лучший паттерн — как в Wikidata:

> statement + qualifiers + references.

Например:

```text
Boyd present in scene 17
qualifier: presence_type = on_screen
reference: FROM S4E5 00:31:12-00:34:02
```

---

## 2. Как сделать LLM librarian, а не author

Температура 0 не решает. Нужны process constraints.

### A. Extraction-only JSON schema

LLM не пишет prose. Только JSON по схеме.

Плохо:

> “Summarize the scene.”

Лучше:

```text
Extract only explicitly supported facts.
Do not infer motives.
Do not resolve ambiguity.
If speaker is unknown, use speaker_id: unknown.
If a character is merely mentioned, do not mark present.
Return empty arrays when unsupported.
```

Schema:

```json
{
  "characters_on_screen": [],
  "characters_mentioned": [],
  "events": [],
  "dialogue_claims": [],
  "uncertain_speaker_lines": [],
  "visions_or_dreams": [],
  "theories": []
}
```

### B. Evidence quote required for every extracted claim

Если claim не может приложить quote/span — он не сохраняется.

```json
{
  "claim": "Mark is aware that Gemma may still be alive.",
  "evidence_quote": "...",
  "source_span": "S2E7 00:18:10-00:18:25"
}
```

### C. Validation pass: claim must be entailed by source

После extraction запускается второй этап:

```text
Given the source span and extracted claim, is the claim:
- entailed
- contradicted
- not enough information
```

Сохранять только `entailed`.

Это FEVER/NLI-style подход. Можно делать LLM-judge, можно маленькой NLI-моделью, можно обеими.

### D. No speaker guessing

Для SRT speaker `?`:

```json
{
  "speaker": "unknown",
  "speaker_candidates": [
    {"character": "Boyd", "confidence": 0.42},
    {"character": "Jade", "confidence": 0.31}
  ],
  "attribution_status": "unverified"
}
```

Нельзя превращать candidate в canon.

### E. Разделить canonical facts и fan theories физически

Не просто поле `type`.

Лучше разные collections/tables:

```text
canon_claims
official_claims
wiki_claims
fan_theories
theory_evidence_links
```

Fan theory не должна попадать в canon retrieval без явного режима:

> “Обсудим теории.”

### F. Temporal model

У каждого claim:

```json
{
  "introduced_in": "S2E3",
  "valid_through": "S4E2",
  "narrative_time": "before Colony House attack",
  "release_order": 17
}
```

И при ответе:

> “as of S2E5”  
> “as of latest aired episode”  
> “known to audience by S3E1”  
> “known to character Boyd by S4E5”

Это важно: знание аудитории ≠ знание персонажа.

---

## 3. Реальные системы и reference architectures

### Google NotebookLM

Ближайший массовый пример source-grounded QA. Сильные стороны:

- отвечает по загруженным источникам;
- показывает цитаты;
- меньше фантазирует, чем обычный чат.

Ограничение: не canonical knowledge graph, слабая структурная память, не решает хорошо chronology/POV/modalities.

### Microsoft GraphRAG

Хорош для corpora-level reasoning:

- извлекает entities/relationships;
- строит community summaries;
- улучшает global questions.

Но vanilla GraphRAG опасен для canon, если summaries становятся source of truth. Для lore надо делать GraphRAG только поверх claim store with provenance.

### LlamaIndex / LangChain / Haystack

Не готовые lore-системы, но дают building blocks:

- citation query engines;
- structured extraction;
- property graph index;
- hybrid search;
- reranking;
- tool-based retrieval.

### Neo4j GraphRAG

Практичный вариант:

- Neo4j для персонажей, событий, эпизодов, отношений;
- vector index для scene retrieval;
- Cypher для точных вопросов типа “в каких сценах X и Y были вместе”.

### Wikibase / Semantic MediaWiki

Очень релевантная модель.

Wikidata-style statement:

```text
claim + qualifiers + references
```

Это почти идеальный формат для lore:

```text
Character: Helly R
Property: employed by
Value: Lumon
Qualifier: identity_context = innie
Reference: Severance S1E1 timestamp...
```

### Fandom/MediaWiki

Хороший source, но не truth. Fandom pages часто уже содержат интерпретации, fanon, outdated info. Их надо парсить как Tier 3, не смешивать с эпизодами.

### Academic-style идеи

Полезные направления:

- FEVER-style fact verification;
- RAG with attribution;
- FactScore-like проверка atomic facts;
- temporal knowledge graphs;
- NLI entailment checking;
- provenance-aware QA.

---

## 4. Attribution UX: минимум нагрузки, максимум доверия

Я бы делал 3 уровня.

### Level 1: compact inline citations

Ответ:

> Jade was physically at the Sheriff Station, but he experienced a vision of the forest. [S4E5 31:12–34:02] The scene is marked as subjective/vision, not an objective location change. [S4E5 32:01]

Не цитировать каждое слово, но каждый смысловой claim должен иметь source.

### Level 2: hover tooltip

При наведении:

```text
FROM S4E5, 00:31:12–00:34:02
Source: transcript
Quote: "..."
Status: canon / subjective vision
```

### Level 3: side panel “Evidence”

Справа:

```text
Evidence used:
1. Episode transcript, S4E5 00:31:12–00:34:02
2. Fandom page: Jade / Visions, retrieved May 18 2026
3. Reddit theory thread, r/FromTVEpix, marked fan theory
```

Цветовая маркировка:

```text
green: canon episode
blue: official/creator
yellow: wiki summary
purple: fan theory
red/gray: ambiguous/unverified
```

Очень важно показывать **status**, не только ссылку.

---

## 5. Explicit retrieval: можно ли запретить писать без источника?

Да, это must-have. Но это не “исключает hallucination на 100%”, а резко снижает её.

Практический pipeline:

### Step 1: classify query

```text
canonical_question
theory_discussion
relationship_graph
timeline_question
character_pov_question
```

### Step 2: retrieve explicit evidence

Hybrid retrieval:

- BM25 по именам/эпизодам;
- vector search по смыслу;
- graph traversal;
- filters по season/episode/source tier;
- reranker.

### Step 3: answer only from retrieved evidence

Prompt:

```text
You may answer only using the evidence blocks below.
Every factual sentence must cite evidence.
If evidence is insufficient, say "I don't have canonical evidence for that."
Separate canon from theory.
Do not use prior knowledge.
```

### Step 4: citation coverage check

После генерации разбить ответ на atomic claims:

```text
1. Jade was at the Sheriff Station.
2. Jade saw a forest.
3. The forest was a vision.
```

Для каждого проверить:

```text
Has citation?
Is claim entailed by cited source?
```

Claims без поддержки удаляются или переводятся в:

> “There is no cited canonical evidence for this.”

### Step 5: answer with abstention

Пример:

> “Canonically, we can say Jade experiences a forest vision while at the Sheriff Station. I don’t have evidence that Boyd was physically in the forest during that scene.”

Это лучше, чем уверенная ложь.

Главный риск explicit retrieval — **retrieval miss**. Если нужная сцена не найдена, модель скажет “не знаю”, хотя факт есть. Это лечится recall-oriented retrieval: multiple retrievers, entity aliases, episode filters, query expansion, graph lookup.

---

## 6. Три design choices, которые я бы сделал первыми

### 1. Claim-level provenance как hard requirement

Не сохранять ни одного факта без:

```text
source_id
timestamp/span
quote
canonicality
modality
confidence
```

Нет citation — нет claim.

Это важнее выбора Neo4j vs Postgres vs Pinecone.

---

### 2. Жёсткая ontological separation: canon / official / wiki / theory

Физически разные типы данных и разные retrieval modes.

Пример ответа:

```text
Canon:
- Mark works at Lumon as an innie/outie split subject. [S1E1...]

Fan theories:
- Some fans speculate that Lumon uses severance for immortality...
  Evidence used by theory: ...
  Contradictions/weak points: ...
```

Теории должны быть объектами:

```json
{
  "theory": "The town feeds on fear",
  "status": "fan_theory",
  "supporting_claims": [],
  "contradicting_claims": [],
  "falsifiability": "Would be weakened if..."
}
```

Это лечит “single-key fallacy”.

---

### 3. Scene/event model with modality and presence type

Минимальный schema:

```json
{
  "scene_id": "...",
  "episode": "S4E5",
  "timestamp": "...",
  "physical_location": "...",
  "perceived_location": "...",
  "modality": "objective_scene | vision | dream | flashback | told_story | ambiguous",
  "characters_on_screen": [],
  "characters_speaking": [],
  "characters_mentioned": [],
  "characters_voice_only": [],
  "pov_character": null
}
```

Это напрямую бьёт по вашим ошибкам:

| Ошибка | Лекарство |
|---|---|
| Hallucinated events | claim requires evidence |
| Canon/fan theory mix | separate stores/retrieval modes |
| Temporal compression | episode/time scoped claims |
| POV confusion | modality + POV fields |
| Mentioned-as-present | presence_type enum |
| Single-key fallacy | theories as hypotheses with support/contradiction |
| Wrong speaker attribution | unknown speaker preserved |

---

## Итоговая recommendation

Архитектура:

```text
Raw Sources
  → scene segmentation
  → structured extraction with strict JSON
  → claim verification / entailment check
  → canonical claim store
  → knowledge graph with references
  → hybrid RAG over scenes + claims + graph
  → cited answer generation
  → post-generation citation/entailment verifier
```

Хранилища:

- Postgres для claims/evidence;
- pgvector/Elasticsearch/OpenSearch для retrieval;
- Neo4j или RDF/Wikibase для graph relationships;
- object storage для raw transcripts/pages;
- Redis/cache для query-time retrieval.

Главный принцип:

> LLM не должен “помнить канон”. Он должен находить evidence, собирать claims и явно показывать, откуда они взяты.

Для фанатов доверие возникает не от красивого ответа, а от ощущения:

> “Система знает разницу между тем, что было показано, что было сказано, что персонаж видел, и что фанаты предполагают.”
