from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="AI Knowledge Platform Backend",
    version="0.1.0",
    description="Minimal backend foundation for the AI Knowledge Platform",
)


class HealthResponse(BaseModel):
    status: str


@app.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    """Return application health status."""
    return HealthResponse(status="ok")
