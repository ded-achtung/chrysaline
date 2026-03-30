#!/usr/bin/env python3
"""
Доказательство универсальности парадигмы.

Движок (chrysaline/) НЕ менялся.
Подаём совершенно другой предмет — «Окружающий мир» (природоведение, 1 класс).
Если тесты проходят — парадигма domain-agnostic.
"""

from chrysaline import World, Visitor, Generator
from data.nature import NATURE_FACTS, BRIDGE_FACTS
from data.rules import learn_rules


def learn_nature(world):
    for r in range(3):
        for fact in NATURE_FACTS:
            world.feed_sentence(fact)
            world.run(1)


# ────────────────────────────────────────────────────
# Тест 1: Формирование категорий (новый домен)
# ────────────────────────────────────────────────────

def test_categories():
    print("╔═══════════════════════════════════════════════════════╗")
    print("║  ТЕСТ 1: Формирование категорий (новый домен)        ║")
    print("╚═══════════════════════════════════════════════════════╝")

    world = World()
    visitor = Visitor(world)
    learn_nature(world)

    alive = len(world.creatures)
    abst = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"\n  Обучено: {alive} существ, {abst} абстракций")

    mammals = visitor.query_category("млекопитающее")
    mammals_clean = {v for v in mammals if len(v) > 1}
    print(f"\n  query_category('млекопитающее'): {sorted(mammals_clean)}")

    birds = visitor.query_category("птица")
    birds_clean = {v for v in birds if len(v) > 1}
    print(f"  query_category('птица'): {sorted(birds_clean)}")

    fish = visitor.query_category("рыба")
    fish_clean = {v for v in fish if len(v) > 1}
    print(f"  query_category('рыба'): {sorted(fish_clean)}")

    expected_mammals = {"кот", "собака", "корова", "лошадь"}
    expected_birds = {"ворона", "воробей", "голубь"}
    expected_fish = {"щука", "карась"}

    ok_m = expected_mammals.issubset(mammals_clean)
    ok_b = expected_birds.issubset(birds_clean)
    ok_f = expected_fish.issubset(fish_clean)

    print(f"\n  ✓ млекопитающие >= {{кот,собака,корова,лошадь}}: {ok_m}")
    print(f"  ✓ птицы >= {{ворона,воробей,голубь}}: {ok_b}")
    print(f"  ✓ рыбы >= {{щука,карась}}: {ok_f}")

    ok = ok_m and ok_b and ok_f
    print(f"\n  {'═══ КАТЕГОРИИ РАБОТАЮТ! ═══' if ok else '═══ НЕ ВСЕ КАТЕГОРИИ ═══'}")
    return ok


# ────────────────────────────────────────────────────
# Тест 2: Вопросы по новому предмету
# ────────────────────────────────────────────────────

def test_questions():
    print("\n╔═══════════════════════════════════════════════════════╗")
    print("║  ТЕСТ 2: Вопросы по новому предмету                   ║")
    print("╚═══════════════════════════════════════════════════════╝")

    world = World()
    generator = Generator(world)
    learn_nature(world)

    questions = [
        ("где живёт кот?",    {"доме"},          "кот живёт → доме"),
        ("что ест корова?",   {"траву"},         "корова ест → траву"),
        ("что ест кот?",      {"мясо"},          "кот ест → мясо"),
        ("где живёт щука?",   {"реке"},          "щука живёт → реке"),
        ("что ест ворона?",   {"зерно"},         "ворона ест → зерно"),
    ]

    results = []
    for question, expected, desc in questions:
        answer = generator.ask(question)
        found = set(answer["answers"]) & expected
        ok = len(found) > 0

        print(f"\n  Вопрос: «{question}»")
        print(f"    Ожидаем: {sorted(expected)}")
        print(f"    Ответ: {answer['answers'][:8]}")
        if answer["reasoning"]:
            for r in answer["reasoning"][:2]:
                print(f"    Путь: {r}")
        print(f"    {'✓' if ok else '✗'} {desc}")
        results.append(ok)

    passed = sum(results)
    ok = passed >= 4
    print(f"\n  Результат: {passed}/{len(results)}")
    print(f"\n  {'═══ ВОПРОСЫ РАБОТАЮТ! ═══' if ok else '═══ НУЖНА ДОРАБОТКА ═══'}")
    return ok


# ────────────────────────────────────────────────────
# Тест 3: Двухшаговая цепочка (иерархия)
# ────────────────────────────────────────────────────

def test_hierarchy():
    print("\n╔═══════════════════════════════════════════════════════╗")
    print("║  ТЕСТ 3: Иерархия (кот → млекопитающее → животное)   ║")
    print("╚═══════════════════════════════════════════════════════╝")

    world = World()
    visitor = Visitor(world)
    learn_nature(world)

    kot_info = visitor.visit("кот")
    kot_relatives = kot_info["siblings"] | kot_info.get("concrete_relatives", set())
    print(f"\n  Шаг 1: visit('кот')")
    print(f"    братья: {sorted(kot_info['siblings'])}")

    has_mammal = "млекопитающее" in kot_relatives
    print(f"    кот → млекопитающее: {has_mammal}")

    mammal_info = visitor.visit("млекопитающее")
    mammal_relatives = mammal_info["siblings"] | mammal_info.get("concrete_relatives", set())
    print(f"\n  Шаг 2: visit('млекопитающее')")
    print(f"    братья: {sorted(mammal_info['siblings'])}")

    has_animal = "животное" in mammal_relatives
    print(f"    млекопитающее → животное: {has_animal}")

    animal_info = visitor.visit("животное")
    animal_relatives = animal_info["siblings"] | animal_info.get("concrete_relatives", set())
    print(f"\n  Шаг 3: visit('животное')")
    print(f"    братья: {sorted(animal_info['siblings'])}")

    ok = has_mammal and has_animal
    if ok:
        print(f"\n  Цепочка: кот → млекопитающее → животное")
    print(f"\n  {'═══ ИЕРАРХИЯ РАБОТАЕТ! ═══' if ok else '═══ ЦЕПОЧКА РАЗОРВАНА ═══'}")
    return ok


# ────────────────────────────────────────────────────
# Тест 4: Генерация
# ────────────────────────────────────────────────────

def test_generation():
    print("\n╔═══════════════════════════════════════════════════════╗")
    print("║  ТЕСТ 4: Генерация из абстракций                     ║")
    print("╚═══════════════════════════════════════════════════════╝")

    world = World()
    generator = Generator(world)
    learn_nature(world)

    print(f"\n  ── Генерация из 'млекопитающее' (категория) ──")
    gen_mammal = generator.generate_from("млекопитающее", max_per_slot=10)
    mammal_found = False
    mammal_sentences = []
    for g in gen_mammal:
        if "это" in g["pattern"]:
            print(f"  Паттерн: {g['pattern']} (fed={g['fed']})")
            for s in g["sentences"][:6]:
                print(f"    → {s}")
            mammal_found = True
            mammal_sentences = g["sentences"]
            break

    print(f"\n  ── Генерация из 'ест' (отношение) ──")
    gen_eat = generator.generate_from("ест", max_per_slot=10)
    eat_found = False
    for g in gen_eat:
        print(f"  Паттерн: {g['pattern']} (fed={g['fed']})")
        for s in g["sentences"][:6]:
            print(f"    → {s}")
        eat_found = True

    print(f"\n  ── Генерация из 'живёт' (отношение) ──")
    gen_lives = generator.generate_from("живёт", max_per_slot=10)
    lives_found = False
    for g in gen_lives:
        print(f"  Паттерн: {g['pattern']} (fed={g['fed']})")
        for s in g["sentences"][:6]:
            print(f"    → {s}")
        if len(g["sentences"]) > 6:
            print(f"    ... и ещё {len(g['sentences']) - 6}")
        lives_found = True

    ok1 = mammal_found
    ok2 = eat_found
    ok3 = lives_found
    print(f"\n  ✓ '$0·это·млекопитающее' → предложения: {ok1}")
    print(f"  ✓ '$0·ест·$1' → предложения: {ok2}")
    print(f"  ✓ '$0·живёт·...' → предложения: {ok3}")

    ok = ok1 and ok2 and ok3
    print(f"\n  {'═══ ГЕНЕРАЦИЯ РАБОТАЕТ! ═══' if ok else '═══ НУЖНА ДОРАБОТКА ═══'}")
    return ok


# ────────────────────────────────────────────────────
# Тест 5: Поглощение нового факта
# ────────────────────────────────────────────────────

def test_absorption():
    print("\n╔═══════════════════════════════════════════════════════╗")
    print("║  ТЕСТ 5: Поглощение (дельфин → млекопитающее)        ║")
    print("╚═══════════════════════════════════════════════════════╝")

    world = World()
    visitor = Visitor(world)
    learn_nature(world)

    mammals_before = visitor.query_category("млекопитающее")
    mammals_before_clean = {v for v in mammals_before if len(v) > 1}
    print(f"\n  ДО: млекопитающие = {sorted(mammals_before_clean)}")
    print(f"  'дельфин' в млекопитающих: {'дельфин' in mammals_before_clean}")

    absorbed_before = world.stats["absorbed"]
    world.feed_sentence(["дельфин", "это", "млекопитающее"])
    world.run(1)
    absorbed_after = world.stats["absorbed"]

    mammals_after = visitor.query_category("млекопитающее")
    mammals_after_clean = {v for v in mammals_after if len(v) > 1}
    print(f"\n  ПОСЛЕ: млекопитающие = {sorted(mammals_after_clean)}")
    print(f"  'дельфин' в млекопитающих: {'дельфин' in mammals_after_clean}")
    print(f"  Поглощений: {absorbed_after - absorbed_before}")

    world.feed_sentence(["кит", "это", "млекопитающее"])
    world.run(1)
    mammals_final = visitor.query_category("млекопитающее")
    mammals_final_clean = {v for v in mammals_final if len(v) > 1}
    print(f"\n  ФИНАЛ (+кит): млекопитающие = {sorted(mammals_final_clean)}")

    ok1 = "дельфин" in mammals_after_clean
    ok2 = absorbed_after > absorbed_before
    ok3 = "кит" in mammals_final_clean

    print(f"\n  ✓ дельфин поглощён: {ok1}")
    print(f"  ✓ absorption сработал: {ok2}")
    print(f"  ✓ кит тоже поглощён: {ok3}")

    ok = ok1 and ok2 and ok3
    print(f"\n  {'═══ ПОГЛОЩЕНИЕ РАБОТАЕТ! ═══' if ok else '═══ НУЖНА ДОРАБОТКА ═══'}")
    return ok


# ────────────────────────────────────────────────────
# Тест 6: Кросс-доменный перенос
# ────────────────────────────────────────────────────

def test_cross_domain():
    print("\n╔═══════════════════════════════════════════════════════╗")
    print("║  ТЕСТ 6: КРОСС-ДОМЕННЫЙ ПЕРЕНОС                      ║")
    print("║  Русский язык + Природоведение в одном мире           ║")
    print("╚═══════════════════════════════════════════════════════╝")

    world = World()
    visitor = Visitor(world)

    learn_rules(world)
    learn_nature(world)

    for r in range(3):
        for fact in BRIDGE_FACTS:
            world.feed_sentence(fact)
            world.run(1)

    alive = len(world.creatures)
    abst = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"\n  Обучено: {alive} существ, {abst} абстракций (оба предмета)")

    # Путь 1: кот → млекопитающее (природоведение)
    kot_info = visitor.visit("кот")
    kot_all = kot_info["siblings"] | kot_info.get("concrete_relatives", set())
    has_mammal = "млекопитающее" in kot_all
    print(f"\n  Путь 1 (природоведение): кот → млекопитающее: {has_mammal}")

    # Путь 2: кот → предмет (мост)
    has_predmet = "предмет" in kot_all
    print(f"  Путь 2 (мост): кот → предмет: {has_predmet}")

    # Путь 3: предмет → существительное (русский язык)
    predmet_info = visitor.visit("предмет")
    predmet_all = predmet_info["siblings"] | predmet_info.get("concrete_relatives", set())
    has_sush = "существительное" in predmet_all
    print(f"  Путь 3 (русский язык): предмет → существительное: {has_sush}")

    # Путь 4: млекопитающее → животное (природоведение)
    mammal_info = visitor.visit("млекопитающее")
    mammal_all = mammal_info["siblings"] | mammal_info.get("concrete_relatives", set())
    has_animal = "животное" in mammal_all
    print(f"  Путь 4 (природоведение): млекопитающее → животное: {has_animal}")

    if has_mammal and has_predmet and has_sush:
        print(f"\n  КРОСС-ДОМЕННАЯ ЦЕПОЧКА:")
        print(f"    кот → млекопитающее → животное (природоведение)")
        print(f"    кот → предмет → существительное (русский язык)")
        print(f"    Оба вывода из ОДНОГО существа 'кот'!")

    ok = has_mammal and has_predmet and has_sush and has_animal
    print(f"\n  {'═══ КРОСС-ДОМЕННЫЙ ПЕРЕНОС РАБОТАЕТ! ═══' if ok else '═══ НУЖНА ДОРАБОТКА ═══'}")
    return ok


# ────────────────────────────────────────────────────
# Тест 7: Вопросы за пределами шаблонов
# ────────────────────────────────────────────────────

def test_beyond_templates():
    print("\n╔═══════════════════════════════════════════════════════╗")
    print("║  ТЕСТ 7: Вопросы ЗА ПРЕДЕЛАМИ шаблонов               ║")
    print("╚═══════════════════════════════════════════════════════╝")

    world = World()
    visitor = Visitor(world)
    generator = Generator(world)
    learn_nature(world)

    # Вопрос 1: "какие млекопитающие?" — прямая категория
    mammals = visitor.query_category("млекопитающее")
    mammals_clean = {v for v in mammals if len(v) > 1 and not v.startswith("$")}
    print(f"\n  Вопрос 1: «какие млекопитающие?»")
    print(f"    Ответ (query_category): {sorted(mammals_clean)}")
    ok1 = {"кот", "собака"}.issubset(mammals_clean)
    print(f"    ✓ Содержит кот, собака: {ok1}")

    # Вопрос 2: "кто ест мясо?" — через ask
    answer2 = generator.ask("кто ест мясо?")
    meat_eaters = set(answer2["answers"])
    print(f"\n  Вопрос 2: «кто ест мясо?»")
    print(f"    Ответ: {answer2['answers'][:8]}")
    if answer2["reasoning"]:
        for r in answer2["reasoning"][:3]:
            print(f"    Путь: {r}")
    ok2 = bool({"кот", "собака"} & meat_eaters)
    print(f"    ✓ Содержит кот или собака: {ok2}")

    # Вопрос 3: "кто живёт в доме?" — через ask
    answer3 = generator.ask("кто живёт в доме?")
    home_dwellers = set(answer3["answers"])
    print(f"\n  Вопрос 3: «кто живёт в доме?»")
    print(f"    Ответ: {answer3['answers'][:8]}")
    if answer3["reasoning"]:
        for r in answer3["reasoning"][:3]:
            print(f"    Путь: {r}")
    ok3 = bool({"кот", "собака"} & home_dwellers)
    print(f"    ✓ Содержит кот или собака: {ok3}")

    # Вопрос 4: "что умеет рыба?" — через ask
    answer4 = generator.ask("что умеет рыба?")
    fish_can = set(answer4["answers"])
    print(f"\n  Вопрос 4: «что умеет рыба?»")
    print(f"    Ответ: {answer4['answers'][:8]}")
    if answer4["reasoning"]:
        for r in answer4["reasoning"][:3]:
            print(f"    Путь: {r}")
    ok4 = bool({"плавать"} & fish_can)
    print(f"    ✓ Содержит 'плавать': {ok4}")

    # Вопрос 5: "кто ест траву?" — агрегация
    answer5 = generator.ask("кто ест траву?")
    grass_eaters = set(answer5["answers"])
    print(f"\n  Вопрос 5: «кто ест траву?»")
    print(f"    Ответ: {answer5['answers'][:8]}")
    if answer5["reasoning"]:
        for r in answer5["reasoning"][:3]:
            print(f"    Путь: {r}")
    ok5 = bool({"корова", "лошадь"} & grass_eaters)
    print(f"    ✓ Содержит корова или лошадь: {ok5}")

    passed = sum([ok1, ok2, ok3, ok4, ok5])
    print(f"\n  Результат: {passed}/5")
    ok = passed >= 3
    print(f"\n  {'═══ ВЫХОД ЗА ШАБЛОНЫ РАБОТАЕТ! ═══' if ok else '═══ НУЖНА ДОРАБОТКА ═══'}")
    return ok


# ────────────────────────────────────────────────────
# MAIN
# ────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  ДОКАЗАТЕЛЬСТВО УНИВЕРСАЛЬНОСТИ ПАРАДИГМЫ")
    print("  Движок (chrysaline/) НЕ менялся.")
    print("  Новый предмет: Окружающий мир (природоведение)")
    print("=" * 60)

    results = []

    r1 = test_categories()
    results.append(("Категории (млекопитающие, птицы, рыбы)", r1))

    r2 = test_questions()
    results.append(("Вопросы по новому предмету", r2))

    r3 = test_hierarchy()
    results.append(("Иерархия (кот→млекопит.→животное)", r3))

    r4 = test_generation()
    results.append(("Генерация из абстракций", r4))

    r5 = test_absorption()
    results.append(("Поглощение (дельфин, кит)", r5))

    r6 = test_cross_domain()
    results.append(("Кросс-доменный перенос", r6))

    r7 = test_beyond_templates()
    results.append(("Выход за пределы шаблонов", r7))

    passed = sum(1 for _, ok in results if ok)
    print("\n" + "=" * 60)
    print("╔═══════════════════════════════════════════════════════╗")
    print("║       ИТОГ: УНИВЕРСАЛЬНОСТЬ ПАРАДИГМЫ                 ║")
    print("╠═══════════════════════════════════════════════════════╣")
    for i, (name, ok) in enumerate(results):
        s = "✓" if ok else "✗"
        print(f"║  {s} {i+1}. {name:42s}    ║")
    print(f"╠═══════════════════════════════════════════════════════╣")
    print(f"║  Результат: {passed}/7                                       ║")
    if passed >= 6:
        print("║                                                       ║")
        print("║  ═══ ПАРАДИГМА УНИВЕРСАЛЬНА! ═══                      ║")
        print("║  Движок domain-agnostic.                              ║")
        print("║  Новый предмет без изменения кода.                    ║")
    elif passed >= 5:
        print("║                                                       ║")
        print("║  ═══ ПАРАДИГМА В ОСНОВНОМ РАБОТАЕТ ═══                ║")
    else:
        print("║                                                       ║")
        print("║  ═══ НУЖНА ДОРАБОТКА ═══                              ║")
    print("╚═══════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    main()
