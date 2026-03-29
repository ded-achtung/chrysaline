#!/usr/bin/env python3
"""
v19: Японский и китайский — найдёт ли система структуру?

Два режима:
  A) Пословно (если мы разделим сами) — как с русским
  B) Посимвольно (как ребёнок видит) — НАСТОЯЩИЙ тест

Японский: 猫が魚を食べた (кот ел рыбу)
Китайский: 猫吃鱼 (кот ел рыбу)
"""
from chrysaline import World, Visitor


def main():
    print("="*60)
    print("  v19: Японский и китайский")
    print("  Найдёт ли система структуру?")
    print("="*60)

    # ═══════════════════════════════════════
    # ТЕСТ A: Пословно (мы помогаем с границами слов)
    # ═══════════════════════════════════════

    print("\n═══ ТЕСТ A: Пословно (японский) ═══\n")

    world_a = World()

    # Японские предложения (слова разделены)
    jp_sentences = [
        ["猫が", "魚を", "食べた"],       # кот ел рыбу
        ["猫が", "ネズミを", "食べた"],    # кот ел мышку
        ["猫が", "寝た"],                  # кот спал
        ["犬が", "骨を", "食べた"],        # собака ела кость
        ["犬が", "肉を", "食べた"],        # собака ела мясо
        ["母が", "窓を", "洗った"],        # мама мыла окно
        ["母が", "床を", "洗った"],        # мама мыла пол
        ["父が", "本を", "読んだ"],        # папа читал книгу
        ["父が", "新聞を", "読んだ"],      # папа читал газету
    ]

    for r in range(3):
        for sent in jp_sentences:
            world_a.feed_sentence(sent)
            world_a.run(1)

    abst_a = [c for c in world_a.creatures.values()
              if c.alive and c.slot_options]
    print(f"  Существ: {len(world_a.creatures)}, Абстракций: {len(abst_a)}")

    print("\n  Абстракции:")
    for a in sorted(abst_a, key=lambda c: -c.times_fed)[:10]:
        slots = {}
        for sn, opts in a.slot_options.items():
            clean = {o for o in opts if not o.startswith("$")}
            if clean:
                slots[sn] = clean
        if slots:
            slots_str = " ".join(f"{k}={{{','.join(sorted(v))}}}"
                                for k, v in slots.items())
            print(f"    {a.name}")
            print(f"      {slots_str}")

    # Тесты
    print("\n  Тесты:")
    visitor_a = Visitor(world_a)
    cat_info = visitor_a.visit("猫が")
    if cat_info["found"]:
        print(f"    visit('猫が'): братья={sorted(cat_info['siblings'])}")
    cat_food = visitor_a.query_category("猫���")
    print(f"    '猫が' категор��я: {sorted(cat_food)}")

    # ═══════════════════════════════════════
    # ТЕСТ B: Китайский пословно
    # ═══════════════════════════════════════

    print(f"\n═══ ТЕСТ B: Пословно (китайский) ═══\n")

    world_b = World()

    cn_sentences = [
        ["猫", "吃", "鱼"],         # кот ест рыбу
        ["猫", "吃", "老鼠"],       # кот ест мышку
        ["猫", "睡觉"],             # кот спит
        ["狗", "吃", "骨头"],       # собака ест кость
        ["狗", "吃", "肉"],         # собака ест мясо
        ["妈妈", "洗", "碗"],       # мама моет посуду
        ["妈妈", "洗", "窗户"],     # мама моет окно
        ["爸爸", "读", "书"],       # папа читает книгу
        ["爸爸", "读", "报纸"],     # папа читает газету
    ]

    for r in range(3):
        for sent in cn_sentences:
            world_b.feed_sentence(sent)
            world_b.run(1)

    abst_b = [c for c in world_b.creatures.values()
              if c.alive and c.slot_options]
    print(f"  Существ: {len(world_b.creatures)}, Абстракций: {len(abst_b)}")

    print("\n  Абстракции:")
    for a in sorted(abst_b, key=lambda c: -c.times_fed)[:10]:
        slots = {}
        for sn, opts in a.slot_options.items():
            clean = {o for o in opts if not o.startswith("$")}
            if clean:
                slots[sn] = clean
        if slots:
            slots_str = " ".join(f"{k}={{{','.join(sorted(v))}}}"
                                for k, v in slots.items())
            print(f"    {a.name}")
            print(f"      {slots_str}")

    # Тесты
    print("\n  Тесты:")
    visitor_b = Visitor(world_b)
    cat_cn = visitor_b.visit("猫")
    if cat_cn["found"]:
        print(f"    visit('猫'): братья={sorted(cat_cn['siblings'])}")
    food_cn = visitor_b.query_category("猫")
    print(f"    '猫' кат��гория: {sorted(food_cn)}")

    # Что ест кот?
    eat_cn = visitor_b.visit("吃")
    if eat_cn["found"]:
        print(f"    visit('吃'): братья={sorted(eat_cn['siblings'])}")

    # ═══════════════════════════════════════
    # ТЕСТ C: ПОСИМВОЛЬНО (настоящий тест!)
    # ═══════════════════════════════════════

    print(f"\n═══ ТЕСТ C: ПОСИМВОЛЬНО (китайский) ═══\n")
    print("  Каждый символ = отдельное существо")
    print("  Система должна САМА найти что 猫=кот, 吃=есть\n")

    world_c = World()

    # Те же предложения но посимвольно
    cn_chars = [
        list("猫吃鱼"),        # кот ест рыбу (3 символа)
        list("猫吃老鼠"),      # кот ест мышку (4 символа)
        list("猫睡觉"),        # кот спит (3 символа)
        list("狗吃骨头"),      # собака ест кость (4 символа)
        list("狗吃肉"),        # собака ест мясо (3 символа)
        list("妈妈洗碗"),      # мама моет посуду (4 символа)
        list("妈妈洗窗户"),    # мама моет окно (5 символов)
        list("爸爸读书"),      # папа читает книгу (4 символа)
        list("爸爸读报纸"),    # папа читает газету (5 символов)
    ]

    print("  Предложения (посимвольно):")
    for sent in cn_chars[:5]:
        print(f"    {'·'.join(sent)} ({len(sent)} символов)")
    print(f"    ... и ещё {len(cn_chars)-5}")

    for r in range(5):  # больше раундов для посимвольного
        for sent in cn_chars:
            world_c.feed_sentence(sent)
            world_c.run(1)

    abst_c = [c for c in world_c.creatures.values()
              if c.alive and c.slot_options]
    print(f"\n  Существ: {len(world_c.creatures)}, Абстракций: {len(abst_c)}")

    # Какие символы самые "сильные"?
    print("\n  Самые сильные символы:")
    singles = [(c.name, c.energy, c.times_fed)
               for c in world_c.creatures.values()
               if c.alive and c.complexity == 1]
    singles.sort(key=lambda x: -x[1])
    for name, energy, fed in singles[:10]:
        bar = "█" * max(1, int(energy * 3))
        print(f"    '{name}' e={energy:.1f} fed={fed:3d} {bar}")

    # Какие ПАРЫ нашлись?
    print("\n  Самые сильные пары:")
    pairs = [(c.name, c.energy, c.times_fed)
             for c in world_c.creatures.values()
             if c.alive and c.complexity == 2 and not c.slot_options]
    pairs.sort(key=lambda x: -x[1])
    for name, energy, fed in pairs[:10]:
        print(f"    '{name}' e={energy:.1f} fed={fed:3d}")

    # Абстракции — нашла ли паттерны?
    print("\n  Абстракции (посимвольно):")
    for a in sorted(abst_c, key=lambda c: -c.times_fed)[:15]:
        slots = {}
        for sn, opts in a.slot_options.items():
            clean = {o for o in opts if not o.startswith("$")}
            if clean:
                slots[sn] = clean
        if slots:
            slots_str = " ".join(f"{k}={{{','.join(sorted(v))}}}"
                                for k, v in slots.items())
            print(f"    {a.name}")
            print(f"      {slots_str}")

    # Visiting по 猫
    visitor_c = Visitor(world_c)
    cat_char = visitor_c.visit("猫")
    if cat_char["found"]:
        print(f"\n  visit('猫'): братья={sorted(cat_char['siblings'])}")
        print(f"  visit('猫'): заменяемые={sorted(cat_char['slot_mates'])[:8]}")

    # ═══════════════════════════════════════
    # ИТОГ
    # ═══════════════════════════════════════

    print(f"\n{'='*60}")
    print("  ИТОГ v19")
    print("="*60)

    print(f"\n  Тест A (японский пословно):")
    print(f"    {len(world_a.creatures)} существ, {len(abst_a)} абстракций")
    print(f"    {'✓ Нашла паттерны' if len(abst_a) > 0 else '✗ Не нашла'}")

    print(f"\n  Тест B (китайский пословно):")
    print(f"    {len(world_b.creatures)} существ, {len(abst_b)} абстракций")
    print(f"    {'✓ Нашла паттерны' if len(abst_b) > 0 else '✗ Не нашла'}")

    print(f"\n  Тест C (китайский ПОСИМВОЛЬНО):")
    print(f"    {len(world_c.creatures)} существ, {len(abst_c)} абстракций")
    print(f"    {'✓ Нашла паттерны' if len(abst_c) > 0 else '✗ Не нашла'}")
    if abst_c:
        print(f"    Это НАСТОЯЩИЙ тест: без пробелов, без подсказок!")

    print()
    print("  Код движка НЕ МЕНЯЛСЯ. Тот же World из v17d.")
    print("="*60)


if __name__ == "__main__":
    main()
