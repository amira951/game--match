import time
from pathlib import Path

import numpy as np

EMBEDDINGS_FILE = Path(__file__).resolve().parents[1] / "data" / "embeddings.npy"


class EmbeddingsNotAvailable(Exception):
    pass


class EmbeddingRecommender:
    def __init__(self, repo):
        self.repo = repo
        self._emb = None

    def _load(self):
        if self._emb is None:
            if not EMBEDDINGS_FILE.exists():
                raise EmbeddingsNotAvailable(
                    "Embeddings non générés : lancez 'python scripts/generate_embeddings.py' depuis le dossier backend."
                )
            emb = np.load(EMBEDDINGS_FILE)
            if emb.shape[0] != self.repo.count():
                raise EmbeddingsNotAvailable(
                    "Le fichier d'embeddings ne correspond pas au CSV : relancez scripts/generate_embeddings.py."
                )
            self._emb = emb
        return self._emb

    def recommend(self, game_id: int, k: int = 10) -> dict:
        emb = self._load()
        start = time.perf_counter()
        scores = emb @ emb[game_id]
        scores[game_id] = -np.inf
        k = min(k, len(scores) - 1)
        top = np.argpartition(-scores, k - 1)[:k]
        top = top[np.argsort(-scores[top])]
        elapsed = (time.perf_counter() - start) * 1000
        return {
            "method": "embeddings",
            "source": self.repo.get(game_id)["title"],
            "results": [{**self.repo.get(int(i)), "score": round(float(scores[i]), 3)} for i in top],
            "metrics": {"time_ms": round(elapsed, 2), "compared": len(scores) - 1},
        }
