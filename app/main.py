from fastapi import FastAPI

from app.api.routes_depseudonymize import router as depseudonymize_router
from app.api.routes_health import router as health_router
from app.api.routes_pseudonymize import router as pseudonymize_router
from app.api.routes_supported_classes import router as supported_classes_router
from app.config.settings import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version=settings.app_version)
    app.include_router(health_router)
    app.include_router(supported_classes_router)
    app.include_router(pseudonymize_router)
    app.include_router(depseudonymize_router)
    return app


app = create_app()
