from fastapi import FastAPI

from app.advisor import build_advice
from app.schemas import AdvisorResponse, UserProfile

app = FastAPI(
    title="AI Financial Planning Advisor",
    version="0.1.0",
    description="Portfolio-grade MVP for personalized long-term investment planning.",
)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": "AI Financial Planning Advisor",
        "docs": "/docs",
        "health": "/health",
    }


@app.post("/advisor/plan", response_model=AdvisorResponse)
def generate_plan(profile: UserProfile) -> AdvisorResponse:
    return build_advice(profile)
