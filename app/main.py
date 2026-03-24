from fastapi import FastAPI

from app.api.v1.api import api_router
from app.core.config import settings
from app.schemas.health import HealthCheckResponse


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
    )
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.get("/health", response_model=HealthCheckResponse, tags=["health"])
    def health_check() -> HealthCheckResponse:
        return HealthCheckResponse(status="ok")

    return app


app = create_application()
