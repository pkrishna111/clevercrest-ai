import unittest
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.email_verification_token import EmailVerificationToken
from app.models.password_reset_token import PasswordResetToken
from app.models.organization import Organization
from app.models.organization_membership import OrganizationMembership
from app.models.user import User, UserStatus
from app.services.auth_service import (
    EmailAlreadyRegisteredError,
    EmailNotVerifiedError,
    InactiveUserError,
    InvalidCredentialsError,
    PasswordResetError,
    SuspendedUserError,
    login_user,
    register_user,
    request_password_reset,
    reset_password,
)
from app.core.security import (
    decode_access_token,
    verify_password,
)
from app.core.tokens import hash_token

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


class AuthServiceTests(unittest.TestCase):
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

        self._clear_test_data()

    def tearDown(self) -> None:
        self.db.rollback()
        self.db.close()

    def _clear_test_data(self) -> None:
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

    def test_successful_registration_creates_expected_records(self) -> None:
        result = register_user(
            self.db,
            email="Krishna@Example.COM",
            password="secure-test-password",
            first_name="Krishna",
            last_name="Parekh",
            organization_name="CleverCrest Test Organization",
        )

        self.assertIsInstance(result.user.id, UUID)
        self.assertIsInstance(result.organization.id, UUID)

        self.assertEqual(
            result.user.email,
            "krishna@example.com",
        )

        self.assertEqual(
            result.user.first_name,
            "Krishna",
        )

        self.assertEqual(
            result.user.last_name,
            "Parekh",
        )

        self.assertFalse(
            result.user.is_email_verified,
        )

        self.assertNotEqual(
            result.user.password_hash,
            "secure-test-password",
        )

        self.assertEqual(
            result.organization.name,
            "CleverCrest Test Organization",
        )

        self.assertEqual(
            result.organization.slug,
            "clevercrest-test-organization",
        )

        membership = self.db.query(
            OrganizationMembership
        ).filter_by(
            user_id=result.user.id,
            organization_id=result.organization.id,
        ).one()

        self.assertEqual(
            membership.role.value,
            "owner",
        )

        self.assertEqual(
            membership.status.value,
            "active",
        )

        verification_token = self.db.query(
            EmailVerificationToken
        ).filter_by(
            user_id=result.user.id,
        ).one()

        self.assertEqual(
            len(verification_token.token_hash),
            64,
        )

        self.assertNotEqual(
            verification_token.token_hash,
            result.verification_token,
        )

        self.assertIsNotNone(
            verification_token.expires_at,
        )

    def test_duplicate_email_is_rejected(self) -> None:
        register_user(
            self.db,
            email="duplicate@example.com",
            password="secure-test-password",
            first_name="First",
            last_name="User",
            organization_name="First Organization",
        )

        with self.assertRaises(EmailAlreadyRegisteredError):
            register_user(
                self.db,
                email="DUPLICATE@example.com",
                password="another-password",
                first_name="Second",
                last_name="User",
                organization_name="Second Organization",
            )

        self.assertEqual(
            self.db.query(User).count(),
            1,
        )

        self.assertEqual(
            self.db.query(Organization).count(),
            1,
        )

    def test_organization_slug_collision_is_handled(self) -> None:
        first = register_user(
            self.db,
            email="first@example.com",
            password="secure-test-password",
            first_name="First",
            last_name="User",
            organization_name="Acme Corporation",
        )

        second = register_user(
            self.db,
            email="second@example.com",
            password="secure-test-password",
            first_name="Second",
            last_name="User",
            organization_name="Acme Corporation",
        )

        self.assertEqual(
            first.organization.slug,
            "acme-corporation",
        )

        self.assertEqual(
            second.organization.slug,
            "acme-corporation-2",
        )

    def test_verification_token_expiry_is_configured_correctly(self) -> None:
        result = register_user(
            self.db,
            email="expiry@example.com",
            password="secure-test-password",
            first_name="Expiry",
            last_name="Test",
            organization_name="Expiry Organization",
        )

        token = self.db.query(
            EmailVerificationToken
        ).filter_by(
            user_id=result.user.id,
        ).one()

        expiry_seconds = (
            token.expires_at - token.created_at
        ).total_seconds()

        expected_seconds = (
            settings.email_verification_token_expire_hours * 60 * 60
        )

        self.assertAlmostEqual(
            expiry_seconds,
            expected_seconds,
            delta=5,
        )
    
    
    def test_successful_login_returns_access_token_and_updates_last_login(
        self,
    ) -> None:
        registration = register_user(
            self.db,
            email="LoginUser@Example.COM",
            password="secure-test-password",
            first_name="Login",
            last_name="User",
            organization_name="Login Organization",
        )

        registration.user.is_email_verified = True
        self.db.commit()

        result = login_user(
            self.db,
            email="LOGINUSER@example.com",
            password="secure-test-password",
        )

        self.assertEqual(
            result.user.id,
            registration.user.id,
        )

        self.assertIsInstance(
            result.access_token,
            str,
        )

        self.assertTrue(
            len(result.access_token) > 0,
        )

        payload = decode_access_token(
            result.access_token,
        )

        self.assertEqual(
            payload["sub"],
            str(registration.user.id),
        )

        self.assertIsNotNone(
            result.user.last_login_at,
        )

        db_user = self.db.get(
            User,
            registration.user.id,
        )

        self.assertIsNotNone(
            db_user,
        )

        self.assertIsNotNone(
            db_user.last_login_at,
        )

    def test_login_normalizes_email(self) -> None:
        registration = register_user(
            self.db,
            email="Normalize@Example.COM",
            password="secure-test-password",
            first_name="Normalize",
            last_name="User",
            organization_name="Normalize Organization",
        )

        registration.user.is_email_verified = True
        self.db.commit()

        result = login_user(
            self.db,
            email="  NORMALIZE@example.com  ",
            password="secure-test-password",
        )

        self.assertEqual(
            result.user.id,
            registration.user.id,
        )

    def test_login_rejects_unknown_email(self) -> None:
        with self.assertRaises(InvalidCredentialsError) as context:
            login_user(
                self.db,
                email="unknown@example.com",
                password="secure-test-password",
            )

        self.assertEqual(
            str(context.exception),
            "Invalid email or password.",
        )

    def test_login_rejects_wrong_password(self) -> None:
        register_user(
            self.db,
            email="wrong-password@example.com",
            password="secure-test-password",
            first_name="Wrong",
            last_name="Password",
            organization_name="Wrong Password Organization",
        )

        user = self.db.query(User).filter_by(
            email="wrong-password@example.com"
        ).one()

        user.is_email_verified = True
        self.db.commit()

        with self.assertRaises(InvalidCredentialsError) as context:
            login_user(
                self.db,
                email="wrong-password@example.com",
                password="incorrect-password",
            )

        self.assertEqual(
            str(context.exception),
            "Invalid email or password.",
        )

    def test_login_rejects_unverified_email(self) -> None:
        register_user(
            self.db,
            email="unverified@example.com",
            password="secure-test-password",
            first_name="Unverified",
            last_name="User",
            organization_name="Unverified Organization",
        )

        with self.assertRaises(EmailNotVerifiedError) as context:
            login_user(
                self.db,
                email="unverified@example.com",
                password="secure-test-password",
            )

        self.assertEqual(
            str(context.exception),
            "Please verify your email before signing in.",
        )

    def test_login_rejects_inactive_user(self) -> None:
        registration = register_user(
            self.db,
            email="inactive@example.com",
            password="secure-test-password",
            first_name="Inactive",
            last_name="User",
            organization_name="Inactive Organization",
        )

        registration.user.is_email_verified = True
        registration.user.status = UserStatus.INACTIVE
        self.db.commit()

        with self.assertRaises(InactiveUserError) as context:
            login_user(
                self.db,
                email="inactive@example.com",
                password="secure-test-password",
            )

        self.assertEqual(
            str(context.exception),
            "This account is inactive.",
        )

    def test_login_rejects_suspended_user(self) -> None:
        registration = register_user(
            self.db,
            email="suspended@example.com",
            password="secure-test-password",
            first_name="Suspended",
            last_name="User",
            organization_name="Suspended Organization",
        )

        registration.user.is_email_verified = True
        registration.user.status = UserStatus.SUSPENDED
        self.db.commit()

        with self.assertRaises(SuspendedUserError) as context:
            login_user(
                self.db,
                email="suspended@example.com",
                password="secure-test-password",
            )

        self.assertEqual(
            str(context.exception),
            "This account is suspended.",
        )

    def test_password_reset_request_creates_token(self) -> None:
        registration = register_user(
            self.db,
            email="reset@example.com",
            password="old-password",
            first_name="Reset",
            last_name="User",
            organization_name="Reset Organization",
        )

        result = request_password_reset(
            self.db,
            email="RESET@example.com",
        )

        self.assertIsNotNone(result)
        self.assertEqual(
            result.user.id,
            registration.user.id,
        )

        token = self.db.query(
            PasswordResetToken
        ).filter_by(
            user_id=registration.user.id,
        ).one()

        self.assertEqual(
            token.token_hash,
            hash_token(result.reset_token),
        )

        self.assertNotEqual(
            token.token_hash,
            result.reset_token,
        )

        self.assertIsNone(
            token.used_at,
        )

    def test_password_reset_request_unknown_email_returns_none(self) -> None:
        result = request_password_reset(
            self.db,
            email="unknown@example.com",
        )

        self.assertIsNone(result)

        self.assertEqual(
            self.db.query(PasswordResetToken).count(),
            0,
        )
    
    def test_password_reset_request_normalizes_email(self) -> None:
        registration = register_user(
            self.db,
            email="NormalizeReset@Example.COM",
            password="old-password",
            first_name="Normalize",
            last_name="Reset",
            organization_name="Normalize Reset Organization",
        )

        result = request_password_reset(
            self.db,
            email="  NORMALIZERESET@example.com  ",
        )

        self.assertIsNotNone(result)
        self.assertEqual(
            result.user.id,
            registration.user.id,
        )

    def test_password_reset_token_expiry_is_configured_correctly(
        self,
    ) -> None:
        registration = register_user(
            self.db,
            email="reset-expiry@example.com",
            password="old-password",
            first_name="Reset",
            last_name="Expiry",
            organization_name="Reset Expiry Organization",
        )

        request_password_reset(
            self.db,
            email=registration.user.email,
        )

        token = self.db.query(
            PasswordResetToken
        ).filter_by(
            user_id=registration.user.id,
        ).one()

        expiry_seconds = (
            token.expires_at - token.created_at
        ).total_seconds()

        expected_seconds = (
            settings.password_reset_token_expire_minutes * 60
        )

        self.assertAlmostEqual(
            expiry_seconds,
            expected_seconds,
            delta=5,
        )

    def test_successful_password_reset_changes_password_and_uses_token(
        self,
    ) -> None:
        registration = register_user(
            self.db,
            email="successful-reset@example.com",
            password="old-password",
            first_name="Successful",
            last_name="Reset",
            organization_name="Successful Reset Organization",
        )

        result = request_password_reset(
            self.db,
            email=registration.user.email,
        )

        self.assertIsNotNone(result)

        reset_password(
            self.db,
            raw_token=result.reset_token,
            new_password="new-password",
        )

        db_user = self.db.get(
            User,
            registration.user.id,
        )

        self.assertIsNotNone(db_user)

        self.assertTrue(
            verify_password(
                "new-password",
                db_user.password_hash,
            )
        )

        self.assertFalse(
            verify_password(
                "old-password",
                db_user.password_hash,
            )
        )

        token = self.db.query(
            PasswordResetToken
        ).filter_by(
            user_id=registration.user.id,
        ).one()

        self.assertIsNotNone(
            token.used_at,
        )
    def test_used_password_reset_token_is_rejected(self) -> None:
        registration = register_user(
            self.db,
            email="used-reset@example.com",
            password="old-password",
            first_name="Used",
            last_name="Reset",
            organization_name="Used Reset Organization",
        )

        result = request_password_reset(
            self.db,
            email=registration.user.email,
        )

        self.assertIsNotNone(result)

        reset_password(
            self.db,
            raw_token=result.reset_token,
            new_password="new-password",
        )

        with self.assertRaises(PasswordResetError) as context:
            reset_password(
                self.db,
                raw_token=result.reset_token,
                new_password="another-password",
            )

        self.assertEqual(
            str(context.exception),
            "Invalid or expired password reset link.",
        )

    def test_invalid_password_reset_token_is_rejected(self) -> None:
        with self.assertRaises(PasswordResetError) as context:
            reset_password(
                self.db,
                raw_token="invalid-reset-token",
                new_password="new-password",
            )

        self.assertEqual(
            str(context.exception),
            "Invalid or expired password reset link.",
        )

    def test_expired_password_reset_token_is_rejected(self) -> None:
        registration = register_user(
            self.db,
            email="expired-reset@example.com",
            password="old-password",
            first_name="Expired",
            last_name="Reset",
            organization_name="Expired Reset Organization",
        )

        result = request_password_reset(
            self.db,
            email=registration.user.email,
        )

        self.assertIsNotNone(result)

        token = self.db.query(
            PasswordResetToken
        ).filter_by(
            user_id=registration.user.id,
        ).one()

        token.expires_at = datetime.now(timezone.utc) - timedelta(
            minutes=1,
        )

        self.db.commit()

        with self.assertRaises(PasswordResetError) as context:
            reset_password(
                self.db,
                raw_token=result.reset_token,
                new_password="new-password",
            )

        self.assertEqual(
            str(context.exception),
            "Invalid or expired password reset link.",
        )


if __name__ == "__main__":
    unittest.main()