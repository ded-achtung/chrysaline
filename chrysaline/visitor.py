class Visitor:
    def __init__(self, world):
        self.world = world

    def visit(self, word, max_depth=3):
        """Существо идёт в гости к родственникам.

        word -> находим существо
        -> идём к ДЕТЯМ (организмы где оно часть)
        -> у детей смотрим КТО ЕЩЁ ТАМ ЖИВЁТ (другие части)
        -> идём к детям ДЕТЕЙ (абстракции)
        -> у абстракций смотрим слоты
        """
        w = self.world
        start = w._find_by_parts((word,))
        if not start:
            return {"found": False, "word": word}

        result = {
            "found": True,
            "word": word,
            "siblings": set(),
            "neg_siblings": set(),
            "slot_mates": set(),
            "contexts": [],
            "rules": [],
            "associated_slots": {},
            "concrete_relatives": set(),
        }

        neg_markers = w.neg_markers

        # ШАГ 1: Найти ВСЕ организмы где это слово — ЧАСТЬ
        my_organisms = []
        for c in w.creatures.values():
            if not c.alive or c.complexity < 2:
                continue
            if word in c.parts:
                my_organisms.append(c)
                result["contexts"].append(c.name)
                target = result["neg_siblings"] if c.valence == -1 else result["siblings"]
                for part in c.parts:
                    if part != word and not part.startswith("$") and part not in neg_markers:
                        target.add(part)

        # ШАГ 2: Пойти к детям моих организмов
        for organism in my_organisms:
            for child_id in organism.children:
                child = w.creatures.get(child_id)
                if child and child.alive:
                    target = result["neg_siblings"] if child.valence == -1 else result["siblings"]
                    for part in child.parts:
                        if part != word and not part.startswith("$") and part not in neg_markers:
                            result["concrete_relatives"].add(part)
                            target.add(part)

        # ШАГ 3: Среди моих организмов есть АБСТРАКЦИИ (со слотами)?
        for c in my_organisms:
            if c.slot_options:
                for slot_name, options in c.slot_options.items():
                    clean = {o for o in options if not o.startswith("$")}
                    if clean:
                        result["associated_slots"][slot_name] = clean
                        result["rules"].append({
                            "pattern": c.name,
                            "slot": slot_name,
                            "options": clean,
                            "fed": c.times_fed,
                        })

        # ШАГ 4: Я в СЛОТЕ какой-то абстракции? (я заменяемый)
        for c in w.creatures.values():
            if not c.alive or not c.slot_options:
                continue
            for slot_name, options in c.slot_options.items():
                clean = {o for o in options if not o.startswith("$")}
                if word in clean:
                    result["slot_mates"].update(clean - {word})
                    fixed = [p for p in c.parts if not p.startswith("$")]
                    result["rules"].append({
                        "pattern": c.name,
                        "slot": slot_name,
                        "context": fixed,
                        "mates": clean - {word},
                        "fed": c.times_fed,
                    })

        # ШАГ 5: Глубже — пойти к братьям и посмотреть ИХ организмы
        if max_depth > 1:
            for sibling in list(result["siblings"]):
                for c in w.creatures.values():
                    if not c.alive or c.complexity < 2:
                        continue
                    if sibling in c.parts:
                        for part in c.parts:
                            if part != sibling and part != word and not part.startswith("$"):
                                result["concrete_relatives"].add(part)
                        if c.slot_options:
                            for slot_name, options in c.slot_options.items():
                                clean = {o for o in options if not o.startswith("$")}
                                if clean and slot_name not in result["associated_slots"]:
                                    result["associated_slots"][slot_name] = clean

        result["rules"].sort(key=lambda r: -r["fed"])
        return result

    def query_category(self, category_word):
        """Какие элементы принадлежат этой категории?

        Собирает positive и negative evidence раздельно.
        Элемент включается только если positive > negative.
        """
        w = self.world
        structural_words = set()
        pos_parts = {}
        neg_parts = {}

        my_organisms = []
        for c in w.creatures.values():
            if not c.alive or c.complexity < 2:
                continue
            if category_word in c.parts:
                my_organisms.append(c)

        if not my_organisms:
            return set()

        for org in my_organisms:
            target = neg_parts if org.valence == -1 else pos_parts
            for part in org.parts:
                if part != category_word and not part.startswith("$") and part not in w.neg_markers:
                    target[part] = target.get(part, 0) + 1
            if org.slot_options:
                for slot_name, options in org.slot_options.items():
                    for opt in options:
                        if not opt.startswith("$") and opt not in w.neg_markers:
                            target[opt] = target.get(opt, 0) + 1

        n_orgs = len(my_organisms)
        for part, count in pos_parts.items():
            local_freq = count / n_orgs
            if local_freq >= 0.5:
                structural_words.add(part)

        results = set()
        for part, count in pos_parts.items():
            if part not in structural_words and count > neg_parts.get(part, 0):
                results.add(part)

        return results

    def query_rule(self, subject):
        """Какое правило связано с этим словом?"""
        info = self.visit(subject)
        if not info["found"]:
            return []

        results = []
        for rule in info["rules"]:
            pattern = rule["pattern"]
            fed = rule["fed"]
            energy = 0

            context = rule.get("context", [])
            mates = rule.get("mates", set())

            rule_text = pattern
            if context:
                rule_text = f"[{subject}]·{'·'.join(context)}"
            if mates:
                rule_text += f" заменяемые: {{{','.join(sorted(mates))}}}"

            results.append((rule_text, fed, energy))

        return results

    def query_associated(self, word1, word2):
        """Как связаны два слова?"""
        info1 = self.visit(word1)
        info2 = self.visit(word2)

        connections = []

        if word2 in info1["siblings"]:
            connections.append(f"'{word1}' и '{word2}' в одном организме")

        if word2 in info1["slot_mates"]:
            connections.append(f"'{word1}' и '{word2}' ЗАМЕНЯЕМЫ (в одном слоте)")

        for rule in info1["rules"]:
            opts = rule.get("options", set())
            if word2 in opts:
                connections.append(
                    f"'{word2}' в слоте абстракции '{rule['pattern']}'")

        return connections
