#!/usr/bin/env python3
"""Пять экспериментов: поглощение, масштаб, конфликт, deep visiting, связь правил."""

import time

from chrysaline import World, Visitor, Splitter
from data.rules import learn_rules
from data.fairy_tales import FAIRY_TALES, EXTRA_SENTENCES, parse_text_to_sentences


def experiment_absorption():
    print("╔═══════════════════════════════════════════════════════╗")
    print("║  ШАГ 1: ПОГЛОЩЕНИЕ (absorption)                      ║")
    print("╚═══════════════════════════════════════════════════════╝")

    world = World()
    visitor = Visitor(world)
    learn_rules(world)

    vowels_before = visitor.query_category("гласные")
    vowels_before_clean = {v for v in vowels_before if len(v) == 1}
    print(f"\n  Гласные ДО поглощения: {sorted(vowels_before_clean)}")
    print(f"  'ю' в гласных: {'ю' in vowels_before_clean}")

    abstractions_before = [c for c in world.creatures.values()
                           if c.alive and c.slot_options]
    target = None
    for a in abstractions_before:
        if "гласные" in a.parts and a.slot_options:
            for slot, opts in a.slot_options.items():
                if "а" in opts and "о" in opts:
                    target = a
                    break

    if target:
        print(f"\n  Абстракция-мишень: {target.name}")
        for slot, opts in target.slot_options.items():
            print(f"    {slot} = {sorted(opts)}")

    absorbed_before = world.stats["absorbed"]
    world.feed_sentence(["гласные", "звуки", "это", "ю"])
    world.run(1)
    absorbed_after = world.stats["absorbed"]

    vowels_after = visitor.query_category("гласные")
    vowels_after_clean = {v for v in vowels_after if len(v) == 1}
    print(f"\n  Гласные ПОСЛЕ: {sorted(vowels_after_clean)}")
    print(f"  'ю' в гласных: {'ю' in vowels_after_clean}")
    print(f"  Поглощений: {absorbed_after - absorbed_before}")

    if target:
        print(f"\n  Абстракция после:")
        for slot, opts in target.slot_options.items():
            print(f"    {slot} = {sorted(opts)}")

    for letter in ["е", "ё", "я"]:
        world.feed_sentence(["гласные", "звуки", "это", letter])
        world.run(1)

    vowels_final = visitor.query_category("гласные")
    vowels_final_clean = {v for v in vowels_final if len(v) == 1}
    print(f"\n  Гласные ФИНАЛ (после е,ё,я): {sorted(vowels_final_clean)}")

    pass1 = "ю" in vowels_after_clean
    pass2 = absorbed_after > absorbed_before
    pass3 = {"е", "ё", "я"}.issubset(vowels_final_clean)
    ok = pass1 and pass2 and pass3

    print(f"\n  ✓ 'ю' поглощена: {pass1}")
    print(f"  ✓ absorption сработал: {pass2}")
    print(f"  ✓ е,ё,я тоже поглощены: {pass3}")
    print(f"\n  {'═══ ПОГЛОЩЕНИЕ РАБОТАЕТ! ═══' if ok else '═══ НУЖНА ДОРАБОТКА ═══'}")

    return ok


def experiment_scale():
    print("\n╔═══════════════════════════════════════════════════════╗")
    print("║  ШАГ 2: МАСШТАБ (1000+ предложений)                  ║")
    print("╚═══════════════════════════════════════════════════════╝")

    sentences = parse_text_to_sentences(FAIRY_TALES + EXTRA_SENTENCES)
    print(f"\n  Подготовлено: {len(sentences)} предложений")
    for s in sentences[:5]:
        print(f"    [{' '.join(s)}]")
    print(f"    ... и ещё {len(sentences) - 5}")

    world = World()
    t0 = time.time()

    for r in range(3):
        for sent in sentences:
            world.feed_sentence(sent)
            world.run(1)

    elapsed = time.time() - t0
    alive = len(world.creatures)
    abst = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)

    print(f"\n  ═══ Результат ═══")
    print(f"  Время: {elapsed:.1f}с")
    print(f"  Существ живых: {alive}")
    print(f"  Абстракций: {abst}")
    print(f"  Статистика: {world.stats}")

    top = sorted(world.creatures.values(), key=lambda c: -c.energy)[:10]
    print(f"\n  Топ-10 по энергии:")
    for c in top:
        slot_info = ""
        if c.slot_options:
            for s, opts in c.slot_options.items():
                slot_info = f" [{s}={sorted(opts)[:5]}{'...' if len(opts)>5 else ''}]"
        print(f"    E={c.energy:.1f} fed={c.times_fed:4d}  {c.name}{slot_info}")

    top_abs = sorted([c for c in world.creatures.values() if c.alive and c.slot_options],
                     key=lambda c: -len(list(c.slot_options.values())[0]) if c.slot_options else 0)[:10]
    print(f"\n  Топ-10 абстракций (по размеру слотов):")
    for c in top_abs:
        for s, opts in c.slot_options.items():
            clean = sorted(o for o in opts if not o.startswith("$"))
            print(f"    {c.name}  {s}={clean[:8]}{'...' if len(clean)>8 else ''} ({len(clean)} вариантов)")
            break

    ok_not_exploded = alive < 10000
    ok_has_abstractions = abst > 10
    ok_fast = elapsed < 300

    print(f"\n  ✓ Не взорвалось (<10k существ): {ok_not_exploded} ({alive})")
    print(f"  ✓ Абстракции появились (>10): {ok_has_abstractions} ({abst})")
    print(f"  ✓ Быстро (<5мин): {ok_fast} ({elapsed:.1f}с)")

    ok = ok_not_exploded and ok_has_abstractions and ok_fast
    print(f"\n  {'═══ МАСШТАБ РАБОТАЕТ! ═══' if ok else '═══ НУЖНА ДОРАБОТКА ═══'}")
    return ok


def experiment_conflict():
    print("\n╔═══════════════════════════════════════════════════════╗")
    print("║  ШАГ 3: КОНФЛИКТ (омонимия — лук)                    ║")
    print("╚═══════════════════════════════════════════════════════╝")

    world = World()
    splitter = Splitter(world)
    visitor = Visitor(world)

    plant_sentences = [
        ["лук", "растёт", "в", "огороде"],
        ["лук", "сажают", "весной"],
        ["лук", "поливают", "водой"],
        ["репа", "растёт", "в", "огороде"],
        ["морковь", "растёт", "в", "огороде"],
        ["репа", "сажают", "весной"],
        ["морковь", "поливают", "водой"],
    ]

    weapon_sentences = [
        ["лук", "стреляет", "далеко"],
        ["лук", "натягивают", "тетивой"],
        ["лук", "используют", "для", "охоты"],
        ["меч", "стреляет", "далеко"],
        ["копьё", "используют", "для", "охоты"],
        ["меч", "натягивают", "тетивой"],
    ]

    for r in range(3):
        for sent in plant_sentences + weapon_sentences:
            world.feed_sentence(sent)
            world.run(1)

    luk_info = visitor.visit("лук")
    print(f"\n  'лук' ДО расщепления:")
    print(f"    братья: {sorted(luk_info['siblings'])}")

    groups = splitter._get_context_groups("лук")
    print(f"\n  Контекстные группы: {len(groups)}")
    for i, g in enumerate(groups):
        print(f"    группа {i+1}: {sorted(g['parts'])}")

    new_senses = splitter.split("лук")
    print(f"\n  Расщепление: {len(new_senses)} смыслов")
    for sense in new_senses:
        sense_info = visitor.visit(sense.parts[0])
        print(f"    '{sense.name}' E={sense.energy:.1f}")

    ok_groups = len(groups) >= 2
    ok_split = len(new_senses) >= 2

    if len(new_senses) >= 2:
        senses_names = {s.name for s in new_senses}
        print(f"    Новые существа: {sorted(senses_names)}")

    print(f"\n  ✓ Группы найдены (>=2): {ok_groups} ({len(groups)})")
    print(f"  ✓ Расщепление сработало (>=2): {ok_split} ({len(new_senses)})")

    ok = ok_groups and ok_split
    print(f"\n  {'═══ КОНФЛИКТ РЕШЁН! ═══' if ok else '═══ НУЖНА ДОРАБОТКА ═══'}")
    return ok


def experiment_deep_visiting():
    print("\n╔═══════════════════════════════════════════════════════╗")
    print("║  ШАГ 4: ДВУХШАГОВЫЙ VISITING                         ║")
    print("║  кот → предмет → существительное                     ║")
    print("╚═══════════════════════════════════════════════════════╝")

    world = World()
    visitor = Visitor(world)
    learn_rules(world)

    experience = [
        ["кот", "это", "предмет"],
        ["собака", "это", "предмет"],
        ["стол", "это", "предмет"],
        ["бегать", "это", "действие"],
        ["прыгать", "это", "действие"],
        ["красный", "это", "признак"],
        ["большой", "это", "признак"],
    ]

    for r in range(3):
        for sent in experience:
            world.feed_sentence(sent)
            world.run(1)

    kot_info = visitor.visit("кот")
    print(f"\n  Шаг 1: 'кот' visiting")
    print(f"    братья: {sorted(kot_info['siblings'])}")
    print(f"    конкретные родственники: {sorted(kot_info['concrete_relatives'])}")

    has_predmet = "предмет" in kot_info["siblings"] or "предмет" in kot_info["concrete_relatives"]
    print(f"    кот → предмет: {has_predmet}")

    predmet_info = visitor.visit("предмет")
    print(f"\n  Шаг 2: 'предмет' visiting")
    print(f"    братья: {sorted(predmet_info['siblings'])}")
    print(f"    конкретные родственники: {sorted(predmet_info['concrete_relatives'])}")

    has_sush = "существительное" in predmet_info["siblings"] or \
               "существительное" in predmet_info["concrete_relatives"]
    print(f"    предмет → существительное: {has_sush}")

    answer = None
    if has_predmet and has_sush:
        answer = "существительное"
        print(f"\n  Вывод: кот → предмет → существительное")

    begat_info = visitor.visit("бегать")
    has_deistvie = "действие" in begat_info["siblings"] or "действие" in begat_info["concrete_relatives"]
    deistvie_info = visitor.visit("действие")
    has_glagol = "глагол" in deistvie_info["siblings"] or "глагол" in deistvie_info["concrete_relatives"]

    print(f"\n  Бонус: 'бегать' → действие: {has_deistvie}")
    print(f"  Бонус: действие → глагол: {has_glagol}")

    if has_deistvie and has_glagol:
        print(f"  Вывод: бегать → действие → глагол")

    ok1 = answer == "существительное"
    ok2 = has_deistvie and has_glagol

    print(f"\n  ✓ кот = существительное: {ok1}")
    print(f"  ✓ бегать = глагол: {ok2}")

    ok = ok1 and ok2
    print(f"\n  {'═══ ДВУХШАГОВЫЙ VISITING РАБОТАЕТ! ═══' if ok else '═══ НУЖНА ДОРАБОТКА ═══'}")
    return ok


def experiment_rule_linking():
    print("\n╔═══════════════════════════════════════════════════════╗")
    print("║  ШАГ 5: СВЯЗЬ МЕЖДУ ПРАВИЛАМИ                        ║")
    print("║  \"и\" в жи-ши = гласная?                              ║")
    print("╚═══════════════════════════════════════════════════════╝")

    world = World()
    visitor = Visitor(world)
    learn_rules(world)

    i_info = visitor.visit("и")
    print(f"\n  Visiting по 'и':")
    print(f"    братья: {sorted(i_info['siblings'])}")
    print(f"    конкретные родственники: {sorted(i_info['concrete_relatives'])[:15]}")
    print(f"    заменяемые: {sorted(i_info['slot_mates'])[:10]}")
    print(f"    контексты: {len(i_info['contexts'])}")

    knows_vowels = "гласные" in i_info["siblings"] or \
                   "гласные" in i_info.get("concrete_relatives", set())
    print(f"\n  'и' знает 'гласные': {knows_vowels}")

    knows_zhi = "жи" in i_info["siblings"] or \
                "пишется" in i_info["siblings"] or \
                "буквой" in i_info["siblings"]
    print(f"  'и' знает 'жи/пишется/буквой': {knows_zhi}")

    vowel_mates = {"а", "о", "у", "ы", "э"} & i_info["slot_mates"]
    knows_mates = len(vowel_mates) > 0
    print(f"  'и' заменяема с гласными: {sorted(vowel_mates)}")

    print(f"\n  Цепочка: жи → и → гласные")
    zhi_info = visitor.visit("жи")
    zhi_knows_i = "и" in zhi_info["siblings"]
    print(f"    жи → и: {zhi_knows_i}")

    glasnye_info = visitor.visit("гласные")
    glasnye_knows_i = "и" in glasnye_info["siblings"] or \
                      "и" in glasnye_info.get("concrete_relatives", set())
    print(f"    гласные → и: {glasnye_knows_i}")

    chain_works = zhi_knows_i and glasnye_knows_i
    print(f"    цепочка замкнута: {chain_works}")

    if chain_works:
        print(f"\n  Вывод: 'и' в жи-ши — это ГЛАСНАЯ буква")
        print(f"  Потому что существо 'и' живёт в обоих семьях:")
        print(f"    семья 'жи·пишется·с·буквой·и'")
        print(f"    семья 'гласные·звуки·это·и'")

    ok = knows_vowels and knows_zhi and chain_works
    print(f"\n  ✓ Знает о гласных: {knows_vowels}")
    print(f"  ✓ Знает о жи-ши: {knows_zhi}")
    print(f"  ✓ Цепочка жи→и→гласные: {chain_works}")

    print(f"\n  {'═══ ПРАВИЛА СВЯЗАНЫ! ═══' if ok else '═══ НУЖНА ДОРАБОТКА ═══'}")
    return ok


def main():
    print("=" * 60)
    print("  ПЯТЬ ЭКСПЕРИМЕНТОВ")
    print("  Каждый — конкретный вопрос, конкретный результат")
    print("=" * 60)

    results = []

    r1 = experiment_absorption()
    results.append(("Поглощение (ю→гласные)", r1))

    r2 = experiment_scale()
    results.append(("Масштаб (1000+ предложений)", r2))

    r3 = experiment_conflict()
    results.append(("Конфликт (лук→два смысла)", r3))

    r4 = experiment_deep_visiting()
    results.append(("Двухшаговый visiting (кот→сущ.)", r4))

    r5 = experiment_rule_linking()
    results.append(("Связь правил (и = жи-ши + гласные)", r5))

    passed = sum(1 for _, ok in results if ok)
    print("\n" + "=" * 60)
    print("╔═══════════════════════════════════════════════════════╗")
    print("║              ИТОГ: ПЯТЬ ЭКСПЕРИМЕНТОВ                 ║")
    print("╠═══════════════════════════════════════════════════════╣")
    for i, (name, ok) in enumerate(results):
        s = "✓" if ok else "✗"
        print(f"║  {s} {i+1}. {name:42s}    ║")
    print(f"╠═══════════════════════════════════════════════════════╣")
    print(f"║  Результат: {passed}/5                                       ║")
    if passed == 5:
        print("║  ═══ ВСЕ ПЯТЬ ЭКСПЕРИМЕНТОВ ПРОЙДЕНЫ! ═══            ║")
    elif passed >= 3:
        print("║  ═══ БОЛЬШИНСТВО ПРОЙДЕНО ═══                        ║")
    print("╚═══════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    main()
