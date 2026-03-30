#!/usr/bin/env python3
"""
Уровень 2: Предложения и пунктуация.

Предусловие: система прошла уровень 1 (буквы, слоги, слова).
Уровень 2 строится поверх. Шаг за шагом учитель объясняет
предложения, точку, большую букву. Потом — упражнения.

Текст подаётся КАК ЕСТЬ. Точка — токен. Никакой разбивки.

Движок НЕ менялся.
"""

from chrysaline import World, Visitor, Generator


# ════════════════════════════════════════════════════════
# УРОВЕНЬ 1: ФУНДАМЕНТ (из level1_letters.py, сжато)
# ════════════════════════════════════════════════════════

LEVEL1_ALPHABET = [
    ["а", "это", "гласная", "буква"],
    ["о", "это", "гласная", "буква"],
    ["у", "это", "гласная", "буква"],
    ["и", "это", "гласная", "буква"],
    ["е", "это", "гласная", "буква"],
    ["ы", "это", "гласная", "буква"],
    ["к", "это", "согласная", "буква"],
    ["т", "это", "согласная", "буква"],
    ["м", "это", "согласная", "буква"],
    ["н", "это", "согласная", "буква"],
    ["р", "это", "согласная", "буква"],
    ["с", "это", "согласная", "буква"],
    ["л", "это", "согласная", "буква"],
    ["д", "это", "согласная", "буква"],
    ["б", "это", "согласная", "буква"],
    ["п", "это", "согласная", "буква"],
]

LEVEL1_SYLLABLES = [
    ["согласная", "и", "гласная", "образуют", "слог"],
    ["м", "и", "а", "это", "слог", "ма"],
    ["к", "и", "о", "это", "слог", "ко"],
    ["р", "и", "а", "это", "слог", "ра"],
    ["л", "и", "о", "это", "слог", "ло"],
    ["к", "и", "а", "это", "слог", "ка"],
    ["с", "и", "о", "это", "слог", "со"],
    ["б", "и", "а", "это", "слог", "ба"],
    ["р", "и", "ы", "это", "слог", "ры"],
    ["п", "и", "а", "это", "слог", "па"],
    ["м", "и", "о", "это", "слог", "мо"],
    ["р", "и", "у", "это", "слог", "ру"],
]

LEVEL1_WORDS = [
    ["ма", "ма", "это", "мама"],
    ["ко", "и", "т", "это", "слово", "кот"],
    ["ры", "ба", "это", "рыба"],
    ["со", "ба", "ка", "это", "собака"],
    ["ра", "ма", "это", "рама"],
    ["па", "па", "это", "папа"],
]

# ════════════════════════════════════════════════════════
# ЭТАП 1: Что такое предложение
# ════════════════════════════════════════════════════════

SENTENCE_RULES = [
    ["слова", "складываются", "в", "предложения"],
    ["предложение", "выражает", "мысль"],
    ["предложение", "это", "законченная", "мысль"],
    ["в", "предложении", "есть", "подлежащее", "и", "сказуемое"],
]

SENTENCE_EXAMPLES = [
    ["кот", "спал", "это", "предложение"],
    ["мама", "мыла", "раму", "это", "предложение"],
    ["рыба", "плавала", "это", "предложение"],
    ["собака", "ела", "это", "предложение"],
    ["папа", "читал", "книгу", "это", "предложение"],
]

# ════════════════════════════════════════════════════════
# ЭТАП 2: Пунктуация — точка
# ════════════════════════════════════════════════════════

DOT_RULES = [
    ["в", "конце", "предложения", "ставится", "точка"],
    ["точка", "означает", "мысль", "закончилась"],
    ["после", "точки", "начинается", "новое", "предложение"],
    ["точка", "стоит", "в", "конце", "предложения"],
    ["точка", "разделяет", "предложения"],
]

DOT_EXAMPLES = [
    # Предложения с точкой как токеном
    ["кот", "спал", ".", "здесь", "точка", "в", "конце"],
    ["мама", "мыла", "раму", ".", "здесь", "точка", "в", "конце"],
    ["рыба", "плавала", ".", "здесь", "точка", "в", "конце"],
    ["собака", "ела", ".", "здесь", "точка", "в", "конце"],
    ["папа", "читал", "книгу", ".", "здесь", "точка", "в", "конце"],

    # Что стоит перед точкой
    ["перед", "точкой", "стоит", "спал"],
    ["перед", "точкой", "стоит", "раму"],
    ["перед", "точкой", "стоит", "плавала"],
    ["перед", "точкой", "стоит", "ела"],
    ["перед", "точкой", "стоит", "книгу"],
]

BRIDGES = [
    [".", "это", "точка"],
    [".", "означает", "конец", "предложения"],
]

# ════════════════════════════════════════════════════════
# ЭТАП 3: Два предложения — точка разделяет
# ════════════════════════════════════════════════════════

TWO_SENTENCES = [
    # Поток с точкой-разделителем
    ["кот", "спал", ".", "собака", "ела"],
    # Учитель объясняет
    ["здесь", "два", "предложения"],
    ["первое", "предложение", "кот", "спал"],
    ["второе", "предложение", "собака", "ела"],
    ["точка", "разделяет", "первое", "и", "второе"],

    # Ещё один пример
    ["мама", "мыла", "раму", ".", "папа", "читал", "книгу"],
    ["здесь", "два", "предложения"],
    ["первое", "предложение", "мама", "мыла", "раму"],
    ["второе", "предложение", "папа", "читал", "книгу"],
    ["точка", "разделяет", "первое", "и", "второе"],
]

# ════════════════════════════════════════════════════════
# ЭТАП 4: Большая буква
# ════════════════════════════════════════════════════════

CAPITAL_LETTER = [
    ["после", "точки", "первое", "слово", "с", "большой", "буквы"],
    ["большая", "буква", "в", "начале", "предложения"],
    ["Кот", "и", "кот", "это", "одно", "слово"],
    ["Собака", "и", "собака", "это", "одно", "слово"],
    ["Мама", "и", "мама", "это", "одно", "слово"],
    ["Папа", "и", "папа", "это", "одно", "слово"],
    ["Рыба", "и", "рыба", "это", "одно", "слово"],
    ["Кот", "это", "кот", "с", "большой", "буквы"],
    ["Собака", "это", "собака", "с", "большой", "буквы"],
]


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
    print("  УРОВЕНЬ 2: ПРЕДЛОЖЕНИЯ И ПУНКТУАЦИЯ")
    print("  Поверх уровня 1. Шаг за шагом.")
    print("  Движок НЕ менялся.")
    print("=" * 60)

    world = World()
    visitor = Visitor(world)
    gen = Generator(world)

    # ════════════════════════════════════════
    # УРОВЕНЬ 1 (фундамент)
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  УРОВЕНЬ 1: ФУНДАМЕНТ")
    print("=" * 60)
    teach(world, LEVEL1_ALPHABET, "Алфавит", repeats=3)
    teach(world, LEVEL1_SYLLABLES, "Слоги", repeats=3)
    teach(world, LEVEL1_WORDS, "Слова", repeats=3)

    # ════════════════════════════════════════
    # ЭТАП 1: Что такое предложение
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ЭТАП 1: ЧТО ТАКОЕ ПРЕДЛОЖЕНИЕ")
    print("=" * 60)
    teach(world, SENTENCE_RULES, "Правила предложений", repeats=3)
    teach(world, SENTENCE_EXAMPLES, "Примеры предложений", repeats=3)

    # ════════════════════════════════════════
    # ЭТАП 2: Пунктуация — точка
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ЭТАП 2: ПУНКТУАЦИЯ — ТОЧКА")
    print("=" * 60)
    teach(world, DOT_RULES, "Правила точки", repeats=3)
    teach(world, DOT_EXAMPLES, "Примеры с точкой", repeats=3)
    teach(world, BRIDGES, "Мосты (.↔точка)", repeats=5)

    # ════════════════════════════════════════
    # ЭТАП 3: Два предложения
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ЭТАП 3: ДВА ПРЕДЛОЖЕНИЯ")
    print("=" * 60)
    teach(world, TWO_SENTENCES, "Два предложения с точкой", repeats=3)

    # ════════════════════════════════════════
    # ЭТАП 4: Большая буква
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ЭТАП 4: БОЛЬШАЯ БУКВА")
    print("=" * 60)
    teach(world, CAPITAL_LETTER, "Большая буква", repeats=3)

    # ════════════════════════════════════════
    # ЭТАП 5: УПРАЖНЕНИЯ
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ЭТАП 5: УПРАЖНЕНИЯ")
    print("=" * 60)

    checks = []

    # ── Упражнение 1: visit(".") ──
    print(f"\n  ── Упражнение 1: visit('.') ──")
    dot_info = visitor.visit(".")
    if dot_info["found"]:
        dot_sibs = dot_info["siblings"]
        print(f"    братья: {sorted(dot_sibs)[:15]}")
        knows_tochka = "точка" in dot_sibs
        print(f"    знает 'точка': {knows_tochka}")
        # Цепочка через мост
        if knows_tochka:
            t_info = visitor.visit("точка")
            t_sibs = t_info["siblings"] if t_info["found"] else set()
            knows_konce = "конце" in t_sibs
            knows_razd = "разделяет" in t_sibs
            print(f"    цепочка: '.' → 'точка' → 'конце': {knows_konce}")
            print(f"    цепочка: '.' → 'точка' → 'разделяет': {knows_razd}")
            ok1 = knows_tochka and (knows_konce or knows_razd)
        else:
            ok1 = False
    else:
        print(f"    '.' не найдена")
        ok1 = False
    checks.append(("visit('.') → цепочка до правил", ok1))

    # ── Упражнение 2: visit("точка") ──
    print(f"\n  ── Упражнение 2: visit('точка') ──")
    tochka_info = visitor.visit("точка")
    if tochka_info["found"]:
        t_sibs = tochka_info["siblings"]
        print(f"    братья: {sorted(t_sibs)[:15]}")
        knows_dot = "." in t_sibs
        knows_razd = "разделяет" in t_sibs
        knows_konce = "конце" in t_sibs
        knows_predl = "предложения" in t_sibs
        print(f"    знает '.': {knows_dot}")
        print(f"    знает 'разделяет': {knows_razd}")
        print(f"    знает 'конце': {knows_konce}")
        print(f"    знает 'предложения': {knows_predl}")
        ok2 = knows_razd and knows_konce
    else:
        ok2 = False
    checks.append(("visit('точка') → разделяет, конце", ok2))

    # ── Упражнение 3: ask("что означает точка?") ──
    print(f"\n  ── Упражнение 3: ask('что означает точка?') ──")
    res3 = gen.ask("что означает точка?")
    print(f"    ответ: {res3['answers'][:8]}")
    if res3["reasoning"]:
        for r in res3["reasoning"][:3]:
            print(f"    логика: {r}")
    ok3_words = {"конец", "конце", "предложения", "мысль", "закончилась", "разделяет"}
    ok3 = bool(set(res3["answers"]) & ok3_words)
    checks.append(("ask('что означает точка?') → конец/мысль", ok3))

    # ── Упражнение 4: Сырой текст ──
    print(f"\n  ── Упражнение 4: Сырой текст как есть ──")
    raw = ["Кот", "ел", "рыбу", ".", "Собака", "спала", "."]
    print(f"    Поток: {raw}")
    print(f"    Один feed_sentence(). Без разбивки.")

    for r in range(5):
        world.feed_sentence(raw)
        world.run(1)

    # 4a: Кот↔кот
    kot_upper = visitor.visit("Кот")
    kot_lower = visitor.visit("кот")
    upper_sibs = kot_upper["siblings"] if kot_upper["found"] else set()
    lower_sibs = kot_lower["siblings"] if kot_lower["found"] else set()
    linked = "кот" in upper_sibs or "Кот" in lower_sibs
    print(f"    'Кот' братья: {sorted(upper_sibs)[:10]}")
    print(f"    'кот' братья: {sorted(lower_sibs)[:10]}")
    print(f"    Кот↔кот связаны: {linked}")
    checks.append(("Кот↔кот связаны", linked))

    # 4b: Абстракции из текста
    print(f"\n    Абстракции из сырого текста:")
    text_abstracts = []
    for c in world.creatures.values():
        if not c.alive or not c.slot_options:
            continue
        parts_set = set(c.parts)
        text_words = {"Кот", "ел", "рыбу", "Собака", "спала", "."}
        if parts_set & text_words:
            slots = {}
            for sn, opts in c.slot_options.items():
                clean = sorted(o for o in opts if not o.startswith("$"))
                if clean:
                    slots[sn] = clean
            if slots:
                text_abstracts.append((c.name, slots, c.times_fed))
                print(f"      {c.name}  {slots}  fed={c.times_fed}")

    # Ищем абстракции с действиями
    has_action = any("ел" in name or "спала" in name or "спал" in name
                     for name, _, _ in text_abstracts)
    # Ищем абстракции с точкой
    has_dot_abst = any("." in name for name, _, _ in text_abstracts)
    ok4b = has_action or has_dot_abst
    checks.append(("Абстракции из сырого текста", ok4b))

    # ── Упражнение 5: ask("что делал кот?") ──
    print(f"\n  ── Упражнение 5: ask('что делал кот?') ──")
    res5 = gen.ask("что делал кот?")
    print(f"    ответ: {res5['answers'][:8]}")
    if res5["reasoning"]:
        for r in res5["reasoning"][:3]:
            print(f"    логика: {r}")
    ok5_words = {"ел", "спал", "рыбу"}
    ok5 = bool(set(res5["answers"]) & ok5_words)
    checks.append(("ask('что делал кот?') → ел/спал", ok5))

    # ── Упражнение 6: ask("что стоит перед точкой?") ──
    print(f"\n  ── Упражнение 6: ask('что стоит перед точкой?') ──")
    res6 = gen.ask("что стоит перед точкой?")
    print(f"    ответ: {res6['answers'][:8]}")
    if res6["reasoning"]:
        for r in res6["reasoning"][:3]:
            print(f"    логика: {r}")
    ok6_words = {"спал", "раму", "плавала", "ела", "книгу", "спала", "рыбу"}
    ok6 = bool(set(res6["answers"]) & ok6_words)
    checks.append(("ask('что перед точкой?') → слова концов", ok6))

    # ════════════════════════════════════════
    # ПОЛНАЯ КАРТИНА
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ПОЛНАЯ КАРТИНА")
    print("=" * 60)

    # Все организмы с "."
    print(f"\n  Организмы с '.' (top-15):")
    dot_orgs = []
    for c in world.creatures.values():
        if not c.alive or c.complexity < 2:
            continue
        if "." in c.parts:
            dot_orgs.append(c)
    dot_orgs.sort(key=lambda c: (-c.times_fed, -c.energy))
    for c in dot_orgs[:15]:
        slots = ""
        if c.slot_options:
            for sn, opts in c.slot_options.items():
                clean = sorted(o for o in opts if not o.startswith("$"))
                if clean:
                    slots += f" {sn}={clean}"
        print(f"    {c.name:50s} fed={c.times_fed:3d}{slots}")

    # Абстракции с действиями
    print(f"\n  Абстракции с действиями:")
    for c in world.creatures.values():
        if not c.alive or not c.slot_options:
            continue
        action_words = {"спал", "спала", "ела", "ел", "мыла", "читал", "плавала"}
        if set(c.parts) & action_words:
            slots = {}
            for sn, opts in c.slot_options.items():
                clean = sorted(o for o in opts if not o.startswith("$"))
                if clean:
                    slots[sn] = clean
            if slots:
                print(f"    {c.name}  {slots}  fed={c.times_fed}")

    # Абстракции "$0 это одно слово"
    print(f"\n  Абстракции связи большая↔маленькая буква:")
    for c in world.creatures.values():
        if not c.alive or not c.slot_options:
            continue
        if "одно" in c.parts and "слово" in c.parts:
            slots = {}
            for sn, opts in c.slot_options.items():
                clean = sorted(o for o in opts if not o.startswith("$"))
                if clean:
                    slots[sn] = clean
            if slots:
                print(f"    {c.name}  {slots}  fed={c.times_fed}")

    # Топ-15
    print(f"\n  Топ-15 абстракций:")
    for c in world.show_abstractions()[:15]:
        slots = {}
        for sn, opts in c.slot_options.items():
            clean = sorted(o for o in opts if not o.startswith("$"))
            if clean:
                slots[sn] = clean[:10]
        if slots:
            print(f"    {c.name:50s} {slots}  fed={c.times_fed}")

    # ════════════════════════════════════════
    # ИТОГ
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("╔═══════════════════════════════════════════════════════╗")
    print("║     ИТОГ: УРОВЕНЬ 2 — ПРЕДЛОЖЕНИЯ И ПУНКТУАЦИЯ       ║")
    print("╠═══════════════════════════════════════════════════════╣")

    passed = 0
    for name, ok in checks:
        s = "+" if ok else "-"
        if ok:
            passed += 1
        print(f"║  {s} {name:52s}║")

    print(f"╠═══════════════════════════════════════════════════════╣")
    print(f"║  Результат: {passed}/{len(checks)}                                     ║")

    alive = sum(1 for c in world.creatures.values() if c.alive)
    abst = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"║  Мир: {alive} существ, {abst} абстракций                  ║")

    if passed >= 6:
        print(f"║                                                       ║")
        print(f"║  УРОВЕНЬ 2 УСВОЕН.                                   ║")
        print(f"║  Можно переходить к уровню 3.                        ║")
    elif passed >= 4:
        print(f"║                                                       ║")
        print(f"║  ЧАСТИЧНО. Основы есть, детали доработать.           ║")
    else:
        print(f"║                                                       ║")
        print(f"║  НУЖНА ДОРАБОТКА.                                     ║")

    print(f"║  Движок НЕ менялся.                                   ║")
    print(f"╚═══════════════════════════════════════════════════════╝")

    print(f"\n  Статистика: {world.stats}")


if __name__ == "__main__":
    main()
