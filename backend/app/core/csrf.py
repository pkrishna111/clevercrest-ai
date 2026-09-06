PUBLIC_AUTH_PATHS = {
    "/auth/register",
    "/auth/login",
    "/auth/forgot-password",
    "/auth/reset-password",
    "/auth/verify-email",
}


def is_state_changing_method(method: str) -> bool:
    return method in ("POST", "PUT", "PATCH", "DELETE")


def should_skip_csrf_check(path: str, method: str) -> bool:
    return path in PUBLIC_AUTH_PATHS and is_state_changing_method(method)
