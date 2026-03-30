#!/usr/bin/env python3
"""
Уровень 4: Чтение настоящей сказки.

Система прошла уровни 1-2 (буквы, пунктуация, мосты).
Метод read() работает. Теперь — настоящий текст.

Курочка Ряба, потом Репка. Через read(). Без подсказок.
Главный вопрос: достаточно ли повторений в естественном тексте
для рождения абстракций без учителя?

Движок НЕ менялся.
"""

from chrysaline import World, Visitor, Generator


# ════════════════════════════════════════════════════════
# read() — патчим World (из level3_read.py)
# ════════════════════════════════════════════════════════

def read(self, text):
    """Прочитать сырой текст, используя знания системы."""
    visitor = Visitor(self)

    knows_space = False
    space_info = visitor.visit(" ")
    if space_info["found"]:
        space_sibs = space_info["siblings"]
        if "пробел" in space_sibs or "разделяет" in space_sibs or "слова" in space_sibs:
            knows_space = True

    knows_dot = False
    dot_info = visitor.visit(".")
    if dot_info["found"]:
        dot_sibs = dot_info["siblings"]
        if "точка" in dot_sibs or "конец" in dot_sibs or "предложения" in dot_sibs:
            knows_dot = True

    if knows_space:
        raw_tokens = text.split(" ")
        raw_tokens = [t for t in raw_tokens if t]

        if knows_dot:
            tokens = []
            for t in raw_tokens:
                if t.endswith(".") and len(t) > 1:
                    tokens.append(t[:-1])
                    tokens.append(".")
                elif t == ".":
                    tokens.append(".")
                else:
                    tokens.append(t)

            sentences = []
            current = []
            for t in tokens:
                if t == ".":
                    if current:
                        current.append(".")
                        sentences.append(current)
                        current = []
                else:
                    current.append(t)
            if current:
                sentences.append(current)

            for sent in sentences:
                self.feed_sentence(sent)
                self.run(1)
        else:
            self.feed_sentence(raw_tokens)
            self.run(1)
    else:
        chars = list(text)
        self.feed_sentence(chars)
        self.run(1)

    return {
        "knows_space": knows_space,
        "knows_dot": knows_dot,
        "mode": "sentences" if (knows_space and knows_dot) else
                "words" if knows_space else "chars"
    }


World.read = read


# ════════════════════════════════════════════════════════
# ОБУЧЕНИЕ (уровни 1-2, из предыдущих экспериментов)
# ════════════════════════════════════════════════════════

LEVEL1_ALPHABET = [
    ["а", "это", "гласная", "буква"],
    ["о", "это", "гласная", "буква"],
    ["у", "это", "гласная", "буква"],
    ["и", "это", "гласная", "буква"],
    ["е", "это", "гласная", "буква"],
    ["ы", "это", "гласная", "буква"],
    ["к", "это", "согласная", "буква"],
    ["т", "это", "согласная", "буква"],
    ["м", "это", "согласная", "буква"],
    ["н", "это", "согласная", "буква"],
    ["р", "это", "согласная", "буква"],
    ["с", "это", "согласная", "буква"],
    ["л", "это", "согласная", "буква"],
    ["д", "это", "согласная", "буква"],
    ["б", "это", "согласная", "буква"],
    ["п", "это", "согласная", "буква"],
]

LEVEL2_PUNCTUATION = [
    ["слова", "складываются", "в", "предложения"],
    ["предложение", "выражает", "мысль"],
    ["в", "конце", "предложения", "ставится", "точка"],
    ["точка", "означает", "конец", "мысли"],
    ["точка", "разделяет", "предложения"],
    ["после", "точки", "начинается", "новое", "предложение"],
    ["пробел", "разделяет", "слова"],
]

LEVEL2_BRIDGES = [
    [".", "это", "точка"],
    [".", "означает", "конец", "предложения"],
    [" ", "это", "пробел"],
    [" ", "разделяет", "слова"],
    ["пробел", "разделяет", "слова"],
]

LEVEL2_EXAMPLES = [
    ["кот", "спал", "это", "предложение"],
    ["мама", "мыла", "раму", "это", "предложение"],
    ["кот", "спал", ".", "здесь", "точка"],
    ["мама", "мыла", "раму", ".", "здесь", "точка"],
]

# ════════════════════════════════════════════════════════
# СКАЗКИ
# ════════════════════════════════════════════════════════

KUROCHKA_RYABA = "Жили-были дед да баба. И была у них курочка Ряба. Снесла курочка яичко. Не простое а золотое. Дед бил бил не разбил. Баба била била не разбила. Мышка бежала хвостиком махнула. Яичко упало и разбилось. Плачет дед плачет баба. А курочка кудахчет. Не плачь дед не плачь баба. Снесу я вам яичко не золотое а простое."

REPKA = "Посадил дед репку. Выросла репка большая пребольшая. Стал дед репку тянуть. Тянет потянет вытянуть не может. Позвал дед бабку. Бабка за дедку дедка за репку тянут потянут вытянуть не могут."


def teach(world, data, label, repeats=3):
    print(f"\n  ── {label} ({len(data)} фраз, {repeats}x) ──")
    for r in range(repeats):
        for phrase in data:
            world.feed_sentence(phrase)
            world.run(1)
    alive = sum(1 for c in world.creatures.values() if c.alive)
    abst = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"    → {alive} существ, {abst} абстракций")


def show_visit(visitor, word):
    info = visitor.visit(word)
    if info["found"]:
        sibs = sorted(info["siblings"])[:15]
        mates = sorted(info.get("slot_mates", set()))[:10]
        print(f"    '{word}' братья: {sibs}")
        if mates:
            print(f"    '{word}' slot_mates: {mates}")
        return info
    else:
        print(f"    '{word}' не найден")
        return info


def main():
    print("=" * 60)
    print("  УРОВЕНЬ 4: ЧТЕНИЕ НАСТОЯЩЕЙ СКАЗКИ")
    print("  Курочка Ряба + Репка. Через read().")
    print("  Движок НЕ менялся.")
    print("=" * 60)

    world = World()
    visitor = Visitor(world)
    gen = Generator(world)

    # ════════════════════════════════════════
    # ОБУЧЕНИЕ (уровни 1-2)
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ОБУЧЕНИЕ: УРОВНИ 1-2")
    print("=" * 60)

    teach(world, LEVEL1_ALPHABET, "Буквы (уровень 1)")
    teach(world, LEVEL2_PUNCTUATION, "Пунктуация (уровень 2)")
    teach(world, LEVEL2_BRIDGES, "Мосты символ↔понятие", repeats=5)
    teach(world, LEVEL2_EXAMPLES, "Примеры предложений")

    alive_before = sum(1 for c in world.creatures.values() if c.alive)
    abst_before = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    absorbed_before = world.stats["absorbed"]
    print(f"\n  После обучения: {alive_before} существ, {abst_before} абстракций")

    # Проверим что read() готов
    ri = world.read.__func__(world, "тест.")
    # Откатим — это был просто тест
    print(f"  read() mode: {ri['mode']} (должен быть 'sentences')")

    # ════════════════════════════════════════
    # ЭТАП 1: КУРОЧКА РЯБА
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ЭТАП 1: КУРОЧКА РЯБА")
    print("=" * 60)

    print(f"\n  Текст ({len(KUROCHKA_RYABA)} символов):")
    print(f"  \"{KUROCHKA_RYABA[:80]}...\"")

    result_kr = world.read(KUROCHKA_RYABA)
    print(f"\n  read() mode: {result_kr['mode']}")

    alive_kr = sum(1 for c in world.creatures.values() if c.alive)
    abst_kr = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    absorbed_kr = world.stats["absorbed"] - absorbed_before
    print(f"  После сказки: {alive_kr} существ, {abst_kr} абстракций")
    print(f"  Поглощений: {absorbed_kr}")

    # ════════════════════════════════════════
    # ЭТАП 2: ПРОВЕРКА — ЧТО ПОНЯЛА
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ЭТАП 2: ЧТО СИСТЕМА ПОНЯЛА ИЗ СКАЗКИ?")
    print("=" * 60)

    checks = []

    # visit("дед")
    print(f"\n  ── visit('дед') ──")
    ded_info = show_visit(visitor, "дед")
    ded_sibs = ded_info["siblings"] if ded_info["found"] else set()
    ded_knows_baba = "баба" in ded_sibs
    ded_knows_bil = "бил" in ded_sibs
    ded_knows_plach = "плачет" in ded_sibs or "плачь" in ded_sibs
    print(f"    знает 'баба': {ded_knows_baba}")
    print(f"    знает 'бил': {ded_knows_bil}")
    print(f"    знает 'плачет'/'плачь': {ded_knows_plach}")
    ok_ded = ded_knows_baba and (ded_knows_bil or ded_knows_plach)
    checks.append(("visit('дед') → баба, бил/плачет", ok_ded))

    # visit("курочка")
    print(f"\n  ── visit('курочка') ──")
    kur_info = show_visit(visitor, "курочка")
    kur_sibs = kur_info["siblings"] if kur_info["found"] else set()
    kur_knows_yaichko = "яичко" in kur_sibs
    kur_knows_ryaba = "Ряба" in kur_sibs
    kur_knows_snesla = "Снесла" in kur_sibs or "снесла" in kur_sibs
    print(f"    знает 'яичко': {kur_knows_yaichko}")
    print(f"    знает 'Ряба': {kur_knows_ryaba}")
    print(f"    знает 'Снесла': {kur_knows_snesla}")
    ok_kur = kur_knows_yaichko or kur_knows_ryaba
    checks.append(("visit('курочка') → яичко/Ряба", ok_kur))

    # visit("яичко")
    print(f"\n  ── visit('яичко') ──")
    ya_info = show_visit(visitor, "яичко")
    ya_sibs = ya_info["siblings"] if ya_info["found"] else set()
    ya_knows_zolotoe = "золотое" in ya_sibs
    ya_knows_prostoe = "простое" in ya_sibs
    ya_knows_upalo = "упало" in ya_sibs
    print(f"    знает 'золотое': {ya_knows_zolotoe}")
    print(f"    знает 'простое': {ya_knows_prostoe}")
    print(f"    знает 'упало': {ya_knows_upalo}")
    ok_ya = ya_knows_zolotoe or ya_knows_prostoe
    checks.append(("visit('яичко') → золотое/простое", ok_ya))

    # ask("кто снесла яичко?")
    print(f"\n  ── ask('кто снесла яичко?') ──")
    res_snesla = gen.ask("кто снесла яичко?")
    print(f"    ответ: {res_snesla['answers'][:8]}")
    if res_snesla["reasoning"]:
        for r in res_snesla["reasoning"][:3]:
            print(f"    логика: {r}")
    ok_snesla = "курочка" in res_snesla["answers"] or "Снесла" in res_snesla["answers"]
    checks.append(("ask('кто снесла яичко?') → курочка", ok_snesla))

    # ask("кто бил яичко?")
    print(f"\n  ── ask('кто бил яичко?') ──")
    res_bil = gen.ask("кто бил яичко?")
    print(f"    ответ: {res_bil['answers'][:8]}")
    ok_bil = "дед" in res_bil["answers"] or "Дед" in res_bil["answers"] or "баба" in res_bil["answers"] or "Баба" in res_bil["answers"]
    checks.append(("ask('кто бил яичко?') → дед/баба", ok_bil))

    # ask("какое яичко?")
    print(f"\n  ── ask('какое яичко?') ──")
    res_kakoe = gen.ask("какое яичко?")
    print(f"    ответ: {res_kakoe['answers'][:8]}")
    ok_kakoe = "золотое" in res_kakoe["answers"] or "простое" in res_kakoe["answers"]
    checks.append(("ask('какое яичко?') → золотое/простое", ok_kakoe))

    # ════════════════════════════════════════
    # ЭТАП 3: АБСТРАКЦИИ
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ЭТАП 3: АБСТРАКЦИИ ИЗ СКАЗКИ")
    print("=" * 60)

    # Все абстракции с персонажами сказки
    fairy_words = {"дед", "баба", "курочка", "яичко", "мышка", "Дед", "Баба",
                   "бил", "била", "плачет", "плачь", "снесла", "Снесла",
                   "золотое", "простое", "упало", "разбилось", "Не", "не"}

    print(f"\n  Абстракции из Курочки Рябы:")
    fairy_abstractions = []
    for c in world.creatures.values():
        if not c.alive or not c.slot_options:
            continue
        parts_set = set(c.parts)
        if parts_set & fairy_words:
            slots = {}
            for sn, opts in c.slot_options.items():
                clean = sorted(o for o in opts if not o.startswith("$"))
                if clean:
                    slots[sn] = clean
            if slots:
                fairy_abstractions.append((c.name, slots, c.times_fed))
                print(f"    {c.name}  {slots}  fed={c.times_fed}")

    if not fairy_abstractions:
        print(f"    (нет абстракций из сказки)")

    has_abstractions = len(fairy_abstractions) >= 1
    checks.append(("Абстракции из сказки родились", has_abstractions))

    # Специально ищем: $0·плачет → {дед, баба}?
    print(f"\n  Ищем '$0·плачет' или 'плачет·$0':")
    found_plach = False
    for c in world.creatures.values():
        if not c.alive or not c.slot_options:
            continue
        if "плачет" in c.parts or "плачь" in c.parts:
            for sn, opts in c.slot_options.items():
                clean = sorted(o for o in opts if not o.startswith("$"))
                if clean:
                    print(f"    {c.name}  {sn}={clean}  fed={c.times_fed}")
                    found_plach = True

    # Ищем: $0·бил → ?
    print(f"\n  Ищем '$0·бил' или 'бил·$0':")
    for c in world.creatures.values():
        if not c.alive or not c.slot_options:
            continue
        if "бил" in c.parts or "била" in c.parts:
            for sn, opts in c.slot_options.items():
                clean = sorted(o for o in opts if not o.startswith("$"))
                if clean:
                    print(f"    {c.name}  {sn}={clean}  fed={c.times_fed}")

    # ════════════════════════════════════════
    # ЭТАП 4: РЕПКА
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ЭТАП 4: РЕПКА")
    print("=" * 60)

    print(f"\n  Текст ({len(REPKA)} символов):")
    print(f"  \"{REPKA[:80]}...\"")

    absorbed_before_repka = world.stats["absorbed"]
    result_rp = world.read(REPKA)
    print(f"\n  read() mode: {result_rp['mode']}")

    alive_rp = sum(1 for c in world.creatures.values() if c.alive)
    abst_rp = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    absorbed_repka = world.stats["absorbed"] - absorbed_before_repka
    print(f"  После Репки: {alive_rp} существ, {abst_rp} абстракций")
    print(f"  Поглощений: {absorbed_repka}")

    # "дед" окреп?
    print(f"\n  ── 'дед' после двух сказок ──")
    ded_after = show_visit(visitor, "дед")
    ded_sibs_after = ded_after["siblings"] if ded_after["found"] else set()
    ded_knows_repku = "репку" in ded_sibs_after
    ded_knows_babku = "бабку" in ded_sibs_after
    ded_cr = world._find_by_parts(("дед",))
    if ded_cr:
        print(f"    energy={ded_cr.energy:.1f}  fed={ded_cr.times_fed}")
    print(f"    знает 'репку': {ded_knows_repku}")
    print(f"    знает 'бабку': {ded_knows_babku}")
    ok_ded2 = ded_knows_repku or ded_knows_babku
    checks.append(("'дед' окреп (знает из Репки)", ok_ded2))

    # ask("что посадил дед?")
    print(f"\n  ── ask('что посадил дед?') ──")
    res_posadil = gen.ask("что посадил дед?")
    print(f"    ответ: {res_posadil['answers'][:8]}")
    ok_posadil = "репку" in res_posadil["answers"]
    checks.append(("ask('что посадил дед?') → репку", ok_posadil))

    # ask("кто тянул репку?")
    print(f"\n  ── ask('кто тянул репку?') ──")
    res_tyanul = gen.ask("кто тянул репку?")
    print(f"    ответ: {res_tyanul['answers'][:8]}")
    ok_tyanul = "дед" in res_tyanul["answers"] or "бабка" in res_tyanul["answers"] or "Бабка" in res_tyanul["answers"]
    checks.append(("ask('кто тянул репку?') → дед/бабка", ok_tyanul))

    # Абстракции из Репки
    print(f"\n  Абстракции из Репки:")
    repka_words = {"репку", "репка", "тянуть", "тянут", "Тянет", "потянет",
                   "потянут", "вытянуть", "Посадил", "Выросла", "бабку", "Бабка",
                   "дедку", "дедка", "Позвал", "Стал"}
    for c in world.creatures.values():
        if not c.alive or not c.slot_options:
            continue
        if set(c.parts) & repka_words:
            slots = {}
            for sn, opts in c.slot_options.items():
                clean = sorted(o for o in opts if not o.startswith("$"))
                if clean:
                    slots[sn] = clean
            if slots:
                print(f"    {c.name}  {slots}  fed={c.times_fed}")

    # ════════════════════════════════════════
    # ЭТАП 5: СТАТИСТИКА
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  ЭТАП 5: СТАТИСТИКА")
    print("=" * 60)

    alive_final = sum(1 for c in world.creatures.values() if c.alive)
    abst_final = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    total_absorbed = world.stats["absorbed"]

    print(f"  Существ: {alive_final}")
    print(f"  Абстракций: {abst_final}")
    print(f"  Поглощений всего: {total_absorbed}")
    print(f"  Соотношение абстракций/существ: {abst_final/alive_final:.2f}")
    print(f"  Статистика: {world.stats}")

    # Топ-15 абстракций по fed
    print(f"\n  Топ-15 абстракций:")
    for c in world.show_abstractions()[:15]:
        slots = {}
        for sn, opts in c.slot_options.items():
            clean = sorted(o for o in opts if not o.startswith("$"))
            if clean:
                slots[sn] = clean[:10]
        if slots:
            print(f"    {c.name:50s} {slots}  fed={c.times_fed}")

    # ════════════════════════════════════════
    # ИТОГ
    # ════════════════════════════════════════
    print(f"\n{'='*60}")
    print("╔═══════════════════════════════════════════════════════╗")
    print("║     ИТОГ: УРОВЕНЬ 4 — НАСТОЯЩИЕ СКАЗКИ               ║")
    print("╠═══════════════════════════════════════════════════════╣")

    passed = 0
    for name, ok in checks:
        s = "+" if ok else "-"
        if ok:
            passed += 1
        print(f"║  {s} {name:52s}║")

    print(f"╠═══════════════════════════════════════════════════════╣")
    print(f"║  Результат: {passed}/{len(checks)}                                    ║")
    print(f"║  Существ: {alive_final}, абстракций: {abst_final}                    ║")
    print(f"╠═══════════════════════════════════════════════════════╣")

    if passed >= 8:
        print(f"║  СКАЗКИ УСВОЕНЫ. Система читает настоящий текст.    ║")
    elif passed >= 5:
        print(f"║  ЧАСТИЧНО. Основные персонажи и связи найдены.      ║")
    elif passed >= 3:
        print(f"║  МИНИМАЛЬНО. Какие-то связи есть.                    ║")
    else:
        print(f"║  НУЖНА ДОРАБОТКА.                                    ║")

    print(f"║  Движок НЕ менялся.                                   ║")
    print(f"╚═══════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    main()
