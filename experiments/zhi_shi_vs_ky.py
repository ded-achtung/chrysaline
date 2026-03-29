#!/usr/bin/env python3
"""
Эксперимент: железное ядро vs слабая периферия.

Подаём 30 слов с жи/ши (из прошлого теста) + 20 слов с кы/ры/ны.
Вопрос: разделит ли система слот $0·и на:
  - железное ядро {ж, ш} — ВСЕГДА перед и
  - слабую периферию {к, р, н, ...} — ИНОГДА перед и, иногда нет

Если ж/ш доминируют по энергии/частоте перед и, а к/р/н — нет,
значит система ВИДИТ разницу между правилом и совпадением.
"""

from chrysaline import World, Visitor


# ════════════════════════════════════════════════════════
# ДАННЫЕ
# ════════════════════════════════════════════════════════

# Слова с ЖИ (из прошлого теста)
ZHI_WORDS = [
    list("жизнь"), list("жираф"), list("живот"), list("жилет"),
    list("жила"), list("ежи"), list("ужи"), list("ножи"),
    list("моржи"), list("стрижи"),
]

# Слова с ШИ
SHI_WORDS = [
    list("шина"), list("шило"), list("широкий"), list("шиповник"),
    list("машина"), list("уши"), list("мыши"), list("камыши"),
    list("малыши"), list("карандаши"),
]

# Контрольные слова БЕЗ жи/ши
CONTROL_WORDS = [
    list("кошка"), list("ложка"), list("мешок"), list("лужа"),
    list("каша"), list("кожа"), list("лошадь"), list("пожар"),
    list("душа"), list("жара"),
]

# НОВОЕ: слова с КЫ/РЫ/НЫ — и перед ними тоже бывает
KY_WORDS = [
    list("рыба"),       # р-ы-б-а
    list("рыжий"),      # р-ы-ж-и-й   (ры + жи!)
    list("рынок"),       # р-ы-н-о-к
    list("рысь"),        # р-ы-с-ь
    list("крыша"),       # к-р-ы-ш-а
    list("крыло"),       # к-р-ы-л-о
    list("тыква"),       # т-ы-к-в-а
    list("дыня"),        # д-ы-н-я
    list("дым"),         # д-ы-м
    list("сын"),         # с-ы-н
    list("мыло"),        # м-ы-л-о
    list("мышь"),        # м-ы-ш-ь   (ы+ш, не и+ш!)
    list("выход"),       # в-ы-х-о-д
    list("язык"),        # я-з-ы-к
    list("быстро"),      # б-ы-с-т-р-о
    list("сыр"),         # с-ы-р
    list("бык"),         # б-ы-к
    list("рыть"),        # р-ы-т-ь
    list("ныть"),        # н-ы-т-ь
    list("выть"),        # в-ы-т-ь
]

# Ещё слова где К/Р/Н стоят перед И (конкурируют с ж/ш)
KI_RI_NI_WORDS = [
    list("кино"),        # к-и-н-о     (к+и)
    list("кит"),         # к-и-т       (к+и)
    list("рис"),         # р-и-с       (р+и)
    list("нитка"),       # н-и-т-к-а   (н+и)
    list("книга"),       # к-н-и-г-а   (н+и)
    list("лиса"),        # л-и-с-а     (л+и)
    list("вилка"),       # в-и-л-к-а   (в+и)
    list("зима"),        # з-и-м-а     (з+и)
    list("пила"),        # п-и-л-а     (п+и)
    list("сила"),        # с-и-л-а     (с+и)
]


def main():
    print("=" * 60)
    print("  ЭКСПЕРИМЕНТ: Железное ядро vs слабая периферия")
    print("  30 слов жи/ши + 20 слов кы/ры + 10 слов ки/ри/ни")
    print("  + 10 контрольных. Посимвольно. Движок НЕ менялся.")
    print("=" * 60)

    world = World()
    visitor = Visitor(world)

    all_words = ZHI_WORDS + SHI_WORDS + CONTROL_WORDS + KY_WORDS + KI_RI_NI_WORDS

    print(f"\n  Всего слов: {len(all_words)}")
    print(f"    жи-слова: {len(ZHI_WORDS)}")
    print(f"    ши-слова: {len(SHI_WORDS)}")
    print(f"    контроль (ж+а, ш+а): {len(CONTROL_WORDS)}")
    print(f"    кы/ры/ны-слова: {len(KY_WORDS)}")
    print(f"    ки/ри/ни-слова: {len(KI_RI_NI_WORDS)}")

    for r in range(5):
        for word in all_words:
            world.feed_sentence(word)
            world.run(1)

    alive = len(world.creatures)
    abst = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"\n  Существ: {alive}, Абстракций: {abst}")

    # ════════════════════════════════════════
    # АНАЛИЗ 1: Кто стоит перед И?
    # ════════════════════════════════════════

    print(f"\n{'='*60}")
    print("  АНАЛИЗ 1: Все пары $X·и — кто стоит перед И?")
    print("=" * 60)

    before_i = {}
    for c in world.creatures.values():
        if not c.alive or c.complexity != 2 or c.slot_options:
            continue
        if c.parts[1] == "и":
            char = c.parts[0]
            before_i[char] = (c.times_fed, c.energy)

    # Кто стоит перед Ы (конкурент)
    before_y = {}
    for c in world.creatures.values():
        if not c.alive or c.complexity != 2 or c.slot_options:
            continue
        if c.parts[1] == "ы":
            char = c.parts[0]
            before_y[char] = (c.times_fed, c.energy)

    print(f"\n  Перед И (отсортировано по частоте):")
    sorted_i = sorted(before_i.items(), key=lambda x: -x[1][0])
    for char, (fed, energy) in sorted_i:
        bar = "█" * max(1, fed // 2)
        # Этот символ бывает и перед Ы?
        y_fed = before_y.get(char, (0, 0))[0]
        ratio = fed / max(1, fed + y_fed)
        exclusive = "  ← ТОЛЬКО перед И!" if y_fed == 0 and fed >= 10 else ""
        both = f"  (и·{fed} vs ы·{y_fed}, верность И: {ratio:.0%})" if y_fed > 0 else ""
        print(f"    {char}·и  fed={fed:3d} e={energy:.1f}  {bar}{exclusive}{both}")

    # ════════════════════════════════════════
    # АНАЛИЗ 2: Верность — кто ВСЕГДА перед И?
    # ════════════════════════════════════════

    print(f"\n{'='*60}")
    print("  АНАЛИЗ 2: Верность — $X перед И vs $X перед Ы")
    print("=" * 60)

    all_chars = set(before_i.keys()) | set(before_y.keys())

    print(f"\n  {'Символ':8s} {'$X·и':>6s} {'$X·ы':>6s} {'Верность И':>12s}  Вердикт")
    print(f"  {'─'*8} {'─'*6} {'─'*6} {'─'*12}  {'─'*20}")

    iron_core = []
    periphery = []
    y_only = []

    for char in sorted(all_chars):
        i_fed = before_i.get(char, (0, 0))[0]
        y_fed = before_y.get(char, (0, 0))[0]
        total = i_fed + y_fed
        if total == 0:
            continue
        loyalty = i_fed / total

        if i_fed > 0 and y_fed == 0 and i_fed >= 10:
            verdict = "ЖЕЛЕЗНОЕ ЯДРО"
            iron_core.append(char)
        elif loyalty > 0.7 and i_fed >= 5:
            verdict = "сильное тяготение к И"
            iron_core.append(char)
        elif loyalty > 0.3:
            verdict = "периферия (и+ы)"
            periphery.append(char)
        elif i_fed > 0:
            verdict = "слабая периферия"
            periphery.append(char)
        else:
            verdict = "только перед Ы"
            y_only.append(char)

        bar_i = "█" * max(0, i_fed // 3)
        bar_y = "░" * max(0, y_fed // 3)
        print(f"  {char:8s} {i_fed:6d} {y_fed:6d} {loyalty:11.0%}   {bar_i}{bar_y}  {verdict}")

    print(f"\n  ── Резюме ──")
    print(f"    Железное ядро (всегда/почти всегда перед И): {sorted(iron_core)}")
    print(f"    Периферия (бывает и перед И, и перед Ы):     {sorted(periphery)}")
    print(f"    Только перед Ы (никогда перед И):            {sorted(y_only)}")

    # ════════════════════════════════════════
    # АНАЛИЗ 3: Абстракция $0·и — что в слоте?
    # ════════════════════════════════════════

    print(f"\n{'='*60}")
    print("  АНАЛИЗ 3: Абстракция $0·и — состав слота")
    print("=" * 60)

    for c in world.creatures.values():
        if not c.alive or not c.slot_options or c.complexity != 2:
            continue
        if c.parts[1] == "и" and c.parts[0].startswith("$"):
            sn = c.parts[0]
            opts = c.slot_options.get(sn, set())
            clean = sorted(o for o in opts if not o.startswith("$"))
            print(f"\n  Абстракция: {c.name}  слот={clean}  fed={c.times_fed}")

            # Разделим слот на ядро и периферию
            core = [ch for ch in clean if ch in iron_core]
            peri = [ch for ch in clean if ch in periphery]
            other = [ch for ch in clean if ch not in iron_core and ch not in periphery]
            print(f"    Ядро в слоте:      {core}")
            print(f"    Периферия в слоте: {peri}")
            print(f"    Остальное:         {other}")

    # Аналогично для $0·ы
    print(f"\n  Абстракция $0·ы — для контраста:")
    for c in world.creatures.values():
        if not c.alive or not c.slot_options or c.complexity != 2:
            continue
        if c.parts[1] == "ы" and c.parts[0].startswith("$"):
            sn = c.parts[0]
            opts = c.slot_options.get(sn, set())
            clean = sorted(o for o in opts if not o.startswith("$"))
            print(f"    {c.name}  слот={clean}  fed={c.times_fed}")

    # ════════════════════════════════════════
    # АНАЛИЗ 4: Энергия конкурентов
    # ════════════════════════════════════════

    print(f"\n{'='*60}")
    print("  АНАЛИЗ 4: Энергия пар — ядро vs периферия")
    print("=" * 60)

    print(f"\n  {'Пара':8s} {'fed':>5s} {'energy':>8s}  {'Тип':15s}")
    print(f"  {'─'*8} {'─'*5} {'─'*8}  {'─'*15}")

    pairs_data = []
    for char in sorted(all_chars):
        i_fed, i_energy = before_i.get(char, (0, 0.0))
        y_fed, y_energy = before_y.get(char, (0, 0.0))
        if i_fed > 0:
            typ = "ЯДРО" if char in iron_core else "периферия"
            pairs_data.append((f"{char}·и", i_fed, i_energy, typ))
        if y_fed > 0:
            pairs_data.append((f"{char}·ы", y_fed, y_energy, "ы-форма"))

    pairs_data.sort(key=lambda x: -x[1])
    for name, fed, energy, typ in pairs_data[:25]:
        bar = "█" * max(1, fed // 3)
        print(f"  {name:8s} {fed:5d} {energy:8.1f}  {typ:15s}  {bar}")

    # ════════════════════════════════════════
    # АНАЛИЗ 5: Visiting — ж и ш ближе друг к другу чем к к/р/н?
    # ════════════════════════════════════════

    print(f"\n{'='*60}")
    print("  АНАЛИЗ 5: Ж и Ш ближе друг к другу чем к Р/К/Н?")
    print("=" * 60)

    zh_info = visitor.visit("ж")
    sh_info = visitor.visit("ш")
    r_info = visitor.visit("р")
    k_info = visitor.visit("к")

    zh_mates = zh_info.get("slot_mates", set()) if zh_info["found"] else set()
    sh_mates = sh_info.get("slot_mates", set()) if sh_info["found"] else set()

    print(f"\n  visit('ж') заменяемые: {sorted(zh_mates)[:12]}")
    print(f"  visit('ш') заменяемые: {sorted(sh_mates)[:12]}")

    zh_sh_mutual = "ш" in zh_mates and "ж" in sh_mates
    print(f"\n  Ж↔Ш взаимно заменяемы: {zh_sh_mutual}")

    # Сколько общих заменяемых у ж и ш?
    common_mates = zh_mates & sh_mates
    print(f"  Общие заменяемые у Ж и Ш: {sorted(common_mates)[:10]}")

    # ════════════════════════════════════════
    # ИТОГ
    # ════════════════════════════════════════

    print(f"\n{'='*60}")
    print("╔═══════════════════════════════════════════════════════╗")
    print("║     ИТОГ: ЖЕЛЕЗНОЕ ЯДРО vs ПЕРИФЕРИЯ                 ║")
    print("╠═══════════════════════════════════════════════════════╣")

    checks = []

    # 1. Ж и Ш — железное ядро
    ok1 = "ж" in iron_core and "ш" in iron_core
    checks.append(ok1)
    s1 = "✓" if ok1 else "✗"
    print(f"║  {s1} 1. Ж и Ш в железном ядре перед И               ║")

    # 2. К, Р, Н — периферия (бывают и перед И, и перед Ы)
    ok2 = any(ch in periphery for ch in ["к", "р", "н"])
    checks.append(ok2)
    s2 = "✓" if ok2 else "✗"
    print(f"║  {s2} 2. К/Р/Н — периферия (И и Ы)                   ║")

    # 3. ж·и СИЛЬНЕЕ чем к·и / р·и
    zh_i_fed = before_i.get("ж", (0, 0))[0]
    k_i_fed = before_i.get("к", (0, 0))[0]
    r_i_fed = before_i.get("р", (0, 0))[0]
    ok3 = zh_i_fed > k_i_fed and zh_i_fed > r_i_fed
    checks.append(ok3)
    s3 = "✓" if ok3 else "✗"
    print(f"║  {s3} 3. ж·и ({zh_i_fed}) сильнее к·и ({k_i_fed}) и р·и ({r_i_fed})     ║")

    # 4. Ж и Ш взаимно заменяемы
    checks.append(zh_sh_mutual)
    s4 = "✓" if zh_sh_mutual else "✗"
    print(f"║  {s4} 4. Ж↔Ш взаимно заменяемы                       ║")

    # 5. Б/Д/В/С/Т — только перед Ы (или вообще не перед И)
    y_exclusive = [ch for ch in y_only if ch in "бдвст"]
    ok5 = len(y_exclusive) >= 2
    checks.append(ok5)
    s5 = "✓" if ok5 else "✗"
    print(f"║  {s5} 5. Б/Д/В/С/Т — только перед Ы ({sorted(y_only)[:6]})   ║")

    # 6. Разница энергии ядра vs периферии
    core_avg = 0
    peri_avg = 0
    if iron_core:
        core_fed = [before_i[ch][0] for ch in iron_core if ch in before_i]
        core_avg = sum(core_fed) / max(1, len(core_fed))
    if periphery:
        peri_fed = [before_i.get(ch, (0,))[0] for ch in periphery if ch in before_i]
        peri_avg = sum(peri_fed) / max(1, len(peri_fed))
    ok6 = core_avg > peri_avg * 1.5 if peri_avg > 0 else core_avg > 0
    checks.append(ok6)
    s6 = "✓" if ok6 else "✗"
    print(f"║  {s6} 6. Ядро сильнее периферии ({core_avg:.0f} vs {peri_avg:.0f} fed) ║")

    passed = sum(checks)
    print(f"╠═══════════════════════════════════════════════════════╣")
    print(f"║  Результат: {passed}/6                                     ║")
    print(f"╠═══════════════════════════════════════════════════════╣")

    if passed >= 5:
        print(f"║                                                       ║")
        print(f"║  СИСТЕМА РАЗДЕЛИЛА СЛОТ НА ЯДРО И ПЕРИФЕРИЮ.         ║")
        print(f"║                                                       ║")
        print(f"║  Железное ядро: {{ж, ш}} — ВСЕГДА перед И.            ║")
        print(f"║  Периферия: {{к, р, н, ...}} — иногда И, иногда Ы.   ║")
        print(f"║                                                       ║")
        print(f"║  Энергия решает: ж·и и ш·и в разы сильнее к·и.      ║")
        print(f"║  Правило «жи-ши» выделяется из шума САМО.            ║")
    elif passed >= 3:
        print(f"║                                                       ║")
        print(f"║  ЧАСТИЧНО: разделение видно, но не чёткое.            ║")
    else:
        print(f"║                                                       ║")
        print(f"║  НЕ РАЗДЕЛИЛА. Шум перевешивает.                      ║")

    print(f"║                                                       ║")
    print(f"║  Движок НЕ менялся. 70 слов. Посимвольно.             ║")
    print(f"╚═══════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    main()
