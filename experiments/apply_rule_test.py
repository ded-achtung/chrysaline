#!/usr/bin/env python3
"""
apply_rule() — система применяет правила к задачам.

Знает правило "жи пишется с буквой и" → применяет к "жираф".
Знает "существительное обозначает предмет" → определяет часть речи.

Использует visiting + think + self_check. Не новый модуль.

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
# apply_rule() — применение правил
# ════════════════════════════════════════════════════════

def apply_rule(self, task, verbose=True):
    """Применить правило к задаче.

    Разбирает задачу, ищет подходящие правила через visiting,
    применяет правило, проверяет результат.

    Возвращает: {
        "task": задача,
        "answer": ответ (или None),
        "rule_used": какое правило применено,
        "reasoning": шаги рассуждения,
        "confidence": уверенность (0.0-1.0)
    }
    """
    visitor = Visitor(self)
    gen = Generator(self)

    result = {
        "task": task,
        "answer": None,
        "rule_used": None,
        "reasoning": [],
        "confidence": 0.0,
    }

    # Парсим задачу
    words = [w.strip("?!., ").lower() for w in task.split()]
    words = [w for w in words if w]

    q_words = {"что", "кто", "где", "как", "какой", "какая", "какое",
               "какие", "сколько", "или"}
    content = [w for w in words if w not in q_words and len(w) > 0]

    if not content:
        return result

    # ═══════════════════════════════════════
    # Стратегия 1: Прямой visiting — правило в братьях
    # "жи или жы?" → visit("жи") → "пишется с буквой и"
    # ═══════════════════════════════════════
    for word in content:
        info = visitor.visit(word)
        if not info["found"]:
            continue

        siblings = info["siblings"]

        # Ищем "пишется" в братьях — орфографическое правило
        if "пишется" in siblings or "буквой" in siblings:
            # Нашли орфографическое правило
            # Ищем абстракцию: $0·пишется·с·буквой·$1
            for c in self.creatures.values():
                if not c.alive or not c.slot_options:
                    continue
                if "пишется" not in c.parts:
                    continue
                fixed = [p for p in c.parts if not p.startswith("$")]
                if word in fixed or word.upper() in fixed or word.capitalize() in fixed:
                    continue  # word — фиксированная часть, не слот
                # word может быть в слоте
                for sn, opts in c.slot_options.items():
                    clean = {o for o in opts if not o.startswith("$")}
                    # Проверяем: word (или его вариант) в слоте?
                    word_variants = {word, word.upper(), word.capitalize(),
                                     word.replace("ы", "и").replace("я", "а").replace("ю", "у")}
                    match = clean & word_variants
                    if match:
                        matched = list(match)[0]
                        result["answer"] = matched
                        result["rule_used"] = c.name
                        result["reasoning"].append(
                            f"visit('{word}') → правило '{c.name}'")
                        result["confidence"] = min(1.0, c.energy / 5.0)
                        if verbose:
                            print(f"    Правило: {c.name} → {matched}")
                        return result

                # word в фиксированных частях — значит правило О нём
                if word in fixed or word.capitalize() in fixed:
                    # Какая буква после word?
                    for sn, opts in c.slot_options.items():
                        clean = sorted(o for o in opts if not o.startswith("$"))
                        if clean:
                            result["answer"] = f"{word} пишется с буквой {clean[0]}"
                            result["rule_used"] = c.name
                            result["reasoning"].append(
                                f"'{word}' в правиле {c.name} → {clean}")
                            result["confidence"] = min(1.0, c.energy / 5.0)
                            if verbose:
                                print(f"    Правило: {c.name} → {clean}")
                            return result

    # ═══════════════════════════════════════
    # Стратегия 2: Выбор из альтернатив
    # "жи или жы?" → сравнить энергию "жи" vs "жы"
    # ═══════════════════════════════════════
    if "или" in words:
        idx = words.index("или")
        if idx > 0 and idx < len(words) - 1:
            option_a = words[idx - 1]
            option_b = words[idx + 1]

            cr_a = self._find_by_parts((option_a,))
            cr_b = self._find_by_parts((option_b,))

            energy_a = cr_a.energy if cr_a else 0
            energy_b = cr_b.energy if cr_b else 0
            fed_a = cr_a.times_fed if cr_a else 0
            fed_b = cr_b.times_fed if cr_b else 0

            # Также проверяем: есть ли правило "X пишется с буквой Y"
            for opt in [option_a, option_b]:
                info_opt = visitor.visit(opt)
                if info_opt["found"] and "пишется" in info_opt["siblings"]:
                    result["answer"] = opt
                    result["rule_used"] = f"'{opt}' знает 'пишется'"
                    result["reasoning"].append(
                        f"visit('{opt}') → знает 'пишется'")
                    result["confidence"] = 0.9
                    if verbose:
                        print(f"    Правило: '{opt}' связан с 'пишется'")
                    return result

            # Нет правила — сравниваем энергию
            if energy_a > 0 or energy_b > 0:
                if energy_a > energy_b:
                    winner = option_a
                    result["reasoning"].append(
                        f"'{option_a}' (e={energy_a:.1f},fed={fed_a}) > "
                        f"'{option_b}' (e={energy_b:.1f},fed={fed_b})")
                else:
                    winner = option_b
                    result["reasoning"].append(
                        f"'{option_b}' (e={energy_b:.1f},fed={fed_b}) > "
                        f"'{option_a}' (e={energy_a:.1f},fed={fed_a})")
                result["answer"] = winner
                result["rule_used"] = "energy comparison"
                result["confidence"] = abs(energy_a - energy_b) / max(energy_a, energy_b, 1)
                if verbose:
                    print(f"    Энергия: '{option_a}'={energy_a:.1f} vs '{option_b}'={energy_b:.1f}")
                return result

    # ═══════════════════════════════════════
    # Стратегия 3: Через ask() → часть речи, категория
    # "кот — часть речи?" → ask("какая часть речи кот?")
    # ═══════════════════════════════════════
    # Определяем тип задачи по ключевым словам
    task_lower = task.lower()
    if "часть речи" in task_lower:
        # Найти слово для которого определяем часть речи
        subject = None
        for w in content:
            if w not in {"часть", "речи", "какая"}:
                subject = w
                break
        if subject:
            # Сначала: visit-цепочка (точнее чем ask)
            info_subj = visitor.visit(subject)
            if info_subj["found"]:
                for brother in info_subj["siblings"]:
                    if brother in {"предмет", "действие", "признак"}:
                        mapping = {
                            "предмет": "существительное",
                            "действие": "глагол",
                            "признак": "прилагательное",
                        }
                        if brother in mapping:
                            result["answer"] = mapping[brother]
                            result["rule_used"] = f"visit('{subject}')→'{brother}'→'{mapping[brother]}'"
                            result["reasoning"].append(
                                f"'{subject}' знает '{brother}', "
                                f"'{brother}' → '{mapping[brother]}'")
                            result["confidence"] = 0.8
                            if verbose:
                                print(f"    Цепочка: {subject}→{brother}→{mapping[brother]}")
                            return result
            # Fallback: ask()
            res = gen.ask(f"какая часть речи {subject}?")
            for a in res["answers"]:
                if a.lower() in {"существительное", "глагол", "прилагательное",
                                  "местоимение", "предлог"}:
                    result["answer"] = a
                    result["rule_used"] = "ask() → часть речи"
                    result["reasoning"] = res["reasoning"][:3]
                    result["confidence"] = 0.7
                    if verbose:
                        print(f"    ask() → {a}")
                    return result

    # "большая буква" задача
    if "большая" in task_lower and "буква" in task_lower:
        subject = None
        for w in content:
            if w not in {"большая", "буква", "как", "писать"}:
                subject = w
                break
        if subject:
            info_subj = visitor.visit(subject)
            if info_subj["found"]:
                sibs = info_subj["siblings"]
                # Знает ли слово "город", "имя", "фамилия"?
                if any(w in sibs for w in ["город", "города", "имена", "фамилии",
                                            "названия", "река", "страна"]):
                    result["answer"] = f"{subject.capitalize()} — с большой буквы"
                    result["rule_used"] = "имя собственное"
                    result["reasoning"].append(
                        f"'{subject}' связан с городами/именами")
                    result["confidence"] = 0.8
                    return result

    # ═══════════════════════════════════════
    # Стратегия 4: Общий ask() как fallback
    # ═══════════════════════════════════════
    res = gen.ask(task)
    if res["answers"]:
        result["answer"] = res["answers"][0]
        result["rule_used"] = "ask() fallback"
        result["reasoning"] = res["reasoning"][:3]
        result["confidence"] = 0.3
        return result

    return result


World.apply_rule = apply_rule


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

RULES = [
    # Орфография
    ["жи", "пишется", "с", "буквой", "и"],
    ["ши", "пишется", "с", "буквой", "и"],
    ["ча", "пишется", "с", "буквой", "а"],
    ["ща", "пишется", "с", "буквой", "а"],
    ["чу", "пишется", "с", "буквой", "у"],
    ["щу", "пишется", "с", "буквой", "у"],
    ["чк", "пишется", "без", "мягкого", "знака"],
    ["чн", "пишется", "без", "мягкого", "знака"],
    # Части речи
    ["существительное", "обозначает", "предмет"],
    ["глагол", "обозначает", "действие"],
    ["прилагательное", "обозначает", "признак"],
    # Предметы и действия
    ["кот", "это", "предмет"],
    ["собака", "это", "предмет"],
    ["мама", "это", "предмет"],
    ["стол", "это", "предмет"],
    ["бегать", "это", "действие"],
    ["читать", "это", "действие"],
    ["красный", "это", "признак"],
    ["большой", "это", "признак"],
    # Большая буква
    ["города", "пишутся", "с", "большой", "буквы"],
    ["москва", "это", "город"],
    ["имена", "пишутся", "с", "большой", "буквы"],
]

BRIDGES = [
    [".", "это", "точка"], [" ", "это", "пробел"],
    [" ", "разделяет", "слова"],
    [".", "означает", "конец", "предложения"],
    ["пробел", "разделяет", "слова"],
]


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
    print("  apply_rule() — ПРИМЕНЕНИЕ ПРАВИЛ")
    print("  Система знает правило и применяет его.")
    print("=" * 60)

    world = World()
    visitor = Visitor(world)
    gen = Generator(world)

    # Обучение
    print(f"\n{'='*60}")
    print("  ОБУЧЕНИЕ")
    print("=" * 60)
    teach(world, LEVEL1, "Буквы")
    teach(world, RULES, "Правила", repeats=3)
    teach(world, BRIDGES, "Мосты", repeats=5)

    alive0 = sum(1 for c in world.creatures.values() if c.alive)
    abst0 = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"\n  После обучения: {alive0} существ, {abst0} абстракций")

    # Проверим абстракции
    print(f"\n  Абстракции 'пишется':")
    for c in world.creatures.values():
        if not c.alive or not c.slot_options:
            continue
        if "пишется" in c.parts:
            slots = {}
            for sn, opts in c.slot_options.items():
                clean = sorted(o for o in opts if not o.startswith("$"))
                if clean:
                    slots[sn] = clean
            if slots:
                print(f"    {c.name}  {slots}  fed={c.times_fed}")

    # ════════════════════════════════════════
    # ТЕСТ 1: Орфография
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ТЕСТ 1: ОРФОГРАФИЯ")
    print("=" * 60)

    checks = []

    tasks_ortho = [
        ("жи или жы?", "жи"),
        ("ши или шы?", "ши"),
        ("ча или чя?", "ча"),
        ("чу или чю?", "чу"),
        ("дочка или дочька?", "дочка"),
    ]

    for task, expected in tasks_ortho:
        print(f"\n  Задача: {task}")
        res = world.apply_rule(task)
        answer = res["answer"]
        ok = answer is not None and expected in str(answer).lower()
        checks.append((f"орфография: {task}", ok))
        print(f"    Ответ: {answer}")
        print(f"    Правило: {res['rule_used']}")
        print(f"    Уверенность: {res['confidence']:.1f}")
        print(f"    {'OK' if ok else 'MISS'}")

    # ════════════════════════════════════════
    # ТЕСТ 2: Части речи
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ТЕСТ 2: ЧАСТИ РЕЧИ")
    print("=" * 60)

    tasks_pos = [
        ("кот — часть речи?", "существительное"),
        ("бегать — часть речи?", "глагол"),
        ("красный — часть речи?", "прилагательное"),
        ("мама — часть речи?", "существительное"),
        ("стол — часть речи?", "существительное"),
        ("читать — часть речи?", "глагол"),
    ]

    for task, expected in tasks_pos:
        print(f"\n  Задача: {task}")
        res = world.apply_rule(task)
        answer = str(res["answer"]).lower() if res["answer"] else ""
        ok = expected in answer
        checks.append((f"часть речи: {task}", ok))
        print(f"    Ответ: {res['answer']}")
        print(f"    Правило: {res['rule_used']}")
        print(f"    {'OK' if ok else 'MISS'}")

    # ════════════════════════════════════════
    # ТЕСТ 3: Большая буква
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ТЕСТ 3: БОЛЬШАЯ БУКВА")
    print("=" * 60)

    print(f"\n  Задача: москва — большая буква?")
    res_moscow = world.apply_rule("москва — большая буква?")
    ok_moscow = res_moscow["answer"] is not None and "Москва" in str(res_moscow["answer"])
    checks.append(("большая буква: москва", ok_moscow))
    print(f"    Ответ: {res_moscow['answer']}")
    print(f"    Правило: {res_moscow['rule_used']}")
    print(f"    {'OK' if ok_moscow else 'MISS'}")

    # ════════════════════════════════════════
    # ТЕСТ 4: ask() как fallback
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ТЕСТ 4: ОБЩИЕ ВОПРОСЫ (fallback)")
    print("=" * 60)

    print(f"\n  Задача: что обозначает существительное?")
    res_fb = world.apply_rule("что обозначает существительное?")
    ok_fb = "предмет" in str(res_fb["answer"]).lower() if res_fb["answer"] else False
    checks.append(("fallback: обозначает сущ.", ok_fb))
    print(f"    Ответ: {res_fb['answer']}")
    print(f"    {'OK' if ok_fb else 'MISS'}")

    # ════════════════════════════════════════
    # ИТОГ
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("╔═══════════════════════════════════════════════════════╗")
    print("║     ИТОГ: apply_rule() — ПРИМЕНЕНИЕ ПРАВИЛ            ║")
    print("╠═══════════════════════════════════════════════════════╣")

    passed = 0
    for name, ok in checks:
        s = "+" if ok else "-"
        if ok:
            passed += 1
        print(f"║  {s} {name:52s}║")

    print(f"╠═══════════════════════════════════════════════════════╣")
    print(f"║  Результат: {passed}/{len(checks)}                                   ║")

    # По типам
    ortho = sum(1 for n, ok in checks if n.startswith("орфография") and ok)
    pos = sum(1 for n, ok in checks if n.startswith("часть") and ok)
    other = sum(1 for n, ok in checks if not n.startswith("орфография") and not n.startswith("часть") and ok)

    print(f"║  Орфография: {ortho}/{sum(1 for n,_ in checks if n.startswith('орфография'))}                                ║")
    print(f"║  Части речи: {pos}/{sum(1 for n,_ in checks if n.startswith('часть'))}                               ║")
    print(f"║  Другое: {other}/{sum(1 for n,_ in checks if not n.startswith('орфография') and not n.startswith('часть'))}                                   ║")

    if passed >= 10:
        print(f"║                                                       ║")
        print(f"║  apply_rule() РАБОТАЕТ.                              ║")
    elif passed >= 7:
        print(f"║                                                       ║")
        print(f"║  ЧАСТИЧНО. Основные правила применяются.             ║")
    else:
        print(f"║                                                       ║")
        print(f"║  НУЖНА ДОРАБОТКА.                                    ║")

    print(f"╚═══════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    main()
