#!/usr/bin/env python3
"""
Эксперимент: может ли система САМА найти правило "жи-ши пишется с и"?

Условия:
  - Движок НЕ менялся
  - Никаких правил не подаётся
  - Только слова, посимвольно: ж-и-з-н-ь, ш-и-н-а, ...
  - Система должна САМА заметить: после ж и ш всегда идёт и

Это тест на индукцию правил из наблюдений.
"""

from chrysaline import World, Visitor


# ════════════════════════════════════════════════════════
# ДАННЫЕ: слова с "жи" и "ши", посимвольно
# ════════════════════════════════════════════════════════

# Слова с ЖИ
ZHI_WORDS = [
    list("жизнь"),      # ж-и-з-н-ь
    list("жираф"),      # ж-и-р-а-ф
    list("живот"),       # ж-и-в-о-т
    list("жилет"),       # ж-и-л-е-т
    list("жила"),        # ж-и-л-а
    list("ежи"),         # е-ж-и
    list("ужи"),         # у-ж-и
    list("ножи"),        # н-о-ж-и
    list("моржи"),       # м-о-р-ж-и
    list("стрижи"),      # с-т-р-и-ж-и
]

# Слова с ШИ
SHI_WORDS = [
    list("шина"),        # ш-и-н-а
    list("шило"),        # ш-и-л-о
    list("широкий"),     # ш-и-р-о-к-и-й
    list("шиповник"),    # ш-и-п-о-в-н-и-к
    list("машина"),      # м-а-ш-и-н-а
    list("уши"),         # у-ш-и
    list("мыши"),        # м-ы-ш-и
    list("камыши"),      # к-а-м-ы-ш-и
    list("малыши"),      # м-а-л-ы-ш-и
    list("карандаши"),    # к-а-р-а-н-д-а-ш-и
]

# Контрольные слова БЕЗ жи/ши (чтобы был контраст)
CONTROL_WORDS = [
    list("кошка"),       # к-о-ш-к-а  (ш но НЕ ши!)
    list("ложка"),       # л-о-ж-к-а  (ж но НЕ жи!)
    list("мешок"),       # м-е-ш-о-к  (ш+о, не ш+и)
    list("лужа"),        # л-у-ж-а    (ж+а, не ж+и)
    list("каша"),        # к-а-ш-а    (ш+а)
    list("кожа"),        # к-о-ж-а    (ж+а)
    list("лошадь"),      # л-о-ш-а-д-ь (ш+а)
    list("пожар"),       # п-о-ж-а-р  (ж+а)
    list("душа"),        # д-у-ш-а    (ш+а)
    list("жара"),        # ж-а-р-а    (ж+а, не ж+и)
]


def main():
    print("=" * 60)
    print("  ЭКСПЕРИМЕНТ: Найдёт ли система правило ЖИ-ШИ?")
    print("  20 слов с жи/ши + 10 контрольных. Посимвольно.")
    print("  Движок НЕ менялся. Правила НЕ подавались.")
    print("=" * 60)

    world = World()
    visitor = Visitor(world)

    all_words = ZHI_WORDS + SHI_WORDS + CONTROL_WORDS
    print(f"\n  Подаём {len(all_words)} слов посимвольно:")
    for w in all_words[:5]:
        print(f"    {'·'.join(w)}")
    print(f"    ... и ещё {len(all_words) - 5}")

    # Подаём 5 раундов
    for r in range(5):
        for word in all_words:
            world.feed_sentence(word)
            world.run(1)

    alive = len(world.creatures)
    abst = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"\n  Существ: {alive}, Абстракций: {abst}")

    # ════════════════════════════════════════
    # АНАЛИЗ 1: Что идёт после Ж?
    # ════════════════════════════════════════

    print(f"\n{'='*60}")
    print("  АНАЛИЗ 1: Что система видит после Ж и Ш?")
    print("=" * 60)

    # Пары с ж
    zh_pairs = {}
    sh_pairs = {}
    for c in world.creatures.values():
        if not c.alive or c.complexity != 2 or c.slot_options:
            continue
        if c.parts[0] == "ж":
            char = c.parts[1]
            zh_pairs[char] = zh_pairs.get(char, 0) + c.times_fed
        if c.parts[0] == "ш":
            char = c.parts[1]
            sh_pairs[char] = sh_pairs.get(char, 0) + c.times_fed

    print(f"\n  После Ж встречается:")
    for char, fed in sorted(zh_pairs.items(), key=lambda x: -x[1]):
        bar = "█" * max(1, fed // 2)
        is_i = " ← И!" if char == "и" else ""
        print(f"    ж+{char}  fed={fed:3d}  {bar}{is_i}")

    print(f"\n  После Ш встречается:")
    for char, fed in sorted(sh_pairs.items(), key=lambda x: -x[1]):
        bar = "█" * max(1, fed // 2)
        is_i = " ← И!" if char == "и" else ""
        print(f"    ш+{char}  fed={fed:3d}  {bar}{is_i}")

    # Доминирует ли И?
    zh_i = zh_pairs.get("и", 0)
    zh_total = sum(zh_pairs.values())
    sh_i = sh_pairs.get("и", 0)
    sh_total = sum(sh_pairs.values())

    zh_ratio = zh_i / max(1, zh_total)
    sh_ratio = sh_i / max(1, sh_total)

    print(f"\n  ── Доминирование И ──")
    print(f"    ж+и: {zh_i}/{zh_total} = {zh_ratio:.0%}")
    print(f"    ш+и: {sh_i}/{sh_total} = {sh_ratio:.0%}")

    # ════════════════════════════════════════
    # АНАЛИЗ 2: Абстракции — нашла ли паттерн?
    # ════════════════════════════════════════

    print(f"\n{'='*60}")
    print("  АНАЛИЗ 2: Абстракции — есть ли паттерн $0·и?")
    print("=" * 60)

    # Ищем абстракции вида $0·и или ж·$0 или ш·$0
    relevant = []
    for c in world.creatures.values():
        if not c.alive or not c.slot_options:
            continue
        parts_str = "·".join(c.parts)
        has_zh = "ж" in c.parts or "ш" in c.parts
        has_i = "и" in c.parts
        has_slot = any(p.startswith("$") for p in c.parts)
        if (has_zh or has_i) and has_slot:
            relevant.append(c)

    relevant.sort(key=lambda c: -c.times_fed)

    if relevant:
        print(f"\n  Найдено {len(relevant)} абстракций с ж/ш/и:")
        for c in relevant[:15]:
            slots = {}
            for sn, opts in c.slot_options.items():
                clean = sorted(o for o in opts if not o.startswith("$"))
                if clean:
                    slots[sn] = clean
            if slots:
                slots_str = " ".join(f"{k}={{{','.join(v)}}}" for k, v in slots.items())
                print(f"    {c.name}  {slots_str}  (fed={c.times_fed})")
    else:
        print(f"\n  Абстракций с ж/ш/и: 0")

    # Ключевой вопрос: есть ли $0·и где $0={ж,ш}?
    print(f"\n  ── Ключевой паттерн: $0·и где $0 содержит ж и ш? ──")
    found_pattern = False
    for c in world.creatures.values():
        if not c.alive or not c.slot_options:
            continue
        if c.complexity == 2 and "и" in c.parts:
            for sn, opts in c.slot_options.items():
                clean = {o for o in opts if not o.startswith("$")}
                has_zh = "ж" in clean
                has_sh = "ш" in clean
                if has_zh or has_sh:
                    print(f"    НАЙДЕН: {c.name}  {sn}={sorted(clean)}")
                    found_pattern = True
                    if has_zh and has_sh:
                        print(f"    ЭТО ПРАВИЛО ЖИ-ШИ! Система нашла: $0·и, $0={{ж, ш}}")

    if not found_pattern:
        # Может быть наоборот: ж·$0 или ш·$0?
        for c in world.creatures.values():
            if not c.alive or not c.slot_options:
                continue
            if "ж" in c.parts or "ш" in c.parts:
                for sn, opts in c.slot_options.items():
                    clean = {o for o in opts if not o.startswith("$")}
                    if "и" in clean:
                        print(f"    НАЙДЕН (обратный): {c.name}  {sn}={sorted(clean)}")
                        found_pattern = True

    if not found_pattern:
        print(f"    Паттерн НЕ найден как абстракция.")
        print(f"    Но пара ж·и существует как организм — проверим visiting.")

    # ════════════════════════════════════════
    # АНАЛИЗ 3: Visiting — что знает Ж? Что знает Ш?
    # ════════════════════════════════════════

    print(f"\n{'='*60}")
    print("  АНАЛИЗ 3: Visiting — родственники Ж и Ш")
    print("=" * 60)

    zh_info = visitor.visit("ж")
    if zh_info["found"]:
        print(f"\n  visit('ж'):")
        print(f"    братья: {sorted(zh_info['siblings'])}")
        print(f"    заменяемые: {sorted(zh_info['slot_mates'])[:10]}")
        print(f"    'и' в братьях: {'и' in zh_info['siblings']}")
        print(f"    'ш' в заменяемых: {'ш' in zh_info['slot_mates']}")

    sh_info = visitor.visit("ш")
    if sh_info["found"]:
        print(f"\n  visit('ш'):")
        print(f"    братья: {sorted(sh_info['siblings'])}")
        print(f"    заменяемые: {sorted(sh_info['slot_mates'])[:10]}")
        print(f"    'и' в братьях: {'и' in sh_info['siblings']}")
        print(f"    'ж' в заменяемых: {'ж' in sh_info['slot_mates']}")

    i_info = visitor.visit("и")
    if i_info["found"]:
        print(f"\n  visit('и'):")
        print(f"    братья: {sorted(i_info['siblings'])[:15]}")
        print(f"    'ж' в братьях: {'ж' in i_info['siblings']}")
        print(f"    'ш' в братьях: {'ш' in i_info['siblings']}")

    # ════════════════════════════════════════
    # АНАЛИЗ 4: Ж и Ш — заменяемы?
    # ════════════════════════════════════════

    print(f"\n{'='*60}")
    print("  АНАЛИЗ 4: Ж и Ш — заменяемы ли они?")
    print("=" * 60)

    zh_mates = zh_info.get("slot_mates", set()) if zh_info["found"] else set()
    sh_mates = sh_info.get("slot_mates", set()) if sh_info["found"] else set()

    zh_and_sh = "ш" in zh_mates or "ж" in sh_mates
    print(f"\n  Ж и Ш в одном слоте (заменяемы): {zh_and_sh}")

    if zh_and_sh:
        print(f"  Система обнаружила: Ж и Ш ведут себя ОДИНАКОВО.")
        print(f"  После обоих — одна и та же буква (И).")
        print(f"  Это и есть правило ЖИ-ШИ, найденное из наблюдений!")

    # ════════════════════════════════════════
    # АНАЛИЗ 5: Контраст — ж+а vs ж+и
    # ════════════════════════════════════════

    print(f"\n{'='*60}")
    print("  АНАЛИЗ 5: Контраст — ж+а vs ж+и в контрольных словах")
    print("=" * 60)

    # Энергия пар
    zhi_creature = world._find_by_parts(("ж", "и"))
    zha_creature = world._find_by_parts(("ж", "а"))
    shi_creature = world._find_by_parts(("ш", "и"))
    sha_creature = world._find_by_parts(("ш", "а"))

    print(f"\n  Энергия пар:")
    if zhi_creature:
        print(f"    ж·и  e={zhi_creature.energy:.1f}  fed={zhi_creature.times_fed}")
    if zha_creature:
        print(f"    ж·а  e={zha_creature.energy:.1f}  fed={zha_creature.times_fed}")
    if shi_creature:
        print(f"    ш·и  e={shi_creature.energy:.1f}  fed={shi_creature.times_fed}")
    if sha_creature:
        print(f"    ш·а  e={sha_creature.energy:.1f}  fed={sha_creature.times_fed}")

    zhi_stronger = (zhi_creature and zha_creature and
                    zhi_creature.times_fed > zha_creature.times_fed)
    shi_stronger = (shi_creature and sha_creature and
                    shi_creature.times_fed > sha_creature.times_fed)

    print(f"\n  ж·и сильнее ж·а: {zhi_stronger}")
    print(f"  ш·и сильнее ш·а: {shi_stronger}")

    # ════════════════════════════════════════
    # ИТОГ
    # ════════════════════════════════════════

    print(f"\n{'='*60}")
    print("╔═══════════════════════════════════════════════════════╗")
    print("║         ИТОГ: ПРАВИЛО ЖИ-ШИ ИЗ НАБЛЮДЕНИЙ          ║")
    print("╠═══════════════════════════════════════════════════════╣")

    checks = []

    # Проверка 1: ж+и доминирует после ж
    ok1 = zh_ratio > 0.4
    checks.append(ok1)
    s1 = "✓" if ok1 else "✗"
    print(f"║  {s1} 1. После Ж доминирует И ({zh_ratio:.0%})              ║")

    # Проверка 2: ш+и доминирует после ш
    ok2 = sh_ratio > 0.4
    checks.append(ok2)
    s2 = "✓" if ok2 else "✗"
    print(f"║  {s2} 2. После Ш доминирует И ({sh_ratio:.0%})              ║")

    # Проверка 3: ж·и сильнее ж·а
    checks.append(zhi_stronger)
    s3 = "✓" if zhi_stronger else "✗"
    print(f"║  {s3} 3. ж·и сильнее ж·а                                ║")

    # Проверка 4: ш·и сильнее ш·а
    checks.append(shi_stronger)
    s4 = "✓" if shi_stronger else "✗"
    print(f"║  {s4} 4. ш·и сильнее ш·а                                ║")

    # Проверка 5: ж и ш — братья (через visiting)
    zh_i_brothers = "и" in zh_info.get("siblings", set()) if zh_info["found"] else False
    sh_i_brothers = "и" in sh_info.get("siblings", set()) if sh_info["found"] else False
    ok5 = zh_i_brothers and sh_i_brothers
    checks.append(ok5)
    s5 = "✓" if ok5 else "✗"
    print(f"║  {s5} 5. И — брат и Ж и Ш (visiting)                    ║")

    # Проверка 6: ж и ш заменяемы
    checks.append(zh_and_sh)
    s6 = "✓" if zh_and_sh else "✗"
    print(f"║  {s6} 6. Ж и Ш заменяемы (в одном слоте)                ║")

    # Проверка 7: абстракция $0·и = {ж, ш, ...}
    checks.append(found_pattern)
    s7 = "✓" if found_pattern else "✗"
    print(f"║  {s7} 7. Абстракция с паттерном ж/ш + и                 ║")

    passed = sum(checks)
    print(f"╠═══════════════════════════════════════════════════════╣")
    print(f"║  Результат: {passed}/7                                     ║")
    print(f"╠═══════════════════════════════════════════════════════╣")

    if passed >= 5:
        print(f"║                                                       ║")
        print(f"║  СИСТЕМА НАШЛА ПРАВИЛО ЖИ-ШИ ИЗ НАБЛЮДЕНИЙ.         ║")
        print(f"║  Без подсказок. Без правил. Из 30 слов.              ║")
        print(f"║  Ж и Ш ведут себя одинаково → после них И.           ║")
        print(f"║  Это индукция правила из данных.                     ║")
    elif passed >= 3:
        print(f"║                                                       ║")
        print(f"║  ЧАСТИЧНО: система видит закономерность,              ║")
        print(f"║  но не оформила её в абстракцию.                     ║")
        print(f"║  Пары ж·и и ш·и сильные. Правило — в зародыше.      ║")
    else:
        print(f"║                                                       ║")
        print(f"║  НЕ НАШЛА. Данных мало или паттерн не тот.           ║")
        print(f"║  Нужно больше слов или другая подача.                 ║")

    print(f"║                                                       ║")
    print(f"║  Движок НЕ менялся. Правила НЕ подавались.            ║")
    print(f"║  Только слова. Посимвольно. 30 штук.                  ║")
    print(f"╚═══════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    main()
