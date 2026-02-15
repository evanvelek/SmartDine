from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from schemas import RecommendRequest, RecommendResponse, UserProfile
from services.recommend_service import recommend
from db import init_db
from repositories.user_repo import upsert_user_profile

app = FastAPI(title="SmartDine Backend (Midterm Demo)")

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

@app.post("/profile")
def upsert_profile(p: UserProfile):
    upsert_user_profile(p)
    return {"ok": True}

