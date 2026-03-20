from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.advisor import build_advice
from app.schemas import AdvisorResponse, UserProfile

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


@app.post("/advisor/plan", response_model=AdvisorResponse)
def generate_plan(profile: UserProfile) -> AdvisorResponse:
    return build_advice(profile)
