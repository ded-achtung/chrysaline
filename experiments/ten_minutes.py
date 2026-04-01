#!/usr/bin/env python3
"""
Эксперимент: 10 минут жизни.

Загружаем ВСЕ знания, потом запускаем систему на 10 минут.
Каждые 30 секунд — снимок: что изменилось? Думает ли система?

Ключевой вопрос: будет ли система обдумывать знания между
подачами данных, или просто стоит?
"""

import time
from chrysaline import World, Visitor, Generator


# ════════════════════════════════════════════════════════
# ВСЕ ЗНАНИЯ
# ════════════════════════════════════════════════════════

ALPHABET = [
    ["а", "это", "гласная", "буква"], ["о", "это", "гласная", "буква"],
    ["у", "это", "гласная", "буква"], ["и", "это", "гласная", "буква"],
    ["е", "это", "гласная", "буква"], ["ы", "это", "гласная", "буква"],
    ["к", "это", "согласная", "буква"], ["т", "это", "согласная", "буква"],
    ["м", "это", "согласная", "буква"], ["н", "это", "согласная", "буква"],
    ["р", "это", "согласная", "буква"], ["с", "это", "согласная", "буква"],
    ["л", "это", "согласная", "буква"], ["д", "это", "согласная", "буква"],
    ["б", "это", "согласная", "буква"], ["п", "это", "согласная", "буква"],
]

RULES = [
    ["жи", "пишется", "с", "буквой", "и"],
    ["ши", "пишется", "с", "буквой", "и"],
    ["ча", "пишется", "с", "буквой", "а"],
    ["ща", "пишется", "с", "буквой", "а"],
    ["чу", "пишется", "с", "буквой", "у"],
    ["щу", "пишется", "с", "буквой", "у"],
    ["существительное", "обозначает", "предмет"],
    ["глагол", "обозначает", "действие"],
    ["прилагательное", "обозначает", "признак"],
    ["предложение", "выражает", "мысль"],
    ["города", "пишутся", "с", "большой", "буквы"],
]

NATURE = [
    ["кот", "это", "предмет"], ["собака", "это", "предмет"],
    ["корова", "это", "предмет"], ["мама", "это", "предмет"],
    ["стол", "это", "предмет"],
    ["бегать", "это", "действие"], ["читать", "это", "действие"],
    ["прыгать", "это", "действие"],
    ["красный", "это", "признак"], ["большой", "это", "признак"],
    ["кот", "это", "млекопитающее"], ["собака", "это", "млекопитающее"],
    ["корова", "это", "млекопитающее"],
    ["ворона", "это", "птица"], ["воробей", "это", "птица"],
    ["птицы", "умеют", "летать"],
    ["страус", "это", "птица"], ["страус", "не", "летает"],
    ["кот", "живёт", "в", "доме"], ["собака", "живёт", "в", "доме"],
    ["корова", "живёт", "на", "ферме"],
    ["кот", "ест", "рыбу"], ["кот", "ест", "мясо"],
    ["собака", "ест", "мясо"], ["корова", "ест", "траву"],
    ["корова", "даёт", "молоко"],
    ["рыба", "живёт", "в", "воде"],
    ["москва", "это", "город"],
]

MATH = [
    ["два", "плюс", "три", "равно", "пять"],
    ["три", "плюс", "два", "равно", "пять"],
    ["один", "плюс", "один", "равно", "два"],
    ["пять", "минус", "два", "равно", "три"],
]

BRIDGES = [
    [".", "это", "точка"], [".", "означает", "конец", "предложения"],
    [" ", "это", "пробел"], [" ", "разделяет", "слова"],
    ["пробел", "разделяет", "слова"],
    ["после", "точки", "слово", "с", "большой", "буквы"],
    ["большая", "буква", "в", "начале", "предложения"],
]

TEXTS = [
    "Кот живёт в доме. Собака живёт в доме. Корова живёт на ферме.",
    "Кот ест рыбу. Собака ест мясо. Корова ест траву.",
    "Мама мыла раму. Папа читал книгу. Бабушка варила кашу.",
    "Жили-были дед да баба. И была у них курочка Ряба. Снесла курочка яичко.",
]


def main():
    print("=" * 60)
    print("  10 МИНУТ ЖИЗНИ")
    print("  Загружаем знания → запускаем → наблюдаем")
    print("=" * 60)

    world = World()
    visitor = Visitor(world)
    gen = Generator(world)
    world.learn_negation("не")

    # ════════════════════════════════════════
    # ЗАГРУЗКА ЗНАНИЙ
    # ════════════════════════════════════════
    print(f"\n  Загружаем знания...")
    all_data = ALPHABET + RULES + NATURE + MATH + BRIDGES
    for r in range(3):
        for p in all_data:
            world.feed_sentence(p)
            world.run(1)

    # Тексты через read()
    for text in TEXTS:
        for _ in range(2):
            world.read(text)

    alive0 = sum(1 for c in world.creatures.values() if c.alive)
    abst0 = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    stats0 = dict(world.stats)

    print(f"  Загружено: {alive0} существ, {abst0} абстракций")
    print(f"  Выводов при чтении: born={stats0['born']}, crossbred={stats0['crossbred']}")

    # Базовые вопросы ДО жизни
    print(f"\n  ── ВОПРОСЫ ДО ЖИЗНИ ──")
    questions = [
        "какая часть речи кот?",
        "что ест корова?",
        "где живёт кот?",
        "кто это млекопитающее?",
        "два плюс три?",
    ]
    answers_before = {}
    for q in questions:
        res = gen.ask(q)
        answers_before[q] = res["answers"][:5]
        print(f"    {q} → {res['answers'][:5]}")

    # Сколько знает кот?
    kot_before = visitor.visit("кот")
    kot_sibs_before = len(kot_before["siblings"]) if kot_before["found"] else 0

    # ════════════════════════════════════════
    # 10 МИНУТ ЖИЗНИ
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ЗАПУСК: 10 МИНУТ ЖИЗНИ")
    print("  Снимок каждые 30 секунд")
    print("=" * 60)

    duration = 600  # 10 минут
    snapshot_interval = 30  # каждые 30 сек
    ticks_per_second = 1  # 1 тик = 1 секунда реального времени

    start_time = time.time()
    last_snapshot = start_time
    last_tick = start_time
    snapshot_num = 0
    total_ticks = 0

    snapshots = []

    while True:
        elapsed = time.time() - start_time
        if elapsed >= duration:
            break

        # 1 тик в секунду
        now = time.time()
        if now - last_tick >= 1.0 / ticks_per_second:
            world.run(1)
            total_ticks += 1
            last_tick = now

        # Снимок каждые 30 сек
        now = time.time()
        if now - last_snapshot >= snapshot_interval:
            snapshot_num += 1
            last_snapshot = now

            alive = sum(1 for c in world.creatures.values() if c.alive)
            abst = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
            stats = dict(world.stats)

            new_born = stats["born"] - stats0["born"]
            new_died = stats["died"] - stats0["died"]
            new_fed = stats["fed"] - stats0["fed"]
            new_crossbred = stats["crossbred"] - stats0["crossbred"]

            snap = {
                "num": snapshot_num,
                "elapsed": int(elapsed),
                "ticks": total_ticks,
                "alive": alive,
                "abst": abst,
                "born": new_born,
                "died": new_died,
                "fed": new_fed,
                "crossbred": new_crossbred,
            }
            snapshots.append(snap)

            minutes = int(elapsed) // 60
            seconds = int(elapsed) % 60
            print(f"  [{minutes:02d}:{seconds:02d}] тиков={total_ticks:5d} "
                  f"живых={alive:4d} абстр={abst:3d} "
                  f"рожд={new_born:3d} умерло={new_died:4d} "
                  f"корм={new_fed:5d} скрещ={new_crossbred:3d}")

    # ════════════════════════════════════════
    # ПОСЛЕ ЖИЗНИ
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print(f"  ПОСЛЕ {duration//60} МИНУТ ЖИЗНИ")
    print("=" * 60)

    elapsed_total = time.time() - start_time
    alive_final = sum(1 for c in world.creatures.values() if c.alive)
    abst_final = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    stats_final = dict(world.stats)

    print(f"\n  Время: {int(elapsed_total)} сек, тиков: {total_ticks}")
    print(f"  Живых: {alive0} → {alive_final}")
    print(f"  Абстракций: {abst0} → {abst_final}")
    print(f"  Родилось: {stats_final['born'] - stats0['born']}")
    print(f"  Умерло: {stats_final['died'] - stats0['died']}")
    print(f"  Подкормлено: {stats_final['fed'] - stats0['fed']}")
    print(f"  Скрещено: {stats_final['crossbred'] - stats0['crossbred']}")

    # Вопросы ПОСЛЕ жизни
    print(f"\n  ── ВОПРОСЫ ПОСЛЕ ЖИЗНИ ──")
    answers_after = {}
    for q in questions:
        res = gen.ask(q)
        answers_after[q] = res["answers"][:5]
        before = answers_before[q]
        changed = answers_after[q] != before
        marker = " ← ИЗМЕНИЛСЯ!" if changed else ""
        print(f"    {q} → {res['answers'][:5]}{marker}")

    # Кот — что знает после?
    kot_after = visitor.visit("кот")
    kot_sibs_after = len(kot_after["siblings"]) if kot_after["found"] else 0
    print(f"\n  visit('кот') братьев: {kot_sibs_before} → {kot_sibs_after}")
    if kot_after["found"]:
        print(f"    братья: {sorted(kot_after['siblings'])[:15]}")

    # Что выжило? Самые сильные
    print(f"\n  ── ВЫЖИВШИЕ (топ-15 по энергии) ──")
    survivors = sorted(
        [c for c in world.creatures.values() if c.alive and c.complexity == 1],
        key=lambda c: -c.energy
    )
    for c in survivors[:15]:
        print(f"    {c.parts[0]:25s} e={c.energy:.1f} fed={c.times_fed}")

    # Что умерло?
    print(f"\n  ── ДИНАМИКА ──")
    if snapshots:
        first = snapshots[0]
        last = snapshots[-1]
        print(f"    Начало: {first['alive']} живых, {first['abst']} абстр")
        print(f"    Конец:  {last['alive']} живых, {last['abst']} абстр")
        print(f"    Подкормок за жизнь: {last['fed']}")
        print(f"    Рождений за жизнь: {last['born']}")

        if last["born"] > 0:
            print(f"\n    СИСТЕМА ДУМАЛА! Родились новые существа.")
        elif last["fed"] > 0:
            print(f"\n    СИСТЕМА ЖИЛА. Подкармливала существующих, но не создавала новых.")
        else:
            print(f"\n    СИСТЕМА СТОЯЛА. Ничего не происходило.")

    # ════════════════════════════════════════
    # ИТОГ
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("╔═══════════════════════════════════════════════════════╗")
    print("║     ИТОГ: 10 МИНУТ ЖИЗНИ                              ║")
    print("╠═══════════════════════════════════════════════════════╣")

    total_born = stats_final["born"] - stats0["born"]
    total_fed = stats_final["fed"] - stats0["fed"]
    total_died = stats_final["died"] - stats0["died"]

    answers_changed = sum(1 for q in questions
                          if answers_after[q] != answers_before[q])
    answers_same = len(questions) - answers_changed

    print(f"║  Тиков: {total_ticks:6d}                                   ║")
    print(f"║  Родилось: {total_born:4d}                                   ║")
    print(f"║  Умерло: {total_died:5d}                                   ║")
    print(f"║  Подкормлено: {total_fed:6d}                                ║")
    print(f"║  Живых: {alive0} → {alive_final}                               ║")
    print(f"║  Ответы: {answers_same}/{len(questions)} стабильны, {answers_changed}/{len(questions)} изменились      ║")

    if total_born > 10:
        print(f"║                                                       ║")
        print(f"║  СИСТЕМА ДУМАЛА.                                     ║")
        print(f"║  Создала {total_born} новых существ за {duration//60} минут.            ║")
    elif total_fed > 100:
        print(f"║                                                       ║")
        print(f"║  СИСТЕМА ЖИЛА.                                       ║")
        print(f"║  Поддерживала связи ({total_fed} подкормок).                ║")
    else:
        print(f"║                                                       ║")
        print(f"║  СИСТЕМА СТОЯЛА.                                     ║")
        print(f"║  Мало активности без новых данных.                    ║")

    print(f"╚═══════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    main()
