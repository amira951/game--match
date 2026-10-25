from fastapi import APIRouter, HTTPException, Query
from models.repository import GameRepository
from services.jaccard_service import JaccardRecommender

router = APIRouter()
repo = GameRepository()
jaccard_reco = JaccardRecommender(repo)

@router.get("/games")
def list_games(search: str = "", limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0)):
    return repo.search(search, limit, offset)

@router.get("/recommend/jaccard/{game_id}")
def rec(game_id: int, k: int = 10):
    if game_id < 0 or game_id >= repo.count(): raise HTTPException(404, "Not found")
    return jaccard_reco.recommend(game_id, k)