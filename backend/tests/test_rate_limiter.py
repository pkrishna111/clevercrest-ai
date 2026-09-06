import os
import time
import unittest
from unittest.mock import patch

from app.core.config import Settings
from app.core.rate_limiter import RateLimiter


class RateLimiterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.limiter = RateLimiter()

    @patch("app.core.rate_limiter.settings")
    def test_allows_requests_within_limit(self, mock_settings) -> None:
        mock_settings.auth_rate_limit_enabled = True
        mock_settings.app_env = "development"
        mock_settings.auth_rate_limit_requests = 3
        mock_settings.auth_rate_limit_window_seconds = 60

        key = "test:allows:within:limit"
        for _ in range(3):
            self.assertTrue(self.limiter.is_allowed(key))

    @patch("app.core.rate_limiter.settings")
    def test_blocks_requests_exceeding_limit(self, mock_settings) -> None:
        mock_settings.auth_rate_limit_enabled = True
        mock_settings.app_env = "development"
        mock_settings.auth_rate_limit_requests = 2
        mock_settings.auth_rate_limit_window_seconds = 60

        key = "test:blocks:exceeding:limit"
        self.assertTrue(self.limiter.is_allowed(key))
        self.assertTrue(self.limiter.is_allowed(key))
        self.assertFalse(self.limiter.is_allowed(key))

    @patch("app.core.rate_limiter.settings")
    def test_allows_requests_after_window_expires(self, mock_settings) -> None:
        mock_settings.auth_rate_limit_enabled = True
        mock_settings.app_env = "development"
        mock_settings.auth_rate_limit_requests = 2
        mock_settings.auth_rate_limit_window_seconds = 1

        key = "test:allows:after:window"

        with patch("time.monotonic", side_effect=[1000.0, 1000.0, 1000.0, 1002.0]):
            self.assertTrue(self.limiter.is_allowed(key))
            self.assertTrue(self.limiter.is_allowed(key))
            self.assertFalse(self.limiter.is_allowed(key))

        with patch("time.monotonic", return_value=1003.0):
            self.assertTrue(self.limiter.is_allowed(key))

    @patch("app.core.rate_limiter.settings")
    def test_disabled_when_rate_limiting_turned_off(self, mock_settings) -> None:
        mock_settings.auth_rate_limit_enabled = False
        mock_settings.app_env = "production"

        key = "test:disabled:when:turned:off"
        for _ in range(100):
            self.assertTrue(self.limiter.is_allowed(key))

    @patch("app.core.rate_limiter.settings")
    def test_disabled_in_test_environment(self, mock_settings) -> None:
        mock_settings.auth_rate_limit_enabled = True
        mock_settings.app_env = "test"
        mock_settings.auth_rate_limit_requests = 1
        mock_settings.auth_rate_limit_window_seconds = 60

        key = "test:disabled:in:test:env"
        for _ in range(10):
            self.assertTrue(self.limiter.is_allowed(key))

    @patch("app.core.rate_limiter.settings")
    def test_different_keys_have_independent_counters(self, mock_settings) -> None:
        mock_settings.auth_rate_limit_enabled = True
        mock_settings.app_env = "development"
        mock_settings.auth_rate_limit_requests = 1
        mock_settings.auth_rate_limit_window_seconds = 60

        self.assertTrue(self.limiter.is_allowed("key:A"))
        self.assertFalse(self.limiter.is_allowed("key:A"))
        self.assertTrue(self.limiter.is_allowed("key:B"))


if __name__ == "__main__":
    unittest.main()
