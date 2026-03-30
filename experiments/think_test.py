#!/usr/bin/env python3
"""
Метод think() — система думает и делает выводы.

think() ищет транзитивные цепочки: если A знает B, и B знает C,
и A не знает C — это потенциальный вывод.

Главный тест: может ли система вывести "кот — существительное"
из "кот — предмет" и "существительное обозначает предмет"?

Движок НЕ менялся (think добавляется как метод).
"""

from chrysaline import World, Visitor, Generator


# ════════════════════════════════════════════════════════
# read() — патчим World
# ════════════════════════════════════════════════════════

def read(self, text):
    visitor = Visitor(self)
    knows_space = False
    space_info = visitor.visit(" ")
    if space_info["found"]:
        s = space_info["siblings"]
        if "пробел" in s or "разделяет" in s or "слова" in s:
            knows_space = True
    knows_dot = False
    dot_info = visitor.visit(".")
    if dot_info["found"]:
        d = dot_info["siblings"]
        if "точка" in d or "конец" in d or "предложения" in d:
            knows_dot = True
    if knows_space:
        raw_tokens = [t for t in text.split(" ") if t]
        if knows_dot:
            tokens = []
            for t in raw_tokens:
                if t.endswith(".") and len(t) > 1:
                    tokens.append(t[:-1])
                    tokens.append(".")
                elif t == ".":
                    tokens.append(".")
                else:
                    tokens.append(t)
            sentences, current = [], []
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
            for sent in sentences:
                self.feed_sentence(sent)
                self.run(1)
        else:
            self.feed_sentence(raw_tokens)
            self.run(1)
    else:
        self.feed_sentence(list(text))
        self.run(1)
    return {"knows_space": knows_space, "knows_dot": knows_dot,
            "mode": "sentences" if (knows_space and knows_dot) else
                    "words" if knows_space else "chars"}

World.read = read


# ════════════════════════════════════════════════════════
# think() — система думает
# ════════════════════════════════════════════════════════

def think(self, max_inferences=10, min_energy=3.0, verbose=True):
    """Система проходит по знаниям и ищет транзитивные цепочки.

    Алгоритм:
    1. Берём сильные слова (energy > min_energy, complexity == 1)
    2. Для каждого — visiting → братья
    3. Для каждого брата — visiting → братья братьев
    4. Ищем транзитивные цепочки: A→B→C где A не знает C
    5. Рождаем вывод через feed_sentence

    Возвращает список сделанных выводов.
    """
    visitor = Visitor(self)
    inferences = []

    # Шаг 1: Сильные слова
    strong_words = []
    for c in self.creatures.values():
        if c.alive and c.complexity == 1 and c.energy >= min_energy:
            strong_words.append(c.parts[0])

    if verbose:
        print(f"    think(): {len(strong_words)} сильных слов (energy >= {min_energy})")

    # Связующие слова — через них строятся цепочки
    link_words = {"это", "обозначает", "означает", "называют",
                  "является", "относятся"}

    # Шумные слова — не должны быть субъектом/объектом вывода
    noise_words = link_words | {".", " ", "в", "и", "с", "на", "не",
                                 "по", "из", "к", "за", "от", "до",
                                 "здесь", "конце", "конец", "ставится",
                                 "разделяет", "складываются", "означает",
                                 "пробел", "предложения", "слова",
                                 "точка", "мысль", "новое", "после"}

    # Шаг 2-4: Для каждого сильного слова ищем цепочки
    existing_pairs = set()
    for c in self.creatures.values():
        if c.alive and c.complexity >= 2:
            for i in range(len(c.parts)):
                for j in range(i + 1, len(c.parts)):
                    p1, p2 = c.parts[i], c.parts[j]
                    if not p1.startswith("$") and not p2.startswith("$"):
                        existing_pairs.add((p1, p2))
                        existing_pairs.add((p2, p1))

    for word_a in strong_words:
        if len(inferences) >= max_inferences:
            break

        # A не должно быть шумным
        if word_a in noise_words or word_a.startswith("$"):
            continue

        info_a = visitor.visit(word_a)
        if not info_a["found"]:
            continue

        siblings_a = info_a["siblings"]
        # B — содержательный посредник
        meaningful_siblings = {s for s in siblings_a
                               if len(s) > 1 and not s.startswith("$")
                               and s not in link_words
                               and s not in noise_words
                               and s != word_a}

        for word_b in meaningful_siblings:
            if len(inferences) >= max_inferences:
                break

            info_b = visitor.visit(word_b)
            if not info_b["found"]:
                continue

            siblings_b = info_b["siblings"]

            for word_c in siblings_b:
                if len(inferences) >= max_inferences:
                    break
                if word_c == word_a or word_c == word_b:
                    continue
                if word_c in noise_words or len(word_c) <= 1:
                    continue
                if word_c.startswith("$"):
                    continue

                # A не знает C напрямую?
                if word_c in siblings_a:
                    continue

                # Уже существует?
                if (word_a, word_c) in existing_pairs:
                    continue

                # Ищем связующее слово: ОБА звена должны иметь
                # link_word, и ОДНО ИЗ НИХ должно быть через "обозначает"
                # (это гарантирует что B — смысловой посредник, не случайность)
                link_ab = None
                link_bc = None
                for c in self.creatures.values():
                    if not c.alive or c.complexity < 2:
                        continue
                    parts = set(c.parts)
                    if word_a in parts and word_b in parts:
                        for p in c.parts:
                            if p in link_words:
                                link_ab = p
                                break
                    if word_b in parts and word_c in parts:
                        for p in c.parts:
                            if p in link_words:
                                link_bc = p
                                break

                # Оба звена должны иметь связующее слово
                if not link_ab or not link_bc:
                    continue

                # Паттерн: "A это B" + "C обозначает B" → "A это C"
                # Или: "A это B" + "B обозначает C" → "A это C"
                # Ключевое: одно звено "это", другое "обозначает"
                links = {link_ab, link_bc}
                if not (("это" in links and "обозначает" in links) or
                        ("это" in links and "называют" in links)):
                    continue

                link = "это"

                inference = [word_a, link, word_c]
                inferences.append({
                    "chain": f"{word_a} → {word_b} → {word_c}",
                    "link": link,
                    "via": word_b,
                    "sentence": inference,
                })

                self.feed_sentence(inference)
                existing_pairs.add((word_a, word_c))
                existing_pairs.add((word_c, word_a))

                if verbose:
                    print(f"    ВЫВОД: {word_a} {link} {word_c}  "
                          f"(через '{word_b}')")

    if verbose:
        print(f"    think(): {len(inferences)} выводов сделано")

    return inferences


World.think = think


# ════════════════════════════════════════════════════════
# ОБУЧЕНИЕ (уровни 1-2)
# ════════════════════════════════════════════════════════

LEVEL1 = [
    ["а", "это", "гласная", "буква"], ["о", "это", "гласная", "буква"],
    ["у", "это", "гласная", "буква"], ["и", "это", "гласная", "буква"],
    ["е", "это", "гласная", "буква"], ["ы", "это", "гласная", "буква"],
    ["к", "это", "согласная", "буква"], ["т", "это", "согласная", "буква"],
    ["м", "это", "согласная", "буква"], ["н", "это", "согласная", "буква"],
    ["р", "это", "согласная", "буква"], ["с", "это", "согласная", "буква"],
    ["л", "это", "согласная", "буква"], ["д", "это", "согласная", "буква"],
    ["б", "это", "согласная", "буква"], ["п", "это", "согласная", "буква"],
]

LEVEL2 = [
    ["слова", "складываются", "в", "предложения"],
    ["предложение", "выражает", "мысль"],
    ["в", "конце", "предложения", "ставится", "точка"],
    ["точка", "разделяет", "предложения"],
    ["пробел", "разделяет", "слова"],
]

BRIDGES = [
    [".", "это", "точка"], [".", "означает", "конец", "предложения"],
    [" ", "это", "пробел"], [" ", "разделяет", "слова"],
]

# ════════════════════════════════════════════════════════
# ТЕСТОВЫЕ ТЕКСТЫ
# ════════════════════════════════════════════════════════

TEXT_FACTS = "Кот это предмет. Собака это предмет. Корова это предмет. Существительное обозначает предмет. Глагол обозначает действие. Бегать это действие. Прыгать это действие. Красный это признак. Большой это признак. Прилагательное обозначает признак."


def teach(world, data, label, repeats=3):
    print(f"\n  ── {label} ({len(data)} фраз, {repeats}x) ──")
    for r in range(repeats):
        for phrase in data:
            world.feed_sentence(phrase)
            world.run(1)
    alive = sum(1 for c in world.creatures.values() if c.alive)
    abst = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"    → {alive} существ, {abst} абстракций")


def main():
    print("=" * 60)
    print("  МЕТОД think() — СИСТЕМА ДУМАЕТ")
    print("  Транзитивные цепочки: A→B→C")
    print("=" * 60)

    world = World()
    visitor = Visitor(world)
    gen = Generator(world)

    # ════════════════════════════════════════
    # ОБУЧЕНИЕ
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ОБУЧЕНИЕ")
    print("=" * 60)

    teach(world, LEVEL1, "Буквы")
    teach(world, LEVEL2, "Пунктуация")
    teach(world, BRIDGES, "Мосты", repeats=5)

    # ════════════════════════════════════════
    # ТЕСТ 1: Базовый — части речи
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ТЕСТ 1: БАЗОВЫЙ — ЧАСТИ РЕЧИ")
    print("=" * 60)

    print(f"\n  Текст: \"{TEXT_FACTS[:60]}...\"")
    for _ in range(3):
        world.read(TEXT_FACTS)

    alive1 = sum(1 for c in world.creatures.values() if c.alive)
    abst1 = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"  После текста: {alive1} существ, {abst1} абстракций")

    # Что знает система ДО think()?
    print(f"\n  ── ДО think() ──")
    for word in ["кот", "Кот", "собака", "предмет", "существительное", "бегать", "глагол"]:
        info = visitor.visit(word)
        if info["found"]:
            sibs = sorted(info["siblings"])[:10]
            print(f"    '{word}' братья: {sibs}")

    # ask ДО think
    print(f"\n  ask() ДО think():")
    r_before1 = gen.ask("какая часть речи кот?")
    print(f"    'какая часть речи кот?' → {r_before1['answers'][:8]}")
    r_before2 = gen.ask("кот это существительное?")
    print(f"    'кот это существительное?' → {r_before2['answers'][:8]}")

    # ════════════════════════════════════════
    # think()
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  think() — СИСТЕМА ДУМАЕТ")
    print("=" * 60)

    inferences = world.think(max_inferences=20, min_energy=2.0, verbose=True)

    # ════════════════════════════════════════
    # ПОСЛЕ think() — что изменилось?
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ПОСЛЕ think()")
    print("=" * 60)

    checks = []

    # Проверка 1: кот это существительное?
    print(f"\n  ── Проверка: кот → существительное? ──")
    kot_info = visitor.visit("кот")
    if kot_info["found"]:
        kot_sibs = kot_info["siblings"]
        knows_sush = "существительное" in kot_sibs or "Существительное" in kot_sibs
        print(f"    visit('кот') братья: {sorted(kot_sibs)[:12]}")
        print(f"    знает 'существительное': {knows_sush}")
    else:
        knows_sush = False
    checks.append(("кот знает существительное (visit)", knows_sush))

    # Проверка 2: собака это существительное?
    print(f"\n  ── Проверка: собака → существительное? ──")
    sob_info = visitor.visit("собака")
    if sob_info["found"]:
        sob_sibs = sob_info["siblings"]
        sob_sush = "существительное" in sob_sibs or "Существительное" in sob_sibs
        print(f"    visit('собака') братья: {sorted(sob_sibs)[:12]}")
        print(f"    знает 'существительное': {sob_sush}")
    else:
        sob_sush = False
    checks.append(("собака знает существительное (visit)", sob_sush))

    # Проверка 3: бегать это глагол?
    print(f"\n  ── Проверка: бегать → глагол? ──")
    beg_info = visitor.visit("бегать")
    if beg_info["found"]:
        beg_sibs = beg_info["siblings"]
        beg_glag = "глагол" in beg_sibs or "Глагол" in beg_sibs
        print(f"    visit('бегать') братья: {sorted(beg_sibs)[:12]}")
        print(f"    знает 'глагол': {beg_glag}")
    else:
        beg_glag = False
    checks.append(("бегать знает глагол (visit)", beg_glag))

    # Проверка 4: красный это прилагательное?
    print(f"\n  ── Проверка: красный → прилагательное? ──")
    kr_info = visitor.visit("красный")
    if kr_info["found"]:
        kr_sibs = kr_info["siblings"]
        kr_pril = "прилагательное" in kr_sibs or "Прилагательное" in kr_sibs
        print(f"    visit('красный') братья: {sorted(kr_sibs)[:12]}")
        print(f"    знает 'прилагательное': {kr_pril}")
    else:
        kr_pril = False
    checks.append(("красный знает прилагательное (visit)", kr_pril))

    # Проверка 5: ask("какая часть речи кот?")
    print(f"\n  ── ask() ПОСЛЕ think() ──")
    r_after1 = gen.ask("какая часть речи кот?")
    ok5 = "существительное" in r_after1["answers"] or "Существительное" in r_after1["answers"]
    print(f"    'какая часть речи кот?' → {r_after1['answers'][:8]}  {'OK' if ok5 else 'MISS'}")
    checks.append(("ask('часть речи кот?') → существительное", ok5))

    # Проверка 6: ask("кот это существительное?")
    r_after2 = gen.ask("кот это существительное?")
    print(f"    'кот это существительное?' → {r_after2['answers'][:8]}")

    # Проверка 7: ask("какая часть речи бегать?")
    r_after3 = gen.ask("какая часть речи бегать?")
    ok7 = "глагол" in r_after3["answers"] or "Глагол" in r_after3["answers"]
    print(f"    'какая часть речи бегать?' → {r_after3['answers'][:8]}  {'OK' if ok7 else 'MISS'}")
    checks.append(("ask('часть речи бегать?') → глагол", ok7))

    # Проверка 8: ask("какая часть речи красный?")
    r_after4 = gen.ask("какая часть речи красный?")
    ok8 = "прилагательное" in r_after4["answers"] or "Прилагательное" in r_after4["answers"]
    print(f"    'какая часть речи красный?' → {r_after4['answers'][:8]}  {'OK' if ok8 else 'MISS'}")
    checks.append(("ask('часть речи красный?') → прилагательное", ok8))

    # ════════════════════════════════════════
    # ТЕСТ 2: Повторный think() — стабильность
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ТЕСТ 2: ПОВТОРНЫЙ think()")
    print("=" * 60)

    inferences2 = world.think(max_inferences=20, min_energy=2.0, verbose=True)
    print(f"  Новых выводов: {len(inferences2)} (должно быть мало — дубли отсекаются)")
    ok_stable = len(inferences2) <= len(inferences)
    checks.append(("Повторный think() стабилен", ok_stable))

    # ════════════════════════════════════════
    # ТЕСТ 3: think() после учебника
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ТЕСТ 3: think() ПОСЛЕ УЧЕБНИКА")
    print("=" * 60)

    textbook = "Существительное это часть речи. Глагол это часть речи. Прилагательное это часть речи. Предлог это часть речи. Существительное обозначает предмет. Глагол обозначает действие. Прилагательное обозначает признак. Кот это предмет. Бегать это действие. Красный это признак. Мама это предмет. Читать это действие. Синий это признак."
    print(f"  Текст: \"{textbook[:60]}...\"")

    for _ in range(3):
        world.read(textbook)

    print(f"\n  think() после учебника:")
    inferences3 = world.think(max_inferences=30, min_energy=2.0, verbose=True)

    # Проверяем: мама это существительное?
    print(f"\n  Проверка после учебника + think():")
    mama_info = visitor.visit("мама")
    if mama_info["found"]:
        mama_sibs = mama_info["siblings"]
        mama_sush = "существительное" in mama_sibs or "Существительное" in mama_sibs
        print(f"    'мама' знает 'существительное': {mama_sush}")
    else:
        mama_sush = False
    checks.append(("мама знает существительное (через think)", mama_sush))

    # читать это глагол?
    chitat_info = visitor.visit("читать")
    if chitat_info["found"]:
        chitat_sibs = chitat_info["siblings"]
        chitat_glag = "глагол" in chitat_sibs or "Глагол" in chitat_sibs
        print(f"    'читать' знает 'глагол': {chitat_glag}")
    else:
        chitat_glag = False
    checks.append(("читать знает глагол (через think)", chitat_glag))

    # ════════════════════════════════════════
    # ИТОГ
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("╔═══════════════════════════════════════════════════════╗")
    print("║     ИТОГ: МЕТОД think()                               ║")
    print("╠═══════════════════════════════════════════════════════╣")

    passed = 0
    for name, ok in checks:
        s = "+" if ok else "-"
        if ok:
            passed += 1
        print(f"║  {s} {name:52s}║")

    print(f"╠═══════════════════════════════════════════════════════╣")
    print(f"║  Результат: {passed}/{len(checks)}                                   ║")

    alive = sum(1 for c in world.creatures.values() if c.alive)
    abst = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"║  Существ: {alive}, абстракций: {abst}                   ║")
    print(f"║  Выводов (тест 1): {len(inferences)}                              ║")

    if passed >= 8:
        print(f"║                                                       ║")
        print(f"║  think() РАБОТАЕТ.                                   ║")
        print(f"║  Система выводит новое знание из существующего.      ║")
    elif passed >= 5:
        print(f"║                                                       ║")
        print(f"║  ЧАСТИЧНО. Выводы делаются, но не все.               ║")
    else:
        print(f"║                                                       ║")
        print(f"║  НУЖНА ДОРАБОТКА.                                    ║")

    print(f"╚═══════════════════════════════════════════════════════╝")

    print(f"\n  Статистика: {world.stats}")


if __name__ == "__main__":
    main()
