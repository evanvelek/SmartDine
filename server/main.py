from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from schemas import RecommendRequest, RecommendResponse, UserProfile
from services.recommend_service import recommend
from db import init_db
from repositories.user_repo import upsert_user_profile
from services.recommend_service import recommend, debug_recommend
from schemas import RecommendRequest, RecommendResponse, UserProfile, VisitRequest
from repositories.user_repo import upsert_user_profile, log_visit
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

app = FastAPI(title="SmartDine Backend (Midterm Demo)")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print("422 body:", await request.body())
    print("422 errors:", exc.errors())
    return JSONResponse(status_code=422, content={"detail": exc.errors()})

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
    print("Got request: ", p)
    upsert_user_profile(p)
    return {"ok": True}

@app.post("/visit")
def visit_endpoint(v: VisitRequest):
    log_visit(v)
    return {"ok": True}

