#!/usr/bin/env python3
"""
Обучение на собственном опыте: learn_from_feedback.

Система пробует ответить → получает обратную связь → учится.
Правильные ответы крепнут, неправильные слабеют.

Движок НЕ менялся (learn_from_feedback добавляется как метод).
"""

from chrysaline import World, Visitor, Generator


# ════════════════════════════════════════════════════════
# read() + think() — из предыдущих экспериментов
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
# learn_from_feedback() — обучение на опыте
# ════════════════════════════════════════════════════════

def learn_from_feedback(self, question, given_answer, correct,
                        right_answer=None, verbose=True):
    """Обучение на обратной связи.

    question: строка вопроса
    given_answer: ответ который система дала
    correct: True/False
    right_answer: правильный ответ (если correct=False и учитель дал)
    """
    # Парсим вопрос
    q_words = {"что", "кто", "где", "как", "какой", "какая", "какое",
               "какие", "сколько", "чем", "кому", "куда", "почему", "когда"}
    words = [w.strip("?!., ").lower() for w in question.split()]
    content = [w for w in words if w not in q_words and len(w) > 1]

    result = {"action": "", "fed": 0, "starved": 0}

    if correct:
        # ═══ ПРАВИЛЬНЫЙ ОТВЕТ — укрепить ═══
        answer_lower = given_answer.lower() if given_answer else ""

        # 1. Подкормить организмы с ответом + словами вопроса
        for c in self.creatures.values():
            if not c.alive or c.complexity < 2:
                continue
            parts_set = set(p.lower() for p in c.parts)
            has_answer = answer_lower in parts_set
            has_question = any(cw in parts_set for cw in content)
            if has_answer and has_question:
                c.feed(0.3)
                self.stats["fed"] += 1
                result["fed"] += 1

        # 2. Подкормить абстракции со слотами содержащими ответ
        for c in self.creatures.values():
            if not c.alive or not c.slot_options:
                continue
            fixed = set(p.lower() for p in c.parts if not p.startswith("$"))
            if not any(cw in fixed for cw in content):
                continue
            for sn, opts in c.slot_options.items():
                clean = {o.lower() for o in opts if not o.startswith("$")}
                if answer_lower in clean:
                    c.feed(0.2)
                    self.stats["fed"] += 1
                    result["fed"] += 1

        # 3. Запомнить: создать опыт "вопрос → ответ"
        experience = content + [given_answer]
        if len(experience) >= 2:
            self.feed_sentence(experience)
            self.run(1)

        result["action"] = "reinforced"

        if verbose:
            print(f"    ВЕРНО: '{given_answer}' — подкормлено {result['fed']} организмов")

    else:
        # ═══ НЕПРАВИЛЬНЫЙ ОТВЕТ — ослабить + дать правильный ═══
        answer_lower = given_answer.lower() if given_answer else ""

        # 1. Ослабить организмы с неправильным ответом + словами вопроса
        for c in self.creatures.values():
            if not c.alive or c.complexity < 2:
                continue
            parts_set = set(p.lower() for p in c.parts)
            has_answer = answer_lower in parts_set
            has_question = any(cw in parts_set for cw in content)
            if has_answer and has_question:
                c.energy = max(0.1, c.energy - 0.2)
                result["starved"] += 1

        # 2. Если учитель дал правильный ответ — усвоить
        if right_answer:
            experience = content + [right_answer]
            if len(experience) >= 2:
                # Подаём несколько раз для усвоения
                for _ in range(3):
                    self.feed_sentence(experience)
                    self.run(1)

            # Подкормить существующие организмы с правильным ответом
            right_lower = right_answer.lower()
            for c in self.creatures.values():
                if not c.alive or c.complexity < 2:
                    continue
                parts_set = set(p.lower() for p in c.parts)
                has_right = right_lower in parts_set
                has_question = any(cw in parts_set for cw in content)
                if has_right and has_question:
                    c.feed(0.3)
                    self.stats["fed"] += 1
                    result["fed"] += 1

        result["action"] = "corrected"

        if verbose:
            msg = f"    НЕВЕРНО: '{given_answer}'"
            if right_answer:
                msg += f" → правильно: '{right_answer}'"
            msg += f" — ослаблено {result['starved']}, подкормлено {result['fed']}"
            print(msg)

    return result


World.learn_from_feedback = learn_from_feedback


# ════════════════════════════════════════════════════════
# ОБУЧЕНИЕ
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

CASE_BRIDGES = [
    ["Кот", "и", "кот", "это", "одно", "слово"],
    ["Собака", "и", "собака", "это", "одно", "слово"],
    ["Корова", "и", "корова", "это", "одно", "слово"],
]

TEXT = "Кот живёт в доме. Собака живёт в доме. Корова живёт на ферме. Кот ест рыбу. Собака ест мясо. Корова ест траву. Корова даёт молоко. Кот это млекопитающее. Собака это млекопитающее. Корова это млекопитающее."


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
    print("  ОБУЧЕНИЕ НА ОПЫТЕ: learn_from_feedback()")
    print("  Система пробует, получает обратную связь, учится.")
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
    teach(world, CASE_BRIDGES, "Мосты букв")
    for _ in range(3):
        world.read(TEXT)

    alive0 = sum(1 for c in world.creatures.values() if c.alive)
    abst0 = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"\n  После обучения: {alive0} существ, {abst0} абстракций")

    # ════════════════════════════════════════
    # РАУНД 1: Первая попытка — система отвечает
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  РАУНД 1: ПЕРВАЯ ПОПЫТКА")
    print("=" * 60)

    questions = [
        ("где живёт кот?", "доме", ["доме", "в"]),
        ("что ест корова?", "траву", ["траву"]),
        ("кто это млекопитающее?", None, ["Кот", "кот", "Собака", "собака", "Корова"]),
        ("что даёт корова?", "молоко", ["молоко"]),
        ("где живёт собака?", "доме", ["доме", "в"]),
    ]

    round1_results = []
    for q, expected_best, expected_any in questions:
        res = gen.ask(q)
        answers = res["answers"][:8]
        hit = any(e in answers for e in expected_any)
        round1_results.append((q, answers, hit, expected_best, expected_any))
        status = "OK" if hit else "MISS"
        print(f"\n  {status} {q}")
        print(f"    ответ: {answers}")

    # ════════════════════════════════════════
    # ОБРАТНАЯ СВЯЗЬ от учителя
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ОБРАТНАЯ СВЯЗЬ ОТ УЧИТЕЛЯ")
    print("=" * 60)

    for q, answers, hit, expected_best, expected_any in round1_results:
        print(f"\n  Вопрос: {q}")
        if hit and expected_best:
            # Система ответила правильно — найдём правильный ответ в списке
            correct_answer = None
            for a in answers:
                if a in expected_any:
                    correct_answer = a
                    break
            if correct_answer:
                world.learn_from_feedback(q, correct_answer, correct=True)
        elif not hit and expected_best:
            # Система ответила неправильно — учитель даёт правильный
            wrong_answer = answers[0] if answers else None
            world.learn_from_feedback(q, wrong_answer, correct=False,
                                     right_answer=expected_best)

    # ════════════════════════════════════════
    # РАУНД 2: Вторая попытка — после обучения
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  РАУНД 2: ПОСЛЕ ОБРАТНОЙ СВЯЗИ")
    print("=" * 60)

    checks = []
    round2_correct = 0

    for q, expected_best, expected_any in questions:
        res = gen.ask(q)
        answers = res["answers"][:8]
        hit = any(e in answers for e in expected_any)
        if hit:
            round2_correct += 1
        status = "OK" if hit else "MISS"
        print(f"\n  {status} {q}")
        print(f"    ответ: {answers}")
        checks.append((f"R2: {q}", hit))

    # ════════════════════════════════════════
    # РАУНД 3: Новые вопросы — обобщение
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  РАУНД 3: НОВЫЕ ВОПРОСЫ")
    print("=" * 60)

    new_questions = [
        ("что ест кот?", ["рыбу"]),
        ("что ест собака?", ["мясо"]),
        ("где живёт корова?", ["ферме", "на"]),
        ("кто живёт в доме?", ["Кот", "кот", "Собака", "собака"]),
    ]

    for q, expected_any in new_questions:
        res = gen.ask(q)
        answers = res["answers"][:8]
        hit = any(e in answers for e in expected_any)
        status = "OK" if hit else "MISS"
        print(f"\n  {status} {q}")
        print(f"    ответ: {answers}")
        checks.append((f"R3: {q}", hit))

    # ════════════════════════════════════════
    # РАУНД 4: Обратная связь на неправильный ответ
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  РАУНД 4: КОРРЕКЦИЯ ОШИБОК")
    print("=" * 60)

    # Намеренно спрашиваем то, что система скорее всего не знает
    # и учим через обратную связь
    print(f"\n  Учитель говорит: 'кит — это млекопитающее'")
    world.learn_from_feedback(
        "что такое кит?", None, correct=False,
        right_answer="млекопитающее")

    print(f"\n  Учитель говорит: 'щука живёт в реке'")
    world.learn_from_feedback(
        "где живёт щука?", None, correct=False,
        right_answer="реке")

    # Проверяем: запомнила?
    print(f"\n  Проверка после коррекции:")

    res_kit = gen.ask("что такое кит?")
    ok_kit = "млекопитающее" in res_kit["answers"]
    print(f"  {'OK' if ok_kit else 'MISS'} что такое кит? → {res_kit['answers'][:6]}")
    checks.append(("R4: кит → млекопитающее", ok_kit))

    res_shchuka = gen.ask("где живёт щука?")
    ok_sh = "реке" in res_shchuka["answers"]
    print(f"  {'OK' if ok_sh else 'MISS'} где живёт щука? → {res_shchuka['answers'][:6]}")
    checks.append(("R4: щука → реке", ok_sh))

    # ════════════════════════════════════════
    # РАУНД 5: Сравнение раунд 1 vs раунд 2
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  СРАВНЕНИЕ: РАУНД 1 vs РАУНД 2")
    print("=" * 60)

    round1_correct = sum(1 for _, _, hit, _, _ in round1_results if hit)
    print(f"  Раунд 1: {round1_correct}/{len(questions)}")
    print(f"  Раунд 2: {round2_correct}/{len(questions)}")
    improved = round2_correct >= round1_correct
    checks.append(("Раунд 2 >= Раунд 1", improved))
    print(f"  Улучшение: {improved}")

    # ════════════════════════════════════════
    # ИТОГ
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("╔═══════════════════════════════════════════════════════╗")
    print("║     ИТОГ: ОБУЧЕНИЕ НА ОПЫТЕ                           ║")
    print("╠═══════════════════════════════════════════════════════╣")

    passed = 0
    for name, ok in checks:
        s = "+" if ok else "-"
        if ok:
            passed += 1
        print(f"║  {s} {name:52s}║")

    print(f"╠═══════════════════════════════════════════════════════╣")
    print(f"║  Результат: {passed}/{len(checks)}                                   ║")

    alive = sum(1 for c in world.creatures.values() if c.alive)
    abst = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"║  Существ: {alive}, абстракций: {abst}                   ║")

    if passed >= 9:
        print(f"║                                                       ║")
        print(f"║  ОБУЧЕНИЕ НА ОПЫТЕ РАБОТАЕТ.                         ║")
    elif passed >= 6:
        print(f"║                                                       ║")
        print(f"║  ЧАСТИЧНО. Система учится из обратной связи.         ║")
    else:
        print(f"║                                                       ║")
        print(f"║  НУЖНА ДОРАБОТКА.                                    ║")

    print(f"╚═══════════════════════════════════════════════════════╝")

    print(f"\n  Статистика: {world.stats}")


if __name__ == "__main__":
    main()
