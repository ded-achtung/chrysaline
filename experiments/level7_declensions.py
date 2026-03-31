#!/usr/bin/env python3
"""
Уровень 7: Склонения и числа существительных.

Настоящий текст учебника через read(). После обучения уровней 1-2.
Проверяем: что система извлечёт из текста о числах и склонениях.

Движок НЕ менялся.
"""

from chrysaline import World, Visitor, Generator


# ════════════════════════════════════════════════════════
# read() — патч
# ════════════════════════════════════════════════════════

def read(self, text):
    visitor = Visitor(self)
    knows_space = False
    si = visitor.visit(" ")
    if si["found"]:
        s = si["siblings"]
        if "пробел" in s or "разделяет" in s or "слова" in s:
            knows_space = True
    knows_dot = False
    di = visitor.visit(".")
    if di["found"]:
        d = di["siblings"]
        if "точка" in d or "конец" in d or "предложения" in d:
            knows_dot = True
    if knows_space:
        raw = [t for t in text.split(" ") if t]
        if knows_dot:
            tokens = []
            for t in raw:
                if t.endswith(".") and len(t) > 1:
                    tokens.append(t[:-1]); tokens.append(".")
                elif t == ".": tokens.append(".")
                else: tokens.append(t)
            sents, cur = [], []
            for t in tokens:
                if t == ".":
                    if cur: cur.append("."); sents.append(cur); cur = []
                else: cur.append(t)
            if cur: sents.append(cur)
            for s in sents: self.feed_sentence(s); self.run(1)
        else: self.feed_sentence(raw); self.run(1)
    else: self.feed_sentence(list(text)); self.run(1)

World.read = read


# ════════════════════════════════════════════════════════
# ОБУЧЕНИЕ (уровни 1-2)
# ════════════════════════════════════════════════════════

LEVEL1 = [
    ["а", "это", "гласная", "буква"], ["о", "это", "гласная", "буква"],
    ["у", "это", "гласная", "буква"], ["и", "это", "гласная", "буква"],
    ["е", "это", "гласная", "буква"], ["ы", "это", "гласная", "буква"],
    ["к", "это", "согласная", "буква"], ["т", "это", "согласная", "буква"],
    ["м", "это", "согласная", "буква"], ["н", "это", "согласная", "буква"],
    ["р", "это", "согласная", "буква"], ["с", "это", "согласная", "буква"],
    ["л", "это", "согласная", "буква"], ["д", "это", "согласная", "буква"],
    ["б", "это", "согласная", "буква"], ["п", "это", "согласная", "буква"],
]

LEVEL2 = [
    ["слова", "складываются", "в", "предложения"],
    ["предложение", "выражает", "мысль"],
    ["в", "конце", "предложения", "ставится", "точка"],
    ["точка", "разделяет", "предложения"],
    ["пробел", "разделяет", "слова"],
]

BRIDGES = [
    [".", "это", "точка"], [".", "означает", "конец", "предложения"],
    [" ", "это", "пробел"], [" ", "разделяет", "слова"],
]

# ════════════════════════════════════════════════════════
# ТЕКСТ УЧЕБНИКА
# ════════════════════════════════════════════════════════

TEXTBOOK = """Имя существительное это часть речи которая обозначает предмет и изменяется по падежам и числам. Число имен существительных это непостоянный грамматический признак существительного. Существительные могут изменяться по числам. Единственное число используют для обозначения одного предмета. Например ложка стол машина. Множественное число используют для обозначения нескольких предметов. Например вилки стулья велосипеды. Существительные изменяются по числам подушка подушки сестра сёстры груша груши. Существительные употребляются только в единственном числе мука любовь снег. Существительные употребляются только во множественном числе обои бусы весы. Форма множественного числа образуется с помощью окончаний. Первое склонение относятся существительные мужского и женского рода с окончанием а или я. Например мужчина баня дорога страна машина. Второе склонение объединяет существительные мужского рода с нулевым окончанием и среднего рода с окончанием о или е. Например гений автор герой слово дело море. Третье склонение относятся существительные женского рода с нулевым окончанием. Например быль радость сирень лазурь роскошь. Разносклоняемые существительные бремя вымя темя пламя стремя время знамя имя племя семя путь дитя. Несклоняемые существительные авеню бюро депо жалюзи желе кафе кенгуру кино метро пальто такси."""


def teach(world, data, label, repeats=3):
    print(f"\n  ── {label} ({len(data)} фраз, {repeats}x) ──")
    for r in range(repeats):
        for phrase in data:
            world.feed_sentence(phrase)
            world.run(1)
    alive = sum(1 for c in world.creatures.values() if c.alive)
    abst = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"    → {alive} существ, {abst} абстракций")


def main():
    print("=" * 60)
    print("  УРОВЕНЬ 7: ЧИСЛА И СКЛОНЕНИЯ СУЩЕСТВИТЕЛЬНЫХ")
    print("  Настоящий учебник через read().")
    print("=" * 60)

    world = World()
    visitor = Visitor(world)
    gen = Generator(world)

    # Обучение
    print(f"\n{'='*60}")
    print("  ОБУЧЕНИЕ")
    print("=" * 60)
    teach(world, LEVEL1, "Буквы")
    teach(world, LEVEL2, "Пунктуация")
    teach(world, BRIDGES, "Мосты", repeats=5)

    alive0 = sum(1 for c in world.creatures.values() if c.alive)
    abst0 = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"\n  После обучения: {alive0} существ, {abst0} абстракций")

    # ════════════════════════════════════════
    # ЧИТАЕМ УЧЕБНИК
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ЧИТАЕМ УЧЕБНИК")
    print("=" * 60)

    print(f"  Текст: {len(TEXTBOOK)} символов")
    absorbed_before = world.stats["absorbed"]
    world.read(TEXTBOOK)

    alive1 = sum(1 for c in world.creatures.values() if c.alive)
    abst1 = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    absorbed = world.stats["absorbed"] - absorbed_before
    print(f"  После: {alive1} существ, {abst1} абстракций, {absorbed} поглощений")

    # ════════════════════════════════════════
    # ПРОВЕРКА
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ПРОВЕРКА: ЧТО СИСТЕМА ПОНЯЛА")
    print("=" * 60)

    checks = []

    # 1. Существительное — часть речи
    print(f"\n  ── 1. Что такое существительное? ──")
    sush_info = visitor.visit("существительное")
    if sush_info["found"]:
        sibs = sorted(sush_info["siblings"])[:15]
        print(f"    братья: {sibs}")
        knows_part = "часть" in sush_info["siblings"] or "речи" in sush_info["siblings"]
        knows_predmet = "предмет" in sush_info["siblings"] or "обозначает" in sush_info["siblings"]
    else:
        knows_part = False
        knows_predmet = False
    ok1 = knows_part or knows_predmet
    checks.append(("существительное → часть речи/предмет", ok1))
    print(f"    знает 'часть'/'речи': {knows_part}")
    print(f"    знает 'предмет'/'обозначает': {knows_predmet}")

    # 2. Единственное и множественное число
    print(f"\n  ── 2. Единственное и множественное число ──")
    ed_info = visitor.visit("единственное")
    mn_info = visitor.visit("множественное")
    ed_sibs = ed_info["siblings"] if ed_info["found"] else set()
    mn_sibs = mn_info["siblings"] if mn_info["found"] else set()
    print(f"    'единственное' братья: {sorted(ed_sibs)[:10]}")
    print(f"    'множественное' братья: {sorted(mn_sibs)[:10]}")
    ok2 = "число" in ed_sibs and "число" in mn_sibs
    checks.append(("единственное/множественное → число", ok2))

    # 3. Склонения
    print(f"\n  ── 3. Склонения ──")
    for skl in ["первое", "второе", "третье"]:
        info = visitor.visit(skl)
        if info["found"]:
            sibs = sorted(info["siblings"])[:10]
            print(f"    '{skl}' братья: {sibs}")

    skl1 = visitor.visit("первое")
    ok3 = skl1["found"] and "склонение" in skl1["siblings"]
    checks.append(("первое → склонение", ok3))

    # 4. ask() — что обозначает существительное
    print(f"\n  ── 4. ask() ──")
    r4 = gen.ask("что обозначает существительное?")
    ok4 = "предмет" in r4["answers"]
    print(f"    что обозначает сущ.? → {r4['answers'][:6]}  {'OK' if ok4 else 'MISS'}")
    checks.append(("ask: обозначает сущ. → предмет", ok4))

    # 5. Знает ли примеры единственного числа
    print(f"\n  ── 5. Примеры ──")
    lozhka = visitor.visit("ложка")
    ok5 = lozhka["found"]
    if lozhka["found"]:
        print(f"    'ложка' братья: {sorted(lozhka['siblings'])[:10]}")
    checks.append(("'ложка' известна системе", ok5))

    # 6. Несклоняемые
    print(f"\n  ── 6. Несклоняемые ──")
    metro = visitor.visit("метро")
    palto = visitor.visit("пальто")
    ok6 = metro["found"] or palto["found"]
    if metro["found"]:
        print(f"    'метро' братья: {sorted(metro['siblings'])[:10]}")
    if palto["found"]:
        print(f"    'пальто' братья: {sorted(palto['siblings'])[:10]}")
    checks.append(("несклоняемые: метро/пальто известны", ok6))

    # 7. Абстракции из учебника
    print(f"\n  ── 7. Абстракции ──")
    content_words = {"существительные", "существительное", "число", "склонение",
                     "единственное", "множественное", "род", "окончанием",
                     "предмет", "обозначает", "изменяется", "падежам", "числам"}
    count = 0
    for c in world.show_abstractions():
        if not (set(c.parts) & content_words):
            continue
        slots = {}
        for sn, opts in c.slot_options.items():
            clean = sorted(o for o in opts if not o.startswith("$"))
            if clean:
                slots[sn] = clean[:10]
        if slots:
            print(f"    {c.name:55s} {slots}  fed={c.times_fed}")
            count += 1
            if count >= 15:
                break

    ok7 = count >= 3
    checks.append((">=3 содержательных абстракций", ok7))

    # 8. Абстракции со склонениями
    print(f"\n  ── 8. Абстракции со 'склонение' ──")
    for c in world.creatures.values():
        if not c.alive or not c.slot_options:
            continue
        if "склонение" in c.parts:
            slots = {}
            for sn, opts in c.slot_options.items():
                clean = sorted(o for o in opts if not o.startswith("$"))
                if clean:
                    slots[sn] = clean
            if slots:
                print(f"    {c.name}  {slots}  fed={c.times_fed}")

    # 9. Абстракции с 'число'
    print(f"\n  ── 9. Абстракции с 'число' ──")
    for c in world.creatures.values():
        if not c.alive or not c.slot_options:
            continue
        if "число" in c.parts or "числе" in c.parts:
            slots = {}
            for sn, opts in c.slot_options.items():
                clean = sorted(o for o in opts if not o.startswith("$"))
                if clean:
                    slots[sn] = clean
            if slots:
                print(f"    {c.name}  {slots}  fed={c.times_fed}")

    # 10. ask — какие бывают склонения
    print(f"\n  ── 10. ask() ──")
    r10 = gen.ask("какие бывают склонения?")
    ok10 = any(w in r10["answers"] for w in ["первое", "второе", "третье"])
    print(f"    какие склонения? → {r10['answers'][:8]}  {'OK' if ok10 else 'MISS'}")
    checks.append(("ask: какие склонения → первое/второе/третье", ok10))

    # ════════════════════════════════════════
    # СТАТИСТИКА
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  СТАТИСТИКА")
    print("=" * 60)
    alive_f = sum(1 for c in world.creatures.values() if c.alive)
    abst_f = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"  Существ: {alive_f}")
    print(f"  Абстракций: {abst_f}")
    print(f"  Статистика: {world.stats}")

    # ════════════════════════════════════════
    # ИТОГ
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("╔═══════════════════════════════════════════════════════╗")
    print("║     ИТОГ: УРОВЕНЬ 7 — ЧИСЛА И СКЛОНЕНИЯ              ║")
    print("╠═══════════════════════════════════════════════════════╣")

    passed = 0
    for name, ok in checks:
        s = "+" if ok else "-"
        if ok:
            passed += 1
        print(f"║  {s} {name:52s}║")

    print(f"╠═══════════════════════════════════════════════════════╣")
    print(f"║  Результат: {passed}/{len(checks)}                                     ║")

    if passed >= 6:
        print(f"║  УЧЕБНИК УСВОЕН.                                     ║")
    elif passed >= 4:
        print(f"║  ЧАСТИЧНО.                                           ║")
    else:
        print(f"║  НУЖНА ДОРАБОТКА.                                    ║")

    print(f"║  Движок НЕ менялся.                                   ║")
    print(f"╚═══════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    main()
