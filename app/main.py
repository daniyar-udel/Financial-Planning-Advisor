from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth import get_current_user, login_user, register_user
from app.advisor import build_advice
from app.database import init_db
from app.schemas import (
    AdvisorResponse,
    LoginRequest,
    SignupRequest,
    TokenResponse,
    UserProfile,
    UserResponse,
)

app = FastAPI(
    title="AI Investment Strategy Advisor",
    version="0.1.0",
    description="Portfolio-grade MVP for market-aware long-term investment strategy planning.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": "AI Investment Strategy Advisor",
        "docs": "/docs",
        "health": "/health",
    }


@app.post("/auth/signup", response_model=TokenResponse)
def signup(payload: SignupRequest) -> TokenResponse:
    return register_user(payload)


@app.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest) -> TokenResponse:
    return login_user(payload)


@app.get("/auth/me", response_model=UserResponse)
def me(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    return current_user


@app.post("/advisor/plan", response_model=AdvisorResponse)
def generate_plan(profile: UserProfile) -> AdvisorResponse:
    return build_advice(profile)
