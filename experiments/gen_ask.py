#!/usr/bin/env python3
"""Генерация предложений из абстракций и ответы на произвольные вопросы."""

from chrysaline import World, Visitor, Generator
from data.rules import learn_rules
from data.experience import EXPERIENCE


def experiment_generation():
    print("╔═══════════════════════════════════════════════════════╗")
    print("║  ГЕНЕРАЦИЯ: абстракция → конкретные предложения       ║")
    print("╚═══════════════════════════════════════════════════════╝")

    world = World()
    generator = Generator(world)

    for r in range(3):
        for sent in EXPERIENCE:
            world.feed_sentence(sent)
            world.run(1)

    alive = len(world.creatures)
    abst = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"\n  Обучено: {alive} существ, {abst} абстракций")

    # 1. "кот·ел"
    print(f"\n  ── Генерация из 'кот·ел' ──")
    gen_kot = generator.generate_from("кот", max_per_slot=10)
    kot_el_found = False
    for g in gen_kot:
        if "ел" in g["pattern"]:
            print(f"  Паттерн: {g['pattern']} (fed={g['fed']})")
            for s in g["sentences"]:
                print(f"    → {s}")
            kot_el_found = True

    # 2. "мама·мыла"
    print(f"\n  ── Генерация из 'мама·мыла' ──")
    gen_mama = generator.generate_from("мама", max_per_slot=10)
    mama_myla_found = False
    for g in gen_mama:
        if "мыла" in g["pattern"]:
            print(f"  Паттерн: {g['pattern']} (fed={g['fed']})")
            for s in g["sentences"]:
                print(f"    → {s}")
            mama_myla_found = True

    # 3. "птица"
    print(f"\n  ── Генерация из 'птица' ──")
    gen_bird = generator.generate_from("птица", max_per_slot=10)
    bird_found = False
    for g in gen_bird:
        print(f"  Паттерн: {g['pattern']} (fed={g['fed']})")
        for s in g["sentences"][:5]:
            print(f"    → {s}")
        if len(g["sentences"]) > 5:
            print(f"    ... и ещё {len(g['sentences']) - 5}")
        bird_found = True

    # 4. Генерация из правил
    print(f"\n  ── Генерация из правил (учебник) ──")
    world2 = World()
    generator2 = Generator(world2)
    learn_rules(world2)
    gen_glasnye = generator2.generate_from("гласные", max_per_slot=10)
    glasnye_found = False
    for g in gen_glasnye:
        if "звуки" in g["pattern"] and "это" in g["pattern"]:
            print(f"  Паттерн: {g['pattern']} (fed={g['fed']})")
            for s in g["sentences"]:
                print(f"    → {s}")
            glasnye_found = True
            break

    gen_zhi = generator2.generate_from("пишется", max_per_slot=10)
    zhi_found = False
    for g in gen_zhi:
        print(f"  Паттерн: {g['pattern']} (fed={g['fed']})")
        for s in g["sentences"][:6]:
            print(f"    → {s}")
        zhi_found = True

    ok1 = kot_el_found
    ok2 = mama_myla_found
    ok3 = bird_found
    ok4 = glasnye_found

    print(f"\n  ── Результат ──")
    print(f"  ✓ 'кот·ел·$0' → предложения: {ok1}")
    print(f"  ✓ 'мама·мыла·$0' → предложения: {ok2}")
    print(f"  ✓ 'птица·...' → предложения: {ok3}")
    print(f"  ✓ 'гласные·звуки·это·$0' → перечисление: {ok4}")

    ok = ok1 and ok2 and ok3 and ok4
    print(f"\n  {'═══ ГЕНЕРАЦИЯ РАБОТАЕТ! ═══' if ok else '═══ НУЖНА ДОРАБОТКА ═══'}")
    return ok


def experiment_questions():
    print("\n╔═══════════════════════════════════════════════════════╗")
    print("║  ВОПРОСЫ: произвольные вопросы → ответ через visiting ║")
    print("╚═══════════════════════════════════════════════════════╝")

    world = World()
    generator = Generator(world)

    learn_rules(world)
    for r in range(3):
        for sent in EXPERIENCE:
            world.feed_sentence(sent)
            world.run(1)

    alive = len(world.creatures)
    abst = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"\n  Обучено: {alive} существ, {abst} абстракций")

    questions = [
        {
            "q": "что ест кот?",
            "expect_any": {"рыбу", "мышку", "сметану"},
            "desc": "кот ест → {рыбу, мышку, сметану}",
        },
        {
            "q": "что мыла мама?",
            "expect_any": {"раму", "посуду", "окно"},
            "desc": "мама мыла → {раму, посуду, окно}",
        },
        {
            "q": "где спал кот?",
            "expect_any": {"диване", "коврике"},
            "desc": "кот спал на → {диване, коврике}",
        },
        {
            "q": "что читал папа?",
            "expect_any": {"газету", "книгу"},
            "desc": "папа читал → {газету, книгу}",
        },
        {
            "q": "что варила мама?",
            "expect_any": {"кашу", "суп"},
            "desc": "мама варила → {кашу, суп}",
        },
        {
            "q": "где плавала рыба?",
            "expect_any": {"реке", "озере", "море"},
            "desc": "рыба плавала в → {реке, озере, море}",
        },
        {
            "q": "какие гласные звуки?",
            "expect_any": {"а", "о", "у", "ы", "и", "э"},
            "desc": "гласные → {а,о,у,ы,и,э}",
        },
        {
            "q": "как пела птица?",
            "expect_any": {"громко", "красиво"},
            "desc": "птица пела → {громко, красиво}",
        },
    ]

    results = []
    for q_info in questions:
        question = q_info["q"]
        expected = q_info["expect_any"]
        desc = q_info["desc"]

        answer = generator.ask(question)

        found = set(answer["answers"]) & expected
        ok = len(found) > 0

        print(f"\n  Вопрос: «{question}»")
        print(f"    Ожидаем (любое из): {sorted(expected)}")
        print(f"    Ответ: {answer['answers'][:8]}")
        if answer["reasoning"]:
            for r in answer["reasoning"][:3]:
                print(f"    Путь: {r}")
        print(f"    Совпало: {sorted(found)} → {'✓' if ok else '✗'}")
        results.append((desc, ok))

    passed = sum(1 for _, ok in results if ok)
    print(f"\n  ── Итог вопросов ──")
    for desc, ok in results:
        s = "✓" if ok else "✗"
        print(f"  {s} {desc}")

    print(f"\n  Результат: {passed}/{len(results)}")
    ok = passed >= 6
    print(f"\n  {'═══ ВОПРОСЫ РАБОТАЮТ! ═══' if ok else '═══ НУЖНА ДОРАБОТКА ═══'}")
    return ok, passed, len(results)


def main():
    print("=" * 60)
    print("  ГЕНЕРАЦИЯ И ВОПРОСЫ")
    print("=" * 60)

    r1 = experiment_generation()
    r2_ok, r2_passed, r2_total = experiment_questions()

    print("\n" + "=" * 60)
    print("╔═══════════════════════════════════════════════════════╗")
    print("║            ИТОГ: ГЕНЕРАЦИЯ И ВОПРОСЫ                  ║")
    print("╠═══════════════════════════════════════════════════════╣")
    s1 = "✓" if r1 else "✗"
    s2 = "✓" if r2_ok else "✗"
    print(f"║  {s1} 1. Генерация из абстракций                      ║")
    print(f"║  {s2} 2. Произвольные вопросы ({r2_passed}/{r2_total})                      ║")
    print(f"╠═══════════════════════════════════════════════════════╣")
    if r1 and r2_ok:
        print("║  ═══ ОБА ЭКСПЕРИМЕНТА ПРОЙДЕНЫ! ═══                  ║")
    else:
        print("║  ═══ ЧАСТИЧНО ═══                                     ║")
    print("╚═══════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    main()
