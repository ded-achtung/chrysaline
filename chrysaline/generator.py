class Generator:

    _Q_WORDS = {
        "что", "кто", "где", "как", "какой", "какая", "какое",
        "какие", "сколько", "чем", "кому", "куда", "откуда",
        "почему", "зачем", "когда",
    }

    def __init__(self, world):
        self.world = world

    def generate(self, creature, max_per_slot=None):
        """Развернуть абстракцию в конкретные предложения.

        Для каждого варианта в каждом слоте — одно предложение.
        Если несколько слотов, берётся декартово произведение
        (ограниченное max_per_slot вариантами на слот).
        """
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
        """Ответить на произвольный вопрос через visiting.

        Разбирает вопрос на слова, находит ключевые (не вопросительные),
        ищет связи между ними, собирает ответ из слотов и родственников.
        """
        w = self.world
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
        unknown_words = [wd for wd in content_words if wd not in known_words]

        search_words = known_words if known_words else content_words

        # Стратегия 1: абстракции где ключевые слова = фиксированные части
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
                                   if not o.startswith("$") and o not in w.neg_markers)
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

        # Стратегия 2: visiting по каждому ключевому слову
        if not result["answers"] and len(search_words) >= 2:
            from .visitor import Visitor
            visitor = Visitor(w)
            primary = search_words[0]
            info = visitor.visit(primary)
            if info["found"]:
                all_relatives = info["siblings"] | info.get("concrete_relatives", set())
                for other in search_words[1:]:
                    if other in all_relatives:
                        result["reasoning"].append(
                            f"'{primary}' visiting → знает '{other}'")
                for rule in info.get("rules", []):
                    opts = rule.get("options", set())
                    clean = sorted(o for o in opts if not o.startswith("$"))
                    if clean:
                        relevant = False
                        pattern_parts = rule["pattern"].split("·")
                        for cw in search_words:
                            if cw in pattern_parts:
                                relevant = True
                        if relevant:
                            result["answers"].extend(clean)
                            result["reasoning"].append(
                                f"{rule['pattern']} → {clean}")

        # Стратегия 3: visiting по каждому слову -> собрать все слоты
        if not result["answers"]:
            from .visitor import Visitor
            visitor = Visitor(w)
            for word in search_words:
                info = visitor.visit(word)
                if not info["found"]:
                    continue
                for slot_name, options in info.get("associated_slots", {}).items():
                    clean = sorted(options)
                    other_sw = [cw for cw in search_words if cw != word]
                    for rule in info.get("rules", []):
                        pattern_parts = rule["pattern"].split("·")
                        if any(cw in pattern_parts for cw in other_sw):
                            opts = rule.get("options", set())
                            slot_clean = sorted(o for o in opts
                                                if not o.startswith("$"))
                            if slot_clean:
                                result["answers"].extend(slot_clean)
                                result["reasoning"].append(
                                    f"'{word}' → {rule['pattern']} → {slot_clean}")

        # Стратегия 4: "что делает X" / "что ест X"
        if not result["answers"]:
            from .visitor import Visitor
            visitor = Visitor(w)
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

        seen = set()
        unique = []
        for a in result["answers"]:
            if a not in seen and a not in self._Q_WORDS and len(a) > 0:
                seen.add(a)
                unique.append(a)
        result["answers"] = unique

        # Subtract negative evidence: collect neg_siblings for each answer
        if result["answers"] and w.neg_markers:
            from .visitor import Visitor
            visitor = Visitor(w)
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

        # ══════════════════════════════════════════════════
        # НОВОЕ: Обучение на собственном опыте
        # Результат ask() возвращается в экосистему
        # ══════════════════════════════════════════════════
        if result["answers"]:
            for answer in result["answers"][:3]:  # максимум 3 ответа
                # Формируем предложение из ключевых слов + ответ
                experience = content_words + [answer]
                if len(experience) >= 2:
                    self.world.feed_sentence(experience)

        return result
