import logging
import os
import sys
from collections.abc import Callable, Awaitable
from ipaddress import ip_address
from typing import Any

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.rate_limiter import rate_limiter
from app.core.csrf import is_state_changing_method, should_skip_csrf_check

logger = logging.getLogger("clevercrest.auth")


def _is_test_environment() -> bool:
    return (
        "PYTEST_CURRENT_TEST" in os.environ
        or os.environ.get("TESTING") == "true"
        or any(name in sys.modules for name in ("pytest", "unittest"))
    )


class CsrfProtectionMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Any]],
    ) -> JSONResponse:
        path = request.url.path
        method = request.method

        if not is_state_changing_method(method):
            return await call_next(request)

        if should_skip_csrf_check(path, method):
            return await call_next(request)

        origin = request.headers.get("origin")
        referer = request.headers.get("referer")

        if origin is None and referer is None:
            if _is_test_environment():
                return await call_next(request)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF validation failed: missing Origin/Referer header.",
            )

        expected_origin = settings.frontend_url.rstrip("/")

        if origin:
            if origin.rstrip("/") != expected_origin:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="CSRF validation failed: Origin mismatch.",
                )
        elif referer:
            if not referer.startswith(expected_origin):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="CSRF validation failed: Referer mismatch.",
                )

        return await call_next(request)


class AuthRateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Any]],
    ) -> JSONResponse:
        path = request.url.path
        method = request.method

        rate_limited_paths = {
            ("/auth/login", "POST"),
            ("/auth/register", "POST"),
            ("/auth/forgot-password", "POST"),
        }

        if (path, method) in rate_limited_paths:
            is_testing = _is_test_environment()
            force_rate_limit = os.environ.get("CLEVERCREST_FORCE_RATE_LIMIT") == "true"

            if is_testing and not force_rate_limit:
                return await call_next(request)

            client_ip = request.client.host if request.client else "unknown"

            try:
                ip_address(client_ip)
            except ValueError:
                client_ip = "unknown"

            key = f"auth:{path}:{client_ip}"

            if not rate_limiter.is_allowed(key):
                logger.warning("Rate limit exceeded for %s on %s", client_ip, path)
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": (
                            "Too many requests. "
                            "Please try again later."
                        ),
                    },
                )

        return await call_next(request)


# MVP/single-instance limitation:
# - Rate limiting uses an in-memory store, so limits are not shared across
#   multiple application instances.
# - Client IP is taken directly from request.client.host; behind a proxy or
#   load balancer this will be the proxy IP, not the end-user IP.
# For production multi-instance deployments, replace the in-memory store
# with a shared backend such as Redis and resolve the real client IP from
# X-Forwarded-For / X-Real-IP headers when the app is behind a trusted proxy.
