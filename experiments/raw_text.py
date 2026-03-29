#!/usr/bin/env python3
"""Тест на сыром тексте учебника (без ручной подготовки)."""

from chrysaline import World, Visitor
from data.textbook import TEXTBOOK, parse_raw


def main():
    print("="*60)
    print("  ПОЛНЫЙ ТЕКСТ учебника (сырой, без подготовки)")
    print("="*60)

    phrases = parse_raw(TEXTBOOK)
    print(f"\n  Парсер: {len(phrases)} фраз из сырого текста")
    for p in phrases[:8]:
        print(f"    [{' '.join(p)}]")
    print(f"    ... и ещё {max(0, len(phrases)-8)}")

    world = World()
    visitor = Visitor(world)

    print(f"\n  Обучение: {len(phrases)} фраз × 3 раунда")
    for r in range(1, 4):
        for phrase in phrases:
            world.feed_sentence(phrase)
            world.run(1)
    alive = len(world.creatures)
    abst = sum(1 for c in world.creatures.values() if c.alive and c.slot_options)
    print(f"  Результат: {alive} существ, {abst} абстракций, {world.stats['crossbred']} скрещиваний")

    # === УПРАЖНЕНИЯ ===
    print(f"\n{'='*60}")
    print("  УПРАЖНЕНИЯ")
    print("="*60)

    results = []

    # 1. Гласные в МОЛОКО
    v = visitor.query_category("гласными") | visitor.query_category("гласные") | visitor.query_category("гласных")
    vc = {x for x in v if len(x)==1 and x.isalpha()}
    f1 = [ch for ch in "молоко" if ch in vc]
    ok1 = f1 == ["о","о","о"]
    results.append(("Гласные в МОЛОКО", ok1, f"гласные={sorted(vc)}, нашли={f1}"))

    # 2. Слоги в МАШИНА
    f2 = [ch for ch in "машина" if ch in vc]
    ok2 = len(f2) == 3
    results.append(("Слоги в МАШИНА", ok2, f"гласных={len(f2)}"))

    # 3. ЖИ или ЖЫ
    ji = visitor.visit("жи")
    ja = ji.get("siblings",set()) | ji.get("concrete_relatives",set())
    ok3 = any(w in ja for w in ["буквой","пишем","и","пишется"])
    results.append(("ЖИ или ЖЫ", ok3, f"жи→{sorted(list(ja)[:8])}"))

    # 4. Часть речи КОШКА
    su = visitor.visit("существительное")
    sa = su.get("siblings",set())
    ok4 = "обозначает" in sa and "предмет" in sa
    results.append(("Часть речи КОШКА", ok4, f"сущ. братья={sorted(sa)}"))

    # 5. Большая буква МОСКВА
    for w in ["городов","города","деревень"]:
        gi = visitor.visit(w)
        if gi["found"]:
            break
    ga = gi.get("siblings",set()) | gi.get("concrete_relatives",set())
    ok5 = "большой" in ga and ("буквы" in ga or "пишутся" in ga)
    results.append(("Большая буква МОСКВА", ok5, f"города→{sorted(list(ga)[:10])}"))

    # 6. ДОЧКА или ДОЧЬКА
    ck = visitor.visit("чк")
    ca = ck.get("siblings",set()) | ck.get("concrete_relatives",set())
    ok6 = any(w in ca for w in ["пишется","знак","мягкий","не"])
    results.append(("ДОЧКА или ДОЧЬКА", ok6, f"чк→{sorted(list(ca)[:8])}"))

    # 7. Согласные в СТОЛ
    co = visitor.query_category("согласными") | visitor.query_category("согласные") | visitor.query_category("согласных")
    cc = {x for x in co if len(x)==1 and x.isalpha()}
    f7 = [ch for ch in "стол" if ch in cc]
    ok7 = sorted(f7) == sorted(["с","т","л"])
    results.append(("Согласные в СТОЛ", ok7, f"согласные={sorted(cc)}, нашли={f7}"))

    # 8. ЧАШКА или ЧЯШКА
    ch = visitor.visit("ча")
    ha = ch.get("siblings",set()) | ch.get("concrete_relatives",set())
    ok8 = any(w in ha for w in ["буквой","а","пишем"])
    results.append(("ЧАШКА или ЧЯШКА", ok8, f"ча→{sorted(list(ha)[:8])}"))

    # Результат
    passed = 0
    for name, ok, detail in results:
        s = "✓" if ok else "✗"
        if ok: passed += 1
        print(f"\n  {s} {name}")
        print(f"    {detail}")

    print(f"\n{'='*60}")
    print(f"  ИТОГ: {passed}/8 на СЫРОМ тексте учебника")
    print(f"  {alive} существ, {abst} абстракций")
    if passed >= 7:
        print(f"  ═══ РАБОТАЕТ НА СЫРОМ ТЕКСТЕ! ═══")
    elif passed >= 5:
        print(f"  ═══ ЧАСТИЧНО ═══")
    else:
        print(f"  ═══ НУЖНА ДОРАБОТКА ═══")
    print("="*60)


if __name__ == "__main__":
    main()
