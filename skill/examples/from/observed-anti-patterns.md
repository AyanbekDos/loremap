# Anti-patterns: ошибки LLM-моделей которые нужно предотвращать

Этот файл - ledger выявленных ошибок и правила их предотвращения. Каждая запись содержит:
- что произошло
- root cause
- prevention rule
- статус (active prevention | observed only)

Обязательно читать перед каждой генерацией state_snapshot / predictions.

---

## AP-001. Temporal compression: события давнего сезона как "недавние"

**Дата выявления:** 2026-05-18 (Босс отловил)

**Что произошло:**
В state-after-S4E5.yaml Fatima Hassan имела `current_state_summary: "Восстанавливается после родов Smiley, тайно работает с Elgin над созданием Golem"`. Босс заметил: Fatima родила Smiley в S2/S3 (давно), в S4 она НЕ "восстанавливается после родов", она строит Голема.

**Root cause:**
1. Wiki entity page Fatima Hassan содержит full bio через все сезоны без явных timestamps "this happened in S2".
2. LLM при компрессии "fill state_summary" склонна сжимать timeline и подавать давние события как "недавние" если они сильно эмоционально окрашены.
3. Prompt не требовал привязки каждого утверждения к конкретному эпизоду.
4. Episode recaps от S4 содержали "Fatima feels connected to Smiley" - LLM экстраполировала "значит роды недавно".

**Prevention rule (active с 2026-05-18):**

В build_state_snapshot.py prompt теперь обязательны:

1. Разделение полей: `historical_background` (1 предложение из прошлых сезонов) + `current_arc_summary` (только S4) + `current_action` (последняя сцена).
2. Каждое утверждение в current_action и current_arc должно быть прослеживаемо к КОНКРЕТНОМУ эпизоду S4E1-target. Если нельзя - переносить в historical.
3. Поля `possessions`, `knows`, `relations`, `unresolved_actions` имеют обязательный `_episode` или `_episode_ref` (либо SxEy либо "before-S4").
4. Явные примеры anti-pattern в prompt с указанием Fatima/Smiley как плохого примера.

**Validation:**
После генерации snapshot ОБЯЗАТЕЛЬНЫЙ verification pass - вторая LLM проверяет каждое утверждение: "is this current activity or historical?". Если LLM не может привязать к S4 episode - переносить в historical_background.

**Status:** active prevention

---

## AP-002. Hallucination/POV-distortion confusion

**Дата выявления:** 2026-05-18 (Босс отловил)

**Что произошло:**
В state-after-S4E5.yaml Boyd location: forest, Jade location: forest. State_summary говорил "Boyd ведёт Jade всё глубже в лес следуя видениям". Active_threads имели T-S4E5-boyd-jade-deeper (urgency: high).

ВСЁ ЭТО НЕВЕРНО.

Канон S4E5 "What a Long Strange Trip It's Been": Jade принимает грибы в Sheriff's Station. Весь эпизод показывает его галлюцинации (лес, Colony House basement, Tunnels, ghoulish children, past lives). Boyd физически остаётся в Sheriff Station и удерживает Jade. В ФИНАЛЕ серии Jade выходит из трипа, удивлённо узнаёт что часы провёл в Station, и говорит "I know how to get them home".

То есть: forest scenes = галлюцинации Jade. Реальное location Boyd+Jade = Sheriff's Station. Реальный cliffhanger = Jade с revelation about saving children, НЕ "поход глубже в лес".

**Root cause:**
1. Fandom recap описывает события глазами Jade-POV. Hallucinated scenes пишутся как "Jade and Boyd wander through the forest" - так словно это реально.
2. Recap указывает на реальность только при "snap back to reality" в конце: "Boyd brings him back to reality in the Sheriff's Station". LLM воспринимает все предыдущие сцены как объективные, а финальную как "вернулись".
3. Prompt не требовал отделять hallucination/dream/vision от objective reality.
4. Это создало вилку: state snapshot полностью неверен про физическое location обоих, активные threads построены вокруг "пути в лесу" которого нет, prediction S4E6 строит на false premise.

**Prevention rule (active с 2026-05-18):**

В build_state_snapshot.py prompt теперь добавлены правила:

1. Для каждого character явно указать: где находится физически в реальности vs где видит/думает что находится в видениях.
2. Если эпизод имеет extended hallucination/dream/vision sequence (mushroom trip, Music Box curse, dream, time-travel sequence) - в prompt указать что эти сцены НЕ должны быть restored как физические события.
3. Поле `last_location` = ТОЛЬКО objective physical location. Если был в видении - возможный отдельное поле `vision_location` или metadata.
4. Поле `liminal_state` обязательно отмечает trips/curses: 'mushroom_trip_in_progress', 'mushroom_trip_just_ended', 'cursed', 'dream', etc.
5. Cliffhanger description должен указывать что РЕАЛЬНО оставлено: 'Jade has revelation after exiting mushroom trip in Sheriff Station' - НЕ 'Jade продолжает идти в лесу'.

**Validation:**
verify_state_snapshot.py должен искать слова hallucinat / vision / dream / trip / curse в episode recap и flag scenes где LLM трактовала их как объективное действие.

**Status:** active prevention. Не повторять никогда.

---

## AP-003. Scene boundary contamination

**Дата выявления:** 2026-05-18 (GPT-5.5 critique PLAN v3)

**Что произошло:**
В PLAN v3 предлагалось использовать 30s mechanical chunks как scene units. Critique поднял что это ломает реальные scene boundaries: реплики из соседней сцены попадают в текущую, location меняется внутри одного chunk, character-set смешивается.

**Root cause:**
Mechanical time-based chunking не учитывает narrative boundaries. Сцена FROM может длиться 14s или 4 min - и в обоих случаях chunk-разрез внутри сцены создаст contamination.

**Prevention rule (active с 2026-05-18):**

1. scene_id присваивается ТОЛЬКО после Pass 1 (LLM-сегментация), не из time-chunks.
2. Pass 1 промпт: "найди реальные scene boundaries по location change, time-of-day change, character-set change, ИЛИ значительному event/cut".
3. Pass 2 (per-scene extraction) использует уже scene_id, не chunk_id.
4. Verifier (Pass 3) проверяет что каждая запись имеет конкретные start_sec/end_sec, а не chunk-границы.

**Status:** active prevention

---

## AP-004. "Mentioned" treated as "present"

**Дата выявления:** 2026-05-18 (GPT-5.5 critique PLAN v3)

**Что произошло:**
LLM при extraction склонна писать "Martin: present" когда персонаж только УПОМЯНУТ в диалоге. Аналогично "BIW present" когда персонаж его только видел в воспоминании.

**Root cause:**
Default literary summary не различает уровни presence. "Boyd mentions Martin" -> модель пишет present=true.

**Prevention rule (active с 2026-05-18):**

scene_ledger обязательные separate поля:
- characters_present_in_scene (физически в кадре в текущий момент)
- characters_mentioned_only (произнесены, но не присутствуют)
- entities_seen_in_vision (видны в галлюцинации/dream/memory)
- entities_referenced_in_memory (упомянуты как воспоминание)
- objects_present_visual (видны на экране)
- objects_mentioned_dialogue (произнесены, но не показаны)

Каждое quote имеет:
- source_character (кто говорит)
- observer_character (про кого утверждение, если применимо)
- viewer_only (зритель знает, персонаж нет)
- claim_type (observed | reported | inferred | theory | lie_possible | hallucination | entity_message)

**Status:** active prevention

---

## Правила для всех будущих LLM-prompts в проекте

1. **Time-grounded claims**: каждое утверждение о "недавнем" / "current" / "только что" ДОЛЖНО иметь episode-ref.
2. **Источник за выводом**: если утверждение не из конкретной сцены - явно метить inference / speculation.
3. **No timeline compression**: события из разных сезонов НЕ сжимать в "недавнее" даже если эмоционально связаны.
4. **Anti-pattern check at end of prompt**: каждый рабочий prompt должен заканчиваться "Перед выводом проверь себя по wiki/synthesis/_anti_patterns.md" (или дублировать ключевые anti-patterns inline).

Этот файл версионируется в git. Каждое исправление = новый коммит с описанием AP-NNN.
