# Anti-patterns LLM-моделей которые надо предотвращать

Эти ошибки реально случались и были задокументированы. Перед каждой генерацией prediction / state snapshot - проверь себя по этому списку.

## AP-001. Temporal compression

Сжатие событий из разных сезонов в "недавнее". LLM видит яркое событие из S2 и подаёт как current в S4.

**Пример (FROM):**
- Wrong: "Fatima восстанавливается после родов" в snapshot S4
- Right: Fatima родила в S2/S3. В S4 строит Голема. "Восстанавливается" - не текущее.

**Правило:**
Каждое утверждение про "current/recent" в state должно иметь episode_ref. Если ты не можешь привязать к последним сериям - это historical_background, не current.

## AP-002. Hallucination POV confusion

Расширенные галлюцинации/dreams/trip-сцены в сериалах часто описываются через POV персонажа. Wiki-recap пишет их как объективные события. LLM трактует как реальность.

**Пример (FROM S4E5):**
- Wiki recap: "Jade and Boyd wander through the forest"
- Реально: Boyd удерживал Jade в Sheriff's Station. ВСЯ "лесная" часть - mushroom trip.
- Wrong inference: location=forest для обоих
- Right inference: location=sheriff_station, Jade liminal_state=mushroom_trip

**Правило:**
В сериалах с trips/curses/dreams/visions/time-travel явно выделяй objective_location vs subjective_perception. Если recap содержит слова hallucinate/vision/dream/trip/curse/mushroom - flag сцены как НЕ-объективные.

## AP-003. Scene boundary contamination

Mechanical time-based chunking (30s окна) ломает реальные scene boundaries. Реплики соседней сцены попадают в текущую.

**Правило:**
Если строишь scene_ledger - сначала отдельный LLM-проход НА сегментацию по реальным границам (location/time/character-set change), потом уже extraction.

## AP-004. "Mentioned" treated as "present"

LLM пишет "Martin: present" когда Martin только упомянут в реплике.

**Правило:**
Разделяй поля строго:
- characters_present_in_scene (физически в кадре)
- characters_mentioned_only (произнесены, не присутствуют)
- entities_seen_in_vision (только в hallucination)
- objects_present_visual VS objects_mentioned_dialogue

## AP-005. Single-key fallacy (для теорий)

Фан-теория объясняет ВСЁ одним ключом (например "это всё симуляция"). Удобно но не falsifiable.

**Правило:**
Если теория покрывает > 80% всех загадок одной механикой - штраф к explanatory_power. Хорошая теория объясняет 3-5 загадок, не 15.

## AP-006. Creator lied (для теорий)

Теория зависит от того что "создатели обманывают" - в интервью говорят одно, а снимают другое. Это escape hatch для retro-fitting.

**Правило:**
Если теория требует считать creator-statements ложью - штраф к creator_plausibility и красный флаг.

## AP-007. Selection bias на reddit

Топовые reddit-теории = популярные, НЕ обязательно правильные. Они отражают что хочет фандом, не что снимут.

**Правило:**
Используй reddit как source for "what fans believe", не как evidence_quality. Status: fan_theory всегда.

## AP-008. Verbose validation rules

Validation rule "Boyd confronts the entity in a meaningful way" - не falsifiable, можно засчитать как угодно.

**Правило:**
Каждый validation_rule = atomic event + actor + object + location + episode. Default outcome = miss если evidence не найден явно.

## Self-check перед сохранением prediction

- [ ] Все факты канона имеют ссылку на эпизод (AP-001)
- [ ] Видения/dreams помечены как hallucination не объективная реальность (AP-002)
- [ ] characters_present не путаются с mentioned (AP-004)
- [ ] Теория не использует single key (AP-005)
- [ ] Не требует creator-lie (AP-006)
- [ ] Validation rules atomic + falsifiable (AP-008)
