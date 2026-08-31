import unittest
from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.tokens import generate_token, hash_token
from app.models.email_verification_token import EmailVerificationToken
from app.models.organization import Organization
from app.models.organization_membership import OrganizationMembership
from app.models.user import User
from app.services.auth_service import (
    EmailVerificationError,
    register_user,
    verify_email,
)


TEST_DATABASE_NAME = "clevercrest_test"


def create_test_engine():
    database_url = URL.create(
        drivername="postgresql+psycopg",
        username=settings.db_user,
        password=settings.db_password,
        host=settings.db_host,
        port=settings.db_port,
        database=TEST_DATABASE_NAME,
    )

    return create_engine(
        database_url,
        pool_pre_ping=True,
    )


test_engine = create_test_engine()

TestSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


class EmailVerificationServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with test_engine.connect() as connection:
            database_name = connection.execute(
                text("SELECT current_database()")
            ).scalar_one()

        if database_name != TEST_DATABASE_NAME:
            raise RuntimeError(
                f"Safety check failed: expected {TEST_DATABASE_NAME!r}, "
                f"but connected to {database_name!r}."
            )

    def setUp(self) -> None:
        self.db = TestSessionLocal()

        self.db.execute(
            text(
                """
                TRUNCATE TABLE
                    email_verification_tokens,
                    password_reset_tokens,
                    organization_invitations,
                    organization_memberships,
                    users,
                    organizations
                RESTART IDENTITY CASCADE
                """
            )
        )
        self.db.commit()

    def tearDown(self) -> None:
        self.db.rollback()
        self.db.close()

    def test_valid_token_verifies_user_and_marks_token_used(self) -> None:
        registration = register_user(
            self.db,
            email="verify@example.com",
            password="secure-test-password",
            first_name="Verify",
            last_name="Test",
            organization_name="Verification Organization",
        )

        verify_email(
            self.db,
            raw_token=registration.verification_token,
        )

        user = self.db.query(User).filter_by(
            email="verify@example.com"
        ).one()

        token = self.db.query(
            EmailVerificationToken
        ).filter_by(
            user_id=user.id,
        ).one()

        self.assertTrue(user.is_email_verified)
        self.assertIsNotNone(token.used_at)

    def test_invalid_token_is_rejected(self) -> None:
        registration = register_user(
            self.db,
            email="invalid@example.com",
            password="secure-test-password",
            first_name="Invalid",
            last_name="Token",
            organization_name="Invalid Token Organization",
        )

        with self.assertRaises(EmailVerificationError):
            verify_email(
                self.db,
                raw_token="completely-invalid-token",
            )

        user = self.db.query(User).filter_by(
            id=registration.user.id
        ).one()

        self.assertFalse(user.is_email_verified)

    def test_expired_token_is_rejected(self) -> None:
        registration = register_user(
            self.db,
            email="expired@example.com",
            password="secure-test-password",
            first_name="Expired",
            last_name="Token",
            organization_name="Expired Token Organization",
        )

        token = self.db.query(
            EmailVerificationToken
        ).filter_by(
            user_id=registration.user.id,
        ).one()

        token.expires_at = datetime.now(timezone.utc) - timedelta(
            minutes=1
        )

        self.db.commit()

        with self.assertRaises(EmailVerificationError):
            verify_email(
                self.db,
                raw_token=registration.verification_token,
            )

        user = self.db.query(User).filter_by(
            id=registration.user.id
        ).one()

        self.assertFalse(user.is_email_verified)

    def test_used_token_cannot_be_reused(self) -> None:
        registration = register_user(
            self.db,
            email="reuse@example.com",
            password="secure-test-password",
            first_name="Reuse",
            last_name="Token",
            organization_name="Reuse Token Organization",
        )

        verify_email(
            self.db,
            raw_token=registration.verification_token,
        )

        with self.assertRaises(EmailVerificationError):
            verify_email(
                self.db,
                raw_token=registration.verification_token,
            )

    def test_raw_token_is_not_stored_in_database(self) -> None:
        registration = register_user(
            self.db,
            email="security@example.com",
            password="secure-test-password",
            first_name="Security",
            last_name="Test",
            organization_name="Security Organization",
        )

        token = self.db.query(
            EmailVerificationToken
        ).filter_by(
            user_id=registration.user.id,
        ).one()

        self.assertEqual(
            token.token_hash,
            hash_token(registration.verification_token),
        )

        self.assertNotEqual(
            token.token_hash,
            registration.verification_token,
        )

        self.assertEqual(
            len(token.token_hash),
            64,
        )


if __name__ == "__main__":
    unittest.main()