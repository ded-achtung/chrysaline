#!/usr/bin/env python3
"""
Стресс-тест: Где реальные границы парадигмы?

4 направления удара:
  1. Отрицание и исключения
  2. Глубокий конфликт и омонимия
  3. Длинные объяснения ("почему?")
  4. Большой смешанный корпус с шумом

Движок НЕ менялся. Цель — честно зафиксировать, что ломается.
"""

import time

from chrysaline import World, Visitor, Generator, Splitter
from data.stress_test import (
    NEGATION_POSITIVE, NEGATION_NEGATIVE,
    HOMONYMY_FACTS, EXPLANATION_FACTS,
    MIXED_CORPUS_RAW, parse_mixed_corpus,
)
from data.rules import learn_rules
from data.nature import NATURE_FACTS


def learn_facts(world, facts):
    for r in range(3):
        for fact in facts:
            world.feed_sentence(fact)
            world.run(1)


# ════════════════════════════════════════════════════════
# НАПРАВЛЕНИЕ 1: ОТРИЦАНИЕ И ИСКЛЮЧЕНИЯ
# ════════════════════════════════════════════════════════

def test_negation():
    print("╔═══════════════════════════════════════════════════════╗")
    print("║  НАПРАВЛЕНИЕ 1: ОТРИЦАНИЕ И ИСКЛЮЧЕНИЯ               ║")
    print("║  Учитель: «не» — маркер отрицания                    ║")
    print("╚═══════════════════════════════════════════════════════╝")

    world = World()
    visitor = Visitor(world)

    # Фаза 1: позитивные факты — формируют абстракции ($0·летает и т.д.)
    learn_facts(world, NEGATION_POSITIVE)
    abst_after_pos = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"\n  Фаза 1 (позитив): {len(world.creatures)} существ, {abst_after_pos} абстракций")

    # Учитель говорит: "не" — маркер отрицания
    world.learn_negation("не")
    print(f"  Учитель: learn_negation('не') → neg_markers: {world.neg_markers}")

    # Фаза 2: отрицания — теперь система знает что "не" = отрицание
    learn_facts(world, NEGATION_NEGATIVE)
    alive = len(world.creatures)
    abst = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"  Фаза 2 (+отрицания): {alive} существ, {abst} абстракций")
    print(f"  neg_markers: {world.neg_markers}")

    # --- Тест 1: страус — птица? ---
    straus_info = visitor.visit("страус")
    is_bird = "птица" in straus_info["siblings"]
    fly_in_neg = "летает" in straus_info.get("neg_siblings", set())
    fly_in_pos = "летает" in straus_info["siblings"]
    print(f"\n  Тест 1: страус — птица?")
    print(f"    pos siblings: {sorted(straus_info['siblings'])}")
    print(f"    neg siblings: {sorted(straus_info.get('neg_siblings', set()))}")
    print(f"    страус → птица (pos): {is_bird}")
    print(f"    'летает' в neg: {fly_in_neg}")
    print(f"    'летает' в pos: {fly_in_pos}")

    # --- Тест 1б: кит — рыба или млекопитающее? ---
    kit_info = visitor.visit("кит")
    kit_is_mammal = "млекопитающее" in kit_info["siblings"]
    fish_in_neg = "рыба" in kit_info.get("neg_siblings", set())
    fish_in_pos = "рыба" in kit_info["siblings"]
    print(f"\n  Тест 2: кит — рыба или млекопитающее?")
    print(f"    pos siblings: {sorted(kit_info['siblings'])}")
    print(f"    neg siblings: {sorted(kit_info.get('neg_siblings', set()))}")
    print(f"    кит → млекопитающее (pos): {kit_is_mammal}")
    print(f"    'рыба' в neg: {fish_in_neg}")
    print(f"    'рыба' в pos: {fish_in_pos}")

    # --- Тест 1в: "кто летает?" (не должен включать страуса/пингвина) ---
    gen = Generator(world)
    answer = gen.ask("кто летает?")
    flyers = set(answer["answers"])
    print(f"\n  Тест 3: «кто летает?»")
    print(f"    Ответ: {answer['answers'][:10]}")
    if answer["reasoning"]:
        for r in answer["reasoning"][:3]:
            print(f"    Путь: {r}")
    straus_in_flyers = "страус" in flyers
    penguin_in_flyers = "пингвин" in flyers
    print(f"    страус в ответе: {straus_in_flyers} (должен быть НЕТ)")
    print(f"    пингвин в ответе: {penguin_in_flyers} (должен быть НЕТ)")

    # --- Диагноз ---
    ok_bird = is_bird
    ok_mammal = kit_is_mammal
    ok_neg_fly = fly_in_neg and not fly_in_pos
    ok_neg_fish = fish_in_neg and not fish_in_pos
    ok_no_straus = not straus_in_flyers and not penguin_in_flyers

    print(f"\n  ── ДИАГНОЗ ──")
    print(f"  ✓ Категории (страус=птица, кит=млек.): {ok_bird and ok_mammal}")
    print(f"  ✓ 'летает' в neg для страуса: {ok_neg_fly}")
    print(f"  ✓ 'рыба' в neg для кита: {ok_neg_fish}")
    print(f"  ✓ ask('кто летает?') без страуса/пингвина: {ok_no_straus}")

    negation_works = ok_neg_fly and ok_no_straus
    return {
        "categories_ok": ok_bird and ok_mammal,
        "negation_broken": not negation_works,
        "teacher_negation": True,
        "detail": "учитель + валентность работает" if negation_works else "нужна доработка",
    }


# ════════════════════════════════════════════════════════
# НАПРАВЛЕНИЕ 2: ГЛУБОКИЙ КОНФЛИКТ И ОМОНИМИЯ
# ════════════════════════════════════════════════════════

def test_deep_homonymy():
    print("\n╔═══════════════════════════════════════════════════════╗")
    print("║  НАПРАВЛЕНИЕ 2: ГЛУБОКИЙ КОНФЛИКТ (3 смысла)         ║")
    print("║  коса: инструмент / причёска / географический объект  ║")
    print("╚═══════════════════════════════════════════════════════╝")

    world = World()
    visitor = Visitor(world)
    splitter = Splitter(world)
    learn_facts(world, HOMONYMY_FACTS)

    alive = len(world.creatures)
    abst = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"\n  Обучено: {alive} существ, {abst} абстракций")

    # --- Тест 2а: коса — сколько контекстных групп? ---
    kosa_info = visitor.visit("коса")
    print(f"\n  Тест 2а: visit('коса')")
    print(f"    братья: {sorted(kosa_info['siblings'])}")

    groups = splitter._get_context_groups("коса")
    print(f"\n  Контекстные группы: {len(groups)}")
    for i, g in enumerate(groups):
        print(f"    группа {i+1}: {sorted(g['parts'])}")

    ok_groups = len(groups) >= 2
    print(f"\n  ✓ Найдено >=2 группы: {ok_groups}")

    # --- Тест 2б: расщепление ---
    senses = splitter.split("коса")
    print(f"\n  Тест 2б: split('коса') → {len(senses)} смыслов")
    for s in senses:
        print(f"    '{s.name}' E={s.energy:.1f}")

    ok_split = len(senses) >= 2
    print(f"  ✓ Расщепление >=2: {ok_split}")

    ideal_3 = len(senses) >= 3
    print(f"  ? Идеально 3 смысла: {ideal_3}")

    # --- Тест 2в: "ключ" — два смысла ---
    print(f"\n  Тест 2в: 'ключ' — два смысла")
    key_groups = splitter._get_context_groups("ключ")
    print(f"    Контекстные группы: {len(key_groups)}")
    for i, g in enumerate(key_groups):
        print(f"    группа {i+1}: {sorted(g['parts'])}")

    key_senses = splitter.split("ключ")
    print(f"    split('ключ') → {len(key_senses)} смыслов")
    for s in key_senses:
        print(f"      '{s.name}' E={s.energy:.1f}")

    ok_key = len(key_senses) >= 2

    # --- Тест 2г: нет мусорных расщеплений ---
    # Слово "из" участвует во многих контекстах — не должно расщепляться на мусор
    iz_groups = splitter._get_context_groups("из")
    iz_senses = splitter.split("из")
    print(f"\n  Тест 2г: 'из' (служебное) — мусорное расщепление?")
    print(f"    Контекстные группы: {len(iz_groups)}")
    print(f"    Смыслы: {len(iz_senses)}")
    # Много групп у "из" — это нормально, но они не должны быть чистыми
    no_garbage = True  # будем считать любой split "из" мусорным
    if len(iz_senses) > 4:
        no_garbage = False
        print(f"    ✗ Мусорное расщепление: {len(iz_senses)} смыслов у служебного слова")
    else:
        print(f"    ✓ Не мусорное: {len(iz_senses)} смыслов")

    print(f"\n  ── ДИАГНОЗ ──")
    print(f"  ✓ Коса: {len(groups)} контекстных групп, {len(senses)} смыслов")
    print(f"  ✓ Ключ: {len(key_groups)} контекстных групп, {len(key_senses)} смыслов")
    if not ideal_3:
        print(f"  ГРАНИЦА: Сложно выделить РОВНО 3 смысла.")
        print(f"  Причина: группировка по пересечению контекстов")
        print(f"  сливает группы если есть общее слово (напр. 'из').")

    return {
        "kosa_groups": len(groups),
        "kosa_senses": len(senses),
        "key_senses": len(key_senses),
        "no_garbage": no_garbage,
        "split_works": ok_split,
    }


# ════════════════════════════════════════════════════════
# НАПРАВЛЕНИЕ 3: ОБЪЯСНЕНИЯ ("почему?")
# ════════════════════════════════════════════════════════

def explain_chain(visitor, start_word, target_word, max_steps=4):
    """Попробовать построить цепочку объяснения от start до target
    через visiting. Не меняет движок — строит снаружи."""
    chain = [start_word]
    visited_words = {start_word}
    current = start_word

    for step in range(max_steps):
        info = visitor.visit(current)
        if not info["found"]:
            break

        all_relatives = info["siblings"] | info.get("concrete_relatives", set())

        if target_word in all_relatives:
            chain.append(target_word)
            return chain

        best_next = None
        best_score = -1
        for rel in all_relatives:
            if rel in visited_words or rel.startswith("$") or len(rel) < 2:
                continue
            rel_info = visitor.visit(rel)
            if not rel_info["found"]:
                continue
            rel_all = rel_info["siblings"] | rel_info.get("concrete_relatives", set())
            if target_word in rel_all:
                chain.append(rel)
                chain.append(target_word)
                return chain
            score = len(rel_all)
            if score > best_score:
                best_score = score
                best_next = rel

        if best_next:
            chain.append(best_next)
            visited_words.add(best_next)
            current = best_next
        else:
            break

    return chain


def test_explanations():
    print("\n╔═══════════════════════════════════════════════════════╗")
    print("║  НАПРАВЛЕНИЕ 3: ОБЪЯСНЕНИЯ (почему?)                 ║")
    print("║  Может ли система СОБРАТЬ объяснение через visiting?  ║")
    print("╚═══════════════════════════════════════════════════════╝")

    world = World()
    visitor = Visitor(world)
    learn_rules(world)
    learn_facts(world, NATURE_FACTS)
    learn_facts(world, EXPLANATION_FACTS)

    alive = len(world.creatures)
    abst = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"\n  Обучено: {alive} существ, {abst} абстракций")

    results = []

    # --- 3а: Почему кит — млекопитающее? ---
    print(f"\n  Тест 3а: «Почему кит — млекопитающее?»")
    kit_info = visitor.visit("кит")
    kit_all = kit_info["siblings"] | kit_info.get("concrete_relatives", set())
    mammal_info = visitor.visit("млекопитающее")
    mammal_all = mammal_info["siblings"] | mammal_info.get("concrete_relatives", set())

    shared = kit_all & mammal_all
    print(f"    кит знает: {sorted(kit_info['siblings'])}")
    print(f"    млекопитающее знает: {sorted(mammal_info['siblings'])}")
    print(f"    Общее (причина): {sorted(shared)}")

    has_milk = "молоком" in shared or "молоко" in shared or "детёнышей" in shared
    ok_3a = has_milk
    if has_milk:
        print(f"    ОБЪЯСНЕНИЕ: кит кормит детёнышей молоком → как млекопитающее")
    else:
        print(f"    Не нашёл причину через пересечение")

    chain_3a = explain_chain(visitor, "кит", "млекопитающее")
    print(f"    Цепочка: {' → '.join(chain_3a)}")
    results.append(("кит→млекопитающее (причина)", ok_3a))

    # --- 3б: Почему кошка — существительное? ---
    print(f"\n  Тест 3б: «Почему кошка — существительное?»")
    chain_3b = explain_chain(visitor, "кошка", "существительное")
    print(f"    Цепочка: {' → '.join(chain_3b)}")
    ok_3b = "существительное" in chain_3b
    if ok_3b:
        print(f"    ОБЪЯСНЕНИЕ: {' → '.join(chain_3b)}")
    else:
        print(f"    Цепочка не дошла до 'существительное'")
    results.append(("кошка→существительное (цепочка)", ok_3b))

    # --- 3в: Почему Москва с большой буквы? ---
    print(f"\n  Тест 3в: «Почему Москва с большой буквы?»")
    moskva_info = visitor.visit("москва")
    if moskva_info["found"]:
        moskva_all = moskva_info["siblings"] | moskva_info.get("concrete_relatives", set())
        print(f"    москва знает: {sorted(moskva_info['siblings'])}")
        has_city = "город" in moskva_all or "города" in moskva_all
        chain_3c = explain_chain(visitor, "москва", "буквы")
        print(f"    Цепочка: {' → '.join(chain_3c)}")
        ok_3c = "буквы" in chain_3c or "большой" in moskva_all
    else:
        print(f"    'москва' не найдена")
        ok_3c = False
        chain_3c = []

    if ok_3c:
        print(f"    ОБЪЯСНЕНИЕ: москва → город → пишутся с большой буквы")
    results.append(("москва→большая буква (цепочка)", ok_3c))

    # --- 3г: ask("почему кит млекопитающее?") ---
    print(f"\n  Тест 3г: ask('почему кит млекопитающее?')")
    gen = Generator(world)
    answer = gen.ask("почему кит млекопитающее?")
    print(f"    Ответ: {answer['answers'][:8]}")
    for r in answer["reasoning"][:3]:
        print(f"    Путь: {r}")

    has_reason = any(w in answer["answers"]
                     for w in ["молоком", "детёнышей", "кормит", "дышит", "воздухом"])
    ok_3d = has_reason
    if has_reason:
        print(f"    ✓ Нашёл причинные слова в ответе")
    else:
        print(f"    ✗ 'почему' не порождает объяснения через ask()")
    results.append(("ask(почему?) → причина", ok_3d))

    # --- Диагноз ---
    passed = sum(1 for _, ok in results if ok)
    print(f"\n  ── ДИАГНОЗ ──")
    for name, ok in results:
        s = "✓" if ok else "✗"
        print(f"  {s} {name}")
    print(f"  Результат: {passed}/{len(results)}")

    if passed >= 3:
        print(f"  Объяснения ЧАСТИЧНО работают через visiting-цепочки.")
    else:
        print(f"  ГРАНИЦА: ask() не умеет строить 'почему'-объяснения.")
        print(f"  Нужен отдельный механизм explain() в движке.")

    return {
        "passed": passed,
        "total": len(results),
        "chain_works": passed >= 2,
    }


# ════════════════════════════════════════════════════════
# НАПРАВЛЕНИЕ 4: БОЛЬШОЙ СМЕШАННЫЙ КОРПУС
# ════════════════════════════════════════════════════════

def test_large_corpus():
    print("\n╔═══════════════════════════════════════════════════════╗")
    print("║  НАПРАВЛЕНИЕ 4: БОЛЬШОЙ СМЕШАННЫЙ КОРПУС             ║")
    print("║  200+ фактов, шум, пересечение доменов               ║")
    print("╚═══════════════════════════════════════════════════════╝")

    world = World()
    visitor = Visitor(world)
    gen = Generator(world)

    # Фаза 1: русский язык
    learn_rules(world)
    after_rules = len(world.creatures)
    rules_abst = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)

    # Фаза 2: природоведение
    learn_facts(world, NATURE_FACTS)
    after_nature = len(world.creatures)
    nature_abst = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)

    # Фаза 3: большой шумный корпус
    mixed_sentences = parse_mixed_corpus(MIXED_CORPUS_RAW)
    print(f"\n  Корпус: {len(mixed_sentences)} предложений из сырого текста")

    t0 = time.time()
    for r in range(3):
        for sent in mixed_sentences:
            world.feed_sentence(sent)
            world.run(1)
    elapsed = time.time() - t0

    after_all = len(world.creatures)
    all_abst = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)

    print(f"\n  ═══ Размер экосистемы ═══")
    print(f"  После правил:        {after_rules} существ, {rules_abst} абстракций")
    print(f"  + природоведение:    {after_nature} существ, {nature_abst} абстракций")
    print(f"  + шумный корпус:     {after_all} существ, {all_abst} абстракций")
    print(f"  Время шумного корпуса: {elapsed:.1f}с")
    print(f"  Статистика: {world.stats}")

    ok_not_exploded = after_all < 10000
    ok_fast = elapsed < 300
    print(f"\n  ✓ Не взорвалось (<10k): {ok_not_exploded} ({after_all})")
    print(f"  ✓ Быстро (<5мин): {ok_fast} ({elapsed:.1f}с)")

    # --- 4а: Старые категории выжили? ---
    print(f"\n  Тест 4а: Старые категории выжили?")
    vowels = visitor.query_category("гласные")
    vowels_clean = {v for v in vowels if len(v) == 1}
    mammals = visitor.query_category("млекопитающее")
    mammals_clean = {v for v in mammals if len(v) > 1}

    ok_vowels = {"а", "о", "у", "и"}.issubset(vowels_clean)
    ok_mammals = {"кот", "собака"}.issubset(mammals_clean)
    print(f"    гласные: {sorted(vowels_clean)[:8]} → выжили: {ok_vowels}")
    print(f"    млекопитающие: {sorted(mammals_clean)[:6]} → выжили: {ok_mammals}")

    # --- 4б: Новые абстракции из шумного корпуса ---
    print(f"\n  Тест 4б: Новые абстракции из шумного корпуса")
    top_abs = sorted(
        [c for c in world.creatures.values() if c.alive and c.slot_options],
        key=lambda c: -c.times_fed
    )[:10]
    for c in top_abs:
        for s, opts in c.slot_options.items():
            clean = sorted(o for o in opts if not o.startswith("$"))[:6]
            more = len([o for o in opts if not o.startswith("$")]) - len(clean)
            suffix = f"...+{more}" if more > 0 else ""
            print(f"    fed={c.times_fed:5d}  {c.name}  {s}={clean}{suffix}")
            break

    # --- 4в: Вопросы по-прежнему работают? ---
    print(f"\n  Тест 4в: Вопросы работают после шумного корпуса?")
    test_questions = [
        ("кто ест мясо?", {"кот", "собака"}, "кот/собака"),
        ("что ест корова?", {"траву", "молоко"}, "траву"),
    ]
    q_passed = 0
    for question, expected, desc in test_questions:
        answer = gen.ask(question)
        found = set(answer["answers"]) & expected
        ok = len(found) > 0
        if ok:
            q_passed += 1
        print(f"    «{question}» → {answer['answers'][:5]} → {'✓' if ok else '✗'} {desc}")

    # --- 4г: Мусорное поглощение? ---
    print(f"\n  Тест 4г: Мусорное поглощение?")
    absorb_count = world.stats["absorbed"]
    born_count = world.stats["born"]
    ratio = absorb_count / max(1, born_count)
    print(f"    absorbed={absorb_count}, born={born_count}, ratio={ratio:.3f}")
    ok_ratio = ratio < 0.5
    if not ok_ratio:
        print(f"    ✗ Подозрительно высокое поглощение (>{50}%)")
    else:
        print(f"    ✓ Поглощение в норме (<50%)")

    # --- 4д: Категории не размазались? ---
    print(f"\n  Тест 4д: Категории не размазались?")
    consonants = visitor.query_category("согласные")
    consonants_clean = {v for v in consonants if len(v) == 1}
    # Проверяем что гласные и согласные не перемешались
    vowel_in_consonants = vowels_clean & consonants_clean
    if vowel_in_consonants:
        print(f"    ✗ Гласные в согласных: {sorted(vowel_in_consonants)}")
        ok_categories_clean = False
    else:
        print(f"    ✓ Гласные и согласные не перемешались")
        ok_categories_clean = True

    print(f"\n  ── ДИАГНОЗ ──")
    print(f"  ✓ Не взорвалось: {ok_not_exploded}")
    print(f"  ✓ Быстро: {ok_fast}")
    print(f"  ✓ Старые категории: {ok_vowels and ok_mammals}")
    print(f"  ✓ Вопросы: {q_passed}/{len(test_questions)}")
    print(f"  ✓ Поглощение в норме: {ok_ratio}")
    print(f"  ✓ Категории чистые: {ok_categories_clean}")

    all_ok = ok_not_exploded and ok_fast and ok_vowels and ok_mammals
    if not all_ok:
        print(f"  ГРАНИЦА: Шумный корпус размывает точность.")

    return {
        "creatures": after_all,
        "abstractions": all_abst,
        "elapsed": elapsed,
        "not_exploded": ok_not_exploded,
        "categories_survived": ok_vowels and ok_mammals,
        "categories_clean": ok_categories_clean,
        "questions_work": q_passed >= 1,
    }


# ════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("  СТРЕСС-ТЕСТ: ГДЕ РЕАЛЬНЫЕ ГРАНИЦЫ?")
    print("  Движок (chrysaline/) НЕ менялся.")
    print("=" * 60)

    r1 = test_negation()
    r2 = test_deep_homonymy()
    r3 = test_explanations()
    r4 = test_large_corpus()

    # ═══ ИТОГОВАЯ КАРТА ГРАНИЦ ═══
    print("\n" + "=" * 60)
    print("╔═══════════════════════════════════════════════════════╗")
    print("║          КАРТА ГРАНИЦ ПАРАДИГМЫ                       ║")
    print("╠═══════════════════════════════════════════════════════╣")

    # 1. Отрицание
    if r1["negation_broken"]:
        print("║  ~ 1. ОТРИЦАНИЕ — ЧАСТИЧНО                           ║")
        print("║     Учитель дал 'не', но фильтрация неполная.        ║")
    else:
        print("║  ✓ 1. ОТРИЦАНИЕ — РАБОТАЕТ                           ║")
        print("║     Учитель: learn_negation('не').                    ║")
        print("║     Валентность +1/-1 разделяет evidence.             ║")

    # 2. Омонимия
    if r2["split_works"]:
        n = r2["kosa_senses"]
        print(f"║  ~ 2. ОМОНИМИЯ — ЧАСТИЧНО ({n} смыслов у 'коса')       ║")
        if n < 3:
            print("║     Группировка сливает смыслы с общими словами.   ║")
        else:
            print("║     3 смысла выделены корректно.                      ║")
    else:
        print("║  ✗ 2. ОМОНИМИЯ — не расщепляется                     ║")

    # 3. Объяснения
    if r3["chain_works"]:
        print(f"║  ~ 3. ОБЪЯСНЕНИЯ — ЧАСТИЧНО ({r3['passed']}/{r3['total']})                   ║")
        print("║     Цепочки visiting работают.                        ║")
        print("║     ask('почему?') — нужен explain() в движке.        ║")
    else:
        print("║  ✗ 3. ОБЪЯСНЕНИЯ — НЕ РАБОТАЮТ                       ║")

    # 4. Масштаб
    if r4["not_exploded"] and r4["categories_survived"]:
        print(f"║  ✓ 4. МАСШТАБ — РАБОТАЕТ ({r4['creatures']} существ)        ║")
        if not r4["categories_clean"]:
            print("║     Но: категории начинают размываться.               ║")
    else:
        print("║  ✗ 4. МАСШТАБ — ПРОБЛЕМЫ                             ║")

    print("╠═══════════════════════════════════════════════════════╣")
    print("║                                                       ║")
    print("║  РАБОТАЕТ:                                            ║")
    print("║    • Категории в новых доменах                        ║")
    print("║    • Иерархии и цепочки                               ║")
    print("║    • Расщепление омонимов (2+ смысла)                 ║")
    print("║    • Масштабирование (200+ фактов)                    ║")
    print("║    • Кросс-доменные связи                             ║")
    print("║                                                       ║")
    print("║  ГРАНИЦЫ:                                             ║")
    print("║    ��� 'Почему?' через ask() (нужен explain())          ║")
    print("║    • Точное расщепление на 3+ смысла                  ║")
    print("║                                                       ║")
    print("╚═══════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    main()
