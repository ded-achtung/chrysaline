#!/usr/bin/env python3
"""
Тест: живые существа с потребностями.

После read() запускаем run(100) — существа живут,
думают, укрепляют связи. Потом проверяем: стало ли лучше.
"""

from chrysaline import World, Visitor, Generator


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


LEVEL1 = [
    ["а", "это", "гласная", "буква"], ["о", "это", "гласная", "буква"],
    ["у", "это", "гласная", "буква"], ["и", "это", "гласная", "буква"],
    ["к", "это", "согласная", "буква"], ["т", "это", "согласная", "буква"],
    ["м", "это", "согласная", "буква"], ["р", "это", "согласная", "буква"],
    ["с", "это", "согласная", "буква"],
]

BRIDGES = [
    [".", "это", "точка"], [" ", "это", "пробел"],
    [" ", "разделяет", "слова"],
    [".", "означает", "конец", "предложения"],
    ["пробел", "разделяет", "слова"],
    ["Кот", "и", "кот", "это", "одно", "слово"],
    ["Собака", "и", "собака", "это", "одно", "слово"],
    ["Корова", "и", "корова", "это", "одно", "слово"],
]

TEXT = "Кот это предмет. Собака это предмет. Корова это предмет. Существительное обозначает предмет. Глагол обозначает действие. Бегать это действие. Читать это действие. Красный это признак. Прилагательное обозначает признак. Кот живёт в доме. Собака живёт в доме. Корова живёт на ферме. Кот ест рыбу. Собака ест мясо. Корова ест траву."


def teach(world, data, label, repeats=3):
    for r in range(repeats):
        for phrase in data:
            world.feed_sentence(phrase)
            world.run(1)


def main():
    print("=" * 60)
    print("  ТЕСТ: ЖИВЫЕ СУЩЕСТВА С ПОТРЕБНОСТЯМИ")
    print("  read() → run(100) → проверка")
    print("=" * 60)

    world = World()
    visitor = Visitor(world)
    gen = Generator(world)

    # Обучение
    teach(world, LEVEL1, "Буквы")
    teach(world, BRIDGES, "Мосты", repeats=5)
    for _ in range(3):
        world.read(TEXT)

    alive0 = sum(1 for c in world.creatures.values() if c.alive)
    abst0 = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"\n  После read(): {alive0} существ, {abst0} абстракций")

    # Замеряем ДО жизни
    print(f"\n{'='*60}")
    print("  ДО run(100)")
    print("=" * 60)

    questions_before = {}
    test_questions = [
        ("какая часть речи кот?", ["существительное", "Существительное"]),
        ("какая часть речи бегать?", ["глагол", "Глагол"]),
        ("где живёт кот?", ["доме", "в"]),
        ("что ест корова?", ["траву"]),
    ]

    for q, expected in test_questions:
        res = gen.ask(q)
        hit = any(e in res["answers"] for e in expected)
        questions_before[q] = (res["answers"][:6], hit)
        print(f"  {'OK' if hit else 'MISS'} {q} → {res['answers'][:6]}")

    # Проверяем: кот знает существительное?
    kot_before = visitor.visit("кот")
    kot_knows_sush_before = "существительное" in (kot_before["siblings"] if kot_before["found"] else set()) or \
                             "Существительное" in (kot_before["siblings"] if kot_before["found"] else set())
    print(f"\n  кот знает существительное: {kot_knows_sush_before}")

    beg_before = visitor.visit("бегать")
    beg_knows_before = "глагол" in (beg_before["siblings"] if beg_before["found"] else set()) or \
                        "Глагол" in (beg_before["siblings"] if beg_before["found"] else set())
    print(f"  бегать знает глагол: {beg_knows_before}")

    # ════════════════════════════════════════
    # ЖИЗНЬ: 100 тиков
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  run(100) — СУЩЕСТВА ЖИВУТ")
    print("=" * 60)

    stats_before = dict(world.stats)
    world.run(100)
    stats_after = dict(world.stats)

    alive1 = sum(1 for c in world.creatures.values() if c.alive)
    abst1 = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    died = stats_after["died"] - stats_before["died"]
    fed = stats_after["fed"] - stats_before["fed"]
    born = stats_after["born"] - stats_before["born"]

    print(f"  После run(100): {alive1} существ, {abst1} абстракций")
    print(f"  Умерло: {died}, подкормлено: {fed}, родилось: {born}")

    # ════════════════════════════════════════
    # ПОСЛЕ жизни
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ПОСЛЕ run(100)")
    print("=" * 60)

    checks = []

    questions_after = {}
    for q, expected in test_questions:
        res = gen.ask(q)
        hit = any(e in res["answers"] for e in expected)
        questions_after[q] = (res["answers"][:6], hit)
        before_hit = questions_before[q][1]
        change = ""
        if hit and not before_hit:
            change = " ← УЛУЧШЕНИЕ!"
        elif not hit and before_hit:
            change = " ← РЕГРЕССИЯ!"
        print(f"  {'OK' if hit else 'MISS'} {q} → {res['answers'][:6]}{change}")
        checks.append((f"ask: {q[:30]}", hit))

    # кот знает существительное?
    kot_after = visitor.visit("кот")
    kot_knows_sush_after = "существительное" in (kot_after["siblings"] if kot_after["found"] else set()) or \
                            "Существительное" in (kot_after["siblings"] if kot_after["found"] else set())
    print(f"\n  кот знает существительное: {kot_knows_sush_after}")
    if kot_knows_sush_after and not kot_knows_sush_before:
        print(f"    ← ВЫВОД ОТ ЖИЗНИ!")
    checks.append(("кот → существительное (после жизни)", kot_knows_sush_after))

    beg_after = visitor.visit("бегать")
    beg_knows_after = "глагол" in (beg_after["siblings"] if beg_after["found"] else set()) or \
                       "Глагол" in (beg_after["siblings"] if beg_after["found"] else set())
    print(f"  бегать знает глагол: {beg_knows_after}")
    if beg_knows_after and not beg_knows_before:
        print(f"    ← ВЫВОД ОТ ЖИЗНИ!")
    checks.append(("бегать → глагол (после жизни)", beg_knows_after))

    # Правда выжила?
    for parts_check, label in [
        (("кот", "это", "предмет"), "кот·это·предмет"),
        (("существительное", "обозначает", "предмет"), "сущ·обозначает·предмет"),
    ]:
        cr = world._find_by_parts(parts_check)
        alive_check = cr.alive if cr else False
        energy = cr.energy if cr and cr.alive else 0
        print(f"  {label}: alive={alive_check} e={energy:.1f}")
        checks.append((f"{label} выжил", alive_check))

    # Не стало хуже?
    before_score = sum(1 for _, (_, h) in questions_before.items() if h)
    after_score = sum(1 for _, (_, h) in questions_after.items() if h)
    no_regression = after_score >= before_score
    checks.append(("ask() не стал хуже", no_regression))
    print(f"\n  ask() до: {before_score}/{len(test_questions)}, после: {after_score}/{len(test_questions)}")

    # ════════════════════════════════════════
    # ИТОГ
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("╔═══════════════════════════════════════════════════════╗")
    print("║     ИТОГ: ЖИВЫЕ СУЩЕСТВА                              ║")
    print("╠═══════════════════════════════════════════════════════╣")

    passed = 0
    for name, ok in checks:
        s = "+" if ok else "-"
        if ok:
            passed += 1
        print(f"║  {s} {name:52s}║")

    print(f"╠═══════════════════════════════════════════════════════╣")
    print(f"║  Результат: {passed}/{len(checks)}                                     ║")
    print(f"║  Умерло: {died}, подкормлено: {fed}, родилось: {born}              ║")

    if passed >= 7:
        print(f"║  ЖИВЫЕ СУЩЕСТВА РАБОТАЮТ.                            ║")
    elif passed >= 5:
        print(f"║  ЧАСТИЧНО. Существа живут, но не все выводы.         ║")
    else:
        print(f"║  НУЖНА ДОРАБОТКА.                                    ║")

    print(f"╚═══════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    main()
