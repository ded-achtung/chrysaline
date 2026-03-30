#!/usr/bin/env python3
"""
Эксперимент: Пунктуация посимвольно — чистое наблюдение.

Не подсказываем. Не программируем поведение с точкой.
Просто даём правила + сырой текст посимвольно и СМОТРИМ.

Фаза 1: Правила пунктуации (учитель, пословно).
Фаза 2: Сырой текст посимвольно: "К о т   е л   р ы б у .   С о б а к а   с п а л а ."
Фаза 3: Наблюдаем — что система сделала с точкой, пробелом, буквами.
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

RAW_TEXT = "Кот ел рыбу. Собака спала."


def text_to_chars(text):
    """Каждый символ — отдельный токен. Пробел = ' '."""
    return list(text)


def main():
    print("=" * 60)
    print("  ЭКСПЕРИМЕНТ: Пунктуация посимвольно")
    print("  Чистое наблюдение. Не подсказываем.")
    print("=" * 60)

    world = World()
    visitor = Visitor(world)

    # ════════════════════════════════════════
    # Фаза 1: Правила пунктуации
    # ════════════════════════════════════════

    print(f"\n  ── Фаза 1: Правила пунктуации ({len(PUNCTUATION_RULES)} правил) ──")
    for r in range(3):
        for rule in PUNCTUATION_RULES:
            world.feed_sentence(rule)
            world.run(1)

    alive1 = sum(1 for c in world.creatures.values() if c.alive)
    abst1 = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"    {alive1} существ, {abst1} абстракций")

    dot_info = visitor.visit("точка")
    if dot_info["found"]:
        print(f"    visit('точка') братья: {sorted(dot_info['siblings'])}")

    # ════════════════════════════════════════
    # Фаза 2: Сырой текст посимвольно
    # ════════════════════════════════════════

    chars = text_to_chars(RAW_TEXT)
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
    # Фаза 3: Чистое наблюдение
    # ════════════════════════════════════════

    print(f"\n{'='*60}")
    print("  ФАЗА 3: НАБЛЮДЕНИЕ")
    print("=" * 60)

    # ── Что произошло с точкой "."? ──
    print(f"\n  ── Что произошло с точкой '.'? ──")
    dot = visitor.visit(".")
    if dot["found"]:
        print(f"    Найдена: да")
        print(f"    Братья: {sorted(dot['siblings'])}")
        print(f"    Slot_mates: {sorted(dot.get('slot_mates', set()))}")
        # Все организмы с "."
        dot_organisms = []
        for c in world.creatures.values():
            if not c.alive or c.complexity < 2:
                continue
            if "." in c.parts:
                dot_organisms.append(c)
        dot_organisms.sort(key=lambda c: (-c.times_fed, -c.energy))
        print(f"    Организмы с '.': ({len(dot_organisms)} шт.)")
        for c in dot_organisms[:20]:
            slots = ""
            if c.slot_options:
                for sn, opts in c.slot_options.items():
                    clean = sorted(o for o in opts if not o.startswith("$"))
                    if clean:
                        slots += f" {sn}={clean}"
            print(f"      {c.name:40s} fed={c.times_fed:3d} e={c.energy:.1f}{slots}")
    else:
        print(f"    '.' не найдена!")

    # ── Что произошло с пробелом " "? ──
    print(f"\n  ── Что произошло с пробелом ' '? ──")
    space = visitor.visit(" ")
    if space["found"]:
        print(f"    Найден: да")
        print(f"    Братья: {sorted(space['siblings'])}")
        print(f"    Slot_mates: {sorted(space.get('slot_mates', set()))}")
        # Организмы с пробелом (только top-5)
        space_organisms = []
        for c in world.creatures.values():
            if not c.alive or c.complexity < 2:
                continue
            if " " in c.parts:
                space_organisms.append(c)
        space_organisms.sort(key=lambda c: (-c.times_fed, -c.energy))
        print(f"    Организмы с ' ': ({len(space_organisms)} шт., показаны top-10)")
        for c in space_organisms[:10]:
            slots = ""
            if c.slot_options:
                for sn, opts in c.slot_options.items():
                    clean = sorted(o for o in opts if not o.startswith("$"))
                    if clean:
                        slots += f" {sn}={clean}"
            print(f"      {c.name:40s} fed={c.times_fed:3d} e={c.energy:.1f}{slots}")
    else:
        print(f"    ' ' не найден!")

    # ── Точка vs обычная буква ──
    print(f"\n  ── Точка vs обычная буква ──")
    for char in [".", " ", "о", "а", "К", "С"]:
        cr = world._find_by_parts((char,))
        if cr:
            # Считаем в скольких организмах участвует
            org_count = sum(1 for c in world.creatures.values()
                           if c.alive and c.complexity >= 2 and char in c.parts)
            print(f"    '{char}': energy={cr.energy:.1f} fed={cr.times_fed:3d} "
                  f"age={cr.age:3d} в {org_count} организмах")
        else:
            print(f"    '{char}': не найден")

    # ── Абстракции с точкой ──
    print(f"\n  ── Абстракции с участием '.' ──")
    dot_abstracts = []
    for c in world.creatures.values():
        if not c.alive or not c.slot_options:
            continue
        if "." in c.parts:
            dot_abstracts.append(c)
    dot_abstracts.sort(key=lambda c: (-c.times_fed, -c.energy))
    if dot_abstracts:
        for c in dot_abstracts:
            slots = {}
            for sn, opts in c.slot_options.items():
                clean = sorted(o for o in opts if not o.startswith("$"))
                if clean:
                    slots[sn] = clean
            if slots:
                print(f"    {c.name}  {slots}  fed={c.times_fed}")
    else:
        print(f"    (нет абстракций с '.')")

    # ── Абстракции с пробелом ──
    print(f"\n  ── Абстракции с участием ' ' ──")
    space_abstracts = []
    for c in world.creatures.values():
        if not c.alive or not c.slot_options:
            continue
        if " " in c.parts:
            space_abstracts.append(c)
    space_abstracts.sort(key=lambda c: (-c.times_fed, -c.energy))
    if space_abstracts:
        for c in space_abstracts[:15]:
            slots = {}
            for sn, opts in c.slot_options.items():
                clean = sorted(o for o in opts if not o.startswith("$"))
                if clean:
                    slots[sn] = clean
            if slots:
                print(f"    {c.name}  {slots}  fed={c.times_fed}")
    else:
        print(f"    (нет абстракций с ' ')")

    # ── Все абстракции (полная картина) ──
    print(f"\n  ── ВСЕ абстракции из посимвольных данных ──")
    all_abstracts = world.show_abstractions()
    # Отфильтруем только те, что содержат символы из текста (не из правил)
    text_chars = set(chars)
    text_abstracts = []
    for c in all_abstracts:
        parts_set = set(c.parts)
        # Хотя бы один символ из текста
        if parts_set & text_chars:
            text_abstracts.append(c)

    for c in text_abstracts[:25]:
        slots = {}
        for sn, opts in c.slot_options.items():
            clean = sorted(o for o in opts if not o.startswith("$"))
            if clean:
                slots[sn] = clean
        if slots:
            print(f"    {c.name:40s} {slots}  fed={c.times_fed}")

    # ── Что знает буква "у"? (есть в "рыбу" и "Собака") ──
    print(f"\n  ── Отдельные буквы: что знают? ──")
    for char in ["К", "к", "С", "с", ".", " "]:
        info = visitor.visit(char)
        if info["found"]:
            sibs = sorted(info["siblings"])[:12]
            mates = sorted(info.get("slot_mates", set()))[:8]
            print(f"    '{char}' братья={sibs}")
            if mates:
                print(f"    '{char}' slot_mates={mates}")

    # ── Есть ли разница между "." и буквами? ──
    print(f"\n  ── Сравнение: точка как особый символ? ──")
    dot_cr = world._find_by_parts((".",))
    space_cr = world._find_by_parts((" ",))
    o_cr = world._find_by_parts(("о",))
    a_cr = world._find_by_parts(("а",))

    chars_to_compare = [
        (".", dot_cr), (" ", space_cr), ("о", o_cr), ("а", a_cr),
    ]
    for name, cr in chars_to_compare:
        if cr:
            orgs = sum(1 for c in world.creatures.values()
                       if c.alive and c.complexity >= 2 and name in c.parts)
            abstracts = sum(1 for c in world.creatures.values()
                           if c.alive and c.slot_options and name in c.parts)
            mates = set()
            for c in world.creatures.values():
                if not c.alive or not c.slot_options:
                    continue
                for sn, opts in c.slot_options.items():
                    if name in opts:
                        mates.update(o for o in opts if o != name and not o.startswith("$"))
            print(f"    '{name}': energy={cr.energy:.1f} fed={cr.times_fed} "
                  f"в {orgs} орг, {abstracts} абстр, "
                  f"заменяема на: {sorted(mates)[:8]}")

    # ════════════════════════════════════════
    # Итоговые наблюдения
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  НАБЛЮДЕНИЯ (без оценки правильности)")
    print("=" * 60)
    print(f"  Мир: {alive2} существ, {abst2} абстракций")
    print(f"  Статистика: {world.stats}")


if __name__ == "__main__":
    main()
