class Creature:
    _next_id = 0

    def __init__(self, parts, parent_ids=None):
        Creature._next_id += 1
        self.id = Creature._next_id
        self.parts = tuple(parts)
        self.energy = 1.0
        self.age = 0
        self.times_fed = 1
        self.alive = True
        self.parent_ids = parent_ids or []
        self.children = []
        self.generation = 0
        self.slot_options = {}
        self.valence = 1  # +1 = факт, -1 = отрицание

    @property
    def complexity(self):
        return len(self.parts)

    @property
    def name(self):
        if self.complexity == 1:
            return self.parts[0]
        return "·".join(self.parts)

    def feed(self, amount=0.5):
        # Потолок зависит от complexity: слова выше, организмы ниже
        cap = 10.0 if self.complexity == 1 else 8.0 if self.complexity <= 3 else 6.0
        self.energy = min(cap, self.energy + amount)
        self.times_fed += 1

    def starve(self, rate=None):
        # Скорость старения зависит от complexity:
        # слова стареют медленнее, длинные организмы — быстрее
        if rate is None:
            if self.complexity == 1:
                rate = 0.003  # слова живут долго
            elif self.complexity <= 3:
                rate = 0.005  # пары/тройки — стандарт
            else:
                rate = 0.008  # длинные — быстрее
        self.energy -= rate
        if self.energy <= 0:
            self.alive = False

    def tick(self):
        self.age += 1
        self.starve()

    def is_similar(self, other):
        """Формализованный порог: >= 75% позиций совпадает,
        минимум 2 общих, ровно 1 отличается."""
        if self.complexity != other.complexity:
            return False
        if self.complexity < 2:
            return False
        common = 0
        for i in range(self.complexity):
            if i < other.complexity and self.parts[i] == other.parts[i]:
                common += 1
        diff = self.complexity - common
        # Ровно 1 отличие И >= 75% совпадение (но минимум 1 общий)
        return diff == 1 and common >= max(1, self.complexity - 1)
