#!/usr/bin/env python3
"""
Уровень 1: Буквы → Слоги → Слова.

Учитель ведёт систему как ребёнка в первом классе.
Последовательно, шаг за шагом. Каждый уровень строится на предыдущем.

Этап 1: Буквы (алфавит, гласные/согласные)
Этап 2: Слоги (буквы складываются в слоги)
Этап 3: Слова (слоги складываются в слова)
Этап 4: Проверка — может ли система разобрать новое слово?

Движок НЕ менялся.
"""

from chrysaline import World, Visitor, Generator


# ════════════════════════════════════════════════════════
# ЭТАП 1: БУКВЫ
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

# ════════════════════════════════════════════════════════
# ЭТАП 2: СЛОГИ
# ════════════════════════════════════════════════════════

SYLLABLE_RULES = [
    ["согласная", "и", "гласная", "образуют", "слог"],
    ["слог", "это", "часть", "слова"],
    ["в", "каждом", "слоге", "одна", "гласная"],
]

# Учитель показывает конкретные слоги
SYLLABLE_EXAMPLES = [
    ["м", "и", "а", "это", "слог", "ма"],
    ["к", "и", "о", "это", "слог", "ко"],
    ["т", "и", "а", "это", "слог", "та"],
    ["н", "и", "а", "это", "слог", "на"],
    ["р", "и", "а", "это", "слог", "ра"],
    ["м", "и", "у", "это", "слог", "му"],
    ["л", "и", "о", "это", "слог", "ло"],
    ["к", "и", "а", "это", "слог", "ка"],
    ["с", "и", "о", "это", "слог", "со"],
    ["б", "и", "а", "это", "слог", "ба"],
    ["р", "и", "у", "это", "слог", "ру"],
    ["п", "и", "а", "это", "слог", "па"],
    ["д", "и", "о", "это", "слог", "до"],
    ["м", "и", "о", "это", "слог", "мо"],
    ["р", "и", "ы", "это", "слог", "ры"],
]

# ════════════════════════════════════════════════════════
# ЭТАП 3: СЛОВА
# ════════════════════════════════════════════════════════

WORD_RULES = [
    ["слоги", "складываются", "в", "слова"],
    ["слово", "состоит", "из", "слогов"],
]

# Учитель показывает: слоги → слово
WORD_EXAMPLES = [
    # ма + ма = мама
    ["слог", "ма", "и", "слог", "ма", "это", "слово", "мама"],
    ["ма", "ма", "это", "мама"],

    # ко + т = кот (т — один согласный, не слог)
    ["ко", "и", "т", "это", "слово", "кот"],

    # ры + ба = рыба
    ["слог", "ры", "и", "слог", "ба", "это", "слово", "рыба"],
    ["ры", "ба", "это", "рыба"],

    # мо + ло + ко = молоко
    ["слог", "мо", "и", "слог", "ло", "и", "слог", "ко", "это", "слово", "молоко"],
    ["мо", "ло", "ко", "это", "молоко"],

    # ра + ма = рама
    ["ра", "ма", "это", "рама"],

    # ру + ка = рука
    ["ру", "ка", "это", "рука"],

    # со + ба + ка = собака
    ["со", "ба", "ка", "это", "собака"],

    # до + ма = дома
    ["до", "ма", "это", "дома"],

    # па + па = папа
    ["па", "па", "это", "папа"],

    # на + со + с = насос (учитель показывает)
    ["на", "со", "с", "это", "насос"],

    # му + ка = мука
    ["му", "ка", "это", "мука"],
]

# Учитель связывает буквы с конкретными словами
LETTER_WORD_BRIDGES = [
    # кот: к + о + т
    ["в", "слове", "кот", "буквы", "к", "о", "т"],
    ["кот", "начинается", "с", "буквы", "к"],

    # мама: м + а + м + а
    ["в", "слове", "мама", "буквы", "м", "а", "м", "а"],
    ["мама", "начинается", "с", "буквы", "м"],

    # рыба: р + ы + б + а
    ["в", "слове", "рыба", "буквы", "р", "ы", "б", "а"],
    ["рыба", "начинается", "с", "буквы", "р"],

    # собака: с + о + б + а + к + а
    ["собака", "начинается", "с", "буквы", "с"],
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
    return alive, abst


def main():
    print("=" * 60)
    print("  УРОВЕНЬ 1: БУКВЫ → СЛОГИ → СЛОВА")
    print("  Как в первом классе. Шаг за шагом.")
    print("  Движок НЕ менялся.")
    print("=" * 60)

    world = World()
    visitor = Visitor(world)
    gen = Generator(world)

    # ════════════════════════════════════════
    # ЭТАП 1: Буквы
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ЭТАП 1: БУКВЫ")
    print("=" * 60)

    teach(world, ALPHABET_VOWELS, "Гласные буквы", repeats=3)
    teach(world, ALPHABET_CONSONANTS, "Согласные буквы", repeats=3)

    # Проверка: система знает гласные?
    vowels = visitor.query_category("гласная")
    vowels_clean = {v for v in vowels if len(v) == 1}
    print(f"\n  Проверка: гласные буквы = {sorted(vowels_clean)}")

    consonants = visitor.query_category("согласная")
    consonants_clean = {v for v in consonants if len(v) == 1}
    print(f"  Проверка: согласные буквы = {sorted(consonants_clean)}")

    ok_vowels = {"а", "о", "у", "и", "е", "ы"}.issubset(vowels_clean)
    ok_consonants = {"к", "т", "м", "н", "р"}.issubset(consonants_clean)
    print(f"  Гласные усвоены: {ok_vowels}")
    print(f"  Согласные усвоены: {ok_consonants}")

    # ════════════════════════════════════════
    # ЭТАП 2: Слоги
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ЭТАП 2: СЛОГИ")
    print("=" * 60)

    teach(world, SYLLABLE_RULES, "Правила слогов", repeats=3)
    teach(world, SYLLABLE_EXAMPLES, "Примеры слогов", repeats=3)

    # Проверка: система знает слоги?
    print(f"\n  Проверка: что знает 'слог'?")
    slog_info = visitor.visit("слог")
    if slog_info["found"]:
        print(f"    братья: {sorted(slog_info['siblings'])[:15]}")
        mates = sorted(slog_info.get("slot_mates", set()))[:15]
        if mates:
            print(f"    заменяемые: {mates}")

    # Проверка: ма — это слог?
    print(f"\n  Проверка: visit('ма')")
    ma_info = visitor.visit("ма")
    if ma_info["found"]:
        print(f"    братья: {sorted(ma_info['siblings'])[:12]}")
        print(f"    заменяемые: {sorted(ma_info.get('slot_mates', set()))[:12]}")
        ma_knows_slog = "слог" in ma_info["siblings"]
        print(f"    'ма' знает 'слог': {ma_knows_slog}")
    else:
        print(f"    'ма' не найдена")
        ma_knows_slog = False

    # Какие слоги система знает?
    print(f"\n  Абстракции со 'слог':")
    for c in world.creatures.values():
        if not c.alive or not c.slot_options:
            continue
        if "слог" in c.parts or "это" in c.parts:
            has_syllable = any(
                p in {"ма", "ко", "та", "на", "ра", "му", "ло", "ка", "со", "ба", "ру", "па", "до", "мо", "ры"}
                for sn, opts in c.slot_options.items()
                for p in opts if not p.startswith("$")
            )
            if has_syllable:
                for sn, opts in c.slot_options.items():
                    clean = sorted(o for o in opts if not o.startswith("$"))
                    if clean:
                        print(f"    {c.name}  {sn}={clean[:15]}  fed={c.times_fed}")

    # Абстракция $0·это·слог·$1 — связь буквы→слог?
    print(f"\n  Абстракции '$0 это слог $1':")
    for c in world.creatures.values():
        if not c.alive or not c.slot_options:
            continue
        if "это" in c.parts and "слог" in c.parts:
            slots = {}
            for sn, opts in c.slot_options.items():
                clean = sorted(o for o in opts if not o.startswith("$"))
                if clean:
                    slots[sn] = clean
            if slots:
                print(f"    {c.name}  {slots}  fed={c.times_fed}")

    # ════════════════════════════════════════
    # ЭТАП 3: Слова
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ЭТАП 3: СЛОВА")
    print("=" * 60)

    teach(world, WORD_RULES, "Правила слов", repeats=3)
    teach(world, WORD_EXAMPLES, "Примеры слов", repeats=3)
    teach(world, LETTER_WORD_BRIDGES, "Мосты буква↔слово", repeats=3)

    # Проверка: мама, кот, рыба — известны?
    print(f"\n  Проверка: что знает 'мама'?")
    mama_info = visitor.visit("мама")
    if mama_info["found"]:
        print(f"    братья: {sorted(mama_info['siblings'])[:12]}")
        print(f"    заменяемые: {sorted(mama_info.get('slot_mates', set()))[:10]}")

    print(f"\n  Проверка: что знает 'кот'?")
    kot_info = visitor.visit("кот")
    if kot_info["found"]:
        print(f"    братья: {sorted(kot_info['siblings'])[:12]}")

    print(f"\n  Проверка: что знает 'рыба'?")
    ryba_info = visitor.visit("рыба")
    if ryba_info["found"]:
        print(f"    братья: {sorted(ryba_info['siblings'])[:12]}")

    # Связь слово↔буква: кот знает к?
    print(f"\n  Проверка: связь слово↔буква")
    for word_name in ["кот", "мама", "рыба"]:
        info = visitor.visit(word_name)
        if info["found"]:
            letters_in_sibs = [s for s in info["siblings"] if len(s) == 1]
            print(f"    '{word_name}' знает буквы: {sorted(letters_in_sibs)}")

    # Абстракции слов
    print(f"\n  Абстракции со 'слово':")
    for c in world.creatures.values():
        if not c.alive or not c.slot_options:
            continue
        if "слово" in c.parts:
            slots = {}
            for sn, opts in c.slot_options.items():
                clean = sorted(o for o in opts if not o.startswith("$"))
                if clean:
                    slots[sn] = clean
            if slots:
                print(f"    {c.name}  {slots}  fed={c.times_fed}")

    # Абстракции слогов→слов: $0·$1·это·$2
    print(f"\n  Абстракции 'слоги → слово' ($0·$1·это·слово·$2):")
    for c in world.creatures.values():
        if not c.alive or not c.slot_options:
            continue
        if "это" in c.parts:
            has_words = False
            slots = {}
            for sn, opts in c.slot_options.items():
                clean = sorted(o for o in opts if not o.startswith("$"))
                if clean:
                    slots[sn] = clean
                    if any(w in clean for w in ["мама", "рыба", "рука", "рама", "мука", "собака", "молоко", "кот", "папа"]):
                        has_words = True
            if has_words and slots:
                print(f"    {c.name}  {slots}  fed={c.times_fed}")

    # ════════════════════════════════════════
    # ЭТАП 4: УПРАЖНЕНИЯ
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ЭТАП 4: УПРАЖНЕНИЯ")
    print("=" * 60)

    checks = []

    # Упражнение 1: Найди гласные в слове МОЛОКО
    print(f"\n  ── Упражнение 1: Найди гласные в МОЛОКО ──")
    vowels_now = visitor.query_category("гласная")
    vowels_now_clean = {v for v in vowels_now if len(v) == 1}
    found_vowels = [ch for ch in "молоко" if ch in vowels_now_clean]
    ok1 = found_vowels == ["о", "о", "о"]
    checks.append(("Гласные в МОЛОКО", ok1, f"нашли: {found_vowels}"))
    print(f"    Гласные: {sorted(vowels_now_clean)}")
    print(f"    В 'молоко': {found_vowels}")
    print(f"    {'OK' if ok1 else 'MISS'}")

    # Упражнение 2: Сколько слогов в РЫБА?
    print(f"\n  ── Упражнение 2: Сколько слогов в РЫБА? ──")
    found_vowels_2 = [ch for ch in "рыба" if ch in vowels_now_clean]
    n_syllables = len(found_vowels_2)
    ok2 = n_syllables == 2
    checks.append(("Слоги в РЫБА", ok2, f"гласных: {n_syllables}"))
    print(f"    Гласные в 'рыба': {found_vowels_2}")
    print(f"    Слогов: {n_syllables}")
    print(f"    {'OK' if ok2 else 'MISS'}")

    # Упражнение 3: Из каких слогов состоит МАМА?
    print(f"\n  ── Упражнение 3: Из каких слогов МАМА? ──")
    mama_visit = visitor.visit("мама")
    mama_sibs = mama_visit["siblings"] if mama_visit["found"] else set()
    mama_mates = mama_visit.get("slot_mates", set()) if mama_visit["found"] else set()
    knows_ma = "ма" in mama_sibs
    ok3 = knows_ma
    checks.append(("Слоги в МАМА", ok3, f"знает 'ма': {knows_ma}"))
    print(f"    'мама' братья: {sorted(mama_sibs)[:10]}")
    print(f"    Знает 'ма': {knows_ma}")
    print(f"    {'OK' if ok3 else 'MISS'}")

    # Упражнение 4: Какая первая буква в КОТ?
    print(f"\n  ── Упражнение 4: Первая буква в КОТ? ──")
    kot_visit = visitor.visit("кот")
    kot_sibs = kot_visit["siblings"] if kot_visit["found"] else set()
    knows_k = "к" in kot_sibs
    # Или через абстракцию "начинается с буквы"
    knows_start = "начинается" in kot_sibs
    ok4 = knows_k or knows_start
    checks.append(("Первая буква КОТ", ok4, f"знает 'к': {knows_k}"))
    print(f"    'кот' братья: {sorted(kot_sibs)[:10]}")
    print(f"    Знает 'к': {knows_k}")
    print(f"    Знает 'начинается': {knows_start}")
    print(f"    {'OK' if ok4 else 'MISS'}")

    # Упражнение 5: ask("из каких слогов состоит рыба?")
    print(f"\n  ── Упражнение 5: ask('из каких слогов рыба?') ──")
    res5 = gen.ask("из каких слогов рыба?")
    ok5 = "ры" in res5["answers"] or "ба" in res5["answers"]
    checks.append(("Слоги рыбы (ask)", ok5, f"ответ: {res5['answers'][:8]}"))
    print(f"    Ответ: {res5['answers'][:8]}")
    if res5["reasoning"]:
        for r in res5["reasoning"][:3]:
            print(f"    Логика: {r}")
    print(f"    {'OK' if ok5 else 'MISS'}")

    # Упражнение 6: ask("какие бывают гласные буквы?")
    print(f"\n  ── Упражнение 6: ask('какие гласные буквы?') ──")
    res6 = gen.ask("какие гласные буквы?")
    found_in_answer = {a for a in res6["answers"] if len(a) == 1 and a in "аоуиеы"}
    ok6 = len(found_in_answer) >= 3
    checks.append(("Гласные (ask)", ok6, f"нашли: {sorted(found_in_answer)}"))
    print(f"    Ответ: {res6['answers'][:10]}")
    print(f"    Гласные в ответе: {sorted(found_in_answer)}")
    print(f"    {'OK' if ok6 else 'MISS'}")

    # ════════════════════════════════════════
    # ПОЛНАЯ КАРТИНА
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ПОЛНАЯ КАРТИНА: ключевые абстракции")
    print("=" * 60)

    all_abst = world.show_abstractions()
    print(f"\n  Топ-20 абстракций по fed:")
    for c in all_abst[:20]:
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
    print("║     ИТОГ: УРОВЕНЬ 1 — БУКВЫ → СЛОГИ → СЛОВА         ║")
    print("╠═══════════════════════════════════════════════════════╣")

    passed = 0
    for name, ok, detail in checks:
        s = "+" if ok else "-"
        if ok:
            passed += 1
        print(f"║  {s} {name:40s}            ║")
        print(f"║    {detail:51s}  ║")

    print(f"╠═══════════════════════════════════════════════════════╣")
    print(f"║  Результат: {passed}/{len(checks)}                                     ║")
    print(f"╠═══════════════════════════════════════════════════════╣")

    alive = sum(1 for c in world.creatures.values() if c.alive)
    abst = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"║  Мир: {alive} существ, {abst} абстракций                  ║")

    if passed >= 5:
        print(f"║                                                       ║")
        print(f"║  УРОВЕНЬ 1 УСВОЕН.                                   ║")
        print(f"║  Система знает буквы, слоги и слова.                 ║")
        print(f"║  Можно переходить к уровню 2.                        ║")
    elif passed >= 3:
        print(f"║                                                       ║")
        print(f"║  ЧАСТИЧНО. Основы есть, детали нужно доработать.     ║")
    else:
        print(f"║                                                       ║")
        print(f"║  НУЖНА ДОРАБОТКА подачи материала.                   ║")

    print(f"║                                                       ║")
    print(f"║  Движок НЕ менялся.                                   ║")
    print(f"╚═══════════════════════════════════════════════════════╝")

    print(f"\n  Статистика: {world.stats}")


if __name__ == "__main__":
    main()
