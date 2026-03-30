#!/usr/bin/env python3
"""
Уровень 3: Метод read() + чтение настоящего текста.

Две части:
  1. Код метода read() для добавления в World
  2. Тест: обучение с учителем → read() на настоящем тексте

read() не хардкодит правила. Он спрашивает систему через visiting:
  - "знаешь ли ты что такое пробел?" → если да, разбиваю по пробелам
  - "знаешь ли ты что такое точка?" → если да, отделяю точку от слова
  - ничего не знаешь? → подаю посимвольно
"""

from chrysaline import World, Visitor, Generator


# ════════════════════════════════════════════════════════
# КОД МЕТОДА read() — ДОБАВИТЬ В World
# ════════════════════════════════════════════════════════

def read(self, text):
    """Прочитать сырой текст, используя знания системы.

    Не хардкод. Система сама решает как разбить текст,
    основываясь на том, что она выучила о пробелах, точках и т.д.
    """
    visitor = Visitor(self)

    # Шаг 1: Знает ли система что такое пробел?
    knows_space = False
    space_info = visitor.visit(" ")
    if space_info["found"]:
        space_sibs = space_info["siblings"]
        # Пробел знает "разделяет" или "слова" или связан с "пробел"?
        if "пробел" in space_sibs or "разделяет" in space_sibs or "слова" in space_sibs:
            knows_space = True
        else:
            # Может через мост: " " → "пробел" → "разделяет"
            if "пробел" in space_sibs:
                probel_info = visitor.visit("пробел")
                if probel_info["found"]:
                    if "разделяет" in probel_info["siblings"]:
                        knows_space = True

    # Шаг 2: Знает ли система что такое точка?
    knows_dot = False
    dot_info = visitor.visit(".")
    if dot_info["found"]:
        dot_sibs = dot_info["siblings"]
        if "точка" in dot_sibs or "конец" in dot_sibs or "предложения" in dot_sibs:
            knows_dot = True
        else:
            if "точка" in dot_sibs:
                tochka_info = visitor.visit("точка")
                if tochka_info["found"]:
                    if "разделяет" in tochka_info["siblings"] or "конце" in tochka_info["siblings"]:
                        knows_dot = True

    # Шаг 3: Разбиваем текст на основе знаний
    if knows_space:
        # Система знает что пробел разделяет слова → split по пробелам
        raw_tokens = text.split(" ")
        raw_tokens = [t for t in raw_tokens if t]  # убрать пустые

        if knows_dot:
            # Система знает что точка — конец предложения
            # Отделяем точку от слова и разбиваем на предложения
            tokens = []
            for t in raw_tokens:
                if t.endswith(".") and len(t) > 1:
                    tokens.append(t[:-1])  # слово без точки
                    tokens.append(".")      # точка отдельно
                elif t == ".":
                    tokens.append(".")
                else:
                    tokens.append(t)

            # Разбиваем на предложения по точке
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

            # Подаём каждое предложение отдельно
            for sent in sentences:
                self.feed_sentence(sent)
                self.run(1)
        else:
            # Знает пробел но не точку → подаём пословно, точка приклеена
            self.feed_sentence(raw_tokens)
            self.run(1)
    else:
        # Ничего не знает → посимвольно
        chars = list(text)
        self.feed_sentence(chars)
        self.run(1)

    return {
        "knows_space": knows_space,
        "knows_dot": knows_dot,
        "mode": "sentences" if (knows_space and knows_dot) else
                "words" if knows_space else "chars"
    }


# Патчим World — добавляем метод read
World.read = read


# ════════════════════════════════════════════════════════
# ОБУЧЕНИЕ С УЧИТЕЛЕМ (уровни 1-2)
# ════════════════════════════════════════════════════════

# Уровень 1: буквы
ALPHABET = [
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

# Уровень 2: предложения и пунктуация
PUNCTUATION = [
    ["слова", "складываются", "в", "предложения"],
    ["предложение", "выражает", "мысль"],
    ["в", "конце", "предложения", "ставится", "точка"],
    ["точка", "означает", "конец", "мысли"],
    ["точка", "разделяет", "предложения"],
    ["после", "точки", "начинается", "новое", "предложение"],
    ["пробел", "разделяет", "слова"],
]

# Мосты: символ ↔ понятие
BRIDGES = [
    [".", "это", "точка"],
    [".", "означает", "конец", "предложения"],
    [" ", "это", "пробел"],
    [" ", "разделяет", "слова"],
    ["пробел", "разделяет", "слова"],
]

# Примеры предложений (учитель показывает)
SENTENCE_EXAMPLES = [
    ["кот", "спал", "это", "предложение"],
    ["мама", "мыла", "раму", "это", "предложение"],
    ["собака", "ела", "кость", "это", "предложение"],

    # Примеры с точкой
    ["кот", "спал", ".", "здесь", "точка"],
    ["мама", "мыла", "раму", ".", "здесь", "точка"],

    # Два предложения
    ["кот", "спал", ".", "собака", "ела", ".", "здесь", "два", "предложения"],
]

# Мосты для заглавных букв
CASE_BRIDGES = [
    ["Кот", "и", "кот", "это", "одно", "слово"],
    ["Собака", "и", "собака", "это", "одно", "слово"],
    ["Корова", "и", "корова", "это", "одно", "слово"],
    ["Лошадь", "и", "лошадь", "это", "одно", "слово"],
    ["Мама", "и", "мама", "это", "одно", "слово"],
    ["Папа", "и", "папа", "это", "одно", "слово"],
    ["после", "точки", "слово", "с", "большой", "буквы"],
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
    print("  УРОВЕНЬ 3: МЕТОД read() + НАСТОЯЩИЙ ТЕКСТ")
    print("  Система учится с учителем, потом читает сама.")
    print("  read() использует знания системы, не хардкод.")
    print("=" * 60)

    world = World()
    visitor = Visitor(world)
    gen = Generator(world)

    # ════════════════════════════════════════
    # ФАЗА 1: Обучение с учителем
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ФАЗА 1: ОБУЧЕНИЕ С УЧИТЕЛЕМ")
    print("=" * 60)

    teach(world, ALPHABET, "Буквы (уровень 1)")
    teach(world, PUNCTUATION, "Правила пунктуации (уровень 2)")
    teach(world, BRIDGES, "Мосты символ↔понятие", repeats=5)
    teach(world, SENTENCE_EXAMPLES, "Примеры предложений")
    teach(world, CASE_BRIDGES, "Мосты заглавных букв")

    # Проверим что система выучила
    print(f"\n  ── Проверка знаний ──")

    space_info = visitor.visit(" ")
    space_knows = False
    if space_info["found"]:
        s_sibs = space_info["siblings"]
        space_knows = "пробел" in s_sibs or "разделяет" in s_sibs or "слова" in s_sibs
        print(f"  ' ' братья: {sorted(s_sibs)[:10]}")
        print(f"  Знает что разделяет слова: {space_knows}")

    dot_info = visitor.visit(".")
    dot_knows = False
    if dot_info["found"]:
        d_sibs = dot_info["siblings"]
        dot_knows = "точка" in d_sibs or "конец" in d_sibs
        print(f"  '.' братья: {sorted(d_sibs)[:10]}")
        print(f"  Знает что это точка/конец: {dot_knows}")

    # ════════════════════════════════════════
    # ФАЗА 2: ТЕСТ read() НА ПУСТОЙ СИСТЕМЕ
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ФАЗА 2: ТЕСТ — ЧТО ДЕЛАЕТ read() ДО ОБУЧЕНИЯ?")
    print("=" * 60)

    # Создаём пустую систему — она ничего не знает
    empty_world = World()
    result_empty = empty_world.read("Кот спал. Собака ела.")
    print(f"  Пустая система:")
    print(f"    mode: {result_empty['mode']}")
    print(f"    knows_space: {result_empty['knows_space']}")
    print(f"    knows_dot: {result_empty['knows_dot']}")
    alive_empty = sum(1 for c in empty_world.creatures.values() if c.alive)
    print(f"    существ: {alive_empty}")
    print(f"    (должен быть 'chars' — система не знает пробел)")

    # ════════════════════════════════════════
    # ФАЗА 3: read() НА ОБУЧЕННОЙ СИСТЕМЕ
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ФАЗА 3: read() НА ОБУЧЕННОЙ СИСТЕМЕ")
    print("=" * 60)

    test_text = "Кот живёт в доме. Собака ест мясо. Корова даёт молоко."
    print(f"\n  Текст: \"{test_text}\"")
    print(f"  Подаём через world.read() — система сама решает как разбить.")

    result = world.read(test_text)
    print(f"\n  Результат read():")
    print(f"    mode: {result['mode']}")
    print(f"    knows_space: {result['knows_space']}")
    print(f"    knows_dot: {result['knows_dot']}")

    alive = sum(1 for c in world.creatures.values() if c.alive)
    abst = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"    Мир: {alive} существ, {abst} абстракций")

    # Повторим текст для закрепления
    for _ in range(2):
        world.read(test_text)

    # ════════════════════════════════════════
    # ФАЗА 4: ПРОВЕРКА — ПОНЯЛА ЛИ СИСТЕМА ТЕКСТ?
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ФАЗА 4: ПРОВЕРКА — ПОНЯЛА ЛИ СИСТЕМА ТЕКСТ?")
    print("=" * 60)

    checks = []

    # 1. read() выбрал правильный режим?
    ok1 = result["mode"] == "sentences"
    checks.append(("read() выбрал режим 'sentences'", ok1, f"mode={result['mode']}"))
    print(f"\n  1. Режим: {result['mode']} {'OK' if ok1 else 'MISS'}")

    # 2. ask("где живёт кот?")
    print(f"\n  2. ask('где живёт кот?')")
    res2 = gen.ask("где живёт кот?")
    ok2 = "доме" in res2["answers"] or "дом" in res2["answers"]
    checks.append(("где живёт кот? → доме", ok2, f"ответ: {res2['answers'][:5]}"))
    print(f"    Ответ: {res2['answers'][:8]}")
    print(f"    {'OK' if ok2 else 'MISS'}")

    # 3. ask("что ест собака?")
    print(f"\n  3. ask('что ест собака?')")
    res3 = gen.ask("что ест собака?")
    ok3 = "мясо" in res3["answers"]
    checks.append(("что ест собака? → мясо", ok3, f"ответ: {res3['answers'][:5]}"))
    print(f"    Ответ: {res3['answers'][:8]}")
    print(f"    {'OK' if ok3 else 'MISS'}")

    # 4. ask("что даёт корова?")
    print(f"\n  4. ask('что даёт корова?')")
    res4 = gen.ask("что даёт корова?")
    ok4 = "молоко" in res4["answers"]
    checks.append(("что даёт корова? → молоко", ok4, f"ответ: {res4['answers'][:5]}"))
    print(f"    Ответ: {res4['answers'][:8]}")
    print(f"    {'OK' if ok4 else 'MISS'}")

    # 5. ask("кто живёт в доме?")
    print(f"\n  5. ask('кто живёт в доме?')")
    res5 = gen.ask("кто живёт в доме?")
    ok5 = "кот" in res5["answers"] or "Кот" in res5["answers"] or "собака" in res5["answers"]
    checks.append(("кто живёт в доме? → кот/собака", ok5, f"ответ: {res5['answers'][:5]}"))
    print(f"    Ответ: {res5['answers'][:8]}")
    print(f"    {'OK' if ok5 else 'MISS'}")

    # 6. Абстракции — что родилось?
    print(f"\n  6. Ключевые абстракции:")
    interesting_abstractions = []
    for c in world.creatures.values():
        if not c.alive or not c.slot_options:
            continue
        parts_set = set(c.parts)
        interesting_words = {"живёт", "ест", "даёт", "."}
        if parts_set & interesting_words:
            slots = {}
            for sn, opts in c.slot_options.items():
                clean = sorted(o for o in opts if not o.startswith("$"))
                if clean:
                    slots[sn] = clean
            if slots:
                interesting_abstractions.append((c.name, slots, c.times_fed))
                print(f"    {c.name}  {slots}  fed={c.times_fed}")

    ok6 = len(interesting_abstractions) >= 2
    checks.append(("Абстракции с живёт/ест/даёт", ok6,
                    f"найдено: {len(interesting_abstractions)}"))
    print(f"    {'OK' if ok6 else 'MISS'} ({len(interesting_abstractions)} абстракций)")

    # ════════════════════════════════════════
    # ФАЗА 5: НОВЫЙ ТЕКСТ (поглощение)
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ФАЗА 5: НОВЫЙ ТЕКСТ — ПОГЛОЩЕНИЕ")
    print("=" * 60)

    new_text = "Лошадь живёт на ферме. Лошадь ест траву."
    print(f"\n  Новый текст: \"{new_text}\"")

    # Мост для заглавной
    world.feed_sentence(["Лошадь", "и", "лошадь", "это", "одно", "слово"])
    world.run(1)

    absorbed_before = world.stats["absorbed"]
    for _ in range(3):
        world.read(new_text)

    absorbed_after = world.stats["absorbed"]
    print(f"  Поглощений: {absorbed_after - absorbed_before}")

    print(f"\n  Проверка:")
    res_horse1 = gen.ask("где живёт лошадь?")
    ok_h1 = "ферме" in res_horse1["answers"] or "ферма" in res_horse1["answers"]
    print(f"    ask('где живёт лошадь?') → {res_horse1['answers'][:5]} {'OK' if ok_h1 else 'MISS'}")

    res_horse2 = gen.ask("что ест лошадь?")
    ok_h2 = "траву" in res_horse2["answers"] or "трава" in res_horse2["answers"]
    print(f"    ask('что ест лошадь?') → {res_horse2['answers'][:5]} {'OK' if ok_h2 else 'MISS'}")

    checks.append(("Новый текст: лошадь → ферме", ok_h1, f"ответ: {res_horse1['answers'][:3]}"))
    checks.append(("Новый текст: лошадь → траву", ok_h2, f"ответ: {res_horse2['answers'][:3]}"))

    # ════════════════════════════════════════
    # ФАЗА 6: ТЕКСТ ПОБОЛЬШЕ
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ФАЗА 6: ТЕКСТ ПОБОЛЬШЕ")
    print("=" * 60)

    big_text = "Кот ест рыбу. Кот ест мясо. Собака ест кость. Собака ест мясо. Корова ест траву. Лошадь ест траву."
    print(f"\n  Текст: \"{big_text[:60]}...\"")

    for _ in range(3):
        world.read(big_text)

    print(f"\n  Проверка после большого текста:")
    res_meat = gen.ask("кто ест мясо?")
    ok_meat = ("кот" in res_meat["answers"] or "Кот" in res_meat["answers"] or
               "собака" in res_meat["answers"] or "Собака" in res_meat["answers"])
    print(f"    ask('кто ест мясо?') → {res_meat['answers'][:8]} {'OK' if ok_meat else 'MISS'}")

    res_grass = gen.ask("кто ест траву?")
    ok_grass = ("корова" in res_grass["answers"] or "Корова" in res_grass["answers"] or
                "лошадь" in res_grass["answers"] or "Лошадь" in res_grass["answers"])
    print(f"    ask('кто ест траву?') → {res_grass['answers'][:8]} {'OK' if ok_grass else 'MISS'}")

    checks.append(("кто ест мясо? → кот/собака", ok_meat, f"ответ: {res_meat['answers'][:5]}"))
    checks.append(("кто ест траву? → корова/лошадь", ok_grass, f"ответ: {res_grass['answers'][:5]}"))

    # ════════════════════════════════════════
    # ИТОГ
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("╔═══════════════════════════════════════════════════════╗")
    print("║     ИТОГ: УРОВЕНЬ 3 — read() + НАСТОЯЩИЙ ТЕКСТ       ║")
    print("╠═══════════════════════════════════════════════════════╣")

    passed = 0
    for name, ok, detail in checks:
        s = "+" if ok else "-"
        if ok:
            passed += 1
        print(f"║  {s} {name:48s}  ║")

    print(f"╠═══════════════════════════════════════════════════════╣")
    print(f"║  Результат: {passed}/{len(checks)}                                     ║")
    print(f"╠═══════════════════════════════════════════════════════╣")

    alive = sum(1 for c in world.creatures.values() if c.alive)
    abst = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"║  Мир: {alive} существ, {abst} абстракций                  ║")

    if passed >= 8:
        print(f"║                                                       ║")
        print(f"║  УРОВЕНЬ 3 ПРОЙДЕН.                                  ║")
        print(f"║  Система читает настоящий текст через read().        ║")
        print(f"║  read() использует знания, не хардкод.               ║")
    elif passed >= 5:
        print(f"║                                                       ║")
        print(f"║  ЧАСТИЧНО. Основы работают.                          ║")
    else:
        print(f"║                                                       ║")
        print(f"║  НУЖНА ДОРАБОТКА.                                    ║")

    print(f"║                                                       ║")
    print(f"║  Ключевое: read() не хардкодит правила.               ║")
    print(f"║  Он спрашивает систему через visiting.                 ║")
    print(f"║  Пустая система → посимвольно.                        ║")
    print(f"║  Обученная система → по предложениям.                 ║")
    print(f"╚═══════════════════════════════════════════════════════╝")

    print(f"\n  Статистика: {world.stats}")


if __name__ == "__main__":
    main()
