from .creature import Creature


class Splitter:
    def __init__(self, world):
        self.world = world

    def _service_threshold(self):
        """Dynamic threshold: a word is a hub if its service_score is
        significantly above the median for all single-word creatures."""
        w = self.world
        scores = []
        for c in w.creatures.values():
            if c.alive and c.complexity == 1:
                scores.append(w.service_score(c.parts[0]))
        if not scores:
            return 0.5
        scores.sort()
        median = scores[len(scores) // 2]
        return min(0.8, median + 0.25)

    def _get_context_groups(self, word):
        """Cluster organisms containing `word` by co-occurring parts.

        Service words (score above dynamic threshold) are excluded
        from context parts so they don't glue unrelated groups together.
        """
        w = self.world
        organisms = [c for c in w.creatures.values()
                     if c.alive and c.complexity >= 2 and word in c.parts]
        if len(organisms) < 2:
            return []

        threshold = self._service_threshold()
        service_cache = {}
        def is_service(part):
            if part not in service_cache:
                service_cache[part] = w.service_score(part)
            return service_cache[part] >= threshold

        contexts = []
        for org in organisms:
            parts = frozenset(
                p for p in org.parts
                if p != word and not p.startswith("$") and not is_service(p)
            )
            if parts:
                contexts.append((org, parts))
        if len(contexts) < 2:
            return []
        groups = []
        for org, parts in contexts:
            merged = False
            for g in groups:
                if g["parts"] & parts:
                    g["parts"] |= parts
                    g["orgs"].append(org)
                    merged = True
                    break
            if not merged:
                groups.append({"parts": set(parts), "orgs": [org]})
        return groups

    def split(self, word, min_groups=2):
        """If a word lives in disconnected context clusters,
        split it into separate sense-creatures.

        Words with service_score above dynamic threshold are skipped —
        they're hubs, not homonyms.
        """
        w = self.world

        threshold = self._service_threshold()
        if w.service_score(word) >= threshold:
            return []

        groups = self._get_context_groups(word)
        if len(groups) < min_groups:
            return []
        all_parts = set()
        for g in groups:
            all_parts |= g["parts"]
        shared = set.intersection(*(g["parts"] for g in groups)) if groups else set()
        unique_per_group = [g["parts"] - shared for g in groups]
        if all(len(u) == 0 for u in unique_per_group):
            return []

        new_senses = []
        for i, g in enumerate(groups):
            unique = unique_per_group[i]
            if not unique:
                continue
            label = sorted(unique)[0]
            sense_name = f"{word}_{label}"
            existing = w._find_by_parts((sense_name,))
            if existing:
                existing.feed(0.5)
                new_senses.append(existing)
                continue
            sense = Creature([sense_name])
            original = w._find_by_parts((word,))
            if original:
                sense.energy = original.energy * 0.5
                sense.times_fed = max(1, original.times_fed // len(groups))
                sense.parent_ids = [original.id]
                original.children.append(sense.id)
            w._register(sense)
            w.stats["split"] += 1
            for org in g["orgs"]:
                sense.children.append(org.id)
            new_senses.append(sense)
        return new_senses
