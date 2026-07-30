from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from fastapi import Request

from app.core.security import decode_access_token
from app.core.logging import get_logger

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

    PUBLIC_PREFIXES = [
        "/webhook/",
        "/risk/",
        "/dashboard",
    ]

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

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
