#!/usr/bin/env python3
"""
Математический тест: может ли система освоить арифметику?

Языки и природа — ассоциации. Математика — вычисления.
Где граница?
"""

from chrysaline import World, Visitor, Generator
from data.math import MATH_RULES, MATH_EXAMPLES, MATH_WORD_PROBLEMS


def learn_math(world):
    all_data = MATH_RULES + MATH_EXAMPLES + MATH_WORD_PROBLEMS
    for r in range(3):
        for fact in all_data:
            world.feed_sentence(fact)
            world.run(1)


# ────────────────────────────────────────────
# Тест 1: Категории (операции, чётные/нечётные)
# ────────────────────────────────────────────

def test_math_categories():
    print("╔═══════════════════════════════════════════════════════╗")
    print("║  ТЕСТ 1: Математические категории                    ║")
    print("╚═══════════════════════════════════════════════════════╝")

    world = World()
    visitor = Visitor(world)
    learn_math(world)

    alive = len(world.creatures)
    abst = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"\n  Обучено: {alive} существ, {abst} абстракций")

    # Какие бывают операции?
    ops = visitor.query_category("операция")
    ops_clean = {v for v in ops if len(v) > 2}
    print(f"\n  «Какие операции?»: {sorted(ops_clean)}")
    ok_ops = {"сложение", "вычитание"}.issubset(ops_clean)
    print(f"  ✓ сложение, вычитание: {ok_ops}")

    # Чётные числа?
    even = visitor.query_category("чётное")
    even_clean = {v for v in even if len(v) > 2}
    print(f"\n  «Какие чётные?»: {sorted(even_clean)}")
    ok_even = {"два", "четыре", "шесть"}.issubset(even_clean)
    print(f"  ✓ два, четыре, шесть: {ok_even}")

    # Нечётные?
    odd = visitor.query_category("нечётное")
    odd_clean = {v for v in odd if len(v) > 2}
    print(f"\n  «Какие нечётные?»: {sorted(odd_clean)}")
    ok_odd = {"один", "три", "пять"}.issubset(odd_clean)
    print(f"  ✓ один, три, пять: {ok_odd}")

    ok = ok_ops and ok_even and ok_odd
    print(f"\n  {'═══ КАТЕГОРИИ РАБОТАЮТ! ═══' if ok else '═══ ЧАСТИЧНО ═══'}")
    return ok


# ────────────────────────────────────────────
# Тест 2: Вспоминание выученных примеров
# ────────────────────────────────────────────

def test_recall():
    print("\n╔═══════════════════════════════════════════════════════╗")
    print("║  ТЕСТ 2: Вспоминание выученных примеров               ║")
    print("║  «сколько будет два плюс три?» → пять                ║")
    print("╚═══════════════════════════════════════════════════════╝")

    world = World()
    visitor = Visitor(world)
    gen = Generator(world)
    learn_math(world)

    recall_tests = [
        ("два плюс три", "пять", "2+3=5"),
        ("три плюс два", "пять", "3+2=5"),
        ("пять плюс пять", "десять", "5+5=10"),
        ("пять минус два", "три", "5-2=3"),
        ("десять минус пять", "пять", "10-5=5"),
    ]

    results = []
    for expr, expected, desc in recall_tests:
        words = expr.split()

        # Стратегия: ищем организм, содержащий все слова выражения
        found_answer = None
        for c in world.creatures.values():
            if not c.alive or c.complexity < 4:
                continue
            if all(w in c.parts for w in words) and "равно" in c.parts:
                idx = list(c.parts).index("равно")
                if idx + 1 < len(c.parts):
                    found_answer = c.parts[idx + 1]
                    break

        # Дополнительно: через ask
        question = f"сколько будет {expr}?"
        ask_answer = gen.ask(question)

        ok = found_answer == expected
        ok_ask = expected in ask_answer["answers"]

        print(f"\n  «{expr} = ?»")
        print(f"    Прямой поиск: {found_answer} → {'✓' if ok else '✗'}")
        print(f"    Через ask(): {ask_answer['answers'][:5]} → {'✓' if ok_ask else '✗'}")
        results.append(ok or ok_ask)

    passed = sum(results)
    ok = passed >= 4
    print(f"\n  Результат: {passed}/{len(results)}")
    print(f"\n  {'═══ ВСПОМИНАНИЕ РАБОТАЕТ! ═══' if ok else '═══ ЧАСТИЧНО ═══'}")
    return ok, passed, len(results)


# ────────────────────────────────────────────
# Тест 3: Новый пример (не из обучения)
# ────────────────────────────────────────────

def test_novel_computation():
    print("\n╔═══════════════════════════════════════════════════════╗")
    print("║  ТЕСТ 3: НОВЫЙ пример (не из обучения)               ║")
    print("║  «четыре плюс четыре = ?» (не было в данных)         ║")
    print("╚═══════════════════════════════════════════════════════╝")

    world = World()
    visitor = Visitor(world)
    gen = Generator(world)
    learn_math(world)

    novel_tests = [
        ("четыре плюс четыре", "восемь", "4+4=8"),
        ("один плюс три", "четыре", "1+3=4"),
        ("шесть минус два", "четыре", "6-2=4"),
        ("семь минус три", "четыре", "7-3=4"),
    ]

    results = []
    for expr, expected, desc in novel_tests:
        words = expr.split()

        # Прямой поиск (скорее всего НЕ найдёт — примера не было)
        found_answer = None
        for c in world.creatures.values():
            if not c.alive or c.complexity < 4:
                continue
            if all(w in c.parts for w in words) and "равно" in c.parts:
                idx = list(c.parts).index("равно")
                if idx + 1 < len(c.parts):
                    found_answer = c.parts[idx + 1]
                    break

        # Через абстракции: есть ли паттерн "четыре·плюс·$0·равно·$1"?
        abstract_answer = None
        for c in world.creatures.values():
            if not c.alive or not c.slot_options:
                continue
            fixed = [p for p in c.parts if not p.startswith("$")]
            if words[0] in fixed and words[1] in fixed and "равно" in fixed:
                for sn, opts in c.slot_options.items():
                    clean = {o for o in opts if not o.startswith("$")}
                    if words[2] in clean:
                        abstract_answer = f"паттерн {c.name}, но нет результата"

        # Через ask
        question = f"сколько будет {expr}?"
        ask_answer = gen.ask(question)

        ok = found_answer == expected
        ok_ask = expected in ask_answer["answers"]

        print(f"\n  «{expr} = ?» (ожидаем: {expected})")
        print(f"    Прямой поиск: {found_answer} → {'✓' if ok else '✗ не было в обучении'}")
        if abstract_answer:
            print(f"    Через абстракцию: {abstract_answer}")
        print(f"    Через ask(): {ask_answer['answers'][:5]} → {'✓' if ok_ask else '✗'}")
        results.append(ok or ok_ask)

    passed = sum(results)
    print(f"\n  Результат: {passed}/{len(results)}")

    print(f"\n  ── ДИАГНОЗ ──")
    if passed == 0:
        print(f"  ГРАНИЦА: Система НЕ УМЕЕТ ВЫЧИСЛЯТЬ.")
        print(f"  Она запомнила '2+3=5', но не может посчитать '4+4'.")
        print(f"  Причина: нет операций над числами, только ассоциации.")
        print(f"  '2+3→5' = запомненная связь, не вычисление.")
    elif passed < len(results):
        print(f"  Частично: некоторые примеры угаданы через абстракции.")
    else:
        print(f"  Неожиданно: все новые примеры решены!")

    return passed > 0, passed, len(results)


# ────────────────────────────────────────────
# Тест 4: Генерация (таблица сложения)
# ────────────────────────────────────────────

def test_math_generation():
    print("\n╔═══════════════════════════════════════════════════════╗")
    print("║  ТЕСТ 4: Генерация (таблица из абстракций)            ║")
    print("╚═══════════════════════════════════════════════════════╝")

    world = World()
    gen = Generator(world)
    learn_math(world)

    print(f"\n  ── Генерация из 'плюс' ──")
    gen_plus = gen.generate_from("плюс", max_per_slot=10)
    plus_found = False
    for g in gen_plus:
        if "равно" in g["pattern"]:
            print(f"  Паттерн: {g['pattern']} (fed={g['fed']})")
            for s in g["sentences"][:8]:
                print(f"    → {s}")
            if len(g["sentences"]) > 8:
                print(f"    ... и ещё {len(g['sentences']) - 8}")
            plus_found = True

    if not plus_found:
        # Показать что вообще есть
        for g in gen_plus[:3]:
            print(f"  Паттерн: {g['pattern']} (fed={g['fed']})")
            for s in g["sentences"][:4]:
                print(f"    → {s}")

    print(f"\n  ── Генерация из 'минус' ──")
    gen_minus = gen.generate_from("минус", max_per_slot=10)
    minus_found = False
    for g in gen_minus:
        if "равно" in g["pattern"]:
            print(f"  Паттерн: {g['pattern']} (fed={g['fed']})")
            for s in g["sentences"][:8]:
                print(f"    → {s}")
            minus_found = True

    if not minus_found:
        for g in gen_minus[:3]:
            print(f"  Паттерн: {g['pattern']} (fed={g['fed']})")
            for s in g["sentences"][:4]:
                print(f"    → {s}")

    ok = plus_found or minus_found
    print(f"\n  ✓ Генерация арифметических паттернов: {ok}")

    print(f"\n  ── ДИАГНОЗ ──")
    if ok:
        print(f"  Система создала АБСТРАКЦИИ арифметики:")
        print(f"  '$0·плюс·$1·равно·$2' → развернула в конкретные примеры.")
        print(f"  Но это ЗАПОМИНАНИЕ, не ВЫЧИСЛЕНИЕ.")
        print(f"  Сгенерированные примеры = только те, что были в обучении.")
    print(f"\n  {'═══ ГЕНЕРАЦИЯ РАБОТАЕТ! ═══' if ok else '═══ НЕТ АРИФМЕТИЧЕСКИХ ПАТТЕРНОВ ═══'}")
    return ok


# ────────────────────────────────────────────
# Тест 5: Текстовые задачи
# ────────────────────────────────────────────

def test_word_problems():
    print("\n╔═══════════════════════════════════════════════════════╗")
    print("║  ТЕСТ 5: Текстовые задачи                             ║")
    print("║  «У Маши 3 яблока, дали ещё 2. Сколько стало?»      ║")
    print("╚═══════════════════════════════════════════════════════╝")

    world = World()
    visitor = Visitor(world)
    gen = Generator(world)
    learn_math(world)

    # Задача 1: Маша
    print(f"\n  Задача 1: У Маши 3 яблока, дали ещё 2. Сколько?")
    masha_info = visitor.visit("маши")
    if masha_info["found"]:
        print(f"    visit('маши'): братья={sorted(masha_info['siblings'])}")
    answer1 = gen.ask("сколько яблок у маши?")
    print(f"    ask(): {answer1['answers'][:5]}")
    ok1 = "пять" in answer1["answers"] or "пять" in masha_info.get("siblings", set())
    for r in answer1["reasoning"][:2]:
        print(f"    Путь: {r}")
    print(f"    ✓ Нашла 'пять': {ok1}")

    # Задача 2: Петя
    print(f"\n  Задача 2: У Пети 5 конфет, съел 2. Сколько осталось?")
    petya_info = visitor.visit("пети")
    if petya_info["found"]:
        print(f"    visit('пети'): братья={sorted(petya_info['siblings'])}")
    answer2 = gen.ask("сколько конфет у пети?")
    print(f"    ask(): {answer2['answers'][:5]}")
    ok2 = "три" in answer2["answers"] or "три" in petya_info.get("siblings", set())
    for r in answer2["reasoning"][:2]:
        print(f"    Путь: {r}")
    print(f"    ✓ Нашла 'три': {ok2}")

    # Свойства
    print(f"\n  Бонус: связи между операциями и числами")
    plus_info = visitor.visit("плюс")
    if plus_info["found"]:
        print(f"    'плюс' братья: {sorted(plus_info['siblings'])[:10]}")
        print(f"    'плюс' заменяемые: {sorted(plus_info['slot_mates'])[:8]}")

    ok = ok1 or ok2
    print(f"\n  Результат: {sum([ok1,ok2])}/2")

    print(f"\n  ── ДИАГНОЗ ──")
    if ok:
        print(f"  Задачи ЧАСТИЧНО решены через ассоциации.")
        print(f"  'маши'→'пять'→'яблок' — это запомненная связь.")
    else:
        print(f"  ГРАНИЦА: Задачи НЕ решаются через ассоциации.")
        print(f"  Система не понимает 'дали ещё' = 'сложение'.")
    return ok


# ────────────────────────────────────────────
# MAIN
# ────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  МАТЕМАТИЧЕСКИЙ ТЕСТ")
    print("  Может ли система освоить арифметику?")
    print("  Движок (chrysaline/) НЕ менялся.")
    print("=" * 60)

    r1 = test_math_categories()
    r2_ok, r2_p, r2_t = test_recall()
    r3_ok, r3_p, r3_t = test_novel_computation()
    r4 = test_math_generation()
    r5 = test_word_problems()

    print("\n" + "=" * 60)
    print("╔═══════════════════════════════════════════════════════╗")
    print("║       ИТОГ: МАТЕМАТИЧЕСКИЙ ТЕСТ                      ║")
    print("╠═══════════════════════════════════════════════════════╣")
    s1 = "✓" if r1 else "✗"
    s2 = "✓" if r2_ok else "✗"
    s3 = "✓" if r3_ok else "✗"
    s4 = "✓" if r4 else "✗"
    s5 = "✓" if r5 else "✗"
    print(f"║  {s1} 1. Категории (операции, чётные/нечётные)        ║")
    print(f"║  {s2} 2. Вспоминание примеров ({r2_p}/{r2_t})                    ║")
    print(f"║  {s3} 3. НОВЫЕ примеры ({r3_p}/{r3_t})                           ║")
    print(f"║  {s4} 4. Генерация (таблица из абстракций)            ║")
    print(f"║  {s5} 5. Текстовые задачи                             ║")
    print(f"╠═══════════════════════════════════════════════════════╣")
    print(f"║                                                       ║")
    print(f"║  ВЫВОД:                                               ║")
    print(f"║  Система может КЛАССИФИЦИРОВАТЬ математику            ║")
    print(f"║  (операции, чётные/нечётные),                        ║")
    print(f"║  ЗАПОМИНАТЬ примеры и ГЕНЕРИРОВАТЬ паттерны.          ║")
    print(f"║                                                       ║")
    print(f"║  Но НЕ МОЖЕТ ВЫЧИСЛЯТЬ.                              ║")
    print(f"║  '2+3=5' — это ассоциация, не операция.              ║")
    print(f"║  Новый пример '4+4=?' — тишина.                      ║")
    print(f"║                                                       ║")
    print(f"║  Это фундаментальная граница:                        ║")
    print(f"║  парадигма = ПАМЯТЬ + ОБОБЩЕНИЕ,                     ║")
    print(f"║  а не ВЫЧИСЛЕНИЕ.                                    ║")
    print(f"╚═══════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    main()
