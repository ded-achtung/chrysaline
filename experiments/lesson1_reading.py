#!/usr/bin/env python3
"""
Урок 1: Алфавит и чтение.

Шаг за шагом, как в школе. Учитель ведёт систему от букв
к слогам, от слогов к словам, от слов к предложениям.
Много примеров. Потом упражнения — смотрим что реально сделает.

Движок НЕ менялся. Новых механизмов НЕТ.
"""

from chrysaline import World, Visitor, Generator


# ════════════════════════════════════════════════════════
# ШАГ 2: Правила чтения
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
    ["в", "предложении", "есть", "смысл"],
]

# ════════════════════════════════════════════════════════
# ШАГ 3: Учитель показывает на примерах
# ════════════════════════════════════════════════════════

# --- Блок А: буквы → слова ---
EXAMPLES_LETTERS_TO_WORDS = [
    # Учитель показывает: вот буквы, а вот слово
    ["к", "о", "т", "это", "слово", "кот"],
    ["е", "л", "это", "слово", "ел"],
    ["р", "ы", "б", "у", "это", "слово", "рыбу"],
    ["с", "о", "б", "а", "к", "а", "это", "слово", "собака"],
    ["с", "п", "а", "л", "а", "это", "слово", "спала"],
    ["м", "а", "м", "а", "это", "слово", "мама"],
    ["м", "ы", "л", "а", "это", "слово", "мыла"],
    ["р", "а", "м", "у", "это", "слово", "раму"],
    ["п", "а", "п", "а", "это", "слово", "папа"],

    # Учитель показывает связь буква → слог → слово
    ["к", "и", "о", "это", "слоги"],
    ["слог", "ко", "и", "слог", "т", "это", "кот"],
    ["слог", "ма", "и", "слог", "ма", "это", "мама"],
    ["слог", "ры", "и", "слог", "ба", "это", "рыба"],
]

# --- Блок Б: слова → предложения ---
EXAMPLES_WORDS_TO_SENTENCES = [
    # Учитель показывает: вот слова, а вот предложение
    ["кот", "ел", "это", "часть", "предложения"],
    ["кот", "ел", "рыбу", "это", "предложение"],
    ["собака", "спала", "это", "предложение"],
    ["мама", "мыла", "раму", "это", "предложение"],
    ["папа", "читал", "книгу", "это", "предложение"],

    # Несколько слов = предложение
    ["в", "предложении", "кот", "ел", "рыбу", "три", "слова"],
    ["в", "предложении", "собака", "спала", "два", "слова"],
    ["в", "предложении", "мама", "мыла", "раму", "три", "слова"],
]

# --- Блок В: точка и предложения ---
EXAMPLES_DOT_AND_SENTENCES = [
    # Учитель показывает: точка в конце
    ["кот", "ел", "рыбу", ".", "здесь", "точка", "в", "конце"],
    ["собака", "спала", ".", "здесь", "точка", "в", "конце"],
    ["мама", "мыла", "раму", ".", "здесь", "точка", "в", "конце"],
    ["папа", "читал", "книгу", ".", "здесь", "точка", "в", "конце"],

    # Два предложения — точка разделяет
    ["кот", "ел", "рыбу", ".", "собака", "спала", ".", "здесь", "два", "предложения"],
    ["мама", "мыла", "раму", ".", "папа", "читал", "книгу", ".", "здесь", "два", "предложения"],

    # Что точка делает
    ["точка", "после", "рыбу", "значит", "конец", "предложения"],
    ["точка", "после", "спала", "значит", "конец", "предложения"],
    ["точка", "после", "раму", "значит", "конец", "предложения"],
    ["точка", "после", "книгу", "значит", "конец", "предложения"],

    # Первое предложение — второе предложение
    ["первое", "предложение", "кот", "ел", "рыбу"],
    ["второе", "предложение", "собака", "спала"],
    ["точка", "разделяет", "первое", "и", "второе"],

    ["первое", "предложение", "мама", "мыла", "раму"],
    ["второе", "предложение", "папа", "читал", "книгу"],
    ["точка", "разделяет", "первое", "и", "второе"],
]

# --- Блок Г: мосты символ↔понятие ---
BRIDGES = [
    [".", "это", "точка"],
    [" ", "это", "пробел"],
    ["пробел", "разделяет", "слова"],
    [".", "означает", "конец", "предложения"],
    ["после", ".", "новое", "предложение"],
]

# --- Блок Д: ещё больше примеров "как работает точка" ---
EXAMPLES_MORE_DOT = [
    # Прямые факты: что стоит перед точкой, что после
    ["перед", "точкой", "стоит", "рыбу"],
    ["перед", "точкой", "стоит", "спала"],
    ["перед", "точкой", "стоит", "раму"],
    ["перед", "точкой", "стоит", "книгу"],
    ["после", "точки", "стоит", "собака"],
    ["после", "точки", "стоит", "папа"],

    # Точка = граница
    ["рыбу", ".", "собака", "здесь", "граница", "предложений"],
    ["раму", ".", "папа", "здесь", "граница", "предложений"],
    ["спала", ".", "конец", "текста"],
    ["книгу", ".", "конец", "текста"],
]

# ════════════════════════════════════════════════════════
# ШАГ 4: Упражнения (данные для проверки)
# ════════════════════════════════════════════════════════

# Подадим сырые предложения (без предобработки) и спросим
EXERCISE_SENTENCES = [
    ["кот", "спал"],
    ["кот", "спал", ".", "собака", "ела", "."],
    ["мама", "мыла", "раму", ".", "папа", "читал", "книгу", "."],
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


def show_visit(visitor, word, label=None):
    """Показать visit() для слова."""
    if label:
        print(f"\n    {label}")
    info = visitor.visit(word)
    if info["found"]:
        print(f"    visit('{word}') братья: {sorted(info['siblings'])[:15]}")
        mates = info.get("slot_mates", set())
        if mates:
            print(f"    visit('{word}') slot_mates: {sorted(mates)[:12]}")
        rules = info.get("rules", [])
        if rules:
            for rule in rules[:5]:
                opts = sorted(rule.get("options", set()))[:8]
                if opts:
                    print(f"    visit('{word}') правило: {rule['pattern']} → {opts}")
        return info
    else:
        print(f"    '{word}' не найдена")
        return info


def main():
    print("=" * 60)
    print("  УРОК 1: АЛФАВИТ И ЧТЕНИЕ")
    print("  Шаг за шагом, как в школе.")
    print("  Движок НЕ менялся.")
    print("=" * 60)

    world = World()
    visitor = Visitor(world)
    generator = Generator(world)

    # ════════════════════════════════════════
    # Шаг 2: Правила чтения
    # ════════════════════════════════════════

    teach(world, READING_RULES, "Шаг 2: Правила чтения", repeats=3)
    show_visit(visitor, "точка", "Что знает 'точка'?")
    show_visit(visitor, "предложение", "Что знает 'предложение'?")
    show_visit(visitor, "слова", "Что знает 'слова'?")

    # ════════════════════════════════════════
    # Шаг 3а: Буквы → слова
    # ════════════════════════════════════════

    teach(world, EXAMPLES_LETTERS_TO_WORDS, "Шаг 3а: Буквы → слова", repeats=3)

    print(f"\n    Что знает 'кот'?")
    show_visit(visitor, "кот")

    print(f"\n    Что знает 'слово'?")
    show_visit(visitor, "слово")

    # Связались ли буквы со словами?
    print(f"\n    Связь буква ↔ слово:")
    for word_name, letters in [("кот", "кот"), ("мама", "мама"), ("собака", "собака")]:
        word_info = visitor.visit(word_name)
        if word_info["found"]:
            letter_siblings = [s for s in word_info["siblings"] if len(s) == 1]
            print(f"      '{word_name}' знает буквы: {sorted(letter_siblings)}")

    # ════════════════════════════════════════
    # Шаг 3б: Слова → предложения
    # ════════════════════════════════════════

    teach(world, EXAMPLES_WORDS_TO_SENTENCES, "Шаг 3б: Слова → предложения", repeats=3)
    show_visit(visitor, "предложение", "Что теперь знает 'предложение'?")

    # ════════════════════════════════════════
    # Шаг 3в: Точка и предложения (много примеров)
    # ════════════════════════════════════════

    teach(world, EXAMPLES_DOT_AND_SENTENCES, "Шаг 3в: Точка и предложения", repeats=3)

    # ════════════════════════════════════════
    # Шаг 3г: Мосты символ↔понятие
    # ════════════════════════════════════════

    teach(world, BRIDGES, "Шаг 3г: Мосты (символ↔понятие)", repeats=5)

    # ════════════════════════════════════════
    # Шаг 3д: Ещё примеры работы точки
    # ════════════════════════════════════════

    teach(world, EXAMPLES_MORE_DOT, "Шаг 3д: Ещё примеры (перед точкой / после точки)", repeats=3)

    # ════════════════════════════════════════
    # ПРОМЕЖУТОЧНЫЙ СРЕЗ: что система знает?
    # ════════════════════════════════════════

    print(f"\n{'='*60}")
    print("  ПРОМЕЖУТОЧНЫЙ СРЕЗ: что система усвоила?")
    print("=" * 60)

    show_visit(visitor, ".", "Символ '.' знает:")
    show_visit(visitor, "точка", "Слово 'точка' знает:")
    show_visit(visitor, " ", "Символ ' ' знает:")
    show_visit(visitor, "пробел", "Слово 'пробел' знает:")

    # Цепочка . → точка → правила
    print(f"\n    Цепочка: '.' → 'точка' → ?")
    dot_info = visitor.visit(".")
    dot_sibs = dot_info["siblings"] if dot_info["found"] else set()
    knows_tochka = "точка" in dot_sibs
    print(f"    '.' знает 'точка': {knows_tochka}")
    if knows_tochka:
        tochka_info = visitor.visit("точка")
        t_sibs = tochka_info["siblings"] if tochka_info["found"] else set()
        for concept in ["конце", "разделяет", "предложения", "после"]:
            print(f"    'точка' знает '{concept}': {concept in t_sibs}")

    # Что стоит "перед точкой"?
    print(f"\n    Абстракция 'перед·точкой·стоит·$0':")
    for c in world.creatures.values():
        if not c.alive or not c.slot_options:
            continue
        if "перед" in c.parts and "точкой" in c.parts and "стоит" in c.parts:
            for sn, opts in c.slot_options.items():
                clean = sorted(o for o in opts if not o.startswith("$"))
                if clean:
                    print(f"      {c.name} → {sn}={clean}  fed={c.times_fed}")

    # Что стоит "после точки"?
    print(f"\n    Абстракция 'после·точки·стоит·$0':")
    for c in world.creatures.values():
        if not c.alive or not c.slot_options:
            continue
        if "после" in c.parts and "точки" in c.parts and "стоит" in c.parts:
            for sn, opts in c.slot_options.items():
                clean = sorted(o for o in opts if not o.startswith("$"))
                if clean:
                    print(f"      {c.name} → {sn}={clean}  fed={c.times_fed}")

    # ════════════════════════════════════════
    # Шаг 4: Упражнения
    # ════════════════════════════════════════

    print(f"\n{'='*60}")
    print("  ШАГ 4: УПРАЖНЕНИЯ")
    print("=" * 60)

    # --- Упражнение 1: "кот спал" — сколько слов? ---
    print(f"\n  ── Упражнение 1: 'кот спал' — что знает система? ──")
    # Подаём как есть
    world.feed_sentence(["кот", "спал"])
    world.run(1)
    show_visit(visitor, "кот", "'кот' после подачи:")
    show_visit(visitor, "спал", "'спал' после подачи:")

    # ask(): сколько слов?
    res1 = generator.ask("сколько слов в кот спал?")
    print(f"\n    ask('сколько слов в кот спал?')")
    print(f"    ответ: {res1['answers'][:8]}")
    print(f"    логика: {res1['reasoning'][:3]}")

    # --- Упражнение 2: "кот спал. собака ела." — сколько предложений? ---
    print(f"\n  ── Упражнение 2: 'кот спал. собака ела.' ──")
    world.feed_sentence(["кот", "спал", ".", "собака", "ела", "."])
    world.run(1)
    # Повторим для усвоения
    for _ in range(3):
        world.feed_sentence(["кот", "спал", ".", "собака", "ела", "."])
        world.run(1)

    res2 = generator.ask("сколько предложений в кот спал собака ела?")
    print(f"    ask('сколько предложений?')")
    print(f"    ответ: {res2['answers'][:8]}")
    print(f"    логика: {res2['reasoning'][:3]}")

    # Посмотрим что система сделала с точкой в этом тексте
    print(f"\n    Организмы с '.' из этого текста:")
    for c in world.creatures.values():
        if not c.alive or c.complexity < 2:
            continue
        if "." in c.parts and ("спал" in c.parts or "ела" in c.parts
                               or "собака" in c.parts or "кот" in c.parts):
            slots = ""
            if c.slot_options:
                for sn, opts in c.slot_options.items():
                    clean = sorted(o for o in opts if not o.startswith("$"))
                    if clean:
                        slots += f" {sn}={clean}"
            print(f"      {c.name:45s} fed={c.times_fed:3d}{slots}")

    # --- Упражнение 3: какие предложения? ---
    print(f"\n  ── Упражнение 3: какие предложения в тексте? ──")
    res3a = generator.ask("что делал кот?")
    print(f"    ask('что делал кот?'): {res3a['answers'][:5]}")
    print(f"    логика: {res3a['reasoning'][:3]}")

    res3b = generator.ask("что делала собака?")
    print(f"    ask('что делала собака?'): {res3b['answers'][:5]}")
    print(f"    логика: {res3b['reasoning'][:3]}")

    # --- Упражнение 4: "мама мыла раму. папа читал книгу." ---
    print(f"\n  ── Упражнение 4: 'мама мыла раму. папа читал книгу.' ──")
    for _ in range(4):
        world.feed_sentence(["мама", "мыла", "раму", ".", "папа", "читал", "книгу", "."])
        world.run(1)

    res4a = generator.ask("что делала мама?")
    print(f"    ask('что делала мама?'): {res4a['answers'][:5]}")
    print(f"    логика: {res4a['reasoning'][:3]}")

    res4b = generator.ask("что делал папа?")
    print(f"    ask('что делал папа?'): {res4b['answers'][:5]}")
    print(f"    логика: {res4b['reasoning'][:3]}")

    # --- Упражнение 5: что перед точкой? что после? ---
    print(f"\n  ── Упражнение 5: что стоит перед/после точки? ──")
    res5a = generator.ask("что стоит перед точкой?")
    print(f"    ask('что стоит перед точкой?'): {res5a['answers'][:8]}")
    print(f"    логика: {res5a['reasoning'][:3]}")

    res5b = generator.ask("что стоит после точки?")
    print(f"    ask('что стоит после точки?'): {res5b['answers'][:8]}")
    print(f"    логика: {res5b['reasoning'][:3]}")

    # ════════════════════════════════════════
    # ПОЛНАЯ КАРТИНА: все абстракции
    # ════════════════════════════════════════

    print(f"\n{'='*60}")
    print("  ПОЛНАЯ КАРТИНА: ключевые абстракции")
    print("=" * 60)

    # Абстракции с "точка"/"."
    print(f"\n  Абстракции с 'точка' или '.':")
    for c in world.creatures.values():
        if not c.alive or not c.slot_options:
            continue
        if "точка" in c.parts or "." in c.parts or "точкой" in c.parts:
            slots = {}
            for sn, opts in c.slot_options.items():
                clean = sorted(o for o in opts if not o.startswith("$"))
                if clean:
                    slots[sn] = clean
            if slots:
                print(f"    {c.name}  {slots}  fed={c.times_fed}")

    # Абстракции с "предложение"
    print(f"\n  Абстракции с 'предложение'/'предложения':")
    for c in world.creatures.values():
        if not c.alive or not c.slot_options:
            continue
        if "предложение" in c.parts or "предложения" in c.parts:
            slots = {}
            for sn, opts in c.slot_options.items():
                clean = sorted(o for o in opts if not o.startswith("$"))
                if clean:
                    slots[sn] = clean
            if slots:
                print(f"    {c.name}  {slots}  fed={c.times_fed}")

    # Абстракции с "это"+"предложение"
    print(f"\n  Абстракции '$0 это предложение' (если есть):")
    for c in world.creatures.values():
        if not c.alive or not c.slot_options:
            continue
        if "это" in c.parts and "предложение" in c.parts:
            slots = {}
            for sn, opts in c.slot_options.items():
                clean = sorted(o for o in opts if not o.startswith("$"))
                if clean:
                    slots[sn] = clean
            if slots:
                print(f"    {c.name}  {slots}  fed={c.times_fed}")

    # Абстракции "это слово $0"
    print(f"\n  Абстракции 'это·слово·$0' (если есть):")
    for c in world.creatures.values():
        if not c.alive or not c.slot_options:
            continue
        if "это" in c.parts and "слово" in c.parts:
            slots = {}
            for sn, opts in c.slot_options.items():
                clean = sorted(o for o in opts if not o.startswith("$"))
                if clean:
                    slots[sn] = clean
            if slots:
                print(f"    {c.name}  {slots}  fed={c.times_fed}")

    # Абстракции с "$0·ел" / "$0·мыла" / "$0·спала"
    print(f"\n  Абстракции действий (кто что делал):")
    for c in world.creatures.values():
        if not c.alive or not c.slot_options:
            continue
        action_words = {"ел", "спал", "спала", "мыла", "читал", "ела"}
        if set(c.parts) & action_words:
            slots = {}
            for sn, opts in c.slot_options.items():
                clean = sorted(o for o in opts if not o.startswith("$"))
                if clean:
                    slots[sn] = clean
            if slots:
                print(f"    {c.name}  {slots}  fed={c.times_fed}")

    # Top-20 абстракций по fed
    print(f"\n  Top-20 абстракций по fed:")
    all_abst = world.show_abstractions()
    for c in all_abst[:20]:
        slots = {}
        for sn, opts in c.slot_options.items():
            clean = sorted(o for o in opts if not o.startswith("$"))
            if clean:
                slots[sn] = clean
        if slots:
            print(f"    {c.name:50s} {slots}  fed={c.times_fed}")

    # ════════════════════════════════════════
    # ИТОГ
    # ════════════════════════════════════════

    print(f"\n{'='*60}")
    print("  ИТОГ НАБЛЮДЕНИЙ")
    print("=" * 60)

    alive = sum(1 for c in world.creatures.values() if c.alive)
    abst = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"  Мир: {alive} существ, {abst} абстракций")
    print(f"  Статистика: {world.stats}")


if __name__ == "__main__":
    main()
