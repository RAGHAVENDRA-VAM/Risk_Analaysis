from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from fastapi import Request
from hmac import compare_digest

from app.core.security import decode_access_token
from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):

    PUBLIC_PATHS = [
        "/",
        "/health",
        "/favicon.ico",
        "/docs",
        "/openapi.json",
        "/redoc",
        "/auth/login",
        "/auth/register",
        "/auth/health",
    ]

    PUBLIC_PREFIXES = []

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Azure DevOps service hooks cannot issue our JWT.  A deployment may
        # explicitly opt into a dedicated shared secret for this one endpoint.
        if path == "/webhook/azure-devops" and settings.AZURE_DEVOPS_WEBHOOK_SECRET:
            supplied_secret = request.headers.get("X-Azure-DevOps-Webhook-Secret", "")
            if compare_digest(supplied_secret, settings.AZURE_DEVOPS_WEBHOOK_SECRET):
                return await call_next(request)
            return JSONResponse(status_code=401, content={"detail": "Invalid webhook secret"})

        if path in self.PUBLIC_PATHS or any(path.startswith(p) for p in self.PUBLIC_PREFIXES):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            logger.warning(f"Missing token for {path}")
            return JSONResponse(
                status_code=401,
                content={"detail": "Authorization token required"}
            )

        try:
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                raise ValueError()
        except Exception:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid authorization format"}
            )

        payload = decode_access_token(token)

        if not payload:
            logger.warning("Invalid JWT token")
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid token"}
            )

        request.state.user = {
            "username": payload.get("sub"),
            "role": payload.get("role"),
            "type": payload.get("type")
        }

        logger.info(f"Authenticated user: {request.state.user['username']}")

        return await call_next(request)
