#!/usr/bin/env python3
"""
Два эксперимента: волна активации vs мышление при чтении.

Эксперимент 1: Волна активации (activation spreading)
  - Числовое поле activation у каждого существа
  - Распространение через братьев с decay
  - Проверка: поднимутся ли нужные существа?

Эксперимент 2: Живое взаимодействие (feeding wave)
  - Существа просто кормятся при активации
  - Не числовой activation, а энергия
  - Та же парадигма что в Chrysaline

Оба проверяются на одних и тех же тестах.
"""

from chrysaline import World, Visitor, Generator
import copy


# ════════════════════════════════════════════════════════
# ОБЩЕЕ ОБУЧЕНИЕ
# ════════════════════════════════════════════════════════

LEVEL1 = [
    ["а", "это", "гласная", "буква"], ["о", "это", "гласная", "буква"],
    ["у", "это", "гласная", "буква"], ["и", "это", "гласная", "буква"],
    ["к", "это", "согласная", "буква"], ["т", "это", "согласная", "буква"],
    ["м", "это", "согласная", "буква"], ["р", "это", "согласная", "буква"],
    ["с", "это", "согласная", "буква"],
]

RULES = [
    ["существительное", "обозначает", "предмет"],
    ["глагол", "обозначает", "действие"],
    ["прилагательное", "обозначает", "признак"],
    ["кот", "это", "предмет"], ["собака", "это", "предмет"],
    ["корова", "это", "предмет"],
    ["бегать", "это", "действие"], ["читать", "это", "действие"],
    ["красный", "это", "признак"], ["большой", "это", "признак"],
    ["кот", "это", "млекопитающее"], ["собака", "это", "млекопитающее"],
    ["кот", "ест", "рыбу"], ["кот", "ест", "мясо"],
    ["собака", "ест", "мясо"], ["корова", "ест", "траву"],
    ["кот", "живёт", "в", "доме"],
    ["страус", "это", "птица"],
    ["ворона", "это", "птица"],
    ["птицы", "умеют", "летать"],
    ["страус", "не", "летает"],
    ["жи", "пишется", "с", "буквой", "и"],
    ["ши", "пишется", "с", "буквой", "и"],
]

BRIDGES = [
    [".", "это", "точка"], [" ", "это", "пробел"],
    [" ", "разделяет", "слова"],
    [".", "означает", "конец", "предложения"],
    ["после", "точки", "слово", "с", "большой", "буквы"],
]


def build_world():
    """Построить обученный мир."""
    world = World()
    for r in range(3):
        for p in LEVEL1:
            world.feed_sentence(p); world.run(1)
    for r in range(5):
        for p in BRIDGES:
            world.feed_sentence(p); world.run(1)
    for r in range(3):
        for p in RULES:
            world.feed_sentence(p); world.run(1)
    world.learn_negation("не")
    return world


# ════════════════════════════════════════════════════════
# ЭКСПЕРИМЕНТ 1: ВОЛНА АКТИВАЦИИ (нейросетевой подход)
# ════════════════════════════════════════════════════════

def activate_wave(world, seed_word, max_depth=2, decay=0.5, max_activated=20):
    """Волна активации: числовое поле, распространение, decay.

    Возвращает dict {word: activation_level}.
    """
    visitor = Visitor(world)
    activated = {}
    queue = [(seed_word, 1.0, 0)]  # (word, level, depth)

    while queue and len(activated) < max_activated:
        word, level, depth = queue.pop(0)
        if word in activated:
            continue
        if level < 0.05:
            continue

        activated[word] = level

        if depth >= max_depth:
            continue

        info = visitor.visit(word)
        if not info["found"]:
            continue

        # Распространяем к братьям
        for brother in info["siblings"]:
            if brother not in activated and len(brother) > 1:
                queue.append((brother, level * decay, depth + 1))

    return activated


# ════════════════════════════════════════════════════════
# ЭКСПЕРИМЕНТ 2: ЖИВОЕ ВЗАИМОДЕЙСТВИЕ (кормление)
# ════════════════════════════════════════════════════════

def activate_feeding(world, seed_word, max_depth=2, feed_amount=0.1, max_fed=20):
    """Живая активация: существа кормятся, не числа.

    Кормит братьев seed_word, потом братьев братьев.
    Возвращает dict {word: energy_gained}.
    """
    visitor = Visitor(world)
    fed_words = {}
    queue = [(seed_word, feed_amount, 0)]

    while queue and len(fed_words) < max_fed:
        word, amount, depth = queue.pop(0)
        if word in fed_words:
            continue
        if amount < 0.01:
            continue

        # Кормим существо
        cr = world._find_by_parts((word,))
        if cr and cr.alive:
            cr.feed(amount)
            fed_words[word] = amount

        if depth >= max_depth:
            continue

        info = visitor.visit(word)
        if not info["found"]:
            continue

        for brother in info["siblings"]:
            if brother not in fed_words and len(brother) > 1:
                queue.append((brother, amount * 0.5, depth + 1))

    return fed_words


# ════════════════════════════════════════════════════════
# ТЕСТЫ
# ════════════════════════════════════════════════════════

def test_activation(label, activated, expected_present, expected_order=None):
    """Проверить результат активации."""
    print(f"\n  ── {label} ──")

    # Топ-10 по уровню
    sorted_act = sorted(activated.items(), key=lambda x: -x[1])
    print(f"    Активировано: {len(activated)} существ")
    for word, level in sorted_act[:12]:
        marker = " ←" if word in expected_present else ""
        print(f"      {word:25s} {level:.3f}{marker}")

    # Проверка: ожидаемые слова активированы?
    found = {w for w in expected_present if w in activated}
    missed = expected_present - found
    print(f"    Найдено: {sorted(found)}")
    if missed:
        print(f"    Пропущено: {sorted(missed)}")
    ok = len(found) >= len(expected_present) * 0.6
    print(f"    Результат: {len(found)}/{len(expected_present)}  {'OK' if ok else 'MISS'}")
    return ok


def main():
    print("=" * 60)
    print("  ДВА ЭКСПЕРИМЕНТА: ВОЛНА vs КОРМЛЕНИЕ")
    print("=" * 60)

    checks_wave = []
    checks_feed = []

    # ════════════════════════════════════════
    # ТЕСТ 1: Активировать "кот"
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ТЕСТ 1: АКТИВИРОВАТЬ 'кот'")
    print("  Ожидаем: ест, рыбу, мясо, млекопитающее, предмет, существительное")
    print("=" * 60)

    expected1 = {"ест", "рыбу", "мясо", "млекопитающее", "предмет", "доме"}

    # Эксперимент 1: волна
    world1 = build_world()
    wave1 = activate_wave(world1, "кот")
    ok1w = test_activation("ВОЛНА: кот", wave1, expected1)
    checks_wave.append(("кот → братья (волна)", ok1w))

    # Эксперимент 2: кормление
    world2 = build_world()
    feed1 = activate_feeding(world2, "кот")
    ok1f = test_activation("КОРМЛЕНИЕ: кот", feed1, expected1)
    checks_feed.append(("кот → братья (кормление)", ok1f))

    # ════════════════════════════════════════
    # ТЕСТ 2: Активировать "кот" + "существительное"
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ТЕСТ 2: АКТИВИРОВАТЬ 'кот' + 'существительное'")
    print("  Ожидаем: пересечение через 'предмет'")
    print("=" * 60)

    # Эксперимент 1: волна
    world3 = build_world()
    wave_kot = activate_wave(world3, "кот")
    wave_sush = activate_wave(world3, "существительное")
    # Пересечение
    common_wave = {w for w in wave_kot if w in wave_sush}
    print(f"\n  ── ВОЛНА: пересечение ──")
    print(f"    Общие: {sorted(common_wave)}")
    has_predmet_w = "предмет" in common_wave
    print(f"    'предмет' в пересечении: {has_predmet_w}")
    checks_wave.append(("кот∩существительное → предмет (волна)", has_predmet_w))

    # Эксперимент 2: кормление
    world4 = build_world()
    feed_kot = activate_feeding(world4, "кот")
    feed_sush = activate_feeding(world4, "существительное")
    common_feed = {w for w in feed_kot if w in feed_sush}
    print(f"\n  ── КОРМЛЕНИЕ: пересечение ──")
    print(f"    Общие: {sorted(common_feed)}")
    has_predmet_f = "предмет" in common_feed
    print(f"    'предмет' в пересечении: {has_predmet_f}")
    checks_feed.append(("кот∩существительное → предмет (кормление)", has_predmet_f))

    # ════════════════════════════════════════
    # ТЕСТ 3: Активировать "страус" — конфликт
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ТЕСТ 3: АКТИВИРОВАТЬ 'страус'")
    print("  Ожидаем: птица, летает, не — напряжение")
    print("=" * 60)

    expected3 = {"птица", "летает", "не"}

    # Волна
    world5 = build_world()
    wave3 = activate_wave(world5, "страус")
    ok3w = test_activation("ВОЛНА: страус", wave3, expected3)
    checks_wave.append(("страус → птица/летает/не (волна)", ok3w))

    # Кормление
    world6 = build_world()
    feed3 = activate_feeding(world6, "страус")
    ok3f = test_activation("КОРМЛЕНИЕ: страус", feed3, expected3)
    checks_feed.append(("страус → птица/летает/не (кормление)", ok3f))

    # ════════════════════════════════════════
    # ТЕСТ 4: Активировать "жи" — правило
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ТЕСТ 4: АКТИВИРОВАТЬ 'жи'")
    print("  Ожидаем: пишется, буквой, и, ши")
    print("=" * 60)

    expected4 = {"пишется", "буквой", "ши"}

    # Волна
    world7 = build_world()
    wave4 = activate_wave(world7, "жи")
    ok4w = test_activation("ВОЛНА: жи", wave4, expected4)
    checks_wave.append(("жи → пишется/буквой/ши (волна)", ok4w))

    # Кормление
    world8 = build_world()
    feed4 = activate_feeding(world8, "жи")
    ok4f = test_activation("КОРМЛЕНИЕ: жи", feed4, expected4)
    checks_feed.append(("жи → пишется/буквой/ши (кормление)", ok4f))

    # ════════════════════════════════════════
    # ТЕСТ 5: После активации — ask() лучше?
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ТЕСТ 5: ask() ПОСЛЕ АКТИВАЦИИ")
    print("=" * 60)

    # Базовый мир без активации
    world_base = build_world()
    gen_base = Generator(world_base)
    r_base = gen_base.ask("какая часть речи кот?")
    base_has = "существительное" in r_base["answers"] or "Существительное" in r_base["answers"]
    print(f"\n  Без активации:")
    print(f"    ask('часть речи кот?') → {r_base['answers'][:6]}  {'OK' if base_has else 'MISS'}")

    # После wave-активации кот + существительное
    world_wave = build_world()
    activate_wave(world_wave, "кот")
    activate_wave(world_wave, "существительное")
    gen_wave = Generator(world_wave)
    r_wave = gen_wave.ask("какая часть речи кот?")
    wave_has = "существительное" in r_wave["answers"] or "Существительное" in r_wave["answers"]
    print(f"\n  После волны (кот + существительное):")
    print(f"    ask('часть речи кот?') → {r_wave['answers'][:6]}  {'OK' if wave_has else 'MISS'}")
    checks_wave.append(("ask после волны → существительное", wave_has))

    # После feed-активации кот + существительное
    world_feed = build_world()
    activate_feeding(world_feed, "кот")
    activate_feeding(world_feed, "существительное")
    gen_feed = Generator(world_feed)
    r_feed = gen_feed.ask("какая часть речи кот?")
    feed_has = "существительное" in r_feed["answers"] or "Существительное" in r_feed["answers"]
    print(f"\n  После кормления (кот + существительное):")
    print(f"    ask('часть речи кот?') → {r_feed['answers'][:6]}  {'OK' if feed_has else 'MISS'}")
    checks_feed.append(("ask после кормления → существительное", feed_has))

    # ════════════════════════════════════════
    # ИТОГ
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("╔═══════════════════════════════════════════════════════╗")
    print("║     СРАВНЕНИЕ: ВОЛНА vs КОРМЛЕНИЕ                     ║")
    print("╠═══════════════════════════════════════════════════════╣")

    wave_passed = sum(1 for _, ok in checks_wave if ok)
    feed_passed = sum(1 for _, ok in checks_feed if ok)

    print(f"║                                                       ║")
    print(f"║  ВОЛНА АКТИВАЦИИ (нейросетевой подход):               ║")
    for name, ok in checks_wave:
        s = "+" if ok else "-"
        print(f"║    {s} {name:48s}  ║")
    print(f"║  Результат: {wave_passed}/{len(checks_wave)}                                   ║")

    print(f"║                                                       ║")
    print(f"║  КОРМЛЕНИЕ (живое взаимодействие):                    ║")
    for name, ok in checks_feed:
        s = "+" if ok else "-"
        print(f"║    {s} {name:48s}  ║")
    print(f"║  Результат: {feed_passed}/{len(checks_feed)}                                   ║")

    print(f"╠═══════════════════════════════════════════════════════╣")
    if wave_passed > feed_passed:
        print(f"║  ВОЛНА побеждает: {wave_passed} vs {feed_passed}                            ║")
    elif feed_passed > wave_passed:
        print(f"║  КОРМЛЕНИЕ побеждает: {feed_passed} vs {wave_passed}                        ║")
    else:
        print(f"║  НИЧЬЯ: {wave_passed} vs {feed_passed}                                   ║")
    print(f"╚═══════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    main()
