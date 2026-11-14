import sys
import time

from services.metrics import MemoryProbe, memory_block

# REMARQUE 1 : approche plate volontaire (pas de hiérarchie dans dataset SteamSpy)
def jaccard(a: set, b: set) -> float:
    if not a and not b: return 0.0
    return len(a & b) / len(a | b)

class JaccardRecommender:
    def __init__(self, repo):
        self.repo = repo
        self._index_mb = None

    def index_mb(self):
        if self._index_mb is None:
            ts = self.repo.tag_sets
            size = sys.getsizeof(ts) + sum(sys.getsizeof(t) + sum(sys.getsizeof(x) for x in t) for t in ts)
            self._index_mb = round(size / 1024 / 1024, 2)
        return self._index_mb

    def recommend(self, game_id: int, k: int = 10, memory: bool = False) -> dict:
        with MemoryProbe(memory) as probe:
            res = self._recommend(game_id, k)
        res["metrics"]["memory"] = memory_block(probe, self.index_mb())
        res["metrics"]["complexity"] = {
            "time": "O(n·t)",
            "index_memory": "O(n·t)",
            "offline_cost": "aucun",
        }
        return res

    def _recommend(self, game_id: int, k: int) -> dict:
        start = time.perf_counter()
        target = self.repo.tag_sets[game_id]
        scores = []
        for i, tags in enumerate(self.repo.tag_sets):
            if i == game_id: continue
            scores.append((i, jaccard(target, tags)))
        scores.sort(key=lambda x: x[1], reverse=True)
        top = scores[:k]
        elapsed = (time.perf_counter() - start) * 1000
        return {
            "method": "jaccard",
            "source": self.repo.get(game_id)["title"],
            "results": [{**self.repo.get(i), "score": round(s,3)} for i,s in top],
            "metrics": {"time_ms": round(elapsed, 2), "compared": len(scores)}
        }