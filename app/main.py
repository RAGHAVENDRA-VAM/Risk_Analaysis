from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine
from app.core.logging import get_logger
import app.models  # noqa: F401 - registers all models with SQLAlchemy
from app.middleware.auth_middleware import AuthMiddleware
from app.middleware.error_handler import register_exception_handlers
from app.api.routes.webhook_api import router as webhook_router
from app.api.routes.risk_api import router as risk_router
from app.api.routes.dashboard_api import router as dashboard_router
from app.core.config import settings

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AI DevOps Risk Platform...")
    if settings.ENVIRONMENT.lower() in {"production", "prod"} and not settings.JWT_SECRET_KEY:
        raise RuntimeError("JWT_SECRET_KEY must be configured in production")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized")
    yield
    logger.info("Stopping AI DevOps Risk Platform...")


app = FastAPI(
    title="AI DevOps Risk Platform",
    description="""
    Intelligent CI/CD risk analysis platform.

    Features:
    - Static Risk Analysis
    - Terraform Validation
    - Kubernetes Validation
    - Pipeline Security Checks
    - Azure OpenAI Risk Assessment
    - Deployment Gate Decisions
    """,
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.add_middleware(AuthMiddleware)

register_exception_handlers(app)

app.include_router(webhook_router)
app.include_router(risk_router)
app.include_router(dashboard_router)


@app.get("/")
async def root():
    return {
        "application": "AI DevOps Risk Platform",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow()
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "backend-api",
        "timestamp": datetime.utcnow()
    }
