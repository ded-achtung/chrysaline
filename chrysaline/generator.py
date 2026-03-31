class Generator:

    _Q_WORDS = {
        "что", "кто", "где", "как", "какой", "какая", "какое",
        "какие", "сколько", "чем", "кому", "куда", "откуда",
        "почему", "зачем", "когда",
    }

    def __init__(self, world):
        self.world = world

    def generate(self, creature, max_per_slot=None):
        """Развернуть абстракцию в конкретные предложения."""
        if not creature.slot_options:
            return [" ".join(creature.parts)]

        slot_names = sorted(creature.slot_options.keys())
        slot_values = []
        for sn in slot_names:
            clean = sorted(o for o in creature.slot_options[sn]
                           if not o.startswith("$"))
            if max_per_slot and len(clean) > max_per_slot:
                clean = clean[:max_per_slot]
            slot_values.append(clean)

        if not slot_values or any(len(v) == 0 for v in slot_values):
            return []

        combos = [[]]
        for values in slot_values:
            combos = [c + [v] for c in combos for v in values]

        results = []
        for combo in combos:
            mapping = dict(zip(slot_names, combo))
            words = [mapping.get(p, p) for p in creature.parts]
            results.append(" ".join(words))
        return results

    def generate_from(self, word, max_per_slot=None):
        """Найти абстракции содержащие word и сгенерировать из них."""
        w = self.world
        results = []
        for c in w.creatures.values():
            if not c.alive or not c.slot_options:
                continue
            fixed_parts = [p for p in c.parts if not p.startswith("$")]
            if word in fixed_parts:
                sentences = self.generate(c, max_per_slot=max_per_slot)
                results.append({
                    "pattern": c.name,
                    "energy": c.energy,
                    "fed": c.times_fed,
                    "sentences": sentences,
                })
        results.sort(key=lambda r: -r["fed"])
        return results

    def ask(self, question):
        """Ответить на вопрос через visiting-цепочки.

        Порядок стратегий:
        1. Пересечение братьев (быстро, точно)
        2. Поиск по слотам абстракций (старый метод)
        3. Транзитивные цепочки (как think())
        4. Фильтрация шума через service_score
        """
        w = self.world
        from .visitor import Visitor
        visitor = Visitor(w)

        words = [wd.strip("?!., ").lower() for wd in question.split()]
        words = [wd for wd in words if wd]

        q_words = [wd for wd in words if wd in self._Q_WORDS]
        content_words = [wd for wd in words if wd not in self._Q_WORDS
                         and len(wd) > 1]

        result = {
            "question": question,
            "q_type": q_words[0] if q_words else "?",
            "content_words": content_words,
            "answers": [],
            "reasoning": [],
        }

        if not content_words:
            return result

        known_words = [wd for wd in content_words
                       if w._find_by_parts((wd,)) is not None]
        search_words = known_words if known_words else content_words

        # ══════════════════════════════════════════
        # Стратегия 1: Пересечение братьев
        # Для каждого слова — visiting. Если два слова из вопроса
        # оба знают третье слово — это кандидат на ответ.
        # ══════════════════════════════════════════
        if len(search_words) >= 2:
            visit_cache = {}
            for sw in search_words:
                info = visitor.visit(sw)
                if info["found"]:
                    visit_cache[sw] = info["siblings"]
                else:
                    visit_cache[sw] = set()

            # Пересечение: слова, которые знают ВСЕ search_words
            if all(visit_cache.get(sw) for sw in search_words):
                sets = [visit_cache[sw] for sw in search_words]
                intersection = sets[0]
                for s in sets[1:]:
                    intersection = intersection & s
                # Убираем сами search_words из пересечения
                intersection -= set(search_words)
                if intersection:
                    # Ранжируем по энергии
                    ranked = []
                    for candidate in intersection:
                        cr = w._find_by_parts((candidate,))
                        energy = cr.energy if cr else 0
                        ranked.append((candidate, energy))
                    ranked.sort(key=lambda x: -x[1])
                    for candidate, _ in ranked:
                        result["answers"].append(candidate)
                    result["reasoning"].append(
                        f"пересечение братьев: {sorted(intersection)[:8]}")

            # Попарное пересечение (если полное не дало результата)
            if not result["answers"] and len(search_words) >= 2:
                for i in range(len(search_words)):
                    for j in range(i + 1, len(search_words)):
                        sw1, sw2 = search_words[i], search_words[j]
                        s1 = visit_cache.get(sw1, set())
                        s2 = visit_cache.get(sw2, set())
                        pair_inter = (s1 & s2) - set(search_words)
                        if pair_inter:
                            for candidate in pair_inter:
                                if candidate not in result["answers"]:
                                    result["answers"].append(candidate)
                            result["reasoning"].append(
                                f"пересечение '{sw1}'∩'{sw2}': {sorted(pair_inter)[:6]}")

        # ══════════════════════════════════════════
        # Стратегия 2: Поиск по слотам абстракций
        # Старый метод — хорошо работает для "что ест кот"
        # ══════════════════════════════════════════
        if not result["answers"]:
            min_match = min(2, len(search_words))
            candidates = []
            for word in search_words:
                for c in w.creatures.values():
                    if not c.alive or not c.slot_options or c.valence == -1:
                        continue
                    fixed = [p for p in c.parts if not p.startswith("$")]
                    if word not in fixed:
                        continue
                    match_count = sum(1 for cw in search_words if cw in fixed)
                    if match_count < min_match:
                        continue
                    for slot_name, options in c.slot_options.items():
                        clean = sorted(o for o in options
                                       if not o.startswith("$")
                                       and o not in w.neg_markers)
                        if clean:
                            candidates.append((c, slot_name, clean, match_count))
            candidates.sort(key=lambda x: (-x[3], -x[0].times_fed))
            seen_patterns = set()
            for c, slot_name, clean, _ in candidates:
                key = (c.name, slot_name)
                if key in seen_patterns:
                    continue
                seen_patterns.add(key)
                result["answers"].extend(clean)
                result["reasoning"].append(f"{c.name} → {slot_name}={clean}")

        # ══════════════════════════════════════════
        # Стратегия 3: Visiting по каждому слову → слоты из правил
        # ══════════════════════════════════════════
        if not result["answers"]:
            for word in search_words:
                info = visitor.visit(word)
                if not info["found"]:
                    continue
                for rule in info.get("rules", []):
                    pattern_parts = rule["pattern"].split("·")
                    # Правило содержит другие search_words?
                    if any(cw in pattern_parts for cw in search_words if cw != word):
                        opts = rule.get("options", set())
                        clean = sorted(o for o in opts if not o.startswith("$"))
                        if clean:
                            result["answers"].extend(clean)
                            result["reasoning"].append(
                                f"'{word}' → {rule['pattern']} → {clean}")

        # ══════════════════════════════════════════
        # Стратегия 4: Организмы с парами слов
        # ══════════════════════════════════════════
        if not result["answers"]:
            for word in search_words:
                info = visitor.visit(word)
                if not info["found"]:
                    continue
                siblings = info["siblings"]
                for other in search_words:
                    if other == word:
                        continue
                    if other in siblings:
                        for c in w.creatures.values():
                            if not c.alive or c.complexity < 2:
                                continue
                            if word in c.parts and other in c.parts:
                                extras = [p for p in c.parts
                                          if p != word and p != other
                                          and not p.startswith("$")]
                                if extras:
                                    result["answers"].extend(extras)
                                    result["reasoning"].append(
                                        f"'{word}'·'{other}' → {extras}")
                                if c.slot_options:
                                    for sn, opts in c.slot_options.items():
                                        clean = [o for o in opts
                                                 if not o.startswith("$")]
                                        result["answers"].extend(clean)
                                        result["reasoning"].append(
                                            f"{c.name} slot → {clean}")

        # ══════════════════════════════════════════
        # Стратегия 5: Транзитивные цепочки (как think())
        # A→B→C: если search_word знает B, и B знает C,
        # и C подходит по типу вопроса — добавить C
        # ══════════════════════════════════════════
        if not result["answers"]:
            link_words = {"это", "обозначает", "означает", "называют"}
            for word in search_words:
                info = visitor.visit(word)
                if not info["found"]:
                    continue
                for brother in info["siblings"]:
                    if brother in set(search_words) | link_words:
                        continue
                    if len(brother) <= 1 or brother.startswith("$"):
                        continue
                    # Visiting по брату
                    info_b = visitor.visit(brother)
                    if not info_b["found"]:
                        continue
                    for candidate in info_b["siblings"]:
                        if candidate == word or candidate == brother:
                            continue
                        if candidate in info["siblings"]:
                            continue  # A уже знает C
                        if candidate in link_words or len(candidate) <= 1:
                            continue
                        if candidate.startswith("$"):
                            continue
                        # Проверяем осмысленность: есть ли link_word в цепочке?
                        has_link = False
                        for c in w.creatures.values():
                            if not c.alive or c.complexity < 2:
                                continue
                            parts = set(c.parts)
                            if word in parts and brother in parts:
                                if parts & link_words:
                                    has_link = True
                                    break
                            if brother in parts and candidate in parts:
                                if parts & link_words:
                                    has_link = True
                                    break
                        if has_link:
                            if candidate not in result["answers"]:
                                result["answers"].append(candidate)
                                result["reasoning"].append(
                                    f"цепочка: {word}→{brother}→{candidate}")

        # ══════════════════════════════════════════
        # Дедупликация
        # ══════════════════════════════════════════
        seen = set()
        unique = []
        for a in result["answers"]:
            if a not in seen and a not in self._Q_WORDS and len(a) > 0:
                seen.add(a)
                unique.append(a)
        result["answers"] = unique

        # ══════════════════════════════════════════
        # Фильтрация шума через service_score
        # ══════════════════════════════════════════
        if len(result["answers"]) > 3:
            filtered = [a for a in result["answers"]
                        if w.service_score(a) < 0.4]
            if filtered:
                result["answers"] = filtered

        # Негативная фильтрация
        if result["answers"] and w.neg_markers:
            neg_evidence = set()
            for word in search_words:
                info = visitor.visit(word)
                if info["found"]:
                    neg_evidence.update(info.get("neg_siblings", set()))
            if neg_evidence:
                filtered = [a for a in result["answers"] if a not in neg_evidence]
                if filtered:
                    result["answers"] = filtered
                    result["reasoning"].append(
                        f"neg-фильтр убрал: {sorted(neg_evidence & seen)}")

        # ══════════════════════════════════════════
        # Обучение на собственном опыте
        # ══════════════════════════════════════════
        if result["answers"]:
            for answer in result["answers"][:3]:
                experience = content_words + [answer]
                if len(experience) >= 2:
                    self.world.feed_sentence(experience)

        return result
