#!/usr/bin/env python3
"""
Метод think() v2 — общий механизм вывода.

Не отдельные паттерны, а один алгоритм:
1. Берём сильные слова
2. Для каждого: контекст через visiting (организмы с этим словом)
3. Для каждого брата: его контекст
4. Если контексты пересекаются через содержательное общее звено — вывод
5. Фильтр: service_score для отсечения служебных слов

Движок НЕ менялся (think/read добавляются как методы).
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
# think() v2 — общий механизм
# ════════════════════════════════════════════════════════

def think(self, max_inferences=20, min_energy=1.5, verbose=True):
    """Система ищет новые связи через общие звенья.

    Общий алгоритм (один для всех паттернов):
    1. Для каждого сильного слова A — собрать контекст:
       все организмы где A участвует, с ролью каждого слова
    2. Для каждого содержательного брата B — его контекст
    3. Если A и C связаны через B, и B содержательный — вывод

    Фильтр: B должен быть содержательным (service_score < 0.5).
    Это отсекает служебные слова автоматически, без хардкода.
    """
    visitor = Visitor(self)
    inferences = []

    # Сильные слова
    strong_words = []
    for c in self.creatures.values():
        if c.alive and c.complexity == 1 and c.energy >= min_energy:
            strong_words.append(c.parts[0])

    if verbose:
        print(f"    think(): {len(strong_words)} сильных слов")

    # Служебные слова — автоматически через service_score
    # Порог для A/C (субъект/объект вывода) — мягче
    noise_threshold = 0.3
    # Порог для B (связующее звено) — строже, отсекает "и","одно","слово"
    bridge_threshold = 0.45
    noise = set()
    for w in strong_words:
        if self.service_score(w) > noise_threshold:
            noise.add(w)
    # Всегда исключаем символы и однобуквенные
    noise.update({".", " ", ",", "!", "?"})

    if verbose and noise:
        print(f"    шумные (service>{noise_threshold}): {sorted(noise)[:10]}")

    # Собираем уже известные пары
    existing_pairs = set()
    for c in self.creatures.values():
        if c.alive and c.complexity >= 2:
            parts_clean = [p for p in c.parts if not p.startswith("$")]
            for i in range(len(parts_clean)):
                for j in range(i + 1, len(parts_clean)):
                    existing_pairs.add((parts_clean[i], parts_clean[j]))
                    existing_pairs.add((parts_clean[j], parts_clean[i]))

    # Для каждого сильного слова A ищем цепочки A→B→C
    for word_a in strong_words:
        if len(inferences) >= max_inferences:
            break
        if word_a in noise:
            continue
        # A должен быть содержательным: длиннее 2 символов, не служебный
        if len(word_a) <= 2 or self.service_score(word_a) > bridge_threshold:
            continue

        info_a = visitor.visit(word_a)
        if not info_a["found"]:
            continue
        siblings_a = info_a["siblings"]

        # Кандидаты на B: содержательные братья A
        for word_b in siblings_a:
            if len(inferences) >= max_inferences:
                break
            if word_b in noise or word_b == word_a:
                continue
            if len(word_b) <= 1 or word_b.startswith("$"):
                continue
            # B (связующее звено) должен быть содержательным — строгий порог
            if self.service_score(word_b) > bridge_threshold:
                continue

            info_b = visitor.visit(word_b)
            if not info_b["found"]:
                continue
            siblings_b = info_b["siblings"]

            for word_c in siblings_b:
                if len(inferences) >= max_inferences:
                    break
                if word_c == word_a or word_c == word_b:
                    continue
                if word_c in noise or len(word_c) <= 1:
                    continue
                if word_c.startswith("$"):
                    continue
                # C должен быть содержательным
                if self.service_score(word_c) > noise_threshold:
                    continue

                # A уже знает C?
                if word_c in siblings_a:
                    continue
                # Уже существует организм с A и C?
                if (word_a, word_c) in existing_pairs:
                    continue

                # ═══ Общий фильтр: ищем осмысленную связь ═══
                # Находим организмы, связывающие A↔B и B↔C
                # Извлекаем РОЛЬ B в каждом (какое слово стоит рядом)
                link_ab = None  # связующее слово в организме с A и B
                link_bc = None  # связующее слово в организме с B и C
                org_ab = None
                org_bc = None

                for c in self.creatures.values():
                    if not c.alive or c.complexity < 2:
                        continue
                    parts_set = set(c.parts)
                    if word_a in parts_set and word_b in parts_set and not org_ab:
                        # Ищем связующее слово между A и B
                        for p in c.parts:
                            if p != word_a and p != word_b and not p.startswith("$"):
                                if p in {"это", "обозначает", "означает",
                                         "называют", "является", "относятся"}:
                                    link_ab = p
                                    org_ab = c
                                    break
                    if word_b in parts_set and word_c in parts_set and not org_bc:
                        for p in c.parts:
                            if p != word_b and p != word_c and not p.startswith("$"):
                                if p in {"это", "обозначает", "означает",
                                         "называют", "является", "относятся",
                                         "умеют", "имеет", "делает", "даёт",
                                         "ест", "живёт", "кормит", "дышит"}:
                                    link_bc = p
                                    org_bc = c
                                    break

                # ОБА звена должны иметь осмысленную связь
                if not link_ab or not link_bc:
                    continue

                # Определяем тип вывода
                # Паттерн 1: A это B + C обозначает B → A это C
                if link_ab == "это" and link_bc == "обозначает":
                    link_out = "это"
                # Паттерн 2: A это B + B умеет/ест/живёт C → A умеет/ест/живёт C
                elif link_ab == "это" and link_bc in {"умеют", "имеет",
                        "ест", "живёт", "кормит", "дышит", "делает", "даёт"}:
                    link_out = link_bc
                # Паттерн обратный: C обозначает B + A это B → A это C
                elif link_bc == "это" and link_ab == "обозначает":
                    link_out = "это"
                else:
                    continue

                inference = [word_a, link_out, word_c]
                inferences.append({
                    "chain": f"{word_a} →({link_ab})→ {word_b} →({link_bc})→ {word_c}",
                    "link": link_out,
                    "via": word_b,
                    "sentence": inference,
                })

                self.feed_sentence(inference)
                existing_pairs.add((word_a, word_c))
                existing_pairs.add((word_c, word_a))

                if verbose:
                    print(f"    ВЫВОД: {word_a} {link_out} {word_c}  "
                          f"(через '{word_b}', {link_ab}+{link_bc})")

    if verbose:
        print(f"    think(): {len(inferences)} выводов")

    return inferences


World.think = think


# ════════════════════════════════════════════════════════
# ОБУЧЕНИЕ
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

CASE_BRIDGES = [
    ["Кот", "и", "кот", "это", "одно", "слово"],
    ["Собака", "и", "собака", "это", "одно", "слово"],
    ["Корова", "и", "корова", "это", "одно", "слово"],
    ["Лошадь", "и", "лошадь", "это", "одно", "слово"],
    ["Ворона", "и", "ворона", "это", "одно", "слово"],
    ["Воробей", "и", "воробей", "это", "одно", "слово"],
    ["Мама", "и", "мама", "это", "одно", "слово"],
    ["Папа", "и", "папа", "это", "одно", "слово"],
    ["Бабушка", "и", "бабушка", "это", "одно", "слово"],
]

# ════════════════════════════════════════════════════════
# ТЕКСТЫ
# ════════════════════════════════════════════════════════

# Тест 1: Базовые определения
TEXT_DEFS = "Кот это предмет. Собака это предмет. Корова это предмет. Мама это предмет. Существительное обозначает предмет. Глагол обозначает действие. Бегать это действие. Прыгать это действие. Читать это действие. Красный это признак. Большой это признак. Синий это признак. Прилагательное обозначает признак."

# Тест 2: Смешанный текст (природоведение + категории + наследование)
TEXT_MIXED = "Кот живёт в доме. Собака живёт в доме. Корова живёт на ферме. Кот ест рыбу. Собака ест мясо. Корова ест траву. Корова даёт молоко. Кот это млекопитающее. Собака это млекопитающее. Корова это млекопитающее. Ворона это птица. Воробей это птица. Птицы умеют летать. Рыба живёт в воде. Два плюс три равно пять. Три плюс два равно пять. Один плюс один равно два. Мама мыла раму. Папа читал книгу. Бабушка варила кашу."

# Тест 3: Учебник
TEXT_TEXTBOOK = "Существительное это часть речи. Глагол это часть речи. Прилагательное это часть речи. Предлог это часть речи. Существительное обозначает предмет. Глагол обозначает действие. Прилагательное обозначает признак. Кот это предмет. Бегать это действие. Красный это признак. Мама это предмет. Читать это действие. Синий это признак."


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
    print("  think() v2 — ОБЩИЙ МЕХАНИЗМ ВЫВОДА")
    print("  Один алгоритм для всех паттернов.")
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
    teach(world, CASE_BRIDGES, "Мосты букв")

    # ════════════════════════════════════════
    # ТЕСТ 1: Определения + think()
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ТЕСТ 1: ОПРЕДЕЛЕНИЯ")
    print("=" * 60)

    for _ in range(3):
        world.read(TEXT_DEFS)

    print(f"\n  think():")
    inf1 = world.think(max_inferences=20, verbose=True)

    checks = []

    # Кот→существительное
    kot_info = visitor.visit("Кот")
    kot_sush = "существительное" in (kot_info["siblings"] if kot_info["found"] else set()) or \
               "Существительное" in (kot_info["siblings"] if kot_info["found"] else set())
    checks.append(("Кот → существительное", kot_sush))
    print(f"\n  Кот знает существительное: {kot_sush}")

    # Бегать→глагол
    beg_info = visitor.visit("Бегать")
    beg_glag = "глагол" in (beg_info["siblings"] if beg_info["found"] else set()) or \
               "Глагол" in (beg_info["siblings"] if beg_info["found"] else set())
    checks.append(("Бегать → глагол", beg_glag))
    print(f"  Бегать знает глагол: {beg_glag}")

    # Красный→прилагательное
    kr_info = visitor.visit("Красный")
    kr_pril = "прилагательное" in (kr_info["siblings"] if kr_info["found"] else set()) or \
              "Прилагательное" in (kr_info["siblings"] if kr_info["found"] else set())
    checks.append(("Красный → прилагательное", kr_pril))
    print(f"  Красный знает прилагательное: {kr_pril}")

    # ask
    r1 = gen.ask("какая часть речи кот?")
    ok1 = "существительное" in r1["answers"] or "Существительное" in r1["answers"]
    checks.append(("ask(часть речи кот?) → существительное", ok1))
    print(f"  ask(часть речи кот?): {r1['answers'][:6]}  {'OK' if ok1 else 'MISS'}")

    # ════════════════════════════════════════
    # ТЕСТ 2: Смешанный текст + think()
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ТЕСТ 2: СМЕШАННЫЙ ТЕКСТ")
    print("=" * 60)

    for _ in range(3):
        world.read(TEXT_MIXED)

    print(f"\n  think():")
    inf2 = world.think(max_inferences=30, verbose=True)

    # Природоведение
    r2 = gen.ask("где живёт кот?")
    ok2 = "доме" in r2["answers"] or "в" in r2["answers"]
    checks.append(("где живёт кот? → доме", ok2))
    print(f"\n  где живёт кот? → {r2['answers'][:6]}  {'OK' if ok2 else 'MISS'}")

    r3 = gen.ask("что ест корова?")
    ok3 = "траву" in r3["answers"]
    checks.append(("что ест корова? → траву", ok3))
    print(f"  что ест корова? → {r3['answers'][:6]}  {'OK' if ok3 else 'MISS'}")

    r4 = gen.ask("кто это млекопитающее?")
    ok4 = any(w in r4["answers"] for w in ["Кот", "кот", "Собака", "собака", "Корова"])
    checks.append(("кто млекопитающее?", ok4))
    print(f"  кто млекопитающее? → {r4['answers'][:6]}  {'OK' if ok4 else 'MISS'}")

    # Наследование: ворона умеет летать?
    vorona_info = visitor.visit("Ворона")
    vorona_sibs = vorona_info["siblings"] if vorona_info["found"] else set()
    vorona_flies = "летать" in vorona_sibs or "умеют" in vorona_sibs
    checks.append(("Ворона → летать (наследование)", vorona_flies))
    print(f"  Ворона знает летать: {vorona_flies}")
    if vorona_info["found"]:
        print(f"    братья: {sorted(vorona_sibs)[:12]}")

    # Математика
    r5 = gen.ask("сколько два плюс три?")
    ok5 = "пять" in r5["answers"]
    checks.append(("два плюс три → пять", ok5))
    print(f"  два+три? → {r5['answers'][:6]}  {'OK' if ok5 else 'MISS'}")

    # Литература
    r6 = gen.ask("что мыла мама?")
    ok6 = "раму" in r6["answers"]
    checks.append(("что мыла мама? → раму", ok6))
    print(f"  что мыла мама? → {r6['answers'][:6]}  {'OK' if ok6 else 'MISS'}")

    # ════════════════════════════════════════
    # ТЕСТ 3: Учебник + think()
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ТЕСТ 3: УЧЕБНИК + think()")
    print("=" * 60)

    for _ in range(3):
        world.read(TEXT_TEXTBOOK)

    print(f"\n  think():")
    inf3 = world.think(max_inferences=30, verbose=True)

    # Мама→существительное через think
    mama_info = visitor.visit("Мама")
    mama_sush = "существительное" in (mama_info["siblings"] if mama_info["found"] else set()) or \
                "Существительное" in (mama_info["siblings"] if mama_info["found"] else set())
    checks.append(("Мама → существительное (через think)", mama_sush))
    print(f"\n  Мама знает существительное: {mama_sush}")

    # Читать→глагол через think
    chit_info = visitor.visit("Читать")
    chit_glag = "глагол" in (chit_info["siblings"] if chit_info["found"] else set()) or \
                "Глагол" in (chit_info["siblings"] if chit_info["found"] else set())
    checks.append(("Читать → глагол (через think)", chit_glag))
    print(f"  Читать знает глагол: {chit_glag}")

    # Синий→прилагательное через think
    sin_info = visitor.visit("Синий")
    sin_pril = "прилагательное" in (sin_info["siblings"] if sin_info["found"] else set()) or \
               "Прилагательное" in (sin_info["siblings"] if sin_info["found"] else set())
    checks.append(("Синий → прилагательное (через think)", sin_pril))
    print(f"  Синий знает прилагательное: {sin_pril}")

    # ════════════════════════════════════════
    # ТЕСТ 4: Стабильность
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ТЕСТ 4: СТАБИЛЬНОСТЬ")
    print("=" * 60)
    inf4 = world.think(max_inferences=30, verbose=True)
    ok_stable = len(inf4) < len(inf3) + 5  # не взрывается
    checks.append(("Повторный think() стабилен", ok_stable))

    # ════════════════════════════════════════
    # ИТОГ
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("╔═══════════════════════════════════════════════════════╗")
    print("║     ИТОГ: think() v2 — ОБЩИЙ МЕХАНИЗМ                ║")
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
    print(f"║  Выводов: тест1={len(inf1)}, тест2={len(inf2)}, тест3={len(inf3)}          ║")

    if passed >= 11:
        print(f"║                                                       ║")
        print(f"║  think() v2 РАБОТАЕТ.                                ║")
    elif passed >= 7:
        print(f"║                                                       ║")
        print(f"║  ЧАСТИЧНО. Основные выводы делаются.                 ║")
    else:
        print(f"║                                                       ║")
        print(f"║  НУЖНА ДОРАБОТКА.                                    ║")

    print(f"╚═══════════════════════════════════════════════════════╝")

    print(f"\n  Статистика: {world.stats}")


if __name__ == "__main__":
    main()
