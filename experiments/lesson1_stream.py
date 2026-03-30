#!/usr/bin/env python3
"""
Урок 1 (v2): Обучение + сырой текст ПОТОКОМ.

Всё то же обучение: правила, примеры, мосты.
Но сырой текст подаётся КАК ЕСТЬ — один поток символов.
Не чанки. Не предложения. Один непрерывный feed_sentence().

Текст: "Кот ел рыбу. Собака спала."
Поток: ['К','о','т',' ','е','л',' ','р','ы','б','у','.',' ','С','о','б','а','к','а',' ','с','п','а','л','а','.']

Смотрим что система сделает сама.
"""

from chrysaline import World, Visitor, Generator


# ════════════════════════════════════════════════════════
# ОБУЧЕНИЕ (то же что в lesson1)
# ════════════════════════════════════════════════════════

READING_RULES = [
    ["буквы", "складываются", "в", "слоги"],
    ["слоги", "складываются", "в", "слова"],
    ["слова", "складываются", "в", "предложения"],
    ["пробел", "разделяет", "слова"],
    ["точка", "стоит", "в", "конце", "предложения"],
    ["после", "точки", "начинается", "новое", "предложение"],
    ["точка", "разделяет", "предложения"],
    ["предложение", "выражает", "мысль"],
]

EXAMPLES_LETTERS_TO_WORDS = [
    ["к", "о", "т", "это", "слово", "кот"],
    ["е", "л", "это", "слово", "ел"],
    ["р", "ы", "б", "у", "это", "слово", "рыбу"],
    ["с", "о", "б", "а", "к", "а", "это", "слово", "собака"],
    ["с", "п", "а", "л", "а", "это", "слово", "спала"],
    ["м", "а", "м", "а", "это", "слово", "мама"],
    ["м", "ы", "л", "а", "это", "слово", "мыла"],
    ["р", "а", "м", "у", "это", "слово", "раму"],
    ["п", "а", "п", "а", "это", "слово", "папа"],
]

EXAMPLES_SENTENCES = [
    ["кот", "ел", "рыбу", "это", "предложение"],
    ["собака", "спала", "это", "предложение"],
    ["мама", "мыла", "раму", "это", "предложение"],
    ["папа", "читал", "книгу", "это", "предложение"],
]

EXAMPLES_DOT = [
    ["кот", "ел", "рыбу", ".", "здесь", "точка", "в", "конце"],
    ["собака", "спала", ".", "здесь", "точка", "в", "конце"],
    ["мама", "мыла", "раму", ".", "здесь", "точка", "в", "конце"],

    ["точка", "после", "рыбу", "значит", "конец", "предложения"],
    ["точка", "после", "спала", "значит", "конец", "предложения"],
    ["точка", "после", "раму", "значит", "конец", "предложения"],

    ["перед", "точкой", "стоит", "рыбу"],
    ["перед", "точкой", "стоит", "спала"],
    ["перед", "точкой", "стоит", "раму"],
    ["после", "точки", "стоит", "собака"],
    ["после", "точки", "стоит", "папа"],
    ["после", "точки", "стоит", "мама"],
]

BRIDGES = [
    [".", "это", "точка"],
    [" ", "это", "пробел"],
    ["пробел", "разделяет", "слова"],
    [".", "означает", "конец", "предложения"],
]

RAW_TEXT = "Кот ел рыбу. Собака спала."


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


def main():
    print("=" * 60)
    print("  УРОК 1 (v2): ОБУЧЕНИЕ + СЫРОЙ ТЕКСТ ПОТОКОМ")
    print("  Один feed_sentence() на весь текст посимвольно.")
    print("=" * 60)

    world = World()
    visitor = Visitor(world)
    generator = Generator(world)

    # ════════════════════════════════════════
    # ОБУЧЕНИЕ
    # ════════════════════════════════════════

    teach(world, READING_RULES, "Правила чтения", repeats=3)
    teach(world, EXAMPLES_LETTERS_TO_WORDS, "Буквы → слова", repeats=3)
    teach(world, EXAMPLES_SENTENCES, "Слова → предложения", repeats=3)
    teach(world, EXAMPLES_DOT, "Точка и предложения", repeats=3)
    teach(world, BRIDGES, "Мосты (символ↔понятие)", repeats=5)

    print(f"\n{'='*60}")
    print("  СРЕЗ ДО ПОДАЧИ ТЕКСТА")
    print("=" * 60)

    # Что знает система до текста
    for word in [".", "точка", " ", "пробел"]:
        info = visitor.visit(word)
        if info["found"]:
            print(f"  '{word}' братья: {sorted(info['siblings'])[:10]}")

    # ════════════════════════════════════════
    # СЫРОЙ ТЕКСТ ПОТОКОМ
    # ════════════════════════════════════════

    stream = list(RAW_TEXT)
    print(f"\n{'='*60}")
    print(f"  ПОДАЧА ПОТОКОМ")
    print(f"  Текст: \"{RAW_TEXT}\"")
    print(f"  Поток ({len(stream)} символов): {stream}")
    print(f"  Один feed_sentence() на весь поток.")
    print("=" * 60)

    for r in range(5):
        world.feed_sentence(stream)
        world.run(1)

    alive = sum(1 for c in world.creatures.values() if c.alive)
    abst = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"\n  После подачи: {alive} существ, {abst} абстракций")

    # ════════════════════════════════════════
    # НАБЛЮДЕНИЕ: что произошло?
    # ════════════════════════════════════════

    print(f"\n{'='*60}")
    print("  НАБЛЮДЕНИЕ")
    print("=" * 60)

    # ── 1. Что видит точка "."? ──
    print(f"\n  ── 1. Символ '.' после потока ──")
    dot = visitor.visit(".")
    if dot["found"]:
        print(f"    братья: {sorted(dot['siblings'])[:20]}")
        mates = sorted(dot.get("slot_mates", set()))[:15]
        if mates:
            print(f"    slot_mates: {mates}")
        rules = dot.get("rules", [])
        for rule in rules[:5]:
            opts = sorted(rule.get("options", set()))[:8]
            if opts:
                print(f"    правило: {rule['pattern']} → {opts}")

    # ── 2. Что видит пробел " "? ──
    print(f"\n  ── 2. Символ ' ' после потока ──")
    space = visitor.visit(" ")
    if space["found"]:
        print(f"    братья: {sorted(space['siblings'])[:20]}")
        mates = sorted(space.get("slot_mates", set()))[:15]
        if mates:
            print(f"    slot_mates: {mates}")

    # ── 3. Все организмы с "." ──
    print(f"\n  ── 3. Организмы с '.' (что точка склеила) ──")
    dot_orgs = []
    for c in world.creatures.values():
        if not c.alive or c.complexity < 2:
            continue
        if "." in c.parts:
            dot_orgs.append(c)
    dot_orgs.sort(key=lambda c: (-c.times_fed, -c.energy))
    for c in dot_orgs[:20]:
        slots = ""
        if c.slot_options:
            for sn, opts in c.slot_options.items():
                clean = sorted(o for o in opts if not o.startswith("$"))
                if clean:
                    slots += f" {sn}={clean}"
        print(f"    {c.name:45s} fed={c.times_fed:3d} e={c.energy:.1f}{slots}")

    # ── 4. Все организмы с " " (пробел) ──
    print(f"\n  ── 4. Организмы с ' ' (что пробел склеил, top-15) ──")
    sp_orgs = []
    for c in world.creatures.values():
        if not c.alive or c.complexity < 2:
            continue
        if " " in c.parts:
            sp_orgs.append(c)
    sp_orgs.sort(key=lambda c: (-c.times_fed, -c.energy))
    for c in sp_orgs[:15]:
        slots = ""
        if c.slot_options:
            for sn, opts in c.slot_options.items():
                clean = sorted(o for o in opts if not o.startswith("$"))
                if clean:
                    slots += f" {sn}={clean}"
        print(f"    {c.name:45s} fed={c.times_fed:3d} e={c.energy:.1f}{slots}")

    # ── 5. Абстракции из потока ──
    print(f"\n  ── 5. Абстракции с символами из текста ──")
    text_chars = set(stream)
    all_abst = world.show_abstractions()
    count = 0
    for c in all_abst:
        if not (set(c.parts) & text_chars):
            continue
        slots = {}
        for sn, opts in c.slot_options.items():
            clean = sorted(o for o in opts if not o.startswith("$"))
            if clean:
                slots[sn] = clean
        if slots:
            print(f"    {c.name:45s} {slots}  fed={c.times_fed}")
            count += 1
            if count >= 25:
                break

    # ── 6. Сравнение: точка vs буква vs пробел ──
    print(f"\n  ── 6. Сравнение символов ──")
    for char in [".", " ", "у", "а", "о", "К", "С"]:
        cr = world._find_by_parts((char,))
        if cr:
            orgs = sum(1 for c in world.creatures.values()
                       if c.alive and c.complexity >= 2 and char in c.parts)
            absts = sum(1 for c in world.creatures.values()
                        if c.alive and c.slot_options and char in c.parts)
            print(f"    '{char}': energy={cr.energy:5.1f}  fed={cr.times_fed:3d}  "
                  f"в {orgs:3d} орг  {absts:2d} абстр")

    # ── 7. Цепочки ──
    print(f"\n  ── 7. Цепочки через мосты ──")

    # . → точка → правила
    dot_info = visitor.visit(".")
    dot_sibs = dot_info["siblings"] if dot_info["found"] else set()
    knows_tochka = "точка" in dot_sibs
    print(f"    '.' знает 'точка': {knows_tochka}")
    if knows_tochka:
        t_info = visitor.visit("точка")
        t_sibs = t_info["siblings"] if t_info["found"] else set()
        for w in ["конце", "разделяет", "предложения", "после"]:
            print(f"      'точка' знает '{w}': {w in t_sibs}")

    # " " → пробел → разделяет слова
    sp_info = visitor.visit(" ")
    sp_sibs = sp_info["siblings"] if sp_info["found"] else set()
    knows_probel = "пробел" in sp_sibs
    print(f"    ' ' знает 'пробел': {knows_probel}")
    if knows_probel:
        p_info = visitor.visit("пробел")
        p_sibs = p_info["siblings"] if p_info["found"] else set()
        for w in ["разделяет", "слова"]:
            print(f"      'пробел' знает '{w}': {w in p_sibs}")

    # ── 8. Контекст точки: что ПЕРЕД и ПОСЛЕ ──
    print(f"\n  ── 8. Контекст точки в потоке ──")
    # Ищем организмы типа X·. и .·Y
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

    # Ищем организмы X·" " и " "·Y
    print(f"\n  ── 9. Контекст пробела в потоке ──")
    before_sp = set()
    after_sp = set()
    for c in world.creatures.values():
        if not c.alive or c.complexity != 2:
            continue
        if c.parts[1] == " ":
            before_sp.add(c.parts[0])
        if c.parts[0] == " ":
            after_sp.add(c.parts[1])
    print(f"    X·' ' (перед пробелом): {sorted(before_sp)}")
    print(f"    ' '·Y (после пробела):  {sorted(after_sp)}")

    # ── 10. Абстракции "перед точкой" из обучения — обновились? ──
    print(f"\n  ── 10. Абстракция 'перед·точкой·стоит·$0' ──")
    for c in world.creatures.values():
        if not c.alive or not c.slot_options:
            continue
        if "перед" in c.parts and "точкой" in c.parts:
            for sn, opts in c.slot_options.items():
                clean = sorted(o for o in opts if not o.startswith("$"))
                if clean:
                    print(f"    {c.name} → {sn}={clean}  fed={c.times_fed}")

    print(f"\n  ── 11. Абстракция 'после·точки·стоит·$0' ──")
    for c in world.creatures.values():
        if not c.alive or not c.slot_options:
            continue
        if "после" in c.parts and "точки" in c.parts and "стоит" in c.parts:
            for sn, opts in c.slot_options.items():
                clean = sorted(o for o in opts if not o.startswith("$"))
                if clean:
                    print(f"    {c.name} → {sn}={clean}  fed={c.times_fed}")

    # ── 11. ask() ──
    print(f"\n  ── 12. ask() — что система может ответить? ──")
    questions = [
        "что стоит перед точкой?",
        "что стоит после точки?",
        "что означает точка?",
        "что разделяет пробел?",
    ]
    for q in questions:
        res = generator.ask(q)
        print(f"    ask('{q}')")
        print(f"      → {res['answers'][:8]}")
        if res['reasoning']:
            print(f"      логика: {res['reasoning'][:2]}")

    # ════════════════════════════════════════
    # ИТОГ
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ИТОГ")
    print("=" * 60)
    print(f"  Мир: {alive} существ, {abst} абстракций")
    print(f"  Статистика: {world.stats}")


if __name__ == "__main__":
    main()
