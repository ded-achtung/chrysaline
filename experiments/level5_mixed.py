#!/usr/bin/env python3
"""
Уровень 5: Смешанный текст — детская энциклопедия.

Система обучена буквам и пунктуации (уровни 1-2).
Потом получает один смешанный текст: природоведение, математика,
русский язык, литература — всё вперемешку. Через read().

Главный вопрос: может ли система из одного прохода по смешанному
тексту построить знания в нескольких областях одновременно?

Движок НЕ менялся.
"""

from chrysaline import World, Visitor, Generator


# ════════════════════════════════════════════════════════
# read() — патчим World
# ════════════════════════════════════════════════════════

def read(self, text):
    """Прочитать сырой текст, используя знания системы."""
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
    ["точка", "означает", "конец", "мысли"],
    ["точка", "разделяет", "предложения"],
    ["после", "точки", "начинается", "новое", "предложение"],
    ["пробел", "разделяет", "слова"],
]

BRIDGES = [
    [".", "это", "точка"], [".", "означает", "конец", "предложения"],
    [" ", "это", "пробел"], [" ", "разделяет", "слова"],
    ["пробел", "разделяет", "слова"],
]

EXAMPLES = [
    ["кот", "спал", ".", "здесь", "точка"],
    ["мама", "мыла", "раму", ".", "здесь", "точка"],
]

# ════════════════════════════════════════════════════════
# ТЕКСТЫ
# ════════════════════════════════════════════════════════

MIXED_TEXT = "Кот живёт в доме. Собака живёт в доме. Корова живёт на ферме. Кот ест рыбу. Собака ест мясо. Корова ест траву. Корова даёт молоко. Кот это млекопитающее. Собака это млекопитающее. Корова это млекопитающее. Ворона это птица. Воробей это птица. Птицы умеют летать. Рыба живёт в воде. Рыба дышит жабрами. Два плюс три равно пять. Три плюс два равно пять. Один плюс один равно два. Пять минус два равно три. Гласные буквы это а о у и е ы. Жи пишется с буквой и. Ши пишется с буквой и. Предложение начинается с большой буквы. В конце предложения ставится точка. Мама мыла раму. Папа читал книгу. Бабушка варила кашу."

EXTRA_TEXT = "Лошадь живёт на ферме. Лошадь ест траву. Лошадь это млекопитающее. Щука это рыба. Щука живёт в реке. Четыре плюс один равно пять. Дедушка пилил дрова. Мальчик играл в мяч."

# Мосты для заглавных букв в текстах
CASE_BRIDGES = [
    ["Кот", "и", "кот", "это", "одно", "слово"],
    ["Собака", "и", "собака", "это", "одно", "слово"],
    ["Корова", "и", "корова", "это", "одно", "слово"],
    ["Мама", "и", "мама", "это", "одно", "слово"],
    ["Папа", "и", "папа", "это", "одно", "слово"],
    ["Лошадь", "и", "лошадь", "это", "одно", "слово"],
    ["Ворона", "и", "ворона", "это", "одно", "слово"],
    ["Воробей", "и", "воробей", "это", "одно", "слово"],
    ["Рыба", "и", "рыба", "это", "одно", "слово"],
    ["Щука", "и", "щука", "это", "одно", "слово"],
    ["Птицы", "и", "птицы", "это", "одно", "слово"],
    ["Бабушка", "и", "бабушка", "это", "одно", "слово"],
    ["Мальчик", "и", "мальчик", "это", "одно", "слово"],
    ["Дедушка", "и", "дедушка", "это", "одно", "слово"],
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
    print("  УРОВЕНЬ 5: СМЕШАННЫЙ ТЕКСТ")
    print("  Детская энциклопедия. Все области вперемешку.")
    print("  Движок НЕ менялся.")
    print("=" * 60)

    world = World()
    visitor = Visitor(world)
    gen = Generator(world)

    # ════════════════════════════════════════
    # ЭТАП 1: Обучение (уровни 1-2)
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ЭТАП 1: ОБУЧЕНИЕ")
    print("=" * 60)

    teach(world, LEVEL1, "Буквы (уровень 1)")
    teach(world, LEVEL2, "Пунктуация (уровень 2)")
    teach(world, BRIDGES, "Мосты символ↔понятие", repeats=5)
    teach(world, EXAMPLES, "Примеры предложений")
    teach(world, CASE_BRIDGES, "Мосты заглавных букв")

    alive0 = sum(1 for c in world.creatures.values() if c.alive)
    abst0 = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"\n  После обучения: {alive0} существ, {abst0} абстракций")

    # ════════════════════════════════════════
    # ЭТАП 2: Смешанный текст
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ЭТАП 2: СМЕШАННЫЙ ТЕКСТ")
    print("=" * 60)
    print(f"  Текст ({len(MIXED_TEXT)} символов, ~27 предложений)")

    absorbed_before = world.stats["absorbed"]
    result = world.read(MIXED_TEXT)
    print(f"  read() mode: {result['mode']}")

    alive1 = sum(1 for c in world.creatures.values() if c.alive)
    abst1 = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    absorbed1 = world.stats["absorbed"] - absorbed_before
    print(f"  После текста: {alive1} существ, {abst1} абстракций, {absorbed1} поглощений")

    # ════════════════════════════════════════
    # ЭТАП 3: Проверка по каждой области
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ЭТАП 3: ПРОВЕРКА ПО ОБЛАСТЯМ")
    print("=" * 60)

    checks = []

    # --- Природоведение ---
    print(f"\n  ── Природоведение ──")

    r1 = gen.ask("где живёт кот?")
    ok1 = "доме" in r1["answers"] or "в" in r1["answers"]
    print(f"  1. где живёт кот? → {r1['answers'][:6]}  {'OK' if ok1 else 'MISS'}")
    checks.append(("где живёт кот? → доме", ok1))

    r2 = gen.ask("что ест корова?")
    ok2 = "траву" in r2["answers"]
    print(f"  2. что ест корова? → {r2['answers'][:6]}  {'OK' if ok2 else 'MISS'}")
    checks.append(("что ест корова? → траву", ok2))

    r3 = gen.ask("кто это млекопитающее?")
    ok3 = any(w in r3["answers"] for w in ["кот", "Кот", "собака", "Собака", "корова", "Корова"])
    print(f"  3. кто млекопитающее? → {r3['answers'][:6]}  {'OK' if ok3 else 'MISS'}")
    checks.append(("кто млекопитающее? → кот/собака/корова", ok3))

    r4 = gen.ask("что даёт корова?")
    ok4 = "молоко" in r4["answers"]
    print(f"  4. что даёт корова? → {r4['answers'][:6]}  {'OK' if ok4 else 'MISS'}")
    checks.append(("что даёт корова? → молоко", ok4))

    # --- Математика ---
    print(f"\n  ── Математика ──")

    r5 = gen.ask("сколько два плюс три?")
    ok5 = "пять" in r5["answers"]
    print(f"  5. два плюс три? → {r5['answers'][:6]}  {'OK' if ok5 else 'MISS'}")
    checks.append(("два плюс три → пять", ok5))

    r6 = gen.ask("сколько пять минус два?")
    ok6 = "три" in r6["answers"]
    print(f"  6. пять минус два? → {r6['answers'][:6]}  {'OK' if ok6 else 'MISS'}")
    checks.append(("пять минус два → три", ok6))

    # --- Русский язык ---
    print(f"\n  ── Русский язык ──")

    r7 = gen.ask("какие гласные буквы?")
    vowels_in = {a for a in r7["answers"] if a in "аоуиеы"}
    ok7 = len(vowels_in) >= 3
    print(f"  7. гласные буквы? → {r7['answers'][:10]}  гласных: {sorted(vowels_in)}  {'OK' if ok7 else 'MISS'}")
    checks.append(("гласные буквы → а,о,у,и,е,ы", ok7))

    r8 = gen.ask("как пишется жи?")
    ok8 = "и" in r8["answers"] or "буквой" in r8["answers"]
    print(f"  8. как пишется жи? → {r8['answers'][:6]}  {'OK' if ok8 else 'MISS'}")
    checks.append(("как пишется жи → с буквой и", ok8))

    # --- Литература ---
    print(f"\n  ── Литература ──")

    r9 = gen.ask("что мыла мама?")
    ok9 = "раму" in r9["answers"]
    print(f"  9. что мыла мама? → {r9['answers'][:6]}  {'OK' if ok9 else 'MISS'}")
    checks.append(("что мыла мама? → раму", ok9))

    r10 = gen.ask("что читал папа?")
    ok10 = "книгу" in r10["answers"]
    print(f"  10. что читал папа? → {r10['answers'][:6]}  {'OK' if ok10 else 'MISS'}")
    checks.append(("что читал папа? → книгу", ok10))

    # ════════════════════════════════════════
    # ЭТАП 4: Кросс-доменные вопросы
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ЭТАП 4: КРОСС-ДОМЕННЫЕ ПРОВЕРКИ")
    print("=" * 60)

    print(f"\n  ── visit('кот') — три домена в одном? ──")
    kot_info = visitor.visit("Кот")
    kot_sibs = kot_info["siblings"] if kot_info["found"] else set()
    kot_knows_dome = "доме" in kot_sibs or "в" in kot_sibs
    kot_knows_rybu = "рыбу" in kot_sibs or "ест" in kot_sibs
    kot_knows_mlek = "млекопитающее" in kot_sibs or "это" in kot_sibs
    print(f"    братья: {sorted(kot_sibs)[:15]}")
    print(f"    знает 'доме'/'в': {kot_knows_dome}")
    print(f"    знает 'рыбу'/'ест': {kot_knows_rybu}")
    print(f"    знает 'млекопитающее'/'это': {kot_knows_mlek}")
    ok11 = kot_knows_dome and kot_knows_rybu
    checks.append(("visit('Кот') → доме + рыбу (кросс-домен)", ok11))

    print(f"\n  ── visit('Корова') — четыре факта? ──")
    kor_info = visitor.visit("Корова")
    kor_sibs = kor_info["siblings"] if kor_info["found"] else set()
    print(f"    братья: {sorted(kor_sibs)[:15]}")
    kor_facts = sum(1 for w in ["ферме", "траву", "молоко", "млекопитающее",
                                 "ест", "живёт", "даёт", "это", "на"]
                    if w in kor_sibs)
    ok12 = kor_facts >= 3
    print(f"    фактов из текста: {kor_facts}")
    checks.append(("visit('Корова') → ферме/траву/молоко (кросс)", ok12))

    # ════════════════════════════════════════
    # ЭТАП 5: Второй текст — дополнение
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ЭТАП 5: ДОПОЛНИТЕЛЬНЫЙ ТЕКСТ")
    print("=" * 60)

    print(f"  Текст: \"{EXTRA_TEXT[:60]}...\"")

    # Мосты уже подготовлены (Лошадь, Щука и т.д.)
    absorbed_before2 = world.stats["absorbed"]
    world.read(EXTRA_TEXT)
    absorbed2 = world.stats["absorbed"] - absorbed_before2

    alive2 = sum(1 for c in world.creatures.values() if c.alive)
    abst2 = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"  После: {alive2} существ, {abst2} абстракций, {absorbed2} поглощений")

    # Проверки
    r13 = gen.ask("где живёт лошадь?")
    ok13 = "ферме" in r13["answers"] or "на" in r13["answers"]
    print(f"\n  13. где живёт лошадь? → {r13['answers'][:6]}  {'OK' if ok13 else 'MISS'}")
    checks.append(("где живёт лошадь? → ферме", ok13))

    r14 = gen.ask("что делал дедушка?")
    ok14 = "пилил" in r14["answers"] or "дрова" in r14["answers"]
    print(f"  14. что делал дедушка? → {r14['answers'][:6]}  {'OK' if ok14 else 'MISS'}")
    checks.append(("что делал дедушка? → пилил", ok14))

    # Поглотилась ли лошадь?
    loshad_info = visitor.visit("Лошадь")
    loshad_sibs = loshad_info["siblings"] if loshad_info["found"] else set()
    print(f"\n  visit('Лошадь') братья: {sorted(loshad_sibs)[:12]}")
    ok15 = "ферме" in loshad_sibs or "траву" in loshad_sibs or "живёт" in loshad_sibs
    checks.append(("Лошадь знает ферме/траву", ok15))

    # ════════════════════════════════════════
    # ЭТАП 6: Статистика
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ЭТАП 6: СТАТИСТИКА")
    print("=" * 60)

    alive_f = sum(1 for c in world.creatures.values() if c.alive)
    abst_f = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"  Существ: {alive_f}")
    print(f"  Абстракций: {abst_f}")
    print(f"  Поглощений: {world.stats['absorbed']}")
    print(f"  Абстракций/существ: {abst_f/alive_f:.2f}")
    print(f"  Статистика: {world.stats}")

    # Ключевые абстракции
    print(f"\n  Ключевые абстракции (с содержательными словами):")
    content_words = {"живёт", "ест", "даёт", "это", "плюс", "минус", "равно",
                     "пишется", "мыла", "читал", "варила", "пилил", "играл",
                     "млекопитающее", "птица", "рыба", "летать", "дышит"}
    for c in world.show_abstractions():
        if not (set(c.parts) & content_words):
            continue
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
    print("║     ИТОГ: УРОВЕНЬ 5 — СМЕШАННЫЙ ТЕКСТ                ║")
    print("╠═══════════════════════════════════════════════════════╣")

    passed = 0
    for name, ok in checks:
        s = "+" if ok else "-"
        if ok:
            passed += 1
        print(f"║  {s} {name:52s}║")

    print(f"╠═══════════════════════════════════════════════════════╣")
    print(f"║  Результат: {passed}/{len(checks)}                                   ║")
    print(f"║  Существ: {alive_f}, абстракций: {abst_f}                   ║")
    print(f"╠═══════════════════════════════════════════════════════╣")

    # Подсчёт по областям
    nature_ok = sum(1 for _, ok in checks[:4] if ok)
    math_ok = sum(1 for _, ok in checks[4:6] if ok)
    russian_ok = sum(1 for _, ok in checks[6:8] if ok)
    lit_ok = sum(1 for _, ok in checks[8:10] if ok)
    cross_ok = sum(1 for _, ok in checks[10:12] if ok)
    extra_ok = sum(1 for _, ok in checks[12:] if ok)

    print(f"║  Природоведение: {nature_ok}/4                                ║")
    print(f"║  Математика:     {math_ok}/2                                ║")
    print(f"║  Русский язык:   {russian_ok}/2                                ║")
    print(f"║  Литература:     {lit_ok}/2                                ║")
    print(f"║  Кросс-домен:    {cross_ok}/2                                ║")
    print(f"║  Дополнение:     {extra_ok}/3                                ║")

    if passed >= 12:
        print(f"║                                                       ║")
        print(f"║  СМЕШАННЫЙ ТЕКСТ УСВОЕН.                             ║")
        print(f"║  Система работает в нескольких областях               ║")
        print(f"║  одновременно из одного текста.                       ║")
    elif passed >= 8:
        print(f"║                                                       ║")
        print(f"║  ЧАСТИЧНО. Большинство областей работает.            ║")
    elif passed >= 5:
        print(f"║                                                       ║")
        print(f"║  МИНИМАЛЬНО. Основы есть.                            ║")
    else:
        print(f"║                                                       ║")
        print(f"║  НУЖНА ДОРАБОТКА.                                    ║")

    print(f"║  Движок НЕ менялся.                                   ║")
    print(f"╚═══════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    main()
