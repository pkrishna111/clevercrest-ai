import time
from collections import defaultdict
from threading import Lock

from app.core.config import settings


class RateLimiter:
    def __init__(self) -> None:
        self._requests: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def is_allowed(self, key: str) -> bool:
        if not settings.auth_rate_limit_enabled:
            return True

        if settings.app_env == "test":
            return True

        now = time.monotonic()
        window = settings.auth_rate_limit_window_seconds
        max_requests = settings.auth_rate_limit_requests

        with self._lock:
            timestamps = self._requests[key]
            cutoff = now - window
            self._requests[key] = [t for t in timestamps if t > cutoff]

            if len(self._requests[key]) >= max_requests:
                return False

            self._requests[key].append(now)
            return True

    def reset(self) -> None:
        with self._lock:
            self._requests.clear()


rate_limiter = RateLimiter()
