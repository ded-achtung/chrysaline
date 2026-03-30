#!/usr/bin/env python3
"""
Эксперимент: Пунктуация после Уровня 1.

Система уже знает буквы, слоги, слова (Уровень 1).
Теперь учитель объясняет пунктуацию, потом подаём сырой текст
КАК ЕСТЬ — одним потоком пословно, с точками и большими буквами.
Не разбиваем. Не нормализуем. Смотрим что произойдёт.

Движок НЕ менялся.
"""

from chrysaline import World, Visitor, Generator


# ════════════════════════════════════════════════════════
# УРОВЕНЬ 1: ФУНДАМЕНТ (буквы, слоги, слова)
# ════════════════════════════════════════════════════════

ALPHABET_VOWELS = [
    ["а", "это", "гласная", "буква"],
    ["о", "это", "гласная", "буква"],
    ["у", "это", "гласная", "буква"],
    ["и", "это", "гласная", "буква"],
    ["е", "это", "гласная", "буква"],
    ["ы", "это", "гласная", "буква"],
]

ALPHABET_CONSONANTS = [
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

SYLLABLE_EXAMPLES = [
    ["м", "и", "а", "это", "слог", "ма"],
    ["к", "и", "о", "это", "слог", "ко"],
    ["р", "и", "а", "это", "слог", "ра"],
    ["м", "и", "у", "это", "слог", "му"],
    ["л", "и", "о", "это", "слог", "ло"],
    ["к", "и", "а", "это", "слог", "ка"],
    ["с", "и", "о", "это", "слог", "со"],
    ["б", "и", "а", "это", "слог", "ба"],
    ["р", "и", "ы", "это", "слог", "ры"],
    ["д", "и", "о", "это", "слог", "до"],
    ["н", "и", "а", "это", "слог", "на"],
    ["п", "и", "а", "это", "слог", "па"],
]

WORD_EXAMPLES = [
    ["ма", "ма", "это", "мама"],
    ["ко", "и", "т", "это", "слово", "кот"],
    ["ры", "ба", "это", "рыба"],
    ["со", "ба", "ка", "это", "собака"],
    ["до", "ма", "это", "дома"],
    ["ра", "ма", "это", "рама"],
    ["па", "па", "это", "папа"],
    ["му", "ка", "это", "мука"],
]

# ════════════════════════════════════════════════════════
# ФАЗА 1: ПУНКТУАЦИЯ — правила + примеры
# ════════════════════════════════════════════════════════

PUNCTUATION_RULES = [
    ["точка", "стоит", "в", "конце", "предложения"],
    ["после", "точки", "начинается", "новое", "предложение"],
    ["после", "точки", "первое", "слово", "пишется", "с", "большой", "буквы"],
    ["запятая", "разделяет", "слова", "в", "перечислении"],
    ["тире", "означает", "определение"],
]

PUNCTUATION_EXAMPLES = [
    ["кот", "ел", "рыбу", "это", "предложение"],
    ["в", "конце", "стоит", "точка"],
    ["собака", "спала", "это", "другое", "предложение"],
    ["точка", "разделяет", "предложения"],

    # Примеры с точкой как токеном
    ["кот", "ел", "рыбу", ".", "здесь", "точка"],
    ["собака", "спала", ".", "здесь", "точка"],

    # Связь большая/маленькая буква
    ["Кот", "и", "кот", "это", "одно", "слово"],
    ["Собака", "и", "собака", "это", "одно", "слово"],
    ["Корова", "и", "корова", "это", "одно", "слово"],
    ["после", "точки", "слово", "с", "большой", "буквы"],
    ["Кот", "это", "кот", "с", "большой", "буквы"],
    ["Собака", "это", "собака", "с", "большой", "буквы"],
    ["Корова", "это", "корова", "с", "большой", "буквы"],
]

BRIDGES = [
    [".", "это", "точка"],
    [".", "означает", "конец", "предложения"],
]

# ════════════════════════════════════════════════════════
# ФАЗА 2: СЫРОЙ ТЕКСТ
# ════════════════════════════════════════════════════════

RAW_TEXT = "Кот живёт в доме. Кот ест рыбу. Собака живёт в доме. Собака ест мясо. Корова живёт на ферме. Корова даёт молоко."


def tokenize_raw(text):
    """Разбить текст на токены пословно, точки — отдельные токены.
    НЕ меняем регистр. НЕ убираем точки. Как есть."""
    tokens = []
    for word in text.split():
        if word.endswith("."):
            tokens.append(word[:-1])  # слово без точки
            tokens.append(".")       # точка отдельно
        else:
            tokens.append(word)
    return tokens


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
    print("  ЭКСПЕРИМЕНТ: ПУНКТУАЦИЯ ПОСЛЕ УРОВНЯ 1")
    print("  Фундамент → Правила → Сырой текст → Проверка")
    print("  Движок НЕ менялся.")
    print("=" * 60)

    world = World()
    visitor = Visitor(world)
    gen = Generator(world)

    # ════════════════════════════════════════
    # УРОВЕНЬ 1: Фундамент
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  УРОВЕНЬ 1: ФУНДАМЕНТ")
    print("=" * 60)

    teach(world, ALPHABET_VOWELS, "Гласные", repeats=3)
    teach(world, ALPHABET_CONSONANTS, "Согласные", repeats=3)
    teach(world, SYLLABLE_EXAMPLES, "Слоги", repeats=3)
    teach(world, WORD_EXAMPLES, "Слова", repeats=3)

    # ════════════════════════════════════════
    # ФАЗА 1: Пунктуация
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ФАЗА 1: ПУНКТУАЦИЯ")
    print("=" * 60)

    teach(world, PUNCTUATION_RULES, "Правила пунктуации", repeats=3)
    teach(world, PUNCTUATION_EXAMPLES, "Примеры пунктуации", repeats=3)
    teach(world, BRIDGES, "Мосты (.=точка)", repeats=5)

    # Срез: что знает система?
    print(f"\n  Срез после обучения:")
    for word in [".", "точка", "Кот", "кот", "предложение"]:
        info = visitor.visit(word)
        if info["found"]:
            print(f"    '{word}' братья: {sorted(info['siblings'])[:10]}")

    # ════════════════════════════════════════
    # ФАЗА 2: Сырой текст — одним потоком
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ФАЗА 2: СЫРОЙ ТЕКСТ")
    print("=" * 60)

    tokens = tokenize_raw(RAW_TEXT)
    print(f"  Текст: \"{RAW_TEXT}\"")
    print(f"  Токены ({len(tokens)}): {tokens}")
    print(f"  Один feed_sentence() на весь текст.")

    for r in range(5):
        world.feed_sentence(tokens)
        world.run(1)

    alive = sum(1 for c in world.creatures.values() if c.alive)
    abst = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"\n  После подачи: {alive} существ, {abst} абстракций")

    # ════════════════════════════════════════
    # ФАЗА 3: ПРОВЕРКА
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ФАЗА 3: ПРОВЕРКА")
    print("=" * 60)

    # ── Проверка 1: Разбила ли система текст по точкам? ──
    print(f"\n  ── Проверка 1: Точка как разделитель ──")
    dot_info = visitor.visit(".")
    if dot_info["found"]:
        print(f"    '.' братья: {sorted(dot_info['siblings'])[:15]}")
        print(f"    '.' slot_mates: {sorted(dot_info.get('slot_mates', set()))[:15]}")

    # Что перед точкой? Что после?
    before_dot = set()
    after_dot = set()
    for c in world.creatures.values():
        if not c.alive or c.complexity != 2:
            continue
        if c.parts[1] == ".":
            before_dot.add(c.parts[0])
        if c.parts[0] == ".":
            after_dot.add(c.parts[1])
    print(f"    X·. (перед точкой): {sorted(before_dot)}")
    print(f"    .·Y (после точки):  {sorted(after_dot)}")

    # Абстракции с точкой
    print(f"\n    Абстракции с '.':")
    for c in world.creatures.values():
        if not c.alive or not c.slot_options:
            continue
        if "." in c.parts:
            slots = {}
            for sn, opts in c.slot_options.items():
                clean = sorted(o for o in opts if not o.startswith("$"))
                if clean:
                    slots[sn] = clean
            if slots:
                print(f"      {c.name}  {slots}  fed={c.times_fed}")

    # Точка знает "конце предложения"?
    knows_tochka = "точка" in dot_info.get("siblings", set()) if dot_info["found"] else False
    check1 = len(before_dot) >= 3  # перед точкой стоят разные слова
    print(f"\n    '.' знает 'точка': {knows_tochka}")
    print(f"    Перед точкой >= 3 разных слов: {check1}")

    # ── Проверка 2: "К" связана с "к"? ──
    print(f"\n  ── Проверка 2: 'Кот' = 'кот'? ──")
    kot_upper = visitor.visit("Кот")
    kot_lower = visitor.visit("кот")
    upper_sibs = kot_upper["siblings"] if kot_upper["found"] else set()
    lower_sibs = kot_lower["siblings"] if kot_lower["found"] else set()
    upper_mates = kot_upper.get("slot_mates", set()) if kot_upper["found"] else set()
    lower_mates = kot_lower.get("slot_mates", set()) if kot_lower["found"] else set()

    linked_sibs = "кот" in upper_sibs or "Кот" in lower_sibs
    linked_mates = "кот" in upper_mates or "Кот" in lower_mates
    check2 = linked_sibs or linked_mates

    print(f"    'Кот' братья: {sorted(upper_sibs)[:10]}")
    print(f"    'кот' братья: {sorted(lower_sibs)[:10]}")
    print(f"    'Кот' slot_mates: {sorted(upper_mates)[:10]}")
    print(f"    Связаны через братья: {linked_sibs}")
    print(f"    Связаны через slot_mates: {linked_mates}")

    # То же для Собака/собака и Корова/корова
    for upper, lower in [("Собака", "собака"), ("Корова", "корова")]:
        u_info = visitor.visit(upper)
        l_info = visitor.visit(lower)
        u_sibs = u_info["siblings"] if u_info["found"] else set()
        linked = lower in u_sibs or upper in (l_info["siblings"] if l_info["found"] else set())
        print(f"    '{upper}' ↔ '{lower}': {linked}")

    # ── Проверка 3: Абстракции ──
    print(f"\n  ── Проверка 3: Абстракции ──")
    interesting = []
    for c in world.creatures.values():
        if not c.alive or not c.slot_options:
            continue
        fixed = [p for p in c.parts if not p.startswith("$")]
        if any(w in fixed for w in ["живёт", "ест", "даёт"]):
            slots = {}
            for sn, opts in c.slot_options.items():
                clean = sorted(o for o in opts if not o.startswith("$"))
                if clean:
                    slots[sn] = clean
            if slots:
                interesting.append((c.name, slots, c.times_fed))

    has_live = False
    has_eat = False
    has_give = False
    for name, slots, fed in interesting:
        print(f"    {name}  {slots}  fed={fed}")
        if "живёт" in name:
            has_live = True
        if "ест" in name:
            has_eat = True
        if "даёт" in name:
            has_give = True

    if not interesting:
        print(f"    (целевые абстракции не найдены)")
        # Показать все абстракции для отладки
        print(f"\n    Все абстракции (top-15):")
        for c in world.show_abstractions()[:15]:
            slots = {}
            for sn, opts in c.slot_options.items():
                clean = sorted(o for o in opts if not o.startswith("$"))
                if clean:
                    slots[sn] = clean
            if slots:
                print(f"      {c.name}  {slots}  fed={c.times_fed}")

    check3 = has_live or has_eat
    print(f"\n    '$0·живёт·...': {has_live}")
    print(f"    '$0·ест·...': {has_eat}")
    print(f"    '$0·даёт·...': {has_give}")

    # ── Проверка 4: ask() ──
    print(f"\n  ── Проверка 4: ask() ──")
    questions = {
        "где живёт кот?": {"доме", "дом", "в"},
        "что ест кот?": {"рыбу", "рыба"},
        "где живёт собака?": {"доме", "дом", "в"},
        "что ест собака?": {"мясо"},
        "где живёт корова?": {"ферме", "ферма", "на"},
        "что даёт корова?": {"молоко"},
    }

    ask_correct = 0
    for q, expected in questions.items():
        res = gen.ask(q)
        answers = res["answers"]
        match = bool(set(answers) & expected)
        if match:
            ask_correct += 1
        status = "OK" if match else "MISS"
        print(f"    {status} {q}")
        print(f"         → {answers[:6]}")
        if res["reasoning"]:
            print(f"         логика: {res['reasoning'][:2]}")

    check4 = ask_correct >= 3

    # ════════════════════════════════════════
    # ИТОГ
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("╔═══════════════════════════════════════════════════════╗")
    print("║     ИТОГ: ПУНКТУАЦИЯ ПОСЛЕ УРОВНЯ 1                  ║")
    print("╠═══════════════════════════════════════════════════════╣")

    checks = [
        (check1, "1. Точка разделяет (перед ней разные слова)"),
        (check2, "2. 'Кот' связан с 'кот'"),
        (check3, "3. Абстракции ($0·живёт, $0·ест...)"),
        (check4, f"4. ask() отвечает ({ask_correct}/6)"),
    ]

    passed = 0
    for ok, desc in checks:
        s = "+" if ok else "-"
        if ok:
            passed += 1
        print(f"║  {s} {desc:52s}║")

    print(f"╠═══════════════════════════════════════════════════════╣")
    print(f"║  Результат: {passed}/4                                     ║")
    print(f"╠═══════════════════════════════════════════════════════╣")

    if passed == 4:
        print(f"║  ПОЛНЫЙ УСПЕХ.                                       ║")
    elif passed >= 2:
        print(f"║  ЧАСТИЧНЫЙ УСПЕХ.                                    ║")
    elif passed >= 1:
        print(f"║  МИНИМАЛЬНЫЙ ПРОРЫВ.                                 ║")
    else:
        print(f"║  НЕ СРАБОТАЛО.                                       ║")

    print(f"║  Движок НЕ менялся.                                   ║")
    print(f"╚═══════════════════════════════════════════════════════╝")

    alive = sum(1 for c in world.creatures.values() if c.alive)
    abst = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"\n  Мир: {alive} существ, {abst} абстракций")
    print(f"  Статистика: {world.stats}")


if __name__ == "__main__":
    main()
