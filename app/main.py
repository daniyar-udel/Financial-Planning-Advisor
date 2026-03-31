import os

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.agent import chat_with_copilot
from app.auth import get_current_user, login_user, register_user
from app.advisor import build_advice
from app.database import init_db
from app.logger import get_logger, setup_logging
from app.onboarding import build_strategy_result, get_onboarding_profile, save_onboarding_profile
from app.schemas import (
    AgentChatRequest,
    AgentChatResponse,
    AdvisorResponse,
    LoginRequest,
    OnboardingProfileRequest,
    OnboardingProfileResponse,
    SignupRequest,
    StrategyResultResponse,
    TokenResponse,
    UserProfile,
    UserResponse,
)

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="AI Investment Strategy Advisor",
    version="0.1.0",
    description="Portfolio-grade MVP for market-aware long-term investment strategy planning.",
)

setup_logging()
log = get_logger(__name__)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

_default_origins = "http://127.0.0.1:5173,http://localhost:5173"
_allowed_origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", _default_origins).split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()
log.info("Application started — database initialized")


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
@limiter.limit("5/minute")
def signup(request: Request, payload: SignupRequest) -> TokenResponse:
    return register_user(payload)


@app.post("/auth/login", response_model=TokenResponse)
@limiter.limit("10/minute")
def login(request: Request, payload: LoginRequest) -> TokenResponse:
    return login_user(payload)


@app.get("/auth/me", response_model=UserResponse)
def me(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    return current_user


@app.get("/onboarding/profile", response_model=OnboardingProfileResponse)
def get_saved_onboarding(
    current_user: UserResponse = Depends(get_current_user),
) -> OnboardingProfileResponse:
    return get_onboarding_profile(current_user)


@app.post("/onboarding/profile", response_model=OnboardingProfileResponse)
def save_onboarding(
    payload: OnboardingProfileRequest,
    current_user: UserResponse = Depends(get_current_user),
) -> OnboardingProfileResponse:
    return save_onboarding_profile(current_user, payload)


@app.get("/strategy/result", response_model=StrategyResultResponse)
@limiter.limit("30/minute")
def get_strategy_result(
    request: Request,
    current_user: UserResponse = Depends(get_current_user),
) -> StrategyResultResponse:
    return build_strategy_result(current_user)


@app.post("/agent/chat", response_model=AgentChatResponse)
@limiter.limit("20/minute")
def agent_chat(
    request: Request,
    payload: AgentChatRequest,
    current_user: UserResponse = Depends(get_current_user),
) -> AgentChatResponse:
    return chat_with_copilot(current_user, payload)


@app.post("/advisor/plan", response_model=AdvisorResponse)
@limiter.limit("10/minute")
def generate_plan(request: Request, profile: UserProfile) -> AdvisorResponse:
    return build_advice(profile)
