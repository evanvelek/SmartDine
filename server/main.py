from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from schemas import RecommendRequest, RecommendResponse, UserProfile, VisitRequest, FavoriteRequest
from services.recommend_service import recommend, debug_recommend
from db import init_db
from repositories.user_repo import (
    upsert_user_profile,
    log_visit,
    get_user_profile,
    delete_user_profile,
    add_favorite,
    get_user_favorites,
)


app = FastAPI(title="SmartDine Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def _startup():
    init_db()

@app.post("/recommend", response_model=RecommendResponse)
async def recommend_endpoint(req: RecommendRequest):
    return await recommend(req)

@app.post("/debug/recommend")
async def debug_recommend_endpoint(req: RecommendRequest):
    return await debug_recommend(req)

@app.post("/profile")
def upsert_profile(p: UserProfile):
    upsert_user_profile(p)
    return {"ok": True}

@app.get("/profile/{user_id}", response_model=UserProfile)
def get_profile_endpoint(user_id: str):
    profile = get_user_profile(user_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@app.post("/visit")
def visit_endpoint(v: VisitRequest):
    log_visit(v)
    return {"ok": True}

@app.delete("/profile/{user_id}")
def delete_profile(user_id: str):
    deleted = delete_user_profile(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {"ok": True, "deleted_user_id": user_id}

@app.post("/favorites")
def add_favorite_endpoint(f: FavoriteRequest):
    add_favorite(
        user_id=f.user_id,
        restaurant_id=f.restaurant_id,
        name=f.name,
        address=f.address,
        rating=f.rating,
        description=f.description,
    )
    return {"ok": True}

@app.get("/favorites/{user_id}")
def get_favorites_endpoint(user_id: str):
    favorites = get_user_favorites(user_id)
    return {"favorites": favorites}
