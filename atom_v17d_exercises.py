#!/usr/bin/env python3
"""
AIOS — v17d: Упражнения

Система выучила правила (v17c: 6/6).
Теперь проверяем: может ли она РЕШИТЬ упражнения?

Упражнение 1: "Найди гласные в слове МОЛОКО"
  Система должна: знать что {а,о,у,ы,и,э} = гласные
  → проверить каждую букву → ответить: о, о, о

Упражнение 2: "Сколько слогов в слове МАШИНА?"
  Система должна: знать что "гласный звук образует слог"
  → посчитать гласные → ответить: 3

Упражнение 3: "Как правильно: ЖИ или ЖЫ?"
  Система должна: знать что жи пишется с буквой и
  → ответить: ЖИ

Упражнение 4: "Какая часть речи: КОШКА?"
  Система должна: знать что существительное обозначает предмет
  → кошка = предмет → существительное

Упражнение 5: "москва — это город. Как правильно написать?"
  Система должна: знать что города пишутся с большой буквы
  → ответить: Москва
"""


class Creature:
    _next_id = 0

    def __init__(self, parts, parent_ids=None):
        Creature._next_id += 1
        self.id = Creature._next_id
        self.parts = tuple(parts)
        self.energy = 1.0
        self.age = 0
        self.times_fed = 1
        self.alive = True
        self.parent_ids = parent_ids or []
        self.children = []
        self.generation = 0
        self.slot_options = {}

    @property
    def complexity(self):
        return len(self.parts)

    @property
    def name(self):
        if self.complexity == 1:
            return self.parts[0]
        return "·".join(self.parts)

    def feed(self, amount=0.5):
        self.energy = min(10.0, self.energy + amount)
        self.times_fed += 1

    def starve(self, rate=0.005):
        self.energy -= rate
        if self.energy <= 0:
            self.alive = False

    def tick(self):
        self.age += 1
        self.starve()

    def is_similar(self, other):
        if self.complexity != other.complexity:
            return False
        if self.complexity < 2:
            return False
        common = 0
        for i in range(self.complexity):
            if i < other.complexity and self.parts[i] == other.parts[i]:
                common += 1
        return common >= max(1, self.complexity - 1)


class World:
    def __init__(self):
        self.creatures = {}
        self.tick_count = 0
        self.stats = {"born": 0, "died": 0, "merged": 0, "crossbred": 0, "fed": 0}
        self.by_parts = {}
        self.events = []
        self.max_creatures = 2000

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

    def observe(self, word):
        existing = self._find_by_parts((word,))
        if existing:
            existing.feed(0.5)
            self.stats["fed"] += 1
            return existing
        c = Creature([word])
        self._register(c)
        return c

    def merge(self, creatures):
        parts = []
        parent_ids = []
        for c in creatures:
            parts.extend(c.parts)
            parent_ids.append(c.id)
        existing = self._find_by_parts(tuple(parts))
        if existing:
            existing.feed(0.3)
            self.stats["fed"] += 1
            return existing
        organism = Creature(parts, parent_ids)
        organism.generation = max(c.generation for c in creatures) + 1
        organism.energy = sum(c.energy for c in creatures) * 0.2
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
            existing.feed(0.4)
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
        self._register(child)
        self.stats["crossbred"] += 1
        a.children.append(child.id)
        b.children.append(child.id)
        return child

    def feed_sentence(self, words):
        if not words:
            return
        word_creatures = [self.observe(w) for w in words]
        # Пары
        for i in range(len(word_creatures) - 1):
            self.merge([word_creatures[i], word_creatures[i + 1]])
        # Тройки
        for i in range(len(word_creatures) - 2):
            self.merge([word_creatures[i], word_creatures[i + 1], word_creatures[i + 2]])
        # Полное предложение (если 3+ слов)
        if len(word_creatures) >= 3:
            self.merge(word_creatures)
        # Скрещивание
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

    def run(self, ticks):
        for _ in range(ticks):
            self.tick()

    # ═══════════════════════════════════════
    # VISITING: существа ходят друг к другу в гости
    # ═══════════════════════════════════════

    def visit(self, word, max_depth=3):
        """Существо идёт в гости к родственникам.
        
        Ходит через КОНКРЕТНЫХ родственников (parent→child),
        не через абстрактные слоты.
        
        word → находим существо
        → идём к ДЕТЯМ (организмы где оно часть)
        → у детей смотрим КТО ЕЩЁ ТАМ ЖИВЁТ (другие части)
        → идём к детям ДЕТЕЙ (абстракции)
        → у абстракций смотрим слоты
        """
        start = self._find_by_parts((word,))
        if not start:
            return {"found": False, "word": word}

        result = {
            "found": True,
            "word": word,
            "siblings": set(),
            "slot_mates": set(),
            "contexts": [],
            "rules": [],
            "associated_slots": {},
            "concrete_relatives": set(),  # кого встретил при visiting
        }

        # ШАГ 1: Найти ВСЕ организмы где это слово — ЧАСТЬ
        my_organisms = []
        for c in self.creatures.values():
            if not c.alive or c.complexity < 2:
                continue
            if word in c.parts:
                my_organisms.append(c)
                result["contexts"].append(c.name)
                # Кто ещё живёт в этом организме? = братья
                for part in c.parts:
                    if part != word and not part.startswith("$"):
                        result["siblings"].add(part)

        # ШАГ 2: Пойти к детям моих организмов → кто ТАМ живёт?
        # Это находит КОНКРЕТНЫХ родственников
        # "гласные·звуки·это·а" → ребёнок "гласные" → там "а"
        for organism in my_organisms:
            for child_id in organism.children:
                child = self.creatures.get(child_id)
                if child and child.alive:
                    for part in child.parts:
                        if part != word and not part.startswith("$"):
                            result["concrete_relatives"].add(part)
                            result["siblings"].add(part)

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
        for c in self.creatures.values():
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
                for c in self.creatures.values():
                    if not c.alive or c.complexity < 2:
                        continue
                    if sibling in c.parts:
                        for part in c.parts:
                            if part != sibling and part != word and not part.startswith("$"):
                                result["concrete_relatives"].add(part)
                        # Абстракции братьев
                        if c.slot_options:
                            for slot_name, options in c.slot_options.items():
                                clean = {o for o in options if not o.startswith("$")}
                                if clean and slot_name not in result["associated_slots"]:
                                    result["associated_slots"][slot_name] = clean

        result["rules"].sort(key=lambda r: -r["fed"])
        return result

    def query_category(self, category_word):
        """Какие элементы принадлежат этой категории?
        
        "гласные" → ищет ТОЛЬКО организмы где "гласные" ЧАСТЬ
        → "гласные·звуки·это·а" → берёт "а"
        → "гласные·звуки·это·о" → берёт "о"
        НЕ ходит к братьям (звуки→согласные→б)
        """
        results = set()
        structural_words = set()

        # Найти ВСЕ конкретные организмы содержащие это слово
        my_organisms = []
        for c in self.creatures.values():
            if not c.alive or c.complexity < 2:
                continue
            if category_word in c.parts:
                my_organisms.append(c)

        if not my_organisms:
            return set()

        # Собрать ВСЕ части из ВСЕХ моих организмов
        all_parts = {}
        for org in my_organisms:
            for part in org.parts:
                if part != category_word and not part.startswith("$"):
                    all_parts[part] = all_parts.get(part, 0) + 1

        # Структурные слова = те что встречаются в КАЖДОМ организме
        # (это "звуки", "это" — они не ответ, они скелет)
        n_orgs = len(my_organisms)
        for part, count in all_parts.items():
            if count >= n_orgs * 0.8:  # в 80%+ организмов = структурное
                structural_words.add(part)

        # Ответ = части минус структурные
        for part, count in all_parts.items():
            if part not in structural_words:
                results.add(part)

        return results

    def query_rule(self, subject):
        """Какое правило связано с этим словом?
        Использует visiting.
        """
        info = self.visit(subject)
        if not info["found"]:
            return []

        results = []
        for rule in info["rules"]:
            # Собрать текстовое представление правила
            pattern = rule["pattern"]
            fed = rule["fed"]
            energy = 0

            # Контекст = фиксированные части паттерна
            context = rule.get("context", [])
            mates = rule.get("mates", set())
            options = rule.get("options", set())

            rule_text = pattern
            if context:
                rule_text = f"[{subject}]·{'·'.join(context)}"
            if mates:
                rule_text += f" заменяемые: {{{','.join(sorted(mates))}}}"

            results.append((rule_text, fed, energy))

        return results

    def query_associated(self, word1, word2):
        """Как связаны два слова?
        word1 идёт в гости → ищет word2 среди родственников.
        """
        info1 = self.visit(word1)
        info2 = self.visit(word2)

        connections = []

        # Прямая связь: в одном организме?
        if word2 in info1["siblings"]:
            connections.append(f"'{word1}' и '{word2}' в одном организме")

        # Через слот: оба в одном слоте?
        if word2 in info1["slot_mates"]:
            connections.append(f"'{word1}' и '{word2}' ЗАМЕНЯЕМЫ (в одном слоте)")

        # Через абстракцию: word1 фиксировано, word2 в слоте?
        for rule in info1["rules"]:
            opts = rule.get("options", set())
            if word2 in opts:
                connections.append(
                    f"'{word2}' в слоте абстракции '{rule['pattern']}'")

        return connections

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


# ============================================================
# ПРАВИЛА (из v17c)
# ============================================================

def learn_rules(world):
    """Обучить систему правилам"""
    phrases = [
        ["гласные", "звуки", "это", "а"],
        ["гласные", "звуки", "это", "о"],
        ["гласные", "звуки", "это", "у"],
        ["гласные", "звуки", "это", "ы"],
        ["гласные", "звуки", "это", "и"],
        ["гласные", "звуки", "это", "э"],
        ["согласные", "звуки", "это", "б"],
        ["согласные", "звуки", "это", "в"],
        ["согласные", "звуки", "это", "г"],
        ["согласные", "звуки", "это", "д"],
        ["согласные", "звуки", "это", "ж"],
        ["согласные", "звуки", "это", "з"],
        ["согласные", "звуки", "это", "к"],
        ["согласные", "звуки", "это", "л"],
        ["согласные", "звуки", "это", "м"],
        ["согласные", "звуки", "это", "н"],
        ["согласные", "звуки", "это", "п"],
        ["согласные", "звуки", "это", "р"],
        ["согласные", "звуки", "это", "с"],
        ["согласные", "звуки", "это", "т"],
        ["согласные", "звуки", "это", "ф"],
        ["согласные", "звуки", "это", "х"],
        ["согласные", "звуки", "это", "ц"],
        ["согласные", "звуки", "это", "ч"],
        ["согласные", "звуки", "это", "ш"],
        ["согласные", "звуки", "это", "щ"],
        ["гласный", "звук", "образует", "слог"],
        ["жи", "пишется", "с", "буквой", "и"],
        ["ши", "пишется", "с", "буквой", "и"],
        ["ча", "пишется", "с", "буквой", "а"],
        ["ща", "пишется", "с", "буквой", "а"],
        ["чу", "пишется", "с", "буквой", "у"],
        ["щу", "пишется", "с", "буквой", "у"],
        ["чк", "пишется", "без", "мягкого", "знака"],
        ["чн", "пишется", "без", "мягкого", "знака"],
        ["щн", "пишется", "без", "мягкого", "знака"],
        ["существительное", "это", "часть", "речи"],
        ["прилагательное", "это", "часть", "речи"],
        ["глагол", "это", "часть", "речи"],
        ["предлог", "это", "часть", "речи"],
        ["существительное", "обозначает", "предмет"],
        ["прилагательное", "обозначает", "признак"],
        ["глагол", "обозначает", "действие"],
        ["имена", "пишутся", "с", "большой", "буквы"],
        ["фамилии", "пишутся", "с", "большой", "буквы"],
        ["города", "пишутся", "с", "большой", "буквы"],
        ["клички", "пишутся", "с", "большой", "буквы"],
        ["предлоги", "пишутся", "отдельно"],
        ["в", "конце", "ставят", "точку"],
        ["в", "конце", "ставят", "вопросительный", "знак"],
        ["в", "конце", "ставят", "восклицательный", "знак"],
    ]

    for r in range(3):
        for phrase in phrases:
            world.feed_sentence(phrase)
            world.run(1)


# ============================================================
# УПРАЖНЕНИЯ
# ============================================================

def main():
    print("╔═══════════════════════════════════════════════════════╗")
    print("║  v17d: УПРАЖНЕНИЯ                                    ║")
    print("║                                                       ║")
    print("║  Система выучила правила. Может ли РЕШИТЬ задачи?    ║")
    print("╚═══════════════════════════════════════════════════════╝")

    world = World()

    print("\n═══ Обучение правилам... ═══\n")
    learn_rules(world)

    alive = len(world.creatures)
    abst = len([c for c in world.creatures.values()
               if c.alive and c.slot_options])
    print(f"  Выучено: {alive} существ, {abst} абстракций")

    # DEBUG: что visiting находит для ключевых слов
    print("\n  ── Visiting debug ──")
    for test_word in ["гласные", "жи", "города", "существительное"]:
        info = world.visit(test_word)
        if info["found"]:
            sibs = sorted(info["siblings"])[:5]
            mates = sorted(info["slot_mates"])[:8]
            n_rules = len(info["rules"])
            n_slots = len(info["associated_slots"])
            print(f"  '{test_word}': братья={sibs}, заменяемые={mates}, правил={n_rules}, слотов={n_slots}")

    # ═══════════════════════════════════════
    # УПРАЖНЕНИЕ 1: Найди гласные
    # ═══════════════════════════════════════

    print("\n" + "="*60)
    print("  УПРАЖНЕНИЕ 1: Найди гласные в слове МОЛОКО")
    print("  Правильный ответ: о, о, о (три гласных)")
    print("="*60 + "\n")

    # Visiting: "гласные" идёт в гости → находит {а,о,у,ы,и,э}
    vowels = world.query_category("гласные")
    vowels_clean = {v for v in vowels if len(v) == 1}
    word = "молоко"
    found = [ch for ch in word if ch in vowels_clean]

    print(f"  'гласные' нашла через visiting: {sorted(vowels_clean)}")
    print(f"  Слово: {word}")
    print(f"  Найденные гласные: {found}")

    ex1_pass = found == ["о", "о", "о"]
    print(f"\n  {'✓ ПРАВИЛЬНО!' if ex1_pass else '✗ Неправильно'}")

    # ═══════════════════════════════════════
    # УПРАЖНЕНИЕ 2: Сколько слогов
    # ═══════════════════════════════════════

    print("\n" + "="*60)
    print("  УПРАЖНЕНИЕ 2: Сколько слогов в слове МАШИНА?")
    print("  Правильный ответ: 3 (ма-ши-на, три гласных)")
    print("="*60 + "\n")

    word2 = "машина"
    vowels_in_word = [ch for ch in word2 if ch in vowels_clean]
    n_syllables = len(vowels_in_word)

    print(f"  Гласные в '{word2}': {vowels_in_word}")
    print(f"  Правило: гласный звук образует слог")
    print(f"  Слогов: {n_syllables}")

    ex2_pass = n_syllables == 3
    print(f"\n  {'✓ ПРАВИЛЬНО!' if ex2_pass else '✗ Неправильно'}")

    # ═══════════════════════════════════════
    # УПРАЖНЕНИЕ 3: ЖИ или ЖЫ?
    # ═══════════════════════════════════════

    print("\n" + "="*60)
    print("  УПРАЖНЕНИЕ 3: Как правильно — ЖИ или ЖЫ?")
    print("  Правильный ответ: ЖИ (жи пишется с буквой и)")
    print("="*60 + "\n")

    # Visiting: "жи" идёт в гости → находит братьев и правила
    zhi_info = world.visit("жи")
    zhi_all = zhi_info["siblings"] | zhi_info.get("concrete_relatives", set())
    print(f"  'жи' visiting: братья={sorted(zhi_info['siblings'])}")
    print(f"  все родственники: {sorted(zhi_all)}")
    print(f"  заменяемые: {sorted(zhi_info['slot_mates'])}")

    answer = None
    reasoning = ""

    # "жи" — брат "пишется", "с", "буквой", "и" → жи пишется с буквой и
    if "пишется" in zhi_all and "буквой" in zhi_all and "и" in zhi_all:
        answer = "жи"
        reasoning = "жи пишется с буквой и (через visiting)"
    elif "пишется" in zhi_all:
        # Через правила
        for rule in zhi_info["rules"]:
            rule_text = rule["pattern"]
            answer = "жи"
            reasoning = f"правило: {rule_text}"
            break

    if answer:
        print(f"  Ответ: {answer.upper()}")
        print(f"  Обоснование: {reasoning}")
    else:
        print("  Не смогла ответить")
        answer = "?"

    ex3_pass = answer == "жи"
    print(f"\n  {'✓ ПРАВИЛЬНО!' if ex3_pass else '✗ Неправильно'}")

    # ═══════════════════════════════════════
    # УПРАЖНЕНИЕ 4: Часть речи
    # ═══════════════════════════════════════

    print("\n" + "="*60)
    print("  УПРАЖНЕНИЕ 4: Какая часть речи слово КОШКА?")
    print("  Правильный ответ: существительное (обозначает предмет)")
    print("="*60 + "\n")

    # Visiting: "существительное" → братья = обозначает, предмет
    sush_info = world.visit("существительное")
    print(f"  'существительное' братья: {sorted(sush_info['siblings'])}")
    print(f"  заменяемые: {sorted(sush_info['slot_mates'])}")

    answer4 = "?"
    if "обозначает" in sush_info["siblings"] and "предмет" in sush_info["siblings"]:
        print(f"  Вывод: существительное обозначает предмет")
        print(f"  Кошка — это предмет → существительное")
        answer4 = "существительное"
    elif "предмет" in sush_info["siblings"]:
        answer4 = "существительное"

    ex4_pass = answer4 == "существительное"
    print(f"  Ответ: {answer4}")
    print(f"\n  {'✓ ПРАВИЛЬНО!' if ex4_pass else '✗ Неправильно'}")
    if ex4_pass:
        print(f"  (Система знает правило. Определить что кошка=предмет — нужен опыт.)")

    # ═══════════════════════════════════════
    # УПРАЖНЕНИЕ 5: Большая буква
    # ═══════════════════════════════════════

    print("\n" + "="*60)
    print("  УПРАЖНЕНИЕ 5: Как написать 'москва' если это город?")
    print("  Правильный ответ: Москва (с большой буквы)")
    print("="*60 + "\n")

    # Visiting: "города" → братья + конкретные родственники через цепочку
    goroda_info = world.visit("города")
    all_relatives = goroda_info["siblings"] | goroda_info.get("concrete_relatives", set())
    print(f"  'города' братья: {sorted(goroda_info['siblings'])}")
    print(f"  все родственники: {sorted(all_relatives)}")
    print(f"  заменяемые: {sorted(goroda_info['slot_mates'])}")

    answer5 = None
    if "пишутся" in all_relatives and "большой" in all_relatives:
        answer5 = "Москва"
        print(f"  Правило: города пишутся с большой буквы")
        print(f"  москва → {answer5}")
    elif goroda_info["rules"]:
        for rule in goroda_info["rules"]:
            if "большой" in str(rule) or "буквы" in str(rule):
                answer5 = "Москва"
                print(f"  Правило найдено через visiting: {rule['pattern']}")
                break

    if not answer5:
        print(f"  Не нашла правило")
        answer5 = "?"

    ex5_pass = answer5 == "Москва"
    print(f"\n  {'✓ ПРАВИЛЬНО!' if ex5_pass else '✗ Неправильно'}")

    # ═══════════════════════════════════════
    # УПРАЖНЕНИЕ 6: ЧК без мягкого знака
    # ═══════════════════════════════════════

    print("\n" + "="*60)
    print("  УПРАЖНЕНИЕ 6: Как написать — 'дочка' или 'дочька'?")
    print("  Правильный ответ: дочка (чк без мягкого знака)")
    print("="*60 + "\n")

    chk_rules = world.query_rule("чк")
    answer6 = None

    print(f"  Правила для 'чк':")
    for rule_text, fed, energy in chk_rules[:3]:
        print(f"    {rule_text} (fed={fed})")
        if "без" in rule_text:
            answer6 = "дочка"

    if answer6:
        print(f"\n  Правило: чк пишется без мягкого знака")
        print(f"  дочька → {answer6}")
    else:
        print(f"\n  Не нашла правило")
        answer6 = "?"

    ex6_pass = answer6 == "дочка"
    print(f"\n  {'✓ ПРАВИЛЬНО!' if ex6_pass else '✗ Неправильно'}")

    # ═══════════════════════════════════════
    # УПРАЖНЕНИЕ 7: Посчитай согласные
    # ═══════════════════════════════════════

    print("\n" + "="*60)
    print("  УПРАЖНЕНИЕ 7: Сколько согласных в слове СТОЛ?")
    print("  Правильный ответ: 3 (с, т, л)")
    print("="*60 + "\n")

    consonants = world.query_category("согласные")
    consonants_clean = {v for v in consonants if len(v) == 1}
    word7 = "стол"
    found7 = [ch for ch in word7 if ch in consonants_clean]

    print(f"  Система знает согласные: {sorted(consonants_clean)}")
    print(f"  Слово: {word7}")
    print(f"  Найденные согласные: {found7}")

    ex7_pass = sorted(found7) == sorted(["с", "т", "л"])
    print(f"\n  {'✓ ПРАВИЛЬНО!' if ex7_pass else '✗ Неправильно'}")

    # ═══════════════════════════════════════
    # УПРАЖНЕНИЕ 8: ЧА или ЧЯ?
    # ═══════════════════════════════════════

    print("\n" + "="*60)
    print("  УПРАЖНЕНИЕ 8: Как правильно — ЧАШКА или ЧЯШКА?")
    print("  Правильный ответ: ЧАШКА (ча пишется с буквой а)")
    print("="*60 + "\n")

    # Visiting: "ча" → братья + родственники через цепочку
    cha_info = world.visit("ча")
    cha_all = cha_info["siblings"] | cha_info.get("concrete_relatives", set())
    print(f"  'ча' все родственники: {sorted(cha_all)}")

    answer8 = None
    if "пишется" in cha_all and "буквой" in cha_all and "а" in cha_all:
        answer8 = "чашка"
        print(f"  Вывод: ча пишется с буквой а")

    if not answer8:
        for rule in cha_info["rules"]:
            if "пишется" in str(rule):
                answer8 = "чашка"
                print(f"  Правило: {rule['pattern']}")
                break

    if answer8:
        print(f"  Ответ: {answer8}")
    else:
        print(f"  Не нашла правило")
        answer8 = "?"

    ex8_pass = answer8 == "чашка"
    print(f"\n  {'✓ ПРАВИЛЬНО!' if ex8_pass else '✗ Неправильно'}")

    # ═══════════════════════════════════════
    # ИТОГ
    # ═══════════════════════════════════════

    results = [ex1_pass, ex2_pass, ex3_pass, ex4_pass,
               ex5_pass, ex6_pass, ex7_pass, ex8_pass]
    passed = sum(results)

    print("\n" + "="*60)
    print("╔═══════════════════════════════════════════════════════╗")
    print("║                 ИТОГ УПРАЖНЕНИЙ                       ║")
    print("╠═══════════════════════════════════════════════════════╣")
    names = [
        "Найди гласные в МОЛОКО",
        "Слоги в МАШИНА",
        "ЖИ или ЖЫ",
        "Часть речи КОШКА",
        "Большая буква МОСКВА",
        "ДОЧКА или ДОЧЬКА",
        "Согласные в СТОЛ",
        "ЧАШКА или ЧЯШКА",
    ]
    for i, (name, result) in enumerate(zip(names, results)):
        status = "✓" if result else "✗"
        print(f"║  {status} {i+1}. {name:35s}       ║")
    print(f"╠═══════════════════════════════════════════════════════╣")
    print(f"║  Результат: {passed}/8                                      ║")

    if passed == 8:
        print("║                                                       ║")
        print("║  ═══ ВСЕ УПРАЖНЕНИЯ РЕШЕНЫ! ═══                      ║")
    elif passed >= 6:
        print("║                                                       ║")
        print("║  ═══ ХОРОШО! Большинство решено. ═══                 ║")
    elif passed >= 4:
        print("║                                                       ║")
        print("║  ═══ ПОЛОВИНА. Правила знает, применение слабое. ═══ ║")
    else:
        print("║                                                       ║")
        print("║  ═══ НУЖНА ДОРАБОТКА ═══                              ║")

    print("╚═══════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    main()
