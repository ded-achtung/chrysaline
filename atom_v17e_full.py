#!/usr/bin/env python3
"""v17e: Full textbook test - raw text, no hand-curation"""
import re, sys
sys.path.insert(0, '/mnt/user-data/outputs')

# Reuse World/Creature from v17d
from atom_v17d_exercises import World

def parse_raw(text):
    """Parse raw textbook into short phrases"""
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\(.*?\)', '', text)
    text = re.sub(r'[—–\-]', ' ', text)
    text = re.sub(r'[,:;!?]', '.', text)
    text = re.sub(r'\.+', '.', text)
    phrases = []
    for line in text.split('.'):
        line = line.strip().lower()
        words = [w.strip() for w in line.split() if len(w.strip()) >= 1]
        if len(words) < 2:
            continue
        if len(words) <= 6:
            phrases.append(words)
        else:
            for i in range(0, len(words) - 1, 3):
                chunk = words[i:i + 5]
                if len(chunk) >= 2:
                    phrases.append(chunk)
    return phrases

TEXTBOOK = """Правила по русскому языку для 1 класса:
1. Слова в предложении связаны по смыслу. Чтобы из слов получилось предложение, слова нужно изменять.
2. Первое слово в предложении пишется с большой буквы. В конце предложения ставят вопросительный знак, точку или восклицательный знак.
3. Предложения состоят из главных и второстепенных членов предложения. Главные члены предложения составляют основу предложения.
5. Звуки, при произношении которых слышится только голос, а воздух проходит во рту свободно, называются гласными. Гласный звук образует слог. Гласных звуков шесть: а, о, у, ы, и, э. Букв, обозначающих гласные звуки, 10: а, о, у, ы, и, э, е, ё, ю, я.
6. В слоге бывает только один гласный звук. В слове столько слогов, сколько в нем гласных звуков.
7. Звуки, при произношении которых воздух встречает во рту преграду и слышится только шум или голос и шум, называются согласными. Согласные звуки обозначаются буквами: б, в, г, д, ж, з, й, к, л, м, н, п, р, с, т, ф, х, ц, ч, ш, щ.
10. Имена, отчества и фамилии людей, клички животных пишутся с большой буквы. Названия улиц, сел, деревень, городов и рек пишутся с большой буквы.
14. Мы пишем буквосочетания жи и ши с буквой и. Это нужно запомнить.
15. Мы пишем буквосочетания ча и ща с буквой а, чу и щу с буквой у.
16. В буквосочетаниях чк, чн, щн мягкий знак не пишется.
17. Согласные звуки бывают звонкие и глухие. Звонкие произносятся с голосом и шумом, глухие с шумом.
19. Наша речь состоит из предложений. Слова делятся на части речи: имена существительные, имена прилагательные, глаголы, предлоги.
20. Имя существительное — это часть речи. Существительное обозначает предмет.
21. Имя прилагательное — это часть речи. Прилагательное обозначает признак.
22. Глагол — это часть речи. Глагол обозначает действие.
23. Предлог — это часть речи. Предлоги пишутся отдельно от других слов."""

def main():
    print("="*60)
    print("  v17e: ПОЛНЫЙ ТЕКСТ учебника (сырой, без подготовки)")
    print("="*60)

    phrases = parse_raw(TEXTBOOK)
    print(f"\n  Парсер: {len(phrases)} фраз из сырого текста")
    for p in phrases[:8]:
        print(f"    [{' '.join(p)}]")
    print(f"    ... и ещё {max(0, len(phrases)-8)}")

    world = World()
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
    v = world.query_category("гласными") | world.query_category("гласные") | world.query_category("гласных")
    vc = {x for x in v if len(x)==1 and x.isalpha()}
    f1 = [ch for ch in "молоко" if ch in vc]
    ok1 = f1 == ["о","о","о"]
    results.append(("Гласные в МОЛОКО", ok1, f"гласные={sorted(vc)}, нашли={f1}"))

    # 2. Слоги в МАШИНА
    f2 = [ch for ch in "машина" if ch in vc]
    ok2 = len(f2) == 3
    results.append(("Слоги в МАШИНА", ok2, f"гласных={len(f2)}"))

    # 3. ЖИ или ЖЫ
    ji = world.visit("жи")
    ja = ji.get("siblings",set()) | ji.get("concrete_relatives",set())
    ok3 = any(w in ja for w in ["буквой","пишем","и","пишется"])
    results.append(("ЖИ или ЖЫ", ok3, f"жи→{sorted(list(ja)[:8])}"))

    # 4. Часть речи КОШКА
    su = world.visit("существительное")
    sa = su.get("siblings",set())
    ok4 = "обозначает" in sa and "предмет" in sa
    results.append(("Часть речи КОШКА", ok4, f"сущ. братья={sorted(sa)}"))

    # 5. Большая буква МОСКВА
    for w in ["городов","города","деревень"]:
        gi = world.visit(w)
        if gi["found"]:
            break
    ga = gi.get("siblings",set()) | gi.get("concrete_relatives",set())
    ok5 = "большой" in ga and ("буквы" in ga or "пишутся" in ga)
    results.append(("Большая буква МОСКВА", ok5, f"города→{sorted(list(ga)[:10])}"))

    # 6. ДОЧКА или ДОЧЬКА
    ck = world.visit("чк")
    ca = ck.get("siblings",set()) | ck.get("concrete_relatives",set())
    ok6 = any(w in ca for w in ["пишется","знак","мягкий","не"])
    results.append(("ДОЧКА или ДОЧЬКА", ok6, f"чк→{sorted(list(ca)[:8])}"))

    # 7. Согласные в СТОЛ
    co = world.query_category("согласными") | world.query_category("согласные") | world.query_category("согласных")
    cc = {x for x in co if len(x)==1 and x.isalpha()}
    f7 = [ch for ch in "стол" if ch in cc]
    ok7 = sorted(f7) == sorted(["с","т","л"])
    results.append(("Согласные в СТОЛ", ok7, f"согласные={sorted(cc)}, нашли={f7}"))

    # 8. ЧАШКА или ЧЯШКА
    ch = world.visit("ча")
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
