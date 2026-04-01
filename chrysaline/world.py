from .creature import Creature


class World:
    def __init__(self):
        self.creatures = {}
        self.tick_count = 0
        self.stats = {
            "born": 0, "died": 0, "merged": 0, "crossbred": 0,
            "fed": 0, "absorbed": 0, "split": 0,
        }
        self.by_parts = {}
        self.events = []
        self.max_creatures = 2000
        self.neg_markers = set()
        self._neg_candidates = {}

    def _register(self, creature):
        self.creatures[creature.id] = creature
        self.by_parts[creature.parts] = creature.id
        self.stats["born"] += 1

    def _find_by_parts(self, parts):
        key = tuple(parts)
        if key in self.by_parts:
            cid = self.by_parts[key]
            if cid in self.creatures and self.creatures[cid].alive:
                return self.creatures[cid]
        return None

    def _find_competitor_energy(self, parts):
        """Найти энергию сильнейшего конкурента для данных parts.

        Два уровня:
        1. Через абстракции с 2+ слотами (точный конфликт)
        2. Middle-match для complexity>=4 (та же середина, разные края)

        Возвращает 0.0 если конкурентов нет.
        """
        complexity = len(parts)
        if complexity < 2:
            return 0.0

        best = 0.0

        # Уровень 1: абстракции с 2+ слотами
        for abst in self.creatures.values():
            if not abst.alive or not abst.slot_options:
                continue
            if abst.complexity != complexity:
                continue
            match = True
            slot_positions = {}
            for i in range(abst.complexity):
                if abst.parts[i].startswith("$"):
                    slot_positions[i] = (abst.parts[i], parts[i])
                elif abst.parts[i] != parts[i]:
                    match = False
                    break
            if not match or len(slot_positions) < 2:
                continue
            for pos, (slot_name, our_value) in slot_positions.items():
                if slot_name not in abst.slot_options:
                    continue
                clean = {o for o in abst.slot_options[slot_name]
                         if not o.startswith("$")}
                if our_value not in clean:
                    continue
                for other_val in clean:
                    if other_val == our_value:
                        continue
                    comp_parts = list(parts)
                    comp_parts[pos] = other_val
                    competitor = self._find_by_parts(tuple(comp_parts))
                    if not competitor or not competitor.alive:
                        continue
                    is_conflict = True
                    for op in slot_positions:
                        if op == pos:
                            continue
                        if parts[op] != comp_parts[op]:
                            is_conflict = False
                            break
                    if is_conflict and competitor.energy > best:
                        best = competitor.energy

        # Уровень 2: прямое сравнение — все кроме одной позиции совпадают
        if best == 0 and complexity >= 2:
            for c in self.creatures.values():
                if not c.alive or c.complexity != complexity:
                    continue
                if c.parts == tuple(parts):
                    continue
                diffs = sum(1 for i in range(complexity) if parts[i] != c.parts[i])
                if diffs == 1 and c.energy > best:
                    best = c.energy

        return best

    def _confirmed_feed(self, creature, base_amount):
        """Питание с проверкой на конкурентов."""
        if creature.complexity < 2:
            creature.feed(base_amount)
            return base_amount

        comp_e = self._find_competitor_energy(creature.parts)

        if comp_e == 0:
            creature.feed(base_amount)
            return base_amount
        elif creature.energy >= comp_e * 0.8:
            weak = base_amount * 0.2
            creature.feed(weak)
            return weak
        else:
            return 0.0

    def observe(self, word):
        existing = self._find_by_parts((word,))
        if existing:
            existing.feed(0.5)
            self.stats["fed"] += 1
            return existing
        c = Creature([word])
        self._register(c)
        return c

    def learn_negation(self, word):
        """Ручной override: пометить слово как маркер отрицания."""
        self.neg_markers.add(word)

    def _detect_valence(self, parts):
        """Если среди частей есть подтверждённый маркер отрицания — организм отрицательный."""
        for part in parts:
            if part in self.neg_markers:
                return -1
        return 1

    def _detect_neg_markers(self, organism):
        """Авто-детекция маркеров отрицания через противоречия.

        Проверяет ТОЛЬКО 3-словные организмы (X·candidate·Y).
        Ищет абстракцию $0·Y где X мог бы быть в слоте но его нет.
        X должен быть СВЯЗАН с существующими членами слота
        через МАЛЕНЬКУЮ абстракцию (< 10 членов) — иначе false positive.
        """
        if organism.complexity != 3:
            return
        subject = organism.parts[0]
        candidate = organism.parts[1]
        predicate = organism.parts[2]
        if candidate.startswith("$") or subject.startswith("$"):
            return

        for c in self.creatures.values():
            if not c.alive or not c.slot_options or c.complexity != 2:
                continue
            if c.parts[1] != predicate or not c.parts[0].startswith("$"):
                continue
            slot_name = c.parts[0]
            existing = c.slot_options.get(slot_name, set())
            clean_existing = {o for o in existing if not o.startswith("$")}
            if subject in clean_existing or len(clean_existing) < 2:
                continue
            for other in self.creatures.values():
                if not other.alive or not other.slot_options:
                    continue
                for sn, opts in other.slot_options.items():
                    slot_clean = {o for o in opts if not o.startswith("$")}
                    if len(slot_clean) > 10:
                        continue
                    if subject in slot_clean and (slot_clean & clean_existing):
                        self._neg_candidates[candidate] = self._neg_candidates.get(candidate, 0) + 1
                        if self._neg_candidates[candidate] >= 2:
                            self.neg_markers.add(candidate)
                        return

    def _apply_valence(self, organism):
        """Пометить организм отрицательным если содержит neg_marker."""
        organism.valence = self._detect_valence(organism.parts)

    def merge(self, creatures):
        parts = []
        parent_ids = []
        for c in creatures:
            parts.extend(c.parts)
            parent_ids.append(c.id)
        existing = self._find_by_parts(tuple(parts))
        if existing:
            self._confirmed_feed(existing, 0.3)
            self.stats["fed"] += 1
            return existing
        organism = Creature(parts, parent_ids)
        organism.generation = max(c.generation for c in creatures) + 1
        base_energy = sum(c.energy for c in creatures) * 0.2
        # Проверка при создании: если конкурент сильнее — родиться слабым
        comp_e = self._find_competitor_energy(parts)
        if comp_e > 0 and base_energy < comp_e:
            organism.energy = 0.1  # слышал но не верю
        else:
            organism.energy = base_energy
        organism.valence = self._detect_valence(parts)
        self._register(organism)
        self.stats["merged"] += 1
        for c in creatures:
            c.children.append(organism.id)
        return organism

    def crossbreed(self, a, b):
        abstract_parts = []
        slot_options = {}
        slot_count = 0
        for i in range(max(a.complexity, b.complexity)):
            part_a = a.parts[i] if i < a.complexity else None
            part_b = b.parts[i] if i < b.complexity else None
            if part_a == part_b and part_a is not None:
                abstract_parts.append(part_a)
            else:
                slot_name = f"${slot_count}"
                abstract_parts.append(slot_name)
                options = set()
                if part_a:
                    options.add(part_a)
                if part_b:
                    options.add(part_b)
                slot_options[slot_name] = options
                slot_count += 1
        existing = self._find_by_parts(tuple(abstract_parts))
        if existing:
            self._confirmed_feed(existing, 0.4)
            self.stats["fed"] += 1
            if hasattr(existing, 'slot_options'):
                for slot, options in slot_options.items():
                    if slot in existing.slot_options:
                        existing.slot_options[slot].update(options)
                    else:
                        existing.slot_options[slot] = options
            return existing
        child = Creature(abstract_parts, [a.id, b.id])
        child.generation = max(a.generation, b.generation) + 1
        child.energy = (a.energy + b.energy) * 0.3
        child.slot_options = slot_options
        child.valence = -1 if (a.valence == -1 and b.valence == -1) else 1
        self._register(child)
        self.stats["crossbred"] += 1
        a.children.append(child.id)
        b.children.append(child.id)
        return child

    def _try_absorb(self, organism):
        """If organism matches an abstraction's skeleton, absorb the
        differing part into the slot."""
        for c in self.creatures.values():
            if not c.alive or not c.slot_options or c.id == organism.id:
                continue
            if c.complexity != organism.complexity:
                continue
            match = True
            new_values = {}
            for i in range(c.complexity):
                if c.parts[i].startswith("$"):
                    new_values[c.parts[i]] = organism.parts[i]
                elif c.parts[i] != organism.parts[i]:
                    match = False
                    break
            if match and new_values:
                absorbed_any = False
                for slot_name, value in new_values.items():
                    if value.startswith("$"):
                        continue
                    if slot_name in c.slot_options:
                        if value not in c.slot_options[slot_name]:
                            c.slot_options[slot_name].add(value)
                            absorbed_any = True
                if absorbed_any:
                    self._confirmed_feed(c, 0.3)
                    self.stats["absorbed"] += 1
                    return True
        return False

    def feed_sentence(self, words):
        if not words:
            return
        word_creatures = [self.observe(w) for w in words]

        # ══════════════════════════════════════════════════
        # Проверка сомнительности: для каждого слова проверяем
        # есть ли у его пар (с соседями) сильный конкурент.
        # Если да — слово сомнительно в этом контексте.
        # ══════════════════════════════════════════════════
        suspect_indices = set()
        if len(words) >= 2:
            for i in range(len(words)):
                w_i = words[i]
                # Проверяем пары: слово + сосед
                for j in [i - 1, i + 1]:
                    if j < 0 or j >= len(words):
                        continue
                    pair = (words[min(i, j)], words[max(i, j)])
                    pair_cr = self._find_by_parts(pair)
                    if not pair_cr:
                        continue
                    # Есть ли конкурент для этой пары?
                    comp_e = self._find_competitor_energy(pair)
                    if comp_e > 0 and (pair_cr.energy < comp_e * 0.5):
                        suspect_indices.add(i)

        new_organisms = []
        for i in range(len(word_creatures) - 1):
            org = self.merge([word_creatures[i], word_creatures[i + 1]])
            # Если один из участников сомнителен — ослабить
            if i in suspect_indices or (i + 1) in suspect_indices:
                if org and org.energy > 0.2:
                    org.energy = 0.2
            new_organisms.append(org)
        for i in range(len(word_creatures) - 2):
            org = self.merge([word_creatures[i], word_creatures[i + 1], word_creatures[i + 2]])
            if any(k in suspect_indices for k in [i, i + 1, i + 2]):
                if org and org.energy > 0.2:
                    org.energy = 0.2
            new_organisms.append(org)
        if len(word_creatures) >= 3:
            org = self.merge(word_creatures)
            if suspect_indices:
                if org and org.energy > 0.2:
                    org.energy = 0.2
            new_organisms.append(org)
        absorbed_ids = set()
        for org in new_organisms:
            if org and not org.slot_options:
                if self._try_absorb(org):
                    absorbed_ids.add(org.id)

        # ══════════════════════════════════════════════════
        # НОВОЕ: Visiting-шаг — подкормка связей через контекст
        # Для каждого слова находим организмы с ним через индекс,
        # если 2+ слов из предложения встречаются в одном организме —
        # подкармливаем его.
        # ══════════════════════════════════════════════════
        if len(words) >= 2:
            words_set = set(words)
            # Собираем кандидатов через children слов (быстрый путь)
            candidate_ids = set()
            for wc in word_creatures:
                for child_id in wc.children:
                    candidate_ids.add(child_id)
            # Проверяем только кандидатов, не все существа
            for cid in candidate_ids:
                if cid not in self.creatures:
                    continue
                c = self.creatures[cid]
                if not c.alive or c.complexity < 2:
                    continue
                overlap = sum(1 for p in c.parts if p in words_set)
                if overlap >= 2:
                    c.feed(0.2)
                    self.stats["fed"] += 1

        # ══════════════════════════════════════════════════
        # Мышление при чтении: для каждого слова в предложении
        # ищем транзитивные цепочки A→B→C.
        # Максимум 2 вывода за предложение.
        # ══════════════════════════════════════════════════
        if len(words) >= 2:
            link_words_set = {"это", "обозначает", "означает"}
            inferences_made = 0
            for word_a in words:
                if inferences_made >= 2:
                    break
                if len(word_a) <= 2 or word_a in link_words_set:
                    continue
                cr_a = self._find_by_parts((word_a,))
                if not cr_a or cr_a.energy < 1.5:
                    continue
                from .visitor import Visitor
                vis = Visitor(self)
                info_a = vis.visit(word_a)
                if not info_a["found"]:
                    continue
                for word_b in info_a["siblings"]:
                    if inferences_made >= 2:
                        break
                    if word_b in link_words_set or len(word_b) <= 1:
                        continue
                    if self.service_score(word_b) > 0.4:
                        continue
                    info_b = vis.visit(word_b)
                    if not info_b["found"]:
                        continue
                    for word_c in info_b["siblings"]:
                        if inferences_made >= 2:
                            break
                        if word_c == word_a or word_c == word_b:
                            continue
                        if word_c in info_a["siblings"]:
                            continue  # A уже знает C
                        if word_c in link_words_set or len(word_c) <= 1:
                            continue
                        # Проверяем: оба звена через link_word?
                        lab, lbc = None, None
                        for org in self.creatures.values():
                            if not org.alive or org.complexity < 2:
                                continue
                            ps = set(org.parts)
                            if word_a in ps and word_b in ps:
                                for p in org.parts:
                                    if p in link_words_set:
                                        lab = p; break
                            if word_b in ps and word_c in ps:
                                for p in org.parts:
                                    if p in link_words_set:
                                        lbc = p; break
                        if not lab or not lbc:
                            continue
                        links = {lab, lbc}
                        if not ("это" in links and "обозначает" in links):
                            continue
                        # Не в одном слоте (коллеги)?
                        same_slot = False
                        for org in self.creatures.values():
                            if not org.alive or not org.slot_options:
                                continue
                            if word_b not in org.parts:
                                continue
                            for sn, opts in org.slot_options.items():
                                cl = {o for o in opts if not o.startswith("$")}
                                if word_a in cl and word_c in cl:
                                    same_slot = True; break
                            if same_slot:
                                break
                        if same_slot:
                            continue
                        # Уже существует?
                        if self._find_by_parts((word_a, "это", word_c)):
                            continue
                        # Создаём вывод + цепочку-путь
                        self.feed_sentence([word_a, "это", word_c])
                        self.feed_sentence([word_a, "через", word_b, "значит", word_c])
                        inferences_made += 1

        # Валентность: применяем только если учитель уже дал neg_markers
        if self.neg_markers:
            for org in new_organisms:
                if org and org.alive:
                    self._apply_valence(org)
        all_complex = [c for c in self.creatures.values()
                       if c.alive and c.complexity >= 2 and c.times_fed >= 2]
        crossed = set()
        for i in range(len(all_complex)):
            for j in range(i + 1, len(all_complex)):
                a, b = all_complex[i], all_complex[j]
                key = (min(a.id, b.id), max(a.id, b.id))
                if key in crossed:
                    continue
                if a.alive and b.alive and a.is_similar(b):
                    if a.complexity == b.complexity:
                        self.crossbreed(a, b)
                        crossed.add(key)

    def tick(self):
        self.tick_count += 1
        dead = []
        for cid, c in self.creatures.items():
            c.tick()
            if not c.alive:
                dead.append(cid)
        for cid in dead:
            c = self.creatures[cid]
            if c.parts in self.by_parts:
                del self.by_parts[c.parts]
            del self.creatures[cid]
            self.stats["died"] += 1

        # ══════════════════════════════════════════════════
        # Мышление над цепочками.
        # Цепочки = организмы с "через" и "значит".
        # Действия: продлить, соединить, проверить.
        # ══════════════════════════════════════════════════
        if self.tick_count % 5 != 0:
            return

        from .visitor import Visitor
        visitor = Visitor(self)
        link_words = {"это", "обозначает", "означает"}

        # Собираем ВСЕ живые цепочки (содержат "через" и "значит")
        chains = []
        for c in self.creatures.values():
            if not c.alive or c.complexity < 5:
                continue
            if "через" in c.parts and "значит" in c.parts:
                chains.append(c)

        # Также: голодные слова подкармливаются
        for c in self.creatures.values():
            if not c.alive or c.complexity != 1:
                continue
            if 1.0 < c.energy < 5.0 and len(c.parts[0]) > 1:
                info = visitor.visit(c.parts[0])
                if not info["found"]:
                    continue
                for brother in info["siblings"]:
                    if len(brother) <= 1:
                        continue
                    br_cr = self._find_by_parts((brother,))
                    if br_cr and br_cr.alive and br_cr.energy > c.energy:
                        c.feed(0.03)
                        self.stats["fed"] += 1
                        # Потомков тоже
                        for child_id in c.children[:5]:
                            if child_id in self.creatures:
                                child = self.creatures[child_id]
                                if child.alive and child.complexity >= 2:
                                    comp = self._find_competitor_energy(child.parts)
                                    if not (comp > 0 and child.energy < comp * 0.5):
                                        child.feed(0.04)
                                        self.stats["fed"] += 1
                        break

        if not chains:
            return

        # Для КАЖДОЙ цепочки — одно действие
        for chain in chains:
            # Разбираем: A через B значит C
            parts = chain.parts
            try:
                idx_через = parts.index("через")
                idx_значит = parts.index("значит")
            except ValueError:
                continue

            word_a = parts[0] if idx_через > 0 else None
            word_b = parts[idx_через + 1] if idx_через + 1 < idx_значит else None
            word_c = parts[idx_значит + 1] if idx_значит + 1 < len(parts) else None

            if not word_a or not word_b or not word_c:
                continue

            # Действие 1: ПРОВЕРИТЬ — оба звена живы и сильны?
            cr_a = self._find_by_parts((word_a,))
            cr_b = self._find_by_parts((word_b,))
            cr_c = self._find_by_parts((word_c,))
            if cr_a and cr_b and cr_c and all(c.alive for c in [cr_a, cr_b, cr_c]):
                # Все звенья живы — подкормить цепочку
                chain.feed(0.05)
                self.stats["fed"] += 1
            else:
                continue  # Звено мертво — цепочка не подтверждается

            # Действие 2: ПРОДЛИТЬ — visiting по C, ищем D
            info_c = visitor.visit(word_c)
            if not info_c["found"]:
                continue
            for word_d in info_c["siblings"]:
                if word_d in {word_a, word_b, word_c}:
                    continue
                if word_d in link_words or len(word_d) <= 1:
                    continue
                if self.service_score(word_d) > 0.4:
                    continue
                # Проверяем: C→D через link_word?
                has_link = False
                for org in self.creatures.values():
                    if not org.alive or org.complexity < 2:
                        continue
                    ps = set(org.parts)
                    if word_c in ps and word_d in ps:
                        if ps & link_words:
                            has_link = True
                            break
                if not has_link:
                    continue
                # Не слишком длинная цепочка? (max 5 звеньев)
                if chain.complexity >= 7:
                    continue
                # A уже знает D?
                info_a = visitor.visit(word_a)
                if info_a["found"] and word_d in info_a["siblings"]:
                    continue
                # Уже существует вывод?
                if self._find_by_parts((word_a, "это", word_d)):
                    continue
                # Создаём новый вывод + удлинённую цепочку
                self.feed_sentence([word_a, "это", word_d])
                self.stats["born"] += 0  # feed_sentence уже считает
                break  # Одно продление за цепочку

            # Действие 3: СОЕДИНИТЬ — найти другую цепочку с общим звеном
            for other in chains:
                if other.id == chain.id:
                    continue
                if not other.alive:
                    continue
                try:
                    oi_через = other.parts.index("через")
                    oi_значит = other.parts.index("значит")
                except ValueError:
                    continue
                other_a = other.parts[0] if oi_через > 0 else None
                other_c = other.parts[oi_значит + 1] if oi_значит + 1 < len(other.parts) else None
                if not other_a or not other_c:
                    continue
                # Общее начало? A = other_A → кросс-доменная связь
                if word_a == other_a and word_c != other_c:
                    # кот → существительное И кот → млекопитающее
                    # Подкормить обе цепочки
                    chain.feed(0.03)
                    other.feed(0.03)
                    self.stats["fed"] += 2

    def run(self, ticks):
        for _ in range(ticks):
            self.tick()

    def get_slot_contents(self, creature, slot_name):
        if not creature.slot_options:
            return set()
        options = creature.slot_options.get(slot_name, set())
        return {o for o in options if not o.startswith("$")}

    def show_abstractions(self, min_energy=0.0):
        result = []
        for c in self.creatures.values():
            if c.alive and c.slot_options and c.energy >= min_energy:
                result.append(c)
        result.sort(key=lambda c: (-c.times_fed, -c.energy))
        return result

    def read(self, text):
        """Прочитать сырой текст, используя знания системы.

        Система сама решает как разбить:
        - Знает пробел → split по пробелам
        - Знает точку → отделить точку, разбить на предложения
        - Знает правило большой буквы → создать мост автоматически
        - Ничего не знает → посимвольно
        """
        from .visitor import Visitor
        visitor = Visitor(self)

        # Знает ли система пробел?
        knows_space = False
        si = visitor.visit(" ")
        if si["found"]:
            s = si["siblings"]
            if "пробел" in s or "разделяет" in s or "слова" in s:
                knows_space = True

        # Знает ли система точку?
        knows_dot = False
        di = visitor.visit(".")
        if di["found"]:
            d = di["siblings"]
            if "точка" in d or "конец" in d or "предложения" in d:
                knows_dot = True

        # Знает ли правило большой буквы?
        knows_capital = False
        for c in self.creatures.values():
            if not c.alive or c.complexity < 3:
                continue
            parts_set = set(c.parts)
            if "большой" in parts_set and ("буквы" in parts_set or "буква" in parts_set):
                if "после" in parts_set or "точки" in parts_set or "начале" in parts_set:
                    knows_capital = True
                    break

        if knows_space:
            raw_tokens = [t for t in text.split(" ") if t]

            if knows_dot:
                # Отделяем точку
                tokens = []
                for t in raw_tokens:
                    if t.endswith(".") and len(t) > 1:
                        tokens.append(t[:-1])
                        tokens.append(".")
                    elif t == ".":
                        tokens.append(".")
                    else:
                        tokens.append(t)

                # Разбиваем на предложения
                sentences = []
                current = []
                for t in tokens:
                    if t == ".":
                        if current:
                            current.append(".")
                            sentences.append(current)
                            current = []
                    else:
                        current.append(t)
                if current:
                    sentences.append(current)

                # Применяем правило большой буквы
                if knows_capital:
                    bridged = set()
                    for sent in sentences:
                        if not sent:
                            continue
                        first_word = sent[0]
                        # Первое слово с большой буквы?
                        if first_word and first_word[0].isupper() and len(first_word) > 1:
                            lower = first_word[0].lower() + first_word[1:]
                            if lower != first_word and lower not in bridged:
                                # Проверяем: мост уже существует?
                                existing = self._find_by_parts(
                                    (first_word, "и", lower, "это", "одно", "слово"))
                                if not existing:
                                    # Создаём мост автоматически
                                    self.feed_sentence(
                                        [first_word, "и", lower, "это", "одно", "слово"])
                                bridged.add(lower)

                # Подаём предложения
                for sent in sentences:
                    self.feed_sentence(sent)
                    self.run(1)
            else:
                self.feed_sentence(raw_tokens)
                self.run(1)
        else:
            self.feed_sentence(list(text))
            self.run(1)

        return {
            "knows_space": knows_space,
            "knows_dot": knows_dot,
            "knows_capital": knows_capital,
            "mode": "sentences" if (knows_space and knows_dot) else
                    "words" if knows_space else "chars"
        }

    def service_score(self, word):
        """Насколько слово «служебное» — по его ПОВЕДЕНИЮ, не по списку.

        Содержательное слово (кот): мало братьев, узкий контекст.
        Служебное слово (из, в, на): братьев у него всё, контекст — весь мир.

        Возвращает 0.0..1.0  (0 = содержательное, 1 = чистый хаб).
        """
        creature = self._find_by_parts((word,))
        if not creature:
            return 0.0

        unique_siblings = set()
        organism_count = 0
        for c in self.creatures.values():
            if not c.alive or c.complexity < 2:
                continue
            if word in c.parts:
                organism_count += 1
                for part in c.parts:
                    if part != word and not part.startswith("$"):
                        unique_siblings.add(part)

        if organism_count == 0:
            return 0.0

        total_words = sum(1 for c in self.creatures.values()
                          if c.alive and c.complexity == 1)
        if total_words == 0:
            return 0.0

        return min(1.0, len(unique_siblings) / max(1, total_words))
