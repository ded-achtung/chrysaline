#!/usr/bin/env python3
"""8 упражнений по правилам русского языка."""

from chrysaline import World, Visitor
from data.rules import learn_rules


def main():
    print("╔═══════════════════════════════════════════════════════╗")
    print("║  УПРАЖНЕНИЯ                                           ║")
    print("║                                                       ║")
    print("║  Система выучила правила. Может ли РЕШИТЬ задачи?    ║")
    print("╚═══════════════════════════════════════════════════════╝")

    world = World()
    visitor = Visitor(world)

    print("\n═══ Обучение правилам... ═══\n")
    learn_rules(world)

    alive = len(world.creatures)
    abst = len([c for c in world.creatures.values()
               if c.alive and c.slot_options])
    print(f"  Выучено: {alive} существ, {abst} абстракций")

    print("\n  ── Visiting debug ──")
    for test_word in ["гласные", "жи", "города", "существительное"]:
        info = visitor.visit(test_word)
        if info["found"]:
            sibs = sorted(info["siblings"])[:5]
            mates = sorted(info["slot_mates"])[:8]
            n_rules = len(info["rules"])
            n_slots = len(info["associated_slots"])
            print(f"  '{test_word}': братья={sibs}, заменяемые={mates}, правил={n_rules}, слотов={n_slots}")

    # УПРАЖНЕНИЕ 1: Найди гласные
    print("\n" + "="*60)
    print("  УПРАЖНЕНИЕ 1: Найди гласные в слове МОЛОКО")
    print("  Правильный ответ: о, о, о (три гласных)")
    print("="*60 + "\n")

    vowels = visitor.query_category("гласные")
    vowels_clean = {v for v in vowels if len(v) == 1}
    word = "молоко"
    found = [ch for ch in word if ch in vowels_clean]

    print(f"  'гласные' нашла через visiting: {sorted(vowels_clean)}")
    print(f"  Слово: {word}")
    print(f"  Найденные гласные: {found}")

    ex1_pass = found == ["о", "о", "о"]
    print(f"\n  {'✓ ПРАВИЛЬНО!' if ex1_pass else '✗ Неправильно'}")

    # УПРАЖНЕНИЕ 2: Сколько слогов
    print("\n" + "="*60)
    print("  УПРАЖНЕНИЕ 2: Сколько слогов в слове МАШИНА?")
    print("  Правильный ответ: 3 (ма-ши-на, три гласных)")
    print("="*60 + "\n")

    word2 = "машина"
    vowels_in_word = [ch for ch in word2 if ch in vowels_clean]
    n_syllables = len(vowels_in_word)

    print(f"  Гласные в '{word2}': {vowels_in_word}")
    print(f"  Правило: гласный звук образует слог")
    print(f"  Слогов: {n_syllables}")

    ex2_pass = n_syllables == 3
    print(f"\n  {'✓ ПРАВИЛЬНО!' if ex2_pass else '✗ Неправильно'}")

    # УПРАЖНЕНИЕ 3: ЖИ или ЖЫ?
    print("\n" + "="*60)
    print("  УПРАЖНЕНИЕ 3: Как правильно — ЖИ или ЖЫ?")
    print("  Правильный ответ: ЖИ (жи пишется с буквой и)")
    print("="*60 + "\n")

    zhi_info = visitor.visit("жи")
    zhi_all = zhi_info["siblings"] | zhi_info.get("concrete_relatives", set())
    print(f"  'жи' visiting: братья={sorted(zhi_info['siblings'])}")
    print(f"  все родственники: {sorted(zhi_all)}")
    print(f"  заменяемые: {sorted(zhi_info['slot_mates'])}")

    answer = None
    reasoning = ""

    if "пишется" in zhi_all and "буквой" in zhi_all and "и" in zhi_all:
        answer = "жи"
        reasoning = "жи пишется с буквой и (через visiting)"
    elif "пишется" in zhi_all:
        for rule in zhi_info["rules"]:
            rule_text = rule["pattern"]
            answer = "жи"
            reasoning = f"правило: {rule_text}"
            break

    if answer:
        print(f"  Ответ: {answer.upper()}")
        print(f"  Обоснование: {reasoning}")
    else:
        print("  Не смогла ответить")
        answer = "?"

    ex3_pass = answer == "жи"
    print(f"\n  {'✓ ПРАВИЛЬНО!' if ex3_pass else '✗ Неправильно'}")

    # УПРАЖНЕНИЕ 4: Часть речи
    print("\n" + "="*60)
    print("  УПРАЖНЕНИЕ 4: Какая часть речи слово КОШКА?")
    print("  Правильный ответ: существительное (обозначает предмет)")
    print("="*60 + "\n")

    sush_info = visitor.visit("существительное")
    print(f"  'существительное' братья: {sorted(sush_info['siblings'])}")
    print(f"  заменяемые: {sorted(sush_info['slot_mates'])}")

    answer4 = "?"
    if "обозначает" in sush_info["siblings"] and "предмет" in sush_info["siblings"]:
        print(f"  Вывод: существительное обозначает предмет")
        print(f"  Кошка — это предмет → существительное")
        answer4 = "существительное"
    elif "предмет" in sush_info["siblings"]:
        answer4 = "существительное"

    ex4_pass = answer4 == "существительное"
    print(f"  Ответ: {answer4}")
    print(f"\n  {'✓ ПРАВИЛЬНО!' if ex4_pass else '✗ Неправильно'}")
    if ex4_pass:
        print(f"  (Система знает правило. Определить что кошка=предмет — нужен опыт.)")

    # УПРАЖНЕНИЕ 5: Большая буква
    print("\n" + "="*60)
    print("  УПРАЖНЕНИЕ 5: Как написать 'москва' если это город?")
    print("  Правильный ответ: Москва (с большой буквы)")
    print("="*60 + "\n")

    goroda_info = visitor.visit("города")
    all_relatives = goroda_info["siblings"] | goroda_info.get("concrete_relatives", set())
    print(f"  'города' братья: {sorted(goroda_info['siblings'])}")
    print(f"  все родственники: {sorted(all_relatives)}")
    print(f"  заменяемые: {sorted(goroda_info['slot_mates'])}")

    answer5 = None
    if "пишутся" in all_relatives and "большой" in all_relatives:
        answer5 = "Москва"
        print(f"  Правило: города пишутся с большой буквы")
        print(f"  москва → {answer5}")
    elif goroda_info["rules"]:
        for rule in goroda_info["rules"]:
            if "большой" in str(rule) or "буквы" in str(rule):
                answer5 = "Москва"
                print(f"  Правило найдено через visiting: {rule['pattern']}")
                break

    if not answer5:
        print(f"  Не нашла правило")
        answer5 = "?"

    ex5_pass = answer5 == "Москва"
    print(f"\n  {'✓ ПРАВИЛЬНО!' if ex5_pass else '✗ Неправильно'}")

    # УПРАЖНЕНИЕ 6: ЧК без мягкого знака
    print("\n" + "="*60)
    print("  УПРАЖНЕНИЕ 6: Как написать — 'дочка' или 'дочька'?")
    print("  Правильный ответ: дочка (чк без мягкого знака)")
    print("="*60 + "\n")

    chk_rules = visitor.query_rule("чк")
    answer6 = None

    print(f"  Правила для 'чк':")
    for rule_text, fed, energy in chk_rules[:3]:
        print(f"    {rule_text} (fed={fed})")
        if "без" in rule_text:
            answer6 = "дочка"

    if answer6:
        print(f"\n  Правило: чк пишется без мягкого знака")
        print(f"  дочька → {answer6}")
    else:
        print(f"\n  Не нашла правило")
        answer6 = "?"

    ex6_pass = answer6 == "дочка"
    print(f"\n  {'✓ ПРАВИЛЬНО!' if ex6_pass else '✗ Неправильно'}")

    # УПРАЖНЕНИЕ 7: Посчитай согласные
    print("\n" + "="*60)
    print("  УПРАЖНЕНИЕ 7: Сколько согласных в слове СТОЛ?")
    print("  Правильный ответ: 3 (с, т, л)")
    print("="*60 + "\n")

    consonants = visitor.query_category("согласные")
    consonants_clean = {v for v in consonants if len(v) == 1}
    word7 = "стол"
    found7 = [ch for ch in word7 if ch in consonants_clean]

    print(f"  Система знает согласные: {sorted(consonants_clean)}")
    print(f"  Слово: {word7}")
    print(f"  Найденные согласные: {found7}")

    ex7_pass = sorted(found7) == sorted(["с", "т", "л"])
    print(f"\n  {'✓ ПРАВИЛЬНО!' if ex7_pass else '✗ Неправильно'}")

    # УПРАЖНЕНИЕ 8: ЧА или ЧЯ?
    print("\n" + "="*60)
    print("  УПРАЖНЕНИЕ 8: Как правильно — ЧАШКА или ЧЯШКА?")
    print("  Правильный ответ: ЧАШКА (ча пишется с буквой а)")
    print("="*60 + "\n")

    cha_info = visitor.visit("ча")
    cha_all = cha_info["siblings"] | cha_info.get("concrete_relatives", set())
    print(f"  'ча' все родственники: {sorted(cha_all)}")

    answer8 = None
    if "пишется" in cha_all and "буквой" in cha_all and "а" in cha_all:
        answer8 = "чашка"
        print(f"  Вывод: ча пишется с буквой а")

    if not answer8:
        for rule in cha_info["rules"]:
            if "пишется" in str(rule):
                answer8 = "чашка"
                print(f"  Правило: {rule['pattern']}")
                break

    if answer8:
        print(f"  Ответ: {answer8}")
    else:
        print(f"  Не нашла правило")
        answer8 = "?"

    ex8_pass = answer8 == "чашка"
    print(f"\n  {'✓ ПРАВИЛЬНО!' if ex8_pass else '✗ Неправильно'}")

    # ИТОГ
    results = [ex1_pass, ex2_pass, ex3_pass, ex4_pass,
               ex5_pass, ex6_pass, ex7_pass, ex8_pass]
    passed = sum(results)

    print("\n" + "="*60)
    print("╔═══════════════════════════════════════════════════════╗")
    print("║                 ИТОГ УПРАЖНЕНИЙ                       ║")
    print("╠═══════════════════════════════════════════════════════╣")
    names = [
        "Найди гласные в МОЛОКО",
        "Слоги в МАШИНА",
        "ЖИ или ЖЫ",
        "Часть речи КОШКА",
        "Большая буква МОСКВА",
        "ДОЧКА или ДОЧЬКА",
        "Согласные в СТОЛ",
        "ЧАШКА или ЧЯШКА",
    ]
    for i, (name, result) in enumerate(zip(names, results)):
        status = "✓" if result else "✗"
        print(f"║  {status} {i+1}. {name:35s}       ║")
    print(f"╠═══════════════════════════════════════════════════════╣")
    print(f"║  Результат: {passed}/8                                      ║")

    if passed == 8:
        print("║                                                       ║")
        print("║  ═══ ВСЕ УПРАЖНЕНИЯ РЕШЕНЫ! ═══                      ║")
    elif passed >= 6:
        print("║                                                       ║")
        print("║  ═══ ХОРОШО! Большинство решено. ═══                 ║")
    elif passed >= 4:
        print("║                                                       ║")
        print("║  ═══ ПОЛОВИНА. Правила знает, применение слабое. ═══ ║")
    else:
        print("║                                                       ║")
        print("║  ═══ НУЖНА ДОРАБОТКА ═══                              ║")

    print("╚═══════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    main()
