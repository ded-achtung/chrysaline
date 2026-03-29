#!/usr/bin/env python3
"""
Два теста на конкуренцию механизмов.

Тест 1: "Птицы летают" + исключения (страус, пингвин)
  Работают ли отрицание и конкуренция энергий ВМЕСТЕ?
  Правило живёт, но исключения его не убивают.

Тест 2: Правило из наблюдений + правило из книги
  30 слов с жи/ши (наблюдения) → $0·и = {ж, ш}
  + текст "жи ши пиши с буквой и" (книга)
  Усиливают ли они друг друга? Или конкурируют?
"""

from chrysaline import World, Visitor, Generator


# ════════════════════════════════════════════════════════
# ТЕСТ 1: Птицы летают + исключения
# ════════════════════════════════════════════════════════

BIRDS_FLY = [
    # Положительные: птицы которые летают
    ["воробей", "летает"],
    ["ворона", "летает"],
    ["голубь", "летает"],
    ["орёл", "летает"],
    ["ласточка", "летает"],
    ["сокол", "летает"],
    ["синица", "летает"],
    ["дятел", "летает"],

    # Все они — птицы
    ["воробей", "это", "птица"],
    ["ворона", "это", "птица"],
    ["голубь", "это", "птица"],
    ["орёл", "это", "птица"],
    ["ласточка", "это", "птица"],
    ["сокол", "это", "птица"],
    ["синица", "это", "птица"],
    ["дятел", "это", "птица"],

    # Исключения — тоже птицы, но НЕ летают
    ["страус", "это", "птица"],
    ["пингвин", "это", "птица"],

    # Отрицания
    ["страус", "не", "летает"],
    ["пингвин", "не", "летает"],

    # Дополнительные факты для контраста
    ["страус", "бегает"],
    ["пингвин", "плавает"],
    ["страус", "большой"],
    ["пингвин", "маленький"],
]


def test_birds():
    print("╔═══════════════════════════════════════════════════════╗")
    print("║  ТЕСТ 1: Птицы летают + исключения                   ║")
    print("║  Правило + отрицание + конкуренция энергий            ║")
    print("╚═══════════════════════════════════════════════════════╝")

    world = World()
    # Учитель: "не" — маркер отрицания
    world.learn_negation("не")

    visitor = Visitor(world)
    gen = Generator(world)

    for r in range(3):
        for fact in BIRDS_FLY:
            world.feed_sentence(fact)
            world.run(1)

    alive = len(world.creatures)
    abst = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"\n  Существ: {alive}, Абстракций: {abst}")
    print(f"  neg_markers: {world.neg_markers}")

    # ── Анализ 1: Кто летает? (абстракция $0·летает) ──
    print(f"\n  ── Кто летает? (абстракция) ──")
    for c in world.creatures.values():
        if not c.alive or not c.slot_options:
            continue
        if "летает" in c.parts:
            for sn, opts in c.slot_options.items():
                clean = sorted(o for o in opts if not o.startswith("$"))
                if clean:
                    val_mark = " [NEG]" if c.valence == -1 else ""
                    print(f"    {c.name}  {sn}={clean}  val={c.valence}{val_mark}")

    # ── Анализ 2: Visiting по страусу ──
    print(f"\n  ── visit('страус') ──")
    straus = visitor.visit("страус")
    if straus["found"]:
        print(f"    pos братья: {sorted(straus['siblings'])}")
        print(f"    neg братья: {sorted(straus.get('neg_siblings', set()))}")
        print(f"    'птица' в pos: {'птица' in straus['siblings']}")
        print(f"    'летает' в neg: {'летает' in straus.get('neg_siblings', set())}")
        print(f"    'летает' в pos: {'летает' in straus['siblings']}")

    # ── Анализ 3: Visiting по пингвину ──
    print(f"\n  ── visit('пингвин') ──")
    pingvin = visitor.visit("пингвин")
    if pingvin["found"]:
        print(f"    pos братья: {sorted(pingvin['siblings'])}")
        print(f"    neg братья: {sorted(pingvin.get('neg_siblings', set()))}")
        print(f"    'птица' в pos: {'птица' in pingvin['siblings']}")
        print(f"    'летает' в neg: {'летает' in pingvin.get('neg_siblings', set())}")

    # ── Анализ 4: Visiting по "летает" ──
    print(f"\n  ── visit('летает') ──")
    fly = visitor.visit("летает")
    if fly["found"]:
        print(f"    pos братья: {sorted(fly['siblings'])}")
        print(f"    neg братья: {sorted(fly.get('neg_siblings', set()))}")

    # ── Анализ 5: ask("кто летает?") ──
    print(f"\n  ── ask('кто летает?') ──")
    answer = gen.ask("кто летает?")
    print(f"    Ответ: {answer['answers'][:10]}")
    for r in answer["reasoning"][:3]:
        print(f"    Путь: {r}")

    straus_in = "страус" in answer["answers"]
    pingvin_in = "пингвин" in answer["answers"]
    print(f"    страус в ответе: {straus_in} (должен быть НЕТ)")
    print(f"    пингвин в ответе: {pingvin_in} (должен быть НЕТ)")

    # ── Анализ 6: ask("кто птица?") — страус должен быть! ──
    print(f"\n  ── ask('кто это птица?') ──")
    birds = gen.ask("кто это птица?")
    print(f"    Ответ: {birds['answers'][:10]}")
    straus_bird = "страус" in birds["answers"]
    pingvin_bird = "пингвин" in birds["answers"]
    print(f"    страус в ответе: {straus_bird} (должен быть ДА)")
    print(f"    пингвин в ответе: {pingvin_bird} (должен быть ДА)")

    # ── Анализ 7: Энергия конкурентов ──
    print(f"\n  ── Энергия конкурентов ──")
    for name in ["воробей", "ворона", "страус", "пингвин"]:
        flies = world._find_by_parts((name, "летает"))
        not_flies = world._find_by_parts((name, "не", "летает"))
        bird = world._find_by_parts((name, "это", "птица"))
        parts = []
        if flies:
            parts.append(f"летает: e={flies.energy:.1f} val={flies.valence}")
        if not_flies:
            parts.append(f"не·летает: e={not_flies.energy:.1f} val={not_flies.valence}")
        if bird:
            parts.append(f"птица: e={bird.energy:.1f} val={bird.valence}")
        print(f"    {name:10s} {' | '.join(parts)}")

    # ── ИТОГ ──
    checks = []

    # 1: страус = птица (pos)
    ok1 = "птица" in straus.get("siblings", set())
    checks.append(ok1)

    # 2: страус НЕ летает (neg)
    ok2 = "летает" in straus.get("neg_siblings", set())
    checks.append(ok2)

    # 3: пингвин = птица (pos)
    ok3 = "птица" in pingvin.get("siblings", set())
    checks.append(ok3)

    # 4: пингвин НЕ летает (neg)
    ok4 = "летает" in pingvin.get("neg_siblings", set())
    checks.append(ok4)

    # 5: "кто летает?" без страуса/пингвина
    ok5 = not straus_in and not pingvin_in
    checks.append(ok5)

    # 6: "кто птица?" включает страуса
    ok6 = straus_bird or pingvin_bird
    checks.append(ok6)

    # 7: летающих птиц >= 4
    real_flyers = [a for a in answer["answers"]
                   if a in {"воробей", "ворона", "голубь", "орёл", "ласточка", "сокол", "синица", "дятел"}]
    ok7 = len(real_flyers) >= 4
    checks.append(ok7)

    passed = sum(checks)
    print(f"\n  ── ИТОГ ──")
    print(f"  {'✓' if ok1 else '✗'} 1. страус = птица (pos)")
    print(f"  {'✓' if ok2 else '✗'} 2. страус НЕ летает (neg)")
    print(f"  {'✓' if ok3 else '✗'} 3. пингвин = птица (pos)")
    print(f"  {'✓' if ok4 else '✗'} 4. пингвин НЕ летает (neg)")
    print(f"  {'✓' if ok5 else '✗'} 5. 'кто летает?' без страуса/пингвина")
    print(f"  {'✓' if ok6 else '✗'} 6. 'кто птица?' включает исключения")
    print(f"  {'✓' if ok7 else '✗'} 7. В ответе >= 4 настоящих летунов ({real_flyers})")
    print(f"\n  Результат: {passed}/7")

    if passed >= 6:
        print(f"\n  ПРАВИЛО + ИСКЛЮЧЕНИЯ РАБОТАЮТ ВМЕСТЕ.")
        print(f"  Отрицание и конкуренция энергий совместимы.")
    elif passed >= 4:
        print(f"\n  ЧАСТИЧНО: механизмы работают, но есть утечки.")
    else:
        print(f"\n  НЕ РАБОТАЕТ: механизмы мешают друг другу.")

    return passed


# ════════════════════════════════════════════════════════
# ТЕСТ 2: Наблюдения + книга
# ════════════════════════════════════════════════════════

# Те же слова с жи/ши из прошлого эксперимента
ZHI_SHI_WORDS = [
    list("жизнь"), list("жираф"), list("живот"), list("жилет"),
    list("жила"), list("ежи"), list("ужи"), list("ножи"),
    list("моржи"), list("стрижи"),
    list("шина"), list("шило"), list("широкий"), list("шиповник"),
    list("машина"), list("уши"), list("мыши"), list("камыши"),
    list("малыши"), list("карандаши"),
]

# Правило из книги (пословно, не посимвольно!)
BOOK_RULE = [
    ["жи", "пишется", "с", "буквой", "и"],
    ["ши", "пишется", "с", "буквой", "и"],
    ["жи", "ши", "пиши", "с", "буквой", "и"],
    ["после", "ж", "пишем", "и"],
    ["после", "ш", "пишем", "и"],
]


def test_observation_plus_book():
    print(f"\n╔═══════════════════════════════════════════════════════╗")
    print(f"║  ТЕСТ 2: Наблюдения + книга                          ║")
    print(f"║  20 слов посимвольно → абстракция $0·и               ║")
    print(f"║  + текст книги «жи ши пиши с буквой и»              ║")
    print(f"║  Усиливают ли друг друга?                            ║")
    print(f"╚═══════════════════════════════════════════════════════╝")

    world = World()
    visitor = Visitor(world)

    # ── Фаза 1: только наблюдения (посимвольно) ──
    print(f"\n  ── Фаза 1: наблюдения (20 слов посимвольно) ──")
    for r in range(5):
        for word in ZHI_SHI_WORDS:
            world.feed_sentence(word)
            world.run(1)

    alive1 = len(world.creatures)
    abst1 = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"    {alive1} существ, {abst1} абстракций")

    # Что знает система после наблюдений?
    zh_info1 = visitor.visit("ж")
    sh_info1 = visitor.visit("ш")
    i_info1 = visitor.visit("и")

    zh_knows_i_1 = "и" in zh_info1.get("siblings", set()) if zh_info1["found"] else False
    sh_knows_i_1 = "и" in sh_info1.get("siblings", set()) if sh_info1["found"] else False
    zh_sh_mates_1 = "ш" in zh_info1.get("slot_mates", set()) if zh_info1["found"] else False

    print(f"    ж знает и: {zh_knows_i_1}")
    print(f"    ш знает и: {sh_knows_i_1}")
    print(f"    ж↔ш заменяемы: {zh_sh_mates_1}")

    # Энергия ж·и до книги
    zhi_before = world._find_by_parts(("ж", "и"))
    shi_before = world._find_by_parts(("ш", "и"))
    zhi_e_before = zhi_before.energy if zhi_before else 0
    shi_e_before = shi_before.energy if shi_before else 0
    zhi_fed_before = zhi_before.times_fed if zhi_before else 0
    shi_fed_before = shi_before.times_fed if shi_before else 0
    print(f"    ж·и: e={zhi_e_before:.1f} fed={zhi_fed_before}")
    print(f"    ш·и: e={shi_e_before:.1f} fed={shi_fed_before}")

    # Абстракция $0·и до книги
    slot_i_before = None
    for c in world.creatures.values():
        if c.alive and c.slot_options and c.complexity == 2:
            if c.parts[1] == "и" and c.parts[0].startswith("$"):
                sn = c.parts[0]
                clean = sorted(o for o in c.slot_options.get(sn, set()) if not o.startswith("$"))
                slot_i_before = clean
                print(f"    $0·и до книги: {clean}")

    # ── Фаза 2: добавляем книжное правило ──
    print(f"\n  ── Фаза 2: + книжное правило (пословно) ──")
    for r in range(3):
        for fact in BOOK_RULE:
            world.feed_sentence(fact)
            world.run(1)

    alive2 = len(world.creatures)
    abst2 = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"    {alive2} существ, {abst2} абстракций")

    # Энергия ж·и ПОСЛЕ книги
    zhi_after = world._find_by_parts(("ж", "и"))
    shi_after = world._find_by_parts(("ш", "и"))
    zhi_e_after = zhi_after.energy if zhi_after else 0
    shi_e_after = shi_after.energy if shi_after else 0
    zhi_fed_after = zhi_after.times_fed if zhi_after else 0
    shi_fed_after = shi_after.times_fed if shi_after else 0

    print(f"    ж·и: e={zhi_e_before:.1f}→{zhi_e_after:.1f}  fed={zhi_fed_before}→{zhi_fed_after}")
    print(f"    ш·и: e={shi_e_before:.1f}→{shi_e_after:.1f}  fed={shi_fed_before}→{shi_fed_after}")

    zhi_grew = zhi_fed_after > zhi_fed_before
    shi_grew = shi_fed_after > shi_fed_before
    print(f"    ж·и окрепла: {zhi_grew}")
    print(f"    ш·и окрепла: {shi_grew}")

    # ── Анализ: что знает visiting после книги? ──
    print(f"\n  ── Visiting после книги ──")

    # visit("жи") — книжное существо "жи" как целое слово
    zhi_word = visitor.visit("жи")
    if zhi_word["found"]:
        print(f"    visit('жи'): братья={sorted(zhi_word['siblings'])}")
        print(f"      'буквой' в братьях: {'буквой' in zhi_word['siblings']}")
        print(f"      'пишется' в братьях: {'пишется' in zhi_word['siblings']}")
        print(f"      'ши' в заменяемых: {'ши' in zhi_word['slot_mates']}")

    shi_word = visitor.visit("ши")
    if shi_word["found"]:
        print(f"    visit('ши'): братья={sorted(shi_word['siblings'])}")
        print(f"      'ши'↔'жи' заменяемы: {'жи' in shi_word['slot_mates']}")

    # visit("ж") — символ из наблюдений
    zh_info2 = visitor.visit("ж")
    if zh_info2["found"]:
        print(f"    visit('ж'): братья={sorted(zh_info2['siblings'])[:10]}")
        # Нашёл ли ж связь с "пишется"?
        knows_pishetsya = "пишется" in zh_info2["siblings"] or "пишем" in zh_info2["siblings"]
        print(f"      'ж' знает 'пишется'/'пишем': {knows_pishetsya}")

    # ── Анализ: два пути к одному выводу ──
    print(f"\n  ── Два пути к одному выводу ──")

    # Путь 1: наблюдения → $0·и = {ж, ш, ...}
    path1 = False
    for c in world.creatures.values():
        if c.alive and c.slot_options and c.complexity == 2:
            if c.parts[1] == "и" and c.parts[0].startswith("$"):
                sn = c.parts[0]
                clean = {o for o in c.slot_options.get(sn, set()) if not o.startswith("$")}
                if "ж" in clean and "ш" in clean:
                    path1 = True
                    print(f"    Путь 1 (наблюдения): $0·и = {sorted(clean)}")

    # Путь 2: книга → "жи·пишется·с·буквой·и"
    path2_creatures = []
    for c in world.creatures.values():
        if not c.alive or c.complexity < 3:
            continue
        parts_set = set(c.parts)
        if "пишется" in parts_set and ("жи" in parts_set or "ши" in parts_set):
            path2_creatures.append(c)
    path2 = len(path2_creatures) > 0
    if path2:
        for c in path2_creatures[:3]:
            print(f"    Путь 2 (книга): {c.name}  val={c.valence}")

    # Мост между путями: "жи" (книга) связано с "ж"+"и" (наблюдения)?
    print(f"\n  ── Мост между путями ──")
    # "жи" как целое слово знает "буквой", "пишется"
    # "ж" как символ знает "и" как брата
    # Связаны ли они через visiting?

    zhi_sibs = zhi_word.get("siblings", set()) if zhi_word.get("found") else set()
    zh_sibs = zh_info2.get("siblings", set()) if zh_info2["found"] else set()

    common = zhi_sibs & zh_sibs
    print(f"    Общие братья у 'жи' (книга) и 'ж' (наблюдения): {sorted(common)[:8]}")
    bridge = len(common) > 0
    print(f"    Мост существует: {bridge}")

    if "и" in common:
        print(f"    Ключ: оба знают 'и' — наблюдения и книга сходятся!")

    # ── ИТОГ ──
    checks = []

    checks.append(zhi_grew)
    checks.append(shi_grew)
    checks.append(path1)
    checks.append(path2)
    checks.append(bridge)

    # жи и ши заменяемы (книга тоже это подтвердила)?
    zhi_shi_mates = "ши" in zhi_word.get("slot_mates", set()) if zhi_word.get("found") else False
    checks.append(zhi_shi_mates)

    passed = sum(checks)
    print(f"\n  ── ИТОГ ──")
    print(f"  {'✓' if zhi_grew else '✗'} 1. ж·и окрепла после книги")
    print(f"  {'✓' if shi_grew else '✗'} 2. ш·и окрепла после книги")
    print(f"  {'✓' if path1 else '✗'} 3. Путь 1 (наблюдения): $0·и = {{ж, ш}}")
    print(f"  {'✓' if path2 else '✗'} 4. Путь 2 (книга): жи·пишется·с·буквой·и")
    print(f"  {'✓' if bridge else '✗'} 5. Мост между путями (общие братья)")
    print(f"  {'✓' if zhi_shi_mates else '✗'} 6. жи↔ши заменяемы (книга подтвердила)")
    print(f"\n  Результат: {passed}/6")

    if passed >= 5:
        print(f"\n  НАБЛЮДЕНИЯ И КНИГА УСИЛИВАЮТ ДРУГ ДРУГА.")
        print(f"  Два разных пути к одному выводу.")
        print(f"  Не конкуренция — подтверждение.")
    elif passed >= 3:
        print(f"\n  ЧАСТИЧНО: оба пути работают, но мост слабый.")
    else:
        print(f"\n  НЕ СВЯЗАЛИСЬ: наблюдения и книга — два отдельных мира.")

    return passed


# ════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("  ТЕСТЫ НА КОНКУРЕНЦИЮ МЕХАНИЗМОВ")
    print("  1. Правило + исключения (птицы + страус)")
    print("  2. Наблюдения + книга (жи-ши)")
    print("  Движок НЕ менялся.")
    print("=" * 60)

    r1 = test_birds()
    r2 = test_observation_plus_book()

    print(f"\n{'='*60}")
    print("╔═══════════════════════════════════════════════════════╗")
    print("║         ИТОГ: КОНКУРЕНЦИЯ МЕХАНИЗМОВ                  ║")
    print("╠═══════════════════════════════════════════════════════╣")
    s1 = "✓" if r1 >= 6 else "~" if r1 >= 4 else "✗"
    s2 = "✓" if r2 >= 5 else "~" if r2 >= 3 else "✗"
    print(f"║  {s1} Тест 1: Правило + исключения ({r1}/7)             ║")
    print(f"║  {s2} Тест 2: Наблюдения + книга ({r2}/6)               ║")
    print(f"╠═══════════════════════════════════════════════════════╣")
    if r1 >= 6 and r2 >= 5:
        print(f"║                                                       ║")
        print(f"║  Механизмы НЕ мешают друг другу.                     ║")
        print(f"║  Отрицание + конкуренция = правило с исключениями.   ║")
        print(f"║  Наблюдения + книга = двойное подтверждение.         ║")
    elif r1 >= 4 and r2 >= 3:
        print(f"║                                                       ║")
        print(f"║  Механизмы ЧАСТИЧНО совместимы.                      ║")
    print(f"╚═══════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    main()
