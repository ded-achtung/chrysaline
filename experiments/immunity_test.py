#!/usr/bin/env python3
"""
Тест иммунитета: ложные факты НЕ должны окрепнуть.

Система знает правильные правила. Подаём ложные.
Правильные должны выжить, ложные — умереть.

Движок изменён: _confirmed_feed() проверяет конкурентов.
"""

from chrysaline import World, Visitor, Generator


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
    print("  ТЕСТ ИММУНИТЕТА: ЛОЖЬ НЕ ДОЛЖНА КРЕПНУТЬ")
    print("=" * 60)

    world = World()
    visitor = Visitor(world)
    gen = Generator(world)

    # ════════════════════════════════════════
    # ОБУЧЕНИЕ: правильные правила
    # ════════════════════════════════════════
    TRUTH = [
        ["жи", "пишется", "с", "буквой", "и"],
        ["ши", "пишется", "с", "буквой", "и"],
        ["ча", "пишется", "с", "буквой", "а"],
        ["кот", "это", "млекопитающее"],
        ["собака", "это", "млекопитающее"],
        ["а", "это", "гласная", "буква"],
        ["о", "это", "гласная", "буква"],
        ["к", "это", "согласная", "буква"],
        ["т", "это", "согласная", "буква"],
    ]

    teach(world, TRUTH, "Правильные правила", repeats=5)

    # Замеряем энергию правильных
    ji_true = world._find_by_parts(("жи", "пишется", "с", "буквой", "и"))
    kot_true = world._find_by_parts(("кот", "это", "млекопитающее"))
    a_true = world._find_by_parts(("а", "это", "гласная", "буква"))

    e_ji = ji_true.energy if ji_true else 0
    e_kot = kot_true.energy if kot_true else 0
    e_a = a_true.energy if a_true else 0

    print(f"\n  ДО атаки:")
    print(f"    'жи пишется с буквой и': energy={e_ji:.1f}")
    print(f"    'кот это млекопитающее': energy={e_kot:.1f}")
    print(f"    'а это гласная буква': energy={e_a:.1f}")

    # ════════════════════════════════════════
    # АТАКА: ложные факты
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  АТАКА: ЛОЖНЫЕ ФАКТЫ (5 повторов каждого)")
    print("=" * 60)

    LIES = [
        ["жы", "пишется", "с", "буквой", "ы"],
        ["кот", "это", "рыба"],
        ["а", "это", "согласная", "буква"],
    ]

    for _ in range(5):
        for lie in LIES:
            world.feed_sentence(lie)
            world.run(1)

    # Замеряем энергию после атаки
    ji_after = world._find_by_parts(("жи", "пишется", "с", "буквой", "и"))
    jy_lie = world._find_by_parts(("жы", "пишется", "с", "буквой", "ы"))
    kot_after = world._find_by_parts(("кот", "это", "млекопитающее"))
    kot_lie = world._find_by_parts(("кот", "это", "рыба"))
    a_after = world._find_by_parts(("а", "это", "гласная", "буква"))
    a_lie = world._find_by_parts(("а", "это", "согласная", "буква"))

    e_ji2 = ji_after.energy if ji_after else 0
    e_jy = jy_lie.energy if jy_lie else 0
    e_kot2 = kot_after.energy if kot_after else 0
    e_kot_lie = kot_lie.energy if kot_lie else 0
    e_a2 = a_after.energy if a_after else 0
    e_a_lie = a_lie.energy if a_lie else 0

    print(f"\n  ПОСЛЕ атаки:")
    print(f"    'жи пишется с буквой и': energy={e_ji2:.1f}  (было {e_ji:.1f})")
    print(f"    'жы пишется с буквой ы': energy={e_jy:.1f}  (ложь)")
    print(f"    'кот это млекопитающее': energy={e_kot2:.1f}  (было {e_kot:.1f})")
    print(f"    'кот это рыба':          energy={e_kot_lie:.1f}  (ложь)")
    print(f"    'а это гласная буква':   energy={e_a2:.1f}  (было {e_a:.1f})")
    print(f"    'а это согласная буква': energy={e_a_lie:.1f}  (ложь)")

    # ════════════════════════════════════════
    # СТАРЕНИЕ: 50 тиков
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  СТАРЕНИЕ: 50 тиков")
    print("=" * 60)

    world.run(50)

    ji_final = world._find_by_parts(("жи", "пишется", "с", "буквой", "и"))
    jy_final = world._find_by_parts(("жы", "пишется", "с", "буквой", "ы"))
    kot_final = world._find_by_parts(("кот", "это", "млекопитающее"))
    kot_lie_final = world._find_by_parts(("кот", "это", "рыба"))
    a_final = world._find_by_parts(("а", "это", "гласная", "буква"))
    a_lie_final = world._find_by_parts(("а", "это", "согласная", "буква"))

    e_ji3 = ji_final.energy if ji_final else 0
    jy_alive = jy_final.alive if jy_final else False
    e_jy3 = jy_final.energy if jy_final and jy_final.alive else 0
    e_kot3 = kot_final.energy if kot_final else 0
    kot_lie_alive = kot_lie_final.alive if kot_lie_final else False
    e_kot_lie3 = kot_lie_final.energy if kot_lie_final and kot_lie_final.alive else 0
    e_a3 = a_final.energy if a_final else 0
    a_lie_alive = a_lie_final.alive if a_lie_final else False
    e_a_lie3 = a_lie_final.energy if a_lie_final and a_lie_final.alive else 0

    print(f"\n  ПОСЛЕ старения:")
    print(f"    'жи пишется с буквой и': energy={e_ji3:.1f}  alive={ji_final.alive if ji_final else False}")
    print(f"    'жы пишется с буквой ы': energy={e_jy3:.1f}  alive={jy_alive}")
    print(f"    'кот это млекопитающее': energy={e_kot3:.1f}  alive={kot_final.alive if kot_final else False}")
    print(f"    'кот это рыба':          energy={e_kot_lie3:.1f}  alive={kot_lie_alive}")
    print(f"    'а это гласная буква':   energy={e_a3:.1f}  alive={a_final.alive if a_final else False}")
    print(f"    'а это согласная буква': energy={e_a_lie3:.1f}  alive={a_lie_alive}")

    # ════════════════════════════════════════
    # ПРОВЕРКА: ask() даёт правильные ответы?
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ПРОВЕРКА: ask() ПОСЛЕ АТАКИ")
    print("=" * 60)

    # Гласные
    vowels = visitor.query_category("гласная")
    vowels_clean = sorted(v for v in vowels if len(v) == 1)
    print(f"\n  Гласные буквы: {vowels_clean}")
    a_is_vowel = "а" in vowels_clean
    print(f"  'а' — гласная: {a_is_vowel}")

    # Кот
    kot_info = visitor.visit("кот")
    if kot_info["found"]:
        print(f"  visit('кот') братья: {sorted(kot_info['siblings'])[:10]}")
        kot_knows_mlek = "млекопитающее" in kot_info["siblings"]
        kot_knows_ryba = "рыба" in kot_info["siblings"]
        print(f"  'кот' знает 'млекопитающее': {kot_knows_mlek}")
        print(f"  'кот' знает 'рыба': {kot_knows_ryba}")
    else:
        kot_knows_mlek = False
        kot_knows_ryba = True  # если кот вообще не найден — плохо

    # ════════════════════════════════════════
    # ИТОГ
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("╔═══════════════════════════════════════════════════════╗")
    print("║     ИТОГ: ТЕСТ ИММУНИТЕТА                             ║")
    print("╠═══════════════════════════════════════════════════════╣")

    checks = []

    # 1. Правильные сильнее ложных
    ok1 = e_ji2 > e_jy
    checks.append(("'жи' сильнее 'жы' после атаки", ok1))

    ok2 = e_kot2 > e_kot_lie
    checks.append(("'кот=млекопит.' сильнее 'кот=рыба'", ok2))

    ok3 = e_a2 > e_a_lie
    checks.append(("'а=гласная' сильнее 'а=согласная'", ok3))

    # 2. После старения — правильные выжили
    ok4 = ji_final is not None and ji_final.alive
    checks.append(("'жи пишется с и' выжило", ok4))

    ok5 = kot_final is not None and kot_final.alive
    checks.append(("'кот это млекопитающее' выжило", ok5))

    # 3. Ложные ослабели или умерли
    ok6 = e_jy3 < e_ji3
    checks.append(("'жы' слабее 'жи' после старения", ok6))

    ok7 = e_kot_lie3 < e_kot3
    checks.append(("'кот=рыба' слабее 'кот=млек.' после старения", ok7))

    # 4. ask() правильно
    ok8 = a_is_vowel
    checks.append(("'а' по-прежнему гласная", ok8))

    ok9 = kot_knows_mlek
    checks.append(("'кот' знает 'млекопитающее'", ok9))

    passed = 0
    for name, ok in checks:
        s = "+" if ok else "-"
        if ok:
            passed += 1
        print(f"║  {s} {name:52s}║")

    print(f"╠═══════════════════════════════════════════════════════╣")
    print(f"║  Результат: {passed}/{len(checks)}                                     ║")

    if passed >= 7:
        print(f"║                                                       ║")
        print(f"║  ИММУНИТЕТ РАБОТАЕТ.                                 ║")
        print(f"║  Ложные факты не крепнут рядом с правильными.        ║")
    elif passed >= 5:
        print(f"║                                                       ║")
        print(f"║  ЧАСТИЧНО. Некоторая защита есть.                    ║")
    else:
        print(f"║                                                       ║")
        print(f"║  НУЖНА ДОРАБОТКА.                                    ║")

    print(f"╚═══════════════════════════════════════════════════════╝")

    print(f"\n  Статистика: {world.stats}")


if __name__ == "__main__":
    main()
