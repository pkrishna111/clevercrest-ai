import unittest

from app.core.csrf import is_state_changing_method, should_skip_csrf_check


class CsrfMiddlewareUtilityTests(unittest.TestCase):
    def test_is_state_changing_method(self) -> None:
        self.assertTrue(is_state_changing_method("POST"))
        self.assertTrue(is_state_changing_method("PUT"))
        self.assertTrue(is_state_changing_method("PATCH"))
        self.assertTrue(is_state_changing_method("DELETE"))
        self.assertFalse(is_state_changing_method("GET"))
        self.assertFalse(is_state_changing_method("OPTIONS"))
        self.assertFalse(is_state_changing_method("HEAD"))

    def test_should_skip_csrf_check_for_public_auth_paths(self) -> None:
        public_paths = [
            "/auth/register",
            "/auth/login",
            "/auth/forgot-password",
            "/auth/reset-password",
            "/auth/verify-email",
        ]

        for path in public_paths:
            self.assertTrue(
                should_skip_csrf_check(path, "POST"),
                f"Expected skip for {path}",
            )

    def test_should_not_skip_csrf_check_for_protected_paths(self) -> None:
        self.assertFalse(should_skip_csrf_check("/auth/logout", "POST"))
        self.assertFalse(should_skip_csrf_check("/app/documents", "POST"))

    def test_should_not_skip_csrf_check_for_get_requests(self) -> None:
        self.assertFalse(should_skip_csrf_check("/app/documents", "GET"))


if __name__ == "__main__":
    unittest.main()
