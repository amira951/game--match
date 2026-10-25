import time

# REMARQUE 1 : approche plate volontaire (pas de hiérarchie dans dataset SteamSpy)
def jaccard(a: set, b: set) -> float:
    if not a and not b: return 0.0
    return len(a & b) / len(a | b)

class JaccardRecommender:
    def __init__(self, repo): self.repo = repo
    def recommend(self, game_id: int, k: int = 10) -> dict:
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