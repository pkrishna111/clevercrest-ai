import unittest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt

from app.core.config import settings
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


class SecurityUtilitiesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.user_id = uuid4()
        self.password = "correct-horse-battery-staple"

    def test_password_hashing_and_verification(self) -> None:
        hashed_password = hash_password(self.password)

        self.assertNotEqual(hashed_password, self.password)
        self.assertTrue(verify_password(self.password, hashed_password))
        self.assertFalse(verify_password("incorrect-password", hashed_password))

    def test_access_token_can_be_created_and_decoded(self) -> None:
        token = create_access_token(self.user_id)
        payload = decode_access_token(token)

        self.assertEqual(payload["sub"], str(self.user_id))
        self.assertNotIn("organization_id", payload)
        self.assertIn("iat", payload)
        self.assertIn("exp", payload)
        self.assertEqual(
            payload["exp"] - payload["iat"],
            settings.jwt_access_token_expire_minutes * 60,
        )

    def test_invalid_and_expired_tokens_are_rejected(self) -> None:
        with self.assertRaises(jwt.InvalidTokenError):
            decode_access_token("not-a-valid-token")

        issued_at = datetime.now(timezone.utc) - timedelta(hours=1)
        expired_token = jwt.encode(
            {
                "sub": str(self.user_id),
                "iat": issued_at,
                "exp": issued_at + timedelta(minutes=1),
            },
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )

        with self.assertRaises(jwt.ExpiredSignatureError):
            decode_access_token(expired_token)


if __name__ == "__main__":
    unittest.main()