#!/usr/bin/env python3
"""
Эксперимент: Мост между наблюдениями и книгой — без нового механизма.

Гипотеза: если дать не одну формулировку правила, а 5 разных,
то "ж" из наблюдений и "жи" из книги свяжутся САМИ через
общих родственников. Мост возникнет из данных.

Ключевые формулировки-мосты:
  "в слове жизнь — жи"  → содержит и "жизнь" (наблюдения) и "жи" (книга)
  "жираф пишется через жи" → содержит и "жираф" (наблюдения) и "жи" (книга)
"""

from chrysaline import World, Visitor


# ════════════════════════════════════════════════════════
# ДАННЫЕ
# ════════════════════════════════════════════════════════

# Наблюдения: слова с жи/ши, посимвольно
ZHI_SHI_WORDS = [
    list("жизнь"), list("жираф"), list("живот"), list("жилет"),
    list("жила"), list("ежи"), list("ужи"), list("ножи"),
    list("моржи"), list("стрижи"),
    list("шина"), list("шило"), list("широкий"), list("шиповник"),
    list("машина"), list("уши"), list("мыши"), list("камыши"),
    list("малыши"), list("карандаши"),
]

# Книга: разные формулировки одного правила (пословно)
BOOK_RULES_RICH = [
    # Формулировка 1: формальное правило
    ["жи", "пишется", "с", "буквой", "и"],
    ["ши", "пишется", "с", "буквой", "и"],

    # Формулировка 2: через "после"
    ["после", "ж", "пишем", "и"],
    ["после", "ш", "пишем", "и"],

    # Формулировка 3: "всегда вместе"
    ["ж", "и", "и", "всегда", "вместе"],
    ["ш", "и", "и", "всегда", "вместе"],

    # Формулировка 4: МОСТЫ — конкретные слова из наблюдений + книжное "жи"
    ["в", "слове", "жизнь", "есть", "жи"],
    ["в", "слове", "жираф", "есть", "жи"],
    ["в", "слове", "машина", "есть", "ши"],
    ["в", "слове", "мыши", "есть", "ши"],
    ["в", "слове", "ежи", "есть", "жи"],
    ["в", "слове", "уши", "есть", "ши"],

    # Формулировка 5: обобщение с конкретикой
    ["жираф", "пишется", "через", "жи"],
    ["машина", "пишется", "через", "ши"],
    ["жизнь", "пишется", "через", "жи"],
    ["камыши", "пишется", "через", "ши"],
]


def main():
    print("=" * 60)
    print("  ЭКСПЕРИМЕНТ: Естественный мост")
    print("  Наблюдения (посимвольно) + книга (5 формулировок)")
    print("  Свяжутся ли два уровня через общих родственников?")
    print("  Движок НЕ менялся. Новых механизмов НЕТ.")
    print("=" * 60)

    world = World()
    visitor = Visitor(world)

    # ════════════════════════════════════════
    # Фаза 1: только наблюдения
    # ════════════════════════════════════════

    print(f"\n  ── Фаза 1: наблюдения (20 слов посимвольно) ──")
    for r in range(5):
        for word in ZHI_SHI_WORDS:
            world.feed_sentence(word)
            world.run(1)

    alive1 = len(world.creatures)
    abst1 = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)

    zhi_pair = world._find_by_parts(("ж", "и"))
    shi_pair = world._find_by_parts(("ш", "и"))

    print(f"    {alive1} существ, {abst1} абстракций")
    zhi_fed = zhi_pair.times_fed if zhi_pair else 0
    zhi_e = zhi_pair.energy if zhi_pair else 0.0
    shi_fed = shi_pair.times_fed if shi_pair else 0
    shi_e = shi_pair.energy if shi_pair else 0.0
    print(f"    ж·и: fed={zhi_fed} e={zhi_e:.1f}")
    print(f"    ш·и: fed={shi_fed} e={shi_e:.1f}")

    # Что знает "ж" до книги?
    zh_before = visitor.visit("ж")
    zh_sibs_before = zh_before["siblings"] if zh_before["found"] else set()
    knows_book_before = any(w in zh_sibs_before for w in ["пишется", "пишем", "буквой", "слове"])
    print(f"    'ж' знает книжные слова: {knows_book_before}")

    # Знает ли "жизнь" что-то о "жи"?
    zhizn_before = visitor.visit("жизнь")
    zhizn_knows_zhi = False  # "жизнь" ещё не видела "жи" как слово

    # ════════════════════════════════════════
    # Фаза 2: добавляем книгу (5 формулировок)
    # ════════════════════════════════════════

    print(f"\n  ── Фаза 2: + книга (5 формулировок, пословно) ──")
    for r in range(3):
        for fact in BOOK_RULES_RICH:
            world.feed_sentence(fact)
            world.run(1)

    alive2 = len(world.creatures)
    abst2 = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)

    zhi_pair2 = world._find_by_parts(("ж", "и"))
    shi_pair2 = world._find_by_parts(("ш", "и"))

    print(f"    {alive2} существ, {abst2} абстракций")
    if zhi_pair2:
        print(f"    ж·и: fed={zhi_pair2.times_fed} e={zhi_pair2.energy:.1f}")
    if shi_pair2:
        print(f"    ш·и: fed={shi_pair2.times_fed} e={shi_pair2.energy:.1f}")

    # ════════════════════════════════════════
    # Анализ 1: "ж" узнал книжные слова?
    # ════════════════════════════════════════

    print(f"\n{'='*60}")
    print("  АНАЛИЗ 1: Символ 'ж' узнал книжные слова?")
    print("=" * 60)

    zh_after = visitor.visit("ж")
    zh_sibs_after = zh_after["siblings"] if zh_after["found"] else set()
    print(f"    visit('ж') братья: {sorted(zh_sibs_after)[:15]}")

    book_words_in_zh = {w for w in ["пишется", "пишем", "буквой", "слове", "всегда", "вместе", "после"]
                        if w in zh_sibs_after}
    print(f"    Книжные слова в братьях 'ж': {sorted(book_words_in_zh)}")
    print(f"    До книги: {knows_book_before} → После: {len(book_words_in_zh) > 0}")

    # ════════════════════════════════════════
    # Анализ 2: "жизнь" узнала "жи"?
    # ════════════════════════════════════════

    print(f"\n{'='*60}")
    print("  АНАЛИЗ 2: Слово 'жизнь' узнало книжное 'жи'?")
    print("=" * 60)

    zhizn_after = visitor.visit("жизнь")
    if zhizn_after["found"]:
        zhizn_sibs = zhizn_after["siblings"]
        print(f"    visit('жизнь') братья: {sorted(zhizn_sibs)[:10]}")
        knows_zhi = "жи" in zhizn_sibs
        knows_book = any(w in zhizn_sibs for w in ["пишется", "через", "слове", "есть"])
        print(f"    'жизнь' знает 'жи': {knows_zhi}")
        print(f"    'жизнь' знает книжные слова: {knows_book}")
    else:
        knows_zhi = False
        knows_book = False
        print(f"    'жизнь' не найдена")

    # ════════════════════════════════════════
    # Анализ 3: "жи" (книга) знает конкретные слова?
    # ════════════════════════════════════════

    print(f"\n{'='*60}")
    print("  АНАЛИЗ 3: Книжное 'жи' знает конкретные слова?")
    print("=" * 60)

    zhi_word = visitor.visit("жи")
    if zhi_word["found"]:
        zhi_sibs = zhi_word["siblings"]
        print(f"    visit('жи') братья: {sorted(zhi_sibs)[:15]}")

        concrete_words = {w for w in ["жизнь", "жираф", "ежи", "машина", "мыши"]
                          if w in zhi_sibs}
        book_context = {w for w in ["пишется", "буквой", "через", "слове", "есть"]
                        if w in zhi_sibs}
        print(f"    Конкретные слова из наблюдений: {sorted(concrete_words)}")
        print(f"    Книжный контекст: {sorted(book_context)}")

        zhi_mates = zhi_word.get("slot_mates", set())
        print(f"    Заменяемые: {sorted(zhi_mates)[:8]}")
        print(f"    'ши' в заменяемых: {'ши' in zhi_mates}")
    else:
        concrete_words = set()
        book_context = set()
        print(f"    'жи' не найдено")

    # ════════════════════════════════════════
    # Анализ 4: "ши" аналогично
    # ════════════════════════════════════════

    print(f"\n{'='*60}")
    print("  АНАЛИЗ 4: Книжное 'ши' знает конкретные слова?")
    print("=" * 60)

    shi_word = visitor.visit("ши")
    if shi_word["found"]:
        shi_sibs = shi_word["siblings"]
        print(f"    visit('ши') братья: {sorted(shi_sibs)[:15]}")
        shi_concrete = {w for w in ["машина", "мыши", "уши", "камыши", "шина", "шило"]
                        if w in shi_sibs}
        print(f"    Конкретные слова: {sorted(shi_concrete)}")
    else:
        shi_concrete = set()
        print(f"    'ши' не найдено")

    # ════════════════════════════════════════
    # Анализ 5: Цепочка — от конкретного к правилу
    # ════════════════════════════════════════

    print(f"\n{'='*60}")
    print("  АНАЛИЗ 5: Цепочка от конкретного слова к правилу")
    print("=" * 60)

    print(f"\n  Цепочка: жизнь → жи → пишется с буквой и")
    step1 = knows_zhi
    print(f"    1. жизнь знает жи: {step1}")

    step2 = "пишется" in (zhi_word.get("siblings", set()) if zhi_word.get("found") else set())
    print(f"    2. жи знает 'пишется': {step2}")

    step3 = "буквой" in (zhi_word.get("siblings", set()) if zhi_word.get("found") else set())
    print(f"    3. жи знает 'буквой': {step3}")

    chain_works = step1 and step2
    print(f"    Цепочка замкнута: {chain_works}")

    if chain_works:
        print(f"    МОСТ РАБОТАЕТ: жизнь → жи → пишется с буквой и")
        print(f"    Конкретное слово привело к абстрактному правилу!")

    # Обратная цепочка: от правила к конкретному
    print(f"\n  Обратная цепочка: жи (правило) → жизнь (пример)")
    reverse = "жизнь" in concrete_words
    print(f"    жи знает жизнь: {reverse}")
    if reverse:
        print(f"    МОСТ ДВУСТОРОННИЙ: правило ↔ пример")

    # ════════════════════════════════════════
    # Анализ 6: Абстракции — слились ли уровни?
    # ════════════════════════════════════════

    print(f"\n{'='*60}")
    print("  АНАЛИЗ 6: Абстракции после объединения")
    print("=" * 60)

    # Абстракция из наблюдений: $0·и = {ж, ш, ...}
    print(f"\n  Абстракции с 'и':")
    for c in world.creatures.values():
        if not c.alive or not c.slot_options or c.complexity != 2:
            continue
        if "и" in c.parts:
            for sn, opts in c.slot_options.items():
                clean = sorted(o for o in opts if not o.startswith("$"))
                if len(clean) >= 2:
                    print(f"    {c.name}  {sn}={clean}  fed={c.times_fed}")

    # Абстракции из книги: $0·пишется·с·буквой·и
    print(f"\n  Абстракции с 'пишется':")
    for c in world.creatures.values():
        if not c.alive or not c.slot_options:
            continue
        if "пишется" in c.parts:
            for sn, opts in c.slot_options.items():
                clean = sorted(o for o in opts if not o.startswith("$"))
                if clean:
                    print(f"    {c.name}  {sn}={clean}  fed={c.times_fed}")

    # Абстракции-мосты: содержат и книжные и наблюдательные элементы
    print(f"\n  Абстракции-мосты (книга + наблюдения):")
    for c in world.creatures.values():
        if not c.alive or not c.slot_options:
            continue
        parts_set = set(c.parts)
        has_book = parts_set & {"пишется", "через", "слове", "есть", "буквой"}
        has_obs = parts_set & {"жизнь", "жираф", "машина", "мыши", "ежи", "уши", "камыши"}
        if has_book and has_obs:
            for sn, opts in c.slot_options.items():
                clean = sorted(o for o in opts if not o.startswith("$"))
                if clean:
                    print(f"    {c.name}  {sn}={clean}  fed={c.times_fed}")

    # Абстракции со "слове"
    print(f"\n  Абстракция 'в слове $0 есть $1':")
    for c in world.creatures.values():
        if not c.alive or not c.slot_options:
            continue
        if "слове" in c.parts and "есть" in c.parts:
            slots = {}
            for sn, opts in c.slot_options.items():
                clean = sorted(o for o in opts if not o.startswith("$"))
                if clean:
                    slots[sn] = clean
            if slots:
                slots_str = " ".join(f"{k}={{{','.join(v)}}}" for k, v in slots.items())
                print(f"    {c.name}  {slots_str}  fed={c.times_fed}")

    # ════════════════════════════════════════
    # ИТОГ
    # ════════════════════════════════════════

    print(f"\n{'='*60}")
    print("╔═══════════════════════════════════════════════════════╗")
    print("║     ИТОГ: ЕСТЕСТВЕННЫЙ МОСТ                           ║")
    print("╠═══════════════════════════════════════════════════════╣")

    checks = []

    # 1. "ж" узнал книжные слова
    ok1 = len(book_words_in_zh) >= 2
    checks.append(ok1)
    s1 = "✓" if ok1 else "✗"
    print(f"║  {s1} 1. Символ 'ж' узнал книжные слова ({sorted(book_words_in_zh)[:3]})  ║")

    # 2. "жизнь" узнала "жи"
    ok2 = knows_zhi
    checks.append(ok2)
    s2 = "✓" if ok2 else "✗"
    print(f"║  {s2} 2. 'жизнь' (наблюд.) узнала 'жи' (книга)         ║")

    # 3. "жи" знает конкретные слова
    ok3 = len(concrete_words) >= 2
    checks.append(ok3)
    s3 = "✓" if ok3 else "✗"
    print(f"║  {s3} 3. 'жи' (книга) знает примеры ({sorted(concrete_words)[:3]})  ║")

    # 4. Цепочка жизнь → жи → пишется
    ok4 = chain_works
    checks.append(ok4)
    s4 = "✓" if ok4 else "✗"
    print(f"║  {s4} 4. Цепочка: жизнь → жи → пишется              ║")

    # 5. Мост двусторонний
    ok5 = reverse
    checks.append(ok5)
    s5 = "✓" if ok5 else "✗"
    print(f"║  {s5} 5. Мост двусторонний (правило ↔ пример)         ║")

    # 6. жи↔ши заменяемы
    ok6 = "ши" in (zhi_word.get("slot_mates", set()) if zhi_word.get("found") else set())
    checks.append(ok6)
    s6 = "✓" if ok6 else "✗"
    print(f"║  {s6} 6. жи↔ши заменяемы (оба уровня)                ║")

    passed = sum(checks)
    print(f"╠═══════════════════════════════════════════════════════╣")
    print(f"║  Результат: {passed}/6                                     ║")
    print(f"╠═══════════════════════════════════════════════════════╣")

    if passed >= 5:
        print(f"║                                                       ║")
        print(f"║  МОСТ ВОЗНИК САМ. Без нового механизма.              ║")
        print(f"║                                                       ║")
        print(f"║  Конкретное слово (жизнь) → книжный термин (жи) →   ║")
        print(f"║  → абстрактное правило (пишется с буквой и).        ║")
        print(f"║                                                       ║")
        print(f"║  Не модуль связывания. Не мост-алгоритм.            ║")
        print(f"║  Просто больше данных + существующие механизмы.      ║")
    elif passed >= 3:
        print(f"║                                                       ║")
        print(f"║  ЧАСТИЧНО: мост есть, но не все связи.               ║")
    else:
        print(f"║                                                       ║")
        print(f"║  НЕ СВЯЗАЛИСЬ. Нужно ещё больше данных               ║")
        print(f"║  или другой формат подачи.                            ║")

    print(f"║                                                       ║")
    print(f"║  Движок НЕ менялся. Новых механизмов НЕТ.             ║")
    print(f"╚═══════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    main()
