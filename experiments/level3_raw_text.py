#!/usr/bin/env python3
"""
Уровень 3: Сырой текст после обучения.

Система прошла уровни 1-2: знает буквы, слоги, слова, предложения, точки.
Теперь получает НОВЫЙ текст, которого не видела.
Пословно (split по пробелам). Точки и большие буквы — как есть.

Вопрос: что система извлечёт из нового текста?

Движок НЕ менялся.
"""

from chrysaline import World, Visitor, Generator


# ════════════════════════════════════════════════════════
# ОБУЧЕНИЕ (уровни 1-2, сжато)
# ════════════════════════════════════════════════════════

LEVEL1_DATA = [
    # Гласные
    ["а", "это", "гласная", "буква"],
    ["о", "это", "гласная", "буква"],
    ["у", "это", "гласная", "буква"],
    ["и", "это", "гласная", "буква"],
    ["е", "это", "гласная", "буква"],
    ["ы", "это", "гласная", "буква"],
    # Согласные
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
    # Слоги
    ["согласная", "и", "гласная", "образуют", "слог"],
    ["слог", "это", "часть", "слова"],
    # Примеры слогов
    ["м", "и", "а", "это", "слог", "ма"],
    ["к", "и", "о", "это", "слог", "ко"],
    ["т", "и", "а", "это", "слог", "та"],
    ["н", "и", "а", "это", "слог", "на"],
    ["р", "и", "а", "это", "слог", "ра"],
    ["л", "и", "о", "это", "слог", "ло"],
    ["к", "и", "а", "это", "слог", "ка"],
    ["с", "и", "о", "это", "слог", "со"],
    ["б", "и", "а", "это", "слог", "ба"],
    ["р", "и", "у", "это", "слог", "ру"],
    ["п", "и", "а", "это", "слог", "па"],
    ["м", "и", "о", "это", "слог", "мо"],
    ["р", "и", "ы", "это", "слог", "ры"],
    # Слова
    ["ма", "ма", "это", "мама"],
    ["ко", "и", "т", "это", "слово", "кот"],
    ["ры", "ба", "это", "рыба"],
    ["со", "ба", "ка", "это", "собака"],
    ["мо", "ло", "ко", "это", "молоко"],
    ["ра", "ма", "это", "рама"],
    ["па", "па", "это", "папа"],
]

LEVEL2_DATA = [
    # Правила предложений и точки
    ["точка", "стоит", "в", "конце", "предложения"],
    ["после", "точки", "начинается", "новое", "предложение"],
    ["точка", "разделяет", "предложения"],
    ["предложение", "выражает", "мысль"],
    ["пробел", "разделяет", "слова"],
    # Мосты
    [".", "это", "точка"],
    [".", "означает", "конец", "предложения"],
    # Примеры предложений
    ["кот", "ел", "рыбу", "это", "предложение"],
    ["собака", "спала", "это", "предложение"],
    ["мама", "мыла", "раму", "это", "предложение"],
    # Связь большая↔маленькая буква
    ["Кот", "и", "кот", "это", "одно", "слово"],
    ["Собака", "и", "собака", "это", "одно", "слово"],
    ["Мама", "и", "мама", "это", "одно", "слово"],
    ["Папа", "и", "папа", "это", "одно", "слово"],
    ["большая", "буква", "в", "начале", "предложения"],
    # Что перед/после точки
    ["точка", "после", "рыбу", "значит", "конец", "предложения"],
    ["точка", "после", "спала", "значит", "конец", "предложения"],
    ["перед", "точкой", "стоит", "последнее", "слово"],
    ["после", "точки", "стоит", "первое", "слово"],
]

# ════════════════════════════════════════════════════════
# СЫРОЙ ТЕКСТ (новый, не видела раньше)
# ════════════════════════════════════════════════════════

RAW_TEXTS = [
    # Текст 1: простой, знакомые слова
    "Кот спал. Собака ела.",

    # Текст 2: новые комбинации знакомых слов
    "Мама варила суп. Папа читал книгу.",

    # Текст 3: частично новые слова
    "Корова ела траву. Лошадь пила воду.",
]


def teach(world, data, label, repeats=3):
    """Подать данные N раз."""
    print(f"\n  ── {label} ({len(data)} фраз, {repeats}x) ──")
    for r in range(repeats):
        for phrase in data:
            world.feed_sentence(phrase)
            world.run(1)
    alive = sum(1 for c in world.creatures.values() if c.alive)
    abst = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"    → {alive} существ, {abst} абстракций")


def parse_raw(text):
    """Минимальный парсинг: split по пробелам. Точки остаются приклеены к словам.
    НО: мы отделяем точку как отдельный токен, потому что система знает
    что '.' — это 'точка'. Это единственная обработка."""
    tokens = []
    for word in text.split():
        if word.endswith("."):
            if len(word) > 1:
                tokens.append(word[:-1])  # слово без точки
            tokens.append(".")           # точка отдельно
        else:
            tokens.append(word)
    return tokens


def feed_raw_text(world, text, label, repeats=3):
    """Разбить сырой текст на предложения по точкам и подать."""
    print(f"\n  ── {label} ──")
    print(f"    Текст: \"{text}\"")

    # Разбиваем по точкам на предложения
    sentences = []
    current = []
    tokens = parse_raw(text)
    print(f"    Токены: {tokens}")

    for token in tokens:
        if token == ".":
            if current:
                # Подаём предложение + точку
                sentences.append(current + ["."])
                # И отдельно предложение без точки (для чистых абстракций)
                sentences.append(current)
                current = []
        else:
            current.append(token)
    if current:
        sentences.append(current)

    print(f"    Предложения: {len(sentences)}")
    for s in sentences:
        print(f"      {s}")

    for r in range(repeats):
        for sent in sentences:
            world.feed_sentence(sent)
            world.run(1)

    alive = sum(1 for c in world.creatures.values() if c.alive)
    abst = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"    → {alive} существ, {abst} абстракций")
    return sentences


def main():
    print("=" * 60)
    print("  УРОВЕНЬ 3: СЫРОЙ ТЕКСТ ПОСЛЕ ОБУЧЕНИЯ")
    print("  Система знает буквы, слоги, слова, предложения.")
    print("  Теперь получает новый текст.")
    print("  Движок НЕ менялся.")
    print("=" * 60)

    world = World()
    visitor = Visitor(world)
    gen = Generator(world)

    # ════════════════════════════════════════
    # ОБУЧЕНИЕ (уровни 1-2)
    # ════════════════════════════════════════
    teach(world, LEVEL1_DATA, "Уровень 1: буквы, слоги, слова", repeats=3)
    teach(world, LEVEL2_DATA, "Уровень 2: предложения, точки, мосты", repeats=3)

    alive_before = sum(1 for c in world.creatures.values() if c.alive)
    abst_before = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"\n  После обучения: {alive_before} существ, {abst_before} абстракций")

    # ════════════════════════════════════════
    # СЫРОЙ ТЕКСТ 1: "Кот спал. Собака ела."
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ТЕКСТ 1: Кот спал. Собака ела.")
    print("  (знакомые слова, новые комбинации)")
    print("=" * 60)

    sents1 = feed_raw_text(world, RAW_TEXTS[0], "Текст 1", repeats=3)

    # Проверка: Кот↔кот связались?
    print(f"\n  ── Проверки после текста 1 ──")
    kot_upper = visitor.visit("Кот")
    kot_lower = visitor.visit("кот")
    if kot_upper["found"] and kot_lower["found"]:
        linked = "кот" in kot_upper["siblings"] or "Кот" in kot_lower["siblings"]
        print(f"  Кот↔кот связаны: {linked}")
    else:
        linked = False
        print(f"  Кот или кот не найдены")

    # Что знает кот после нового текста?
    if kot_lower["found"]:
        print(f"  visit('кот') братья: {sorted(kot_lower['siblings'])[:15]}")

    # ask: что делал кот?
    res1a = gen.ask("что делал кот?")
    print(f"  ask('что делал кот?'): {res1a['answers'][:8]}")

    res1b = gen.ask("что делала собака?")
    print(f"  ask('что делала собака?'): {res1b['answers'][:8]}")

    # ════════════════════════════════════════
    # СЫРОЙ ТЕКСТ 2: "Мама варила суп. Папа читал книгу."
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ТЕКСТ 2: Мама варила суп. Папа читал книгу.")
    print("  (знакомые субъекты, новые глаголы и объекты)")
    print("=" * 60)

    sents2 = feed_raw_text(world, RAW_TEXTS[1], "Текст 2", repeats=3)

    # Проверки
    print(f"\n  ── Проверки после текста 2 ──")

    res2a = gen.ask("что варила мама?")
    print(f"  ask('что варила мама?'): {res2a['answers'][:8]}")

    res2b = gen.ask("что читал папа?")
    print(f"  ask('что читал папа?'): {res2b['answers'][:8]}")

    # Мама↔мама связались?
    mama_upper = visitor.visit("Мама")
    mama_lower = visitor.visit("мама")
    if mama_upper["found"] and mama_lower["found"]:
        mama_linked = "мама" in mama_upper["siblings"] or "Мама" in mama_lower["siblings"]
        print(f"  Мама↔мама связаны: {mama_linked}")

    # ════════════════════════════════════════
    # СЫРОЙ ТЕКСТ 3: "Корова ела траву. Лошадь пила воду."
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ТЕКСТ 3: Корова ела траву. Лошадь пила воду.")
    print("  (частично новые слова)")
    print("=" * 60)

    sents3 = feed_raw_text(world, RAW_TEXTS[2], "Текст 3", repeats=3)

    # Проверки
    print(f"\n  ── Проверки после текста 3 ──")

    res3a = gen.ask("что ела корова?")
    print(f"  ask('что ела корова?'): {res3a['answers'][:8]}")

    res3b = gen.ask("что пила лошадь?")
    print(f"  ask('что пила лошадь?'): {res3b['answers'][:8]}")

    # Новые слова поглотились?
    korova = visitor.visit("Корова")
    if korova["found"]:
        print(f"  visit('Корова') братья: {sorted(korova['siblings'])[:10]}")

    loshad = visitor.visit("Лошадь")
    if loshad["found"]:
        print(f"  visit('Лошадь') братья: {sorted(loshad['siblings'])[:10]}")

    # ════════════════════════════════════════
    # ОБЩИЕ ПРОВЕРКИ
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ОБЩИЕ ПРОВЕРКИ")
    print("=" * 60)

    # Абстракции из текстов
    print(f"\n  ── Абстракции с действиями ──")
    for c in world.creatures.values():
        if not c.alive or not c.slot_options:
            continue
        action_words = {"спал", "спала", "ела", "ел", "варила", "читал", "пила", "мыла"}
        if set(c.parts) & action_words:
            slots = {}
            for sn, opts in c.slot_options.items():
                clean = sorted(o for o in opts if not o.startswith("$"))
                if clean:
                    slots[sn] = clean
            if slots:
                print(f"    {c.name}  {slots}  fed={c.times_fed}")

    # Абстракции с точкой
    print(f"\n  ── Абстракции с '.' ──")
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
                print(f"    {c.name}  {slots}  fed={c.times_fed}")

    # Абстракции "$0 это одно слово"
    print(f"\n  ── Абстракции связи большая↔маленькая буква ──")
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

    # Топ абстракции
    print(f"\n  ── Топ-15 абстракций ──")
    all_abst = world.show_abstractions()
    for c in all_abst[:15]:
        slots = {}
        for sn, opts in c.slot_options.items():
            clean = sorted(o for o in opts if not o.startswith("$"))
            if clean:
                slots[sn] = clean[:10]
        if slots:
            print(f"    {c.name:45s} {slots}  fed={c.times_fed}")

    # ════════════════════════════════════════
    # ИТОГ
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("╔═══════════════════════════════════════════════════════╗")
    print("║     ИТОГ: СЫРОЙ ТЕКСТ ПОСЛЕ ОБУЧЕНИЯ                 ║")
    print("╠═══════════════════════════════════════════════════════╣")

    checks = []

    # 1. Кот↔кот связались
    ok1 = linked
    checks.append(("Кот↔кот связались", ok1))

    # 2. ask("что делал кот?") → спал
    ok2 = "спал" in res1a["answers"] or "ел" in res1a["answers"]
    checks.append(("ask('что делал кот?') → ответ", ok2))

    # 3. ask("что варила мама?") → суп
    ok3 = "суп" in res2a["answers"]
    checks.append(("ask('что варила мама?') → суп", ok3))

    # 4. ask("что читал папа?") → книгу
    ok4 = "книгу" in res2b["answers"]
    checks.append(("ask('что читал папа?') → книгу", ok4))

    # 5. ask("что ела корова?") → траву
    ok5 = "траву" in res3a["answers"]
    checks.append(("ask('что ела корова?') → траву", ok5))

    # 6. Абстракции из текстов (хоть одна с действием)
    has_action_abst = False
    for c in world.creatures.values():
        if not c.alive or not c.slot_options:
            continue
        action_words = {"спал", "ела", "варила", "читал", "пила"}
        if set(c.parts) & action_words and any(
            len([o for o in opts if not o.startswith("$")]) >= 2
            for opts in c.slot_options.values()
        ):
            has_action_abst = True
            break
    ok6 = has_action_abst
    checks.append(("Абстракции действий из текста", ok6))

    # 7. Точка знает новые слова (из текстов)
    dot_info = visitor.visit(".")
    dot_sibs = dot_info["siblings"] if dot_info["found"] else set()
    new_dot_words = {"суп", "книгу", "траву", "воду"} & dot_sibs
    ok7 = len(new_dot_words) >= 1
    checks.append(("Точка знает новые слова", ok7))

    passed = sum(1 for _, ok in checks if ok)
    for name, ok in checks:
        s = "+" if ok else "-"
        print(f"║  {s} {name:48s}  ║")

    print(f"╠═══════════════════════════════════════════════════════╣")
    print(f"║  Результат: {passed}/{len(checks)}                                     ║")

    alive = sum(1 for c in world.creatures.values() if c.alive)
    abst = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"║  Мир: {alive} существ, {abst} абстракций                  ║")

    if passed >= 5:
        print(f"║                                                       ║")
        print(f"║  СЫРОЙ ТЕКСТ УСВОЕН.                                 ║")
        print(f"║  Система читает новый текст, строит абстракции,      ║")
        print(f"║  отвечает на вопросы.                                 ║")
    elif passed >= 3:
        print(f"║                                                       ║")
        print(f"║  ЧАСТИЧНО. Текст усвоен, но не все связи найдены.    ║")
    else:
        print(f"║                                                       ║")
        print(f"║  НУЖНА ДОРАБОТКА.                                     ║")

    print(f"║                                                       ║")
    print(f"║  Движок НЕ менялся.                                   ║")
    print(f"╚═══════════════════════════════════════════════════════╝")

    print(f"\n  Статистика: {world.stats}")


if __name__ == "__main__":
    main()
