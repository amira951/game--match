import sys
from pathlib import Path
import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))
from services.jaccard_service import jaccard, JaccardRecommender


def test_exemple_du_sujet():
    a = {"action", "combat", "hackandslash"}
    b = {"action", "mondeouvert", "rpg"}
    assert jaccard(a, b) == pytest.approx(0.2)      # 1 tag commun sur 5 distincts


def test_jeux_identiques():
    assert jaccard({"a", "b"}, {"a", "b"}) == 1.0


def test_aucun_tag_commun():
    assert jaccard({"a"}, {"b"}) == 0.0


def test_ensembles_vides():
    assert jaccard(set(), set()) == 0.0              # pas de division par zéro


class FakeRepo:
    tag_sets = [{"a", "b"}, {"a", "b"}, {"c"}]
    def get(self, i):
        return {"id": i, "title": f"jeu{i}"}


def test_recommandation_exclut_le_jeu_lui_meme():
    res = JaccardRecommender(FakeRepo()).recommend(0, k=2)
    ids = [r["id"] for r in res["results"]]
    assert 0 not in ids
    assert ids[0] == 1                               # le jeu avec les mêmes tags arrive en premier
    assert res["metrics"]["compared"] == 2