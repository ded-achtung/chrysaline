#!/usr/bin/env python3
"""
Эксперимент: Пунктуация посимвольно — с мостами.

Фаза 1: Правила пунктуации (учитель, пословно).
Фаза 1б: Мосты — учитель связывает символы с понятиями:
    [".", "это", "точка"]
    [" ", "это", "пробел"]
    ["пробел", "разделяет", "слова"]
Фаза 2: Сырой текст посимвольно.
Фаза 3: Наблюдаем — связались ли символы с правилами через мосты?
"""

from chrysaline import World, Visitor


# ════════════════════════════════════════════════════════
# ДАННЫЕ
# ════════════════════════════════════════════════════════

PUNCTUATION_RULES = [
    ["точка", "стоит", "в", "конце", "предложения"],
    ["после", "точки", "начинается", "новое", "предложение"],
    ["после", "точки", "первое", "слово", "с", "большой", "буквы"],
    ["точка", "разделяет", "предложения"],
    ["запятая", "разделяет", "слова", "в", "перечислении"],
    ["тире", "означает", "определение"],
    ["большая", "буква", "после", "точки"],
    ["первое", "слово", "предложения", "с", "большой", "буквы"],
]

BRIDGES = [
    [".", "это", "точка"],
    [" ", "это", "пробел"],
    ["пробел", "разделяет", "слова"],
]

RAW_TEXT = "Кот ел рыбу. Собака спала."


def main():
    print("=" * 60)
    print("  ЭКСПЕРИМЕНТ: Пунктуация посимвольно + МОСТЫ")
    print("  Свяжутся ли символы с правилами?")
    print("=" * 60)

    world = World()
    visitor = Visitor(world)

    # ════════════════════════════════════════
    # Фаза 1а: Правила пунктуации
    # ════════════════════════════════════════

    print(f"\n  ── Фаза 1а: Правила пунктуации ({len(PUNCTUATION_RULES)} правил) ──")
    for r in range(3):
        for rule in PUNCTUATION_RULES:
            world.feed_sentence(rule)
            world.run(1)

    alive1 = sum(1 for c in world.creatures.values() if c.alive)
    abst1 = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"    {alive1} существ, {abst1} абстракций")

    # Что знает "точка" ДО мостов?
    dot_word_before = visitor.visit("точка")
    dot_sibs_before = sorted(dot_word_before["siblings"]) if dot_word_before["found"] else []
    print(f"    visit('точка') братья: {dot_sibs_before}")

    # ════════════════════════════════════════
    # Фаза 1б: Мосты
    # ════════════════════════════════════════

    print(f"\n  ── Фаза 1б: Мосты ({len(BRIDGES)} мостов) ──")
    for b in BRIDGES:
        print(f"    {b}")

    for r in range(5):
        for bridge in BRIDGES:
            world.feed_sentence(bridge)
            world.run(1)

    alive1b = sum(1 for c in world.creatures.values() if c.alive)
    abst1b = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"    После мостов: {alive1b} существ, {abst1b} абстракций")

    # Что знает "." ПОСЛЕ мостов, но ДО текста?
    dot_sym_after_bridge = visitor.visit(".")
    if dot_sym_after_bridge["found"]:
        print(f"    visit('.') братья: {sorted(dot_sym_after_bridge['siblings'])}")
        print(f"    visit('.') slot_mates: {sorted(dot_sym_after_bridge.get('slot_mates', set()))}")
    else:
        print(f"    '.' не найдена")

    # Знает ли "." слово "точка" через мост?
    dot_knows_tochka = "точка" in dot_sym_after_bridge.get("siblings", set())
    print(f"    '.' знает 'точка': {dot_knows_tochka}")

    # Знает ли "точка" символ "."?
    tochka_after = visitor.visit("точка")
    tochka_knows_dot = "." in tochka_after.get("siblings", set()) if tochka_after["found"] else False
    print(f"    'точка' знает '.': {tochka_knows_dot}")

    # Пробел
    space_after_bridge = visitor.visit(" ")
    if space_after_bridge["found"]:
        print(f"    visit(' ') братья: {sorted(space_after_bridge['siblings'])}")
    space_knows_probel = "пробел" in space_after_bridge.get("siblings", set())
    print(f"    ' ' знает 'пробел': {space_knows_probel}")

    probel_after = visitor.visit("пробел")
    if probel_after["found"]:
        print(f"    visit('пробел') братья: {sorted(probel_after['siblings'])}")

    # ════════════════════════════════════════
    # Фаза 2: Сырой текст посимвольно
    # ════════════════════════════════════════

    chars = list(RAW_TEXT)
    print(f"\n  ── Фаза 2: Сырой текст посимвольно ──")
    print(f"    Текст: \"{RAW_TEXT}\"")
    print(f"    Токены ({len(chars)}): {chars}")

    for r in range(5):
        world.feed_sentence(chars)
        world.run(1)

    alive2 = sum(1 for c in world.creatures.values() if c.alive)
    abst2 = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"\n    После подачи: {alive2} существ, {abst2} абстракций")

    # ════════════════════════════════════════
    # Фаза 3: Наблюдение — что изменилось?
    # ════════════════════════════════════════

    print(f"\n{'='*60}")
    print("  ФАЗА 3: НАБЛЮДЕНИЕ")
    print("=" * 60)

    # ── Главный вопрос: "." знает "конце предложения"? ──
    print(f"\n  ── ГЛАВНЫЙ ВОПРОС: '.' знает что она 'в конце предложения'? ──")
    dot_final = visitor.visit(".")
    if dot_final["found"]:
        dot_sibs = dot_final["siblings"]
        dot_mates = dot_final.get("slot_mates", set())
        dot_rules = dot_final.get("rules", [])
        dot_concrete = dot_final.get("concrete_relatives", set())

        print(f"    братья: {sorted(dot_sibs)}")
        print(f"    slot_mates: {sorted(dot_mates)[:15]}")
        if dot_rules:
            print(f"    правила:")
            for rule in dot_rules:
                print(f"      {rule['pattern']} → {sorted(rule.get('options', set()))[:8]}")
        if dot_concrete:
            print(f"    concrete_relatives: {sorted(dot_concrete)[:15]}")

        # Цепочка: "." → "точка" → "конце предложения"
        knows_tochka = "точка" in dot_sibs
        print(f"\n    Цепочка: '.' → 'точка' → правила?")
        print(f"    Шаг 1: '.' знает 'точка': {knows_tochka}")

        if knows_tochka:
            tochka_info = visitor.visit("точка")
            if tochka_info["found"]:
                t_sibs = tochka_info["siblings"]
                print(f"    Шаг 2: 'точка' братья: {sorted(t_sibs)}")
                knows_konce = "конце" in t_sibs
                knows_razdelyaet = "разделяет" in t_sibs
                knows_predlozheniya = "предложения" in t_sibs
                print(f"    'точка' знает 'конце': {knows_konce}")
                print(f"    'точка' знает 'разделяет': {knows_razdelyaet}")
                print(f"    'точка' знает 'предложения': {knows_predlozheniya}")
                chain_works = knows_tochka and (knows_konce or knows_razdelyaet)
                print(f"    ЦЕПОЧКА ЗАМКНУТА: {chain_works}")
                if chain_works:
                    print(f"    '.' → 'точка' → 'в конце предложения' / 'разделяет предложения'")
            else:
                chain_works = False
        else:
            chain_works = False
            # Может "." знает через slot_mates?
            book_words_in_mates = {"конце", "предложения", "разделяет", "стоит"} & dot_mates
            if book_words_in_mates:
                print(f"    Нет прямой связи, но в slot_mates есть: {sorted(book_words_in_mates)}")
    else:
        print(f"    '.' не найдена!")
        chain_works = False

    # ── Пробел знает что "разделяет слова"? ──
    print(f"\n  ── ПРОБЕЛ: знает что 'разделяет слова'? ──")
    space_final = visitor.visit(" ")
    if space_final["found"]:
        sp_sibs = space_final["siblings"]
        sp_mates = space_final.get("slot_mates", set())

        print(f"    братья: {sorted(sp_sibs)}")
        print(f"    slot_mates: {sorted(sp_mates)[:15]}")

        knows_probel = "пробел" in sp_sibs
        print(f"\n    Цепочка: ' ' → 'пробел' → 'разделяет слова'?")
        print(f"    Шаг 1: ' ' знает 'пробел': {knows_probel}")

        if knows_probel:
            probel_info = visitor.visit("пробел")
            if probel_info["found"]:
                p_sibs = probel_info["siblings"]
                print(f"    Шаг 2: 'пробел' братья: {sorted(p_sibs)}")
                knows_razd = "разделяет" in p_sibs
                knows_slova = "слова" in p_sibs
                print(f"    'пробел' знает 'разделяет': {knows_razd}")
                print(f"    'пробел' знает 'слова': {knows_slova}")
                space_chain = knows_probel and knows_razd
                print(f"    ЦЕПОЧКА ЗАМКНУТА: {space_chain}")
                if space_chain:
                    print(f"    ' ' → 'пробел' → 'разделяет слова'")
            else:
                space_chain = False
        else:
            space_chain = False
    else:
        space_chain = False

    # ── Что видит "." в тексте? ──
    print(f"\n  ── Организмы с '.' ──")
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
        print(f"    {c.name:40s} fed={c.times_fed:3d} e={c.energy:.1f}{slots}")

    # ── Абстракции с "." ──
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

    # ── Абстракции с " " ──
    print(f"\n  ── Абстракции с ' ' ──")
    for c in world.creatures.values():
        if not c.alive or not c.slot_options:
            continue
        if " " in c.parts:
            slots = {}
            for sn, opts in c.slot_options.items():
                clean = sorted(o for o in opts if not o.startswith("$"))
                if clean:
                    slots[sn] = clean
            if slots:
                print(f"    {c.name}  {slots}  fed={c.times_fed}")

    # ── Сравнительная таблица: с мостами vs без ──
    print(f"\n  ── Сравнение: точка и пробел ──")
    for char, label in [(".", "точка"), (" ", "пробел")]:
        cr = world._find_by_parts((char,))
        if cr:
            orgs = sum(1 for c in world.creatures.values()
                       if c.alive and c.complexity >= 2 and char in c.parts)
            abst = sum(1 for c in world.creatures.values()
                       if c.alive and c.slot_options and char in c.parts)
            mates = set()
            for c in world.creatures.values():
                if not c.alive or not c.slot_options:
                    continue
                for sn, opts in c.slot_options.items():
                    if char in opts:
                        mates.update(o for o in opts if o != char and not o.startswith("$"))
            print(f"    '{char}' ({label}): energy={cr.energy:.1f} fed={cr.times_fed} "
                  f"в {orgs} орг, {abst} абстр, "
                  f"заменяема на: {sorted(mates)[:10]}")

    # ── ВСЕ абстракции (полная картина) ──
    print(f"\n  ── Все абстракции из текстовых символов ──")
    text_chars = set(list(RAW_TEXT))
    all_abst = world.show_abstractions()
    for c in all_abst[:30]:
        if not (set(c.parts) & text_chars):
            continue
        slots = {}
        for sn, opts in c.slot_options.items():
            clean = sorted(o for o in opts if not o.startswith("$"))
            if clean:
                slots[sn] = clean
        if slots:
            print(f"    {c.name:40s} {slots}  fed={c.times_fed}")

    # ════════════════════════════════════════
    # ИТОГ
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ИТОГ НАБЛЮДЕНИЙ")
    print("=" * 60)
    print(f"  '.' → 'точка' (мост): {dot_knows_tochka or ('точка' in dot_final.get('siblings', set()) if dot_final.get('found') else False)}")
    print(f"  ' ' → 'пробел' (мост): {space_knows_probel or ('пробел' in space_final.get('siblings', set()) if space_final.get('found') else False)}")
    print(f"  Цепочка '.' → 'точка' → 'конце/разделяет': {chain_works}")
    print(f"  Цепочка ' ' → 'пробел' → 'разделяет слова': {space_chain}")
    print(f"\n  Мир: {alive2} существ, {abst2} абстракций")
    print(f"  Статистика: {world.stats}")


if __name__ == "__main__":
    main()
