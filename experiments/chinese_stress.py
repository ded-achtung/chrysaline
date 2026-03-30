#!/usr/bin/env python3
"""
Китайский посимвольный стресс-тест: 4 удара.

Система получает ТОЛЬКО отдельные символы. Без пробелов. Без подсказок.
Может ли она найти слова, структуру и отличить настоящее от шума?

Удар 1: Неочевидные двухсимвольные слова (не 爸爸/妈妈)
Удар 2: Длинный поток без пробелов
Удар 3: Ложные склейки — сколько мусора?
Удар 4: Сегмент как кандидат на существо высшего уровня
"""

import time
from chrysaline import World, Visitor


# ════════════════════════════════════════════════════════
# ДАННЫЕ
# ════════════════════════════════════════════════════════

# Удар 1: неочевидные двухсимвольные слова
# Все символы РАЗНЫЕ (не 爸爸, 妈妈)
HARD_WORDS = [
    # Существительные
    list("学生看书"),      # xuéshēng kàn shū — студент читает книгу
    list("学生写字"),      # xuéshēng xiě zì — студент пишет иероглифы
    list("老师教书"),      # lǎoshī jiāo shū — учитель преподаёт
    list("老师说话"),      # lǎoshī shuō huà — учитель говорит
    list("朋友喝茶"),      # péngyou hē chá — друг пьёт чай
    list("朋友吃饭"),      # péngyou chī fàn — друг ест рис
    list("孩子喝水"),      # háizi hē shuǐ — ребёнок пьёт воду
    list("孩子吃饭"),      # háizi chī fàn — ребёнок ест рис
    # Глаголы + прилагательные
    list("学生很聪明"),    # студент очень умный
    list("老师很高兴"),    # учитель очень рад
    list("朋友很开心"),    # друг очень весёлый
    list("孩子很可爱"),    # ребёнок очень милый
    # Ещё контексты для тех же слов
    list("学生学习"),      # студент учится
    list("老师工作"),      # учитель работает
    list("朋友来了"),      # друг пришёл
    list("孩子睡觉"),      # ребёнок спит
]

# Настоящие двухсимвольные слова в данных:
# 学生(студент), 老师(учитель), 朋友(друг), 孩子(ребёнок)
# 看书(читать), 写字(писать), 教书(преподавать), 说话(говорить)
# 喝茶(пить чай), 吃饭(есть рис), 喝水(пить воду)
# 聪明(умный), 高兴(рад), 开心(весёлый), 可爱(милый)
# 学习(учиться), 工作(работать), 睡觉(спать)

REAL_WORDS = {
    "学生", "老师", "朋友", "孩子",
    "看书", "写字", "教书", "说话",
    "喝茶", "吃饭", "喝水",
    "聪明", "高兴", "开心", "可爱",
    "学习", "工作", "睡觉", "来了",
}

# Удар 2: длинный поток — много предложений подряд
LONG_STREAM = [
    list("猫吃鱼"),
    list("狗吃肉"),
    list("猫睡觉"),
    list("狗睡觉"),
    list("鸟吃虫"),        # птица ест червей
    list("鸟会飞"),        # птица умеет летать
    list("鱼会游"),        # рыба умеет плавать
    list("猫喝水"),        # кот пьёт воду
    list("狗喝水"),        # собака пьёт воду
    list("学生看书"),
    list("学生写字"),
    list("老师教书"),
    list("老师说话"),
    list("朋友喝茶"),
    list("朋友吃饭"),
    list("孩子喝水"),
    list("孩子吃饭"),
    list("学生学习"),
    list("老师工作"),
    list("朋友来了"),
    list("孩子睡觉"),
    list("猫吃老鼠"),      # кот ест мышь
    list("狗吃骨头"),      # собака ест кость
    list("鸟吃种子"),      # птица ест семена
    list("鱼吃草"),        # рыба ест траву
    list("妈妈洗碗"),
    list("爸爸读书"),
    list("妈妈做饭"),      # мама готовит еду
    list("爸爸工作"),      # папа работает
    list("孩子很可爱"),
    list("学生很聪明"),
    list("老师很高兴"),
    list("朋友很开心"),
]


# ════════════════════════════════════════════════════════
# УДАР 1: Неочевидные двухсимвольные слова
# ════════════════════════════════════════════════════════

def test_hard_words():
    print("╔═══════════════════════════════════════════════════════╗")
    print("║  УДАР 1: Неочевидные двухсимвольные слова            ║")
    print("║  学生, 老师, 朋友, 孩子 — все символы РАЗНЫЕ         ║")
    print("╚═══════════════════════════════════════════════════════╝")

    world = World()

    for r in range(5):
        for sent in HARD_WORDS:
            world.feed_sentence(sent)
            world.run(1)

    alive = len(world.creatures)
    abst = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"\n  Существ: {alive}, Абстракций: {abst}")

    # Какие пары нашлись?
    print("\n  Найденные пары (сложность=2, без слотов):")
    pairs = []
    for c in world.creatures.values():
        if c.alive and c.complexity == 2 and not c.slot_options:
            pairs.append((c.name, c.energy, c.times_fed))
    pairs.sort(key=lambda x: -x[2])

    real_found = set()
    false_found = set()
    for name, energy, fed in pairs:
        pair_str = name.replace("·", "")
        is_real = pair_str in REAL_WORDS
        marker = "✓" if is_real else "·"
        if is_real:
            real_found.add(pair_str)
        else:
            false_found.add(pair_str)
        if fed >= 3 or is_real:  # показываем все реальные + сильные ложные
            print(f"    {marker} '{name}' fed={fed:3d} e={energy:.1f}"
                  f"  {'← НАСТОЯЩЕЕ СЛОВО' if is_real else ''}")

    print(f"\n  ── Точность ──")
    print(f"    Настоящих слов найдено: {len(real_found)}/{len(REAL_WORDS)}")
    print(f"    Найдены: {sorted(real_found)}")
    not_found = REAL_WORDS - real_found
    if not_found:
        print(f"    НЕ найдены: {sorted(not_found)}")
    print(f"    Ложных пар: {len(false_found)}")

    # Абстракции — нашла ли паттерны?
    print(f"\n  Абстракции:")
    abstractions = sorted(
        [c for c in world.creatures.values() if c.alive and c.slot_options],
        key=lambda c: -c.times_fed
    )[:10]
    for a in abstractions:
        slots = {}
        for sn, opts in a.slot_options.items():
            clean = {o for o in opts if not o.startswith("$")}
            if clean:
                slots[sn] = clean
        if slots:
            slots_str = " ".join(f"{k}={{{','.join(sorted(v))}}}"
                                 for k, v in slots.items())
            print(f"    {a.name}  {slots_str}")

    precision = len(real_found) / max(1, len(real_found) + len(false_found))
    recall = len(real_found) / len(REAL_WORDS)
    print(f"\n  Precision: {precision:.0%} ({len(real_found)}/{len(real_found)+len(false_found)})")
    print(f"  Recall:    {recall:.0%} ({len(real_found)}/{len(REAL_WORDS)})")

    return {
        "real_found": len(real_found),
        "real_total": len(REAL_WORDS),
        "false_found": len(false_found),
        "precision": precision,
        "recall": recall,
    }


# ════════════════════════════════════════════════════════
# УДАР 2: Длинный поток без пробелов
# ════════════════════════════════════════════════════════

def test_long_stream():
    print("\n╔═══════════════════════════════════════════════════════╗")
    print("║  УДАР 2: Длинный поток без пробелов                  ║")
    print("║  33 предложения, 5 раундов, посимвольно              ║")
    print("╚═══════════════════════════════════════════════════════╝")

    world = World()

    t0 = time.time()
    for r in range(5):
        for sent in LONG_STREAM:
            world.feed_sentence(sent)
            world.run(1)
    elapsed = time.time() - t0

    alive = len(world.creatures)
    abst = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"\n  Существ: {alive}, Абстракций: {abst}")
    print(f"  Время: {elapsed:.1f}с")
    print(f"  Статистика: born={world.stats['born']}, died={world.stats['died']}, "
          f"merged={world.stats['merged']}, crossbred={world.stats['crossbred']}")

    ok_not_exploded = alive < 5000
    ok_fast = elapsed < 120
    print(f"\n  ✓ Не взорвалось (<5000): {ok_not_exploded} ({alive})")
    print(f"  ✓ Быстро (<2мин): {ok_fast} ({elapsed:.1f}с)")

    # Самые сильные одиночные символы
    print(f"\n  Топ символов (по энергии):")
    singles = sorted(
        [(c.name, c.energy, c.times_fed)
         for c in world.creatures.values()
         if c.alive and c.complexity == 1],
        key=lambda x: -x[1]
    )
    for name, energy, fed in singles[:15]:
        bar = "█" * max(1, int(energy * 2))
        print(f"    '{name}' e={energy:.1f} fed={fed:3d} {bar}")

    # Самые сильные пары
    print(f"\n  Топ пар (по кормлениям):")
    pairs = sorted(
        [(c.name, c.energy, c.times_fed)
         for c in world.creatures.values()
         if c.alive and c.complexity == 2 and not c.slot_options],
        key=lambda x: -x[2]
    )
    for name, energy, fed in pairs[:15]:
        pair_str = name.replace("·", "")
        is_real = pair_str in REAL_WORDS or pair_str in {
            "猫吃", "狗吃", "鸟吃", "猫喝", "狗喝", "吃鱼", "吃肉",
            "喝水", "睡觉", "老鼠", "骨头", "种子", "做饭", "读书",
            "洗碗", "妈妈", "爸爸",
        }
        marker = "✓" if is_real else "·"
        print(f"    {marker} '{name}' fed={fed:3d} e={energy:.1f}")

    # Абстракции
    print(f"\n  Топ абстракций:")
    abstractions = sorted(
        [c for c in world.creatures.values() if c.alive and c.slot_options],
        key=lambda c: -c.times_fed
    )[:10]
    for a in abstractions:
        slots = {}
        for sn, opts in a.slot_options.items():
            clean = {o for o in opts if not o.startswith("$")}
            if clean:
                slots[sn] = clean
        if slots:
            slots_str = " ".join(f"{k}={{{','.join(sorted(v))}}}"
                                 for k, v in slots.items())
            print(f"    {a.name}  {slots_str}")

    return {
        "creatures": alive,
        "abstractions": abst,
        "elapsed": elapsed,
        "not_exploded": ok_not_exploded,
        "fast": ok_fast,
    }


# ════════════════════════════════════════════════════════
# УДАР 3: Ложные склейки — честный аудит
# ════════════════════════════════════════════════════════

def test_false_bonds():
    print("\n╔═══════════════════════════════════════════════════════╗")
    print("║  УДАР 3: Ложные склейки — честный аудит              ║")
    print("║  Сколько мусора? Сколько случайных пар?              ║")
    print("╚═══════════════════════════════════════════════════════╝")

    world = World()

    for r in range(5):
        for sent in LONG_STREAM:
            world.feed_sentence(sent)
            world.run(1)

    # ВСЕ пары (сложность=2) — и реальные и ложные
    all_pairs = []
    for c in world.creatures.values():
        if c.alive and c.complexity == 2 and not c.slot_options:
            pair_str = c.name.replace("·", "")
            all_pairs.append((pair_str, c.name, c.energy, c.times_fed))
    all_pairs.sort(key=lambda x: -x[3])

    # Расширенный набор "правильных" пар для потока
    REAL_PAIRS = {
        # Настоящие слова
        "学生", "老师", "朋友", "孩子",
        "看书", "写字", "教书", "说话",
        "喝茶", "吃饭", "喝水",
        "聪明", "高兴", "开心", "可爱",
        "学习", "工作", "睡觉", "来了",
        "老鼠", "骨头", "种子", "做饭", "读书", "洗碗",
        "妈妈", "爸爸",
        # Реальные биграммы (субъект+глагол, глагол+объект)
        "猫吃", "狗吃", "鸟吃", "猫喝", "狗喝",
        "吃鱼", "吃肉", "吃草", "会飞", "会游",
    }

    real = []
    false = []
    for pair_str, name, energy, fed in all_pairs:
        if pair_str in REAL_PAIRS:
            real.append((pair_str, name, energy, fed))
        else:
            false.append((pair_str, name, energy, fed))

    print(f"\n  Всего пар: {len(all_pairs)}")
    print(f"  Настоящие: {len(real)}")
    print(f"  Ложные:    {len(false)}")

    if real:
        print(f"\n  ✓ Настоящие пары:")
        for pair_str, name, energy, fed in real[:20]:
            print(f"    '{name}' fed={fed:3d} e={energy:.1f}")

    if false:
        print(f"\n  ✗ Ложные пары (МУСОР):")
        for pair_str, name, energy, fed in false[:20]:
            print(f"    '{name}' fed={fed:3d} e={energy:.1f}")

    # Соотношение сигнал/шум
    precision = len(real) / max(1, len(all_pairs))
    print(f"\n  ── Соотношение сигнал/шум ──")
    print(f"    Precision (пары): {precision:.0%}")

    # Сильные ложные (fed >= 5) — самый опасный мусор
    strong_false = [(p, n, e, f) for p, n, e, f in false if f >= 5]
    strong_real = [(p, n, e, f) for p, n, e, f in real if f >= 5]
    if strong_false or strong_real:
        strong_prec = len(strong_real) / max(1, len(strong_real) + len(strong_false))
        print(f"    Precision (сильные, fed>=5): {strong_prec:.0%} "
              f"({len(strong_real)} настоящих / {len(strong_real)+len(strong_false)} всего)")
        if strong_false:
            print(f"    Сильные ложные: {[n for _, n, _, _ in strong_false[:5]]}")

    # Абстракции — ложные паттерны
    print(f"\n  ── Абстракции: ложные паттерны? ──")
    abstractions = sorted(
        [c for c in world.creatures.values() if c.alive and c.slot_options],
        key=lambda c: -c.times_fed
    )
    useful = 0
    noisy = 0
    for a in abstractions[:15]:
        slots = {}
        for sn, opts in a.slot_options.items():
            clean = {o for o in opts if not o.startswith("$")}
            if clean:
                slots[sn] = clean
        if not slots:
            continue
        # Абстракция полезна если фиксированные части — реальные
        fixed = [p for p in a.parts if not p.startswith("$")]
        has_real_context = len(fixed) > 0
        if has_real_context:
            useful += 1
        else:
            noisy += 1
        slots_str = " ".join(f"{k}={{{','.join(sorted(v))}}}"
                             for k, v in slots.items())
        marker = "~" if not has_real_context else " "
        print(f"    {marker} {a.name}  {slots_str}")

    print(f"\n    С фиксированным контекстом: {useful}")
    print(f"    Только слоты (шум): {noisy}")

    return {
        "total_pairs": len(all_pairs),
        "real_pairs": len(real),
        "false_pairs": len(false),
        "precision": precision,
    }


# ════════════════════════════════════════════════════════
# УДАР 4: Сегмент как кандидат на существо
# ════════════════════════════════════════════════════════

def test_segment_as_entity():
    print("\n╔═══════════════════════════════════════════════════════╗")
    print("║  УДАР 4: Сегмент → существо высшего уровня?          ║")
    print("║  学·生 пара → 学生 слово → подлежащее?               ║")
    print("╚═══════════════════════════════════════════════════════╝")

    world = World()
    visitor = Visitor(world)

    for r in range(5):
        for sent in LONG_STREAM:
            world.feed_sentence(sent)
            world.run(1)

    # Ищем устойчивые пары (fed >= 5, energy >= 1.0)
    strong_pairs = []
    for c in world.creatures.values():
        if c.alive and c.complexity == 2 and not c.slot_options:
            if c.times_fed >= 5 and c.energy >= 1.0:
                strong_pairs.append(c)
    strong_pairs.sort(key=lambda c: -c.times_fed)

    print(f"\n  Устойчивые пары (fed>=5, e>=1.0): {len(strong_pairs)}")
    for c in strong_pairs[:15]:
        pair_str = c.name.replace("·", "")
        print(f"    '{c.name}' fed={c.times_fed} e={c.energy:.1f} "
              f"gen={c.generation} children={len(c.children)}")

    # Какие пары стали ЧАСТЬЮ более сложных организмов?
    print(f"\n  ── Пары → организмы высшего уровня ──")
    promoted = []
    for pair in strong_pairs[:10]:
        # Ищем организмы где обе части пары идут подряд
        p0, p1 = pair.parts
        higher = []
        for c in world.creatures.values():
            if not c.alive or c.complexity < 3:
                continue
            parts = c.parts
            for i in range(len(parts) - 1):
                if parts[i] == p0 and parts[i+1] == p1:
                    higher.append(c)
                    break
        if higher:
            promoted.append((pair, higher))
            print(f"\n    '{pair.name}' → участвует в {len(higher)} организмах:")
            for h in sorted(higher, key=lambda c: -c.times_fed)[:3]:
                slots_info = ""
                if h.slot_options:
                    for sn, opts in h.slot_options.items():
                        clean = {o for o in opts if not o.startswith("$")}
                        if clean:
                            slots_info += f" {sn}={{{','.join(sorted(clean))}}}"
                print(f"      '{h.name}' fed={h.times_fed} gen={h.generation}{slots_info}")

    # Ищем абстракции где пара — фиксированная часть (= стала "словом")
    print(f"\n  ── Пары как фиксированные части абстракций ──")
    pair_as_word = 0
    for pair in strong_pairs[:10]:
        p0, p1 = pair.parts
        for c in world.creatures.values():
            if not c.alive or not c.slot_options:
                continue
            parts = c.parts
            for i in range(len(parts) - 1):
                if parts[i] == p0 and parts[i+1] == p1:
                    # Пара — фиксированная часть абстракции
                    has_slot_elsewhere = any(p.startswith("$") for p in parts
                                            if p != parts[i] and p != parts[i+1])
                    if has_slot_elsewhere:
                        pair_as_word += 1
                        slots_str = ""
                        for sn, opts in c.slot_options.items():
                            clean = sorted(o for o in opts if not o.startswith("$"))
                            slots_str += f" {sn}={{{','.join(clean)}}}"
                        print(f"    '{pair.name}' в '{c.name}'{slots_str}")
                    break

    if pair_as_word == 0:
        print(f"    (пока нет — пары ещё не стабилизировались как слова)")

    # Visiting по устойчивой паре — видит ли система её как единицу?
    print(f"\n  ── Visiting по паре ──")
    test_pairs = ["学", "老", "朋", "孩"]
    for char in test_pairs:
        info = visitor.visit(char)
        if info["found"]:
            sibs = sorted(info["siblings"])[:8]
            mates = sorted(info["slot_mates"])[:5]
            print(f"    visit('{char}'): братья={sibs}")
            if mates:
                print(f"      заменяемые={mates}")

    return {
        "strong_pairs": len(strong_pairs),
        "promoted": len(promoted),
        "pair_as_word": pair_as_word,
    }


# ════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("  КИТАЙСКИЙ ПОСИМВОЛЬНЫЙ СТРЕСС-ТЕСТ")
    print("  4 удара: слова, поток, мусор, сегменты")
    print("  Движок НЕ менялся.")
    print("=" * 60)

    r1 = test_hard_words()
    r2 = test_long_stream()
    r3 = test_false_bonds()
    r4 = test_segment_as_entity()

    # ═══ ИТОГ ═══
    print(f"\n{'='*60}")
    print("╔═══════════════════════════════════════════════════════╗")
    print("║       ИТОГ: 4 УДАРА ПО КИТАЙСКОМУ                    ║")
    print("╠═══════════════════════════════════════════════════════╣")

    s1 = "✓" if r1["recall"] > 0.3 else "~" if r1["recall"] > 0.1 else "✗"
    s2 = "✓" if r2["not_exploded"] and r2["fast"] else "✗"
    s3 = "✓" if r3["precision"] > 0.5 else "~" if r3["precision"] > 0.3 else "✗"
    s4 = "✓" if r4["promoted"] > 3 else "~" if r4["promoted"] > 0 else "✗"

    print(f"║  {s1} 1. Неочевидные слова:                             ║")
    print(f"║     recall={r1['recall']:.0%} ({r1['real_found']}/{r1['real_total']})"
          f" precision={r1['precision']:.0%}             ║")
    print(f"║  {s2} 2. Длинный поток:                                 ║")
    print(f"║     {r2['creatures']} существ, {r2['abstractions']} абстр,"
          f" {r2['elapsed']:.1f}с         ║")
    print(f"║  {s3} 3. Ложные склейки:                                ║")
    print(f"║     precision={r3['precision']:.0%} ({r3['real_pairs']}"
          f" настоящих / {r3['total_pairs']} всего)    ║")
    print(f"║  {s4} 4. Сегмент → существо:                            ║")
    print(f"║     {r4['strong_pairs']} устойчивых пар,"
          f" {r4['promoted']} в организмах        ║")
    print("╠═══════════════════════════════════════════════════════╣")
    print("║                                                       ║")
    print("║  Система НЕ ЗНАЕТ китайского.                        ║")
    print("║  Она видит только символы и их соседство.             ║")
    print("║  Всё что она нашла — из статистики жизни.            ║")
    print("╚═══════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    main()
