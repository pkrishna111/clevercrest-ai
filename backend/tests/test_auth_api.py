import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.core.security import decode_access_token
from app.core.tokens import hash_token
from app.main import app
from app.models.email_verification_token import EmailVerificationToken
from app.models.organization import Organization
from app.models.organization_membership import OrganizationMembership
from app.models.user import User, UserStatus


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


def override_get_db():
    db = TestSessionLocal()

    try:
        yield db
    finally:
        db.close()


class AuthApiTests(unittest.TestCase):
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

        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.client.close()

    def setUp(self) -> None:
        self.db = TestSessionLocal()
        self._clear_test_data()
        self.db.close()

        app.dependency_overrides = {
            __import__(
                "app.db.session",
                fromlist=["get_db"],
            ).get_db: override_get_db
        }

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

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

    def test_successful_registration_returns_201_and_sends_email(self) -> None:
        with patch(
            "app.api.routes.auth.email_service.send_verification_email"
        ) as mock_send_email:
            response = self.client.post(
                "/auth/register",
                json={
                    "first_name": "Krishna",
                    "last_name": "Parekh",
                    "email": "Krishna@Example.COM",
                    "password": "secure-test-password",
                    "organization_name": "CleverCrest API Test",
                },
            )

        self.assertEqual(response.status_code, 201)

        self.assertEqual(
            response.json(),
            {
                "message": (
                    "Registration successful. "
                    "Please check your email to verify your account."
                )
            },
        )

        mock_send_email.assert_called_once()

        call_kwargs = mock_send_email.call_args.kwargs

        self.assertEqual(
            call_kwargs["recipient"],
            "krishna@example.com",
        )

        self.assertIn(
            "/verify-email?token=",
            call_kwargs["verification_url"],
        )

        verification_url = call_kwargs["verification_url"]

        self.assertNotIn(
            "None",
            verification_url,
        )

        db = TestSessionLocal()

        try:
            user = db.query(User).filter_by(
                email="krishna@example.com"
            ).one()

            organization = db.query(Organization).filter_by(
                slug="clevercrest-api-test"
            ).one()

            membership = db.query(
                OrganizationMembership
            ).filter_by(
                user_id=user.id,
                organization_id=organization.id,
            ).one()

            verification_token = db.query(
                EmailVerificationToken
            ).filter_by(
                user_id=user.id,
            ).one()

            self.assertEqual(
                membership.role.value,
                "owner",
            )

            self.assertFalse(
                user.is_email_verified,
            )

            self.assertEqual(
                len(verification_token.token_hash),
                64,
            )

        finally:
            db.close()

    def test_successful_login_returns_200_and_sets_auth_cookie(self) -> None:
        with patch(
            "app.api.routes.auth.email_service.send_verification_email"
        ):
            registration_response = self.client.post(
                "/auth/register",
                json={
                    "first_name": "Login",
                    "last_name": "User",
                    "email": "login-api@example.com",
                    "password": "secure-test-password",
                    "organization_name": "Login API Organization",
                },
            )

        self.assertEqual(
            registration_response.status_code,
            201,
        )

        db = TestSessionLocal()

        try:
            user = db.query(User).filter_by(
                email="login-api@example.com"
            ).one()

            user.is_email_verified = True
            db.commit()

            user_id = user.id

        finally:
            db.close()

        response = self.client.post(
            "/auth/login",
            json={
                "email": "LOGIN-API@example.com",
                "password": "secure-test-password",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.json(),
            {
                "message": "Login successful.",
            },
        )

        self.assertIn(
            settings.auth_cookie_name,
            response.cookies,
        )

        access_token = response.cookies.get(
            settings.auth_cookie_name
        )

        self.assertIsNotNone(
            access_token,
        )

        payload = decode_access_token(
            access_token,
        )

        self.assertEqual(
            payload["sub"],
            str(user_id),
        )

        self.assertIn(
            "HttpOnly",
            response.headers["set-cookie"],
        )

        self.assertIn(
            "SameSite=lax",
            response.headers["set-cookie"],
        )

        self.assertIn(
            f"Max-Age={settings.jwt_access_token_expire_minutes * 60}",
            response.headers["set-cookie"],
        )

    def test_login_with_unknown_email_returns_401(self) -> None:
        response = self.client.post(
            "/auth/login",
            json={
                "email": "unknown@example.com",
                "password": "secure-test-password",
            },
        )

        self.assertEqual(
            response.status_code,
            401,
        )

        self.assertEqual(
            response.json()["detail"],
            "Invalid email or password.",
        )

        self.assertNotIn(
            settings.auth_cookie_name,
            response.cookies,
        )

    def test_login_with_wrong_password_returns_401(self) -> None:
        with patch(
            "app.api.routes.auth.email_service.send_verification_email"
        ):
            registration_response = self.client.post(
                "/auth/register",
                json={
                    "first_name": "Wrong",
                    "last_name": "Password",
                    "email": "wrong-password-api@example.com",
                    "password": "secure-test-password",
                    "organization_name": "Wrong Password API Organization",
                },
            )

        self.assertEqual(
            registration_response.status_code,
            201,
        )

        db = TestSessionLocal()

        try:
            user = db.query(User).filter_by(
                email="wrong-password-api@example.com"
            ).one()

            user.is_email_verified = True
            db.commit()

        finally:
            db.close()

        response = self.client.post(
            "/auth/login",
            json={
                "email": "wrong-password-api@example.com",
                "password": "incorrect-password",
            },
        )

        self.assertEqual(
            response.status_code,
            401,
        )

        self.assertEqual(
            response.json()["detail"],
            "Invalid email or password.",
        )

        self.assertNotIn(
            settings.auth_cookie_name,
            response.cookies,
        )

    def test_login_with_unverified_email_returns_403(self) -> None:
        with patch(
            "app.api.routes.auth.email_service.send_verification_email"
        ):
            registration_response = self.client.post(
                "/auth/register",
                json={
                    "first_name": "Unverified",
                    "last_name": "Login",
                    "email": "unverified-login-api@example.com",
                    "password": "secure-test-password",
                    "organization_name": "Unverified Login API Organization",
                },
            )

        self.assertEqual(
            registration_response.status_code,
            201,
        )

        response = self.client.post(
            "/auth/login",
            json={
                "email": "unverified-login-api@example.com",
                "password": "secure-test-password",
            },
        )

        self.assertEqual(
            response.status_code,
            403,
        )

        self.assertEqual(
            response.json()["detail"],
            "Please verify your email before signing in.",
        )

        self.assertNotIn(
            settings.auth_cookie_name,
            response.cookies,
        )

    def test_login_with_inactive_user_returns_403(self) -> None:
        with patch(
            "app.api.routes.auth.email_service.send_verification_email"
        ):
            registration_response = self.client.post(
                "/auth/register",
                json={
                    "first_name": "Inactive",
                    "last_name": "Login",
                    "email": "inactive-login-api@example.com",
                    "password": "secure-test-password",
                    "organization_name": "Inactive Login API Organization",
                },
            )

        self.assertEqual(
            registration_response.status_code,
            201,
        )

        db = TestSessionLocal()

        try:
            user = db.query(User).filter_by(
                email="inactive-login-api@example.com"
            ).one()

            user.is_email_verified = True
            user.status = UserStatus.INACTIVE
            db.commit()

        finally:
            db.close()

        response = self.client.post(
            "/auth/login",
            json={
                "email": "inactive-login-api@example.com",
                "password": "secure-test-password",
            },
        )

        self.assertEqual(
            response.status_code,
            403,
        )

        self.assertEqual(
            response.json()["detail"],
            "This account is inactive.",
        )

        self.assertNotIn(
            settings.auth_cookie_name,
            response.cookies,
        )

    def test_login_with_suspended_user_returns_403(self) -> None:
        with patch(
            "app.api.routes.auth.email_service.send_verification_email"
        ):
            registration_response = self.client.post(
                "/auth/register",
                json={
                    "first_name": "Suspended",
                    "last_name": "Login",
                    "email": "suspended-login-api@example.com",
                    "password": "secure-test-password",
                    "organization_name": "Suspended Login API Organization",
                },
            )

        self.assertEqual(
            registration_response.status_code,
            201,
        )

        db = TestSessionLocal()

        try:
            user = db.query(User).filter_by(
                email="suspended-login-api@example.com"
            ).one()

            user.is_email_verified = True
            user.status = UserStatus.SUSPENDED
            db.commit()

        finally:
            db.close()

        response = self.client.post(
            "/auth/login",
            json={
                "email": "suspended-login-api@example.com",
                "password": "secure-test-password",
            },
        )

        self.assertEqual(
            response.status_code,
            403,
        )

        self.assertEqual(
            response.json()["detail"],
            "This account is suspended.",
        )

        self.assertNotIn(
            settings.auth_cookie_name,
            response.cookies,
        )

    def test_invalid_registration_request_returns_422(self) -> None:
        response = self.client.post(
            "/auth/register",
            json={
                "first_name": "",
                "email": "invalid-email",
                "password": "short",
                "organization_name": "",
            },
        )

        self.assertEqual(
            response.status_code,
            422,
        )

    def test_duplicate_email_returns_409(self) -> None:
        first_response = self.client.post(
            "/auth/register",
            json={
                "first_name": "First",
                "last_name": "User",
                "email": "duplicate@example.com",
                "password": "secure-test-password",
                "organization_name": "First Organization",
            },
        )

        self.assertEqual(
            first_response.status_code,
            201,
        )

        with patch(
            "app.api.routes.auth.email_service.send_verification_email"
        ):
            second_response = self.client.post(
                "/auth/register",
                json={
                    "first_name": "Second",
                    "last_name": "User",
                    "email": "DUPLICATE@example.com",
                    "password": "another-password",
                    "organization_name": "Second Organization",
                },
            )

        self.assertEqual(
            second_response.status_code,
            409,
        )

        self.assertEqual(
            second_response.json()["detail"],
            "An account with this email already exists.",
        )

    def test_email_service_failure_returns_503(self) -> None:
        from app.services.email_service import EmailServiceError

        with patch(
            "app.api.routes.auth.email_service.send_verification_email",
            side_effect=EmailServiceError("SMTP failure"),
        ):
            response = self.client.post(
                "/auth/register",
                json={
                    "first_name": "Email",
                    "last_name": "Failure",
                    "email": "email-failure@example.com",
                    "password": "secure-test-password",
                    "organization_name": "Email Failure Organization",
                },
            )

        self.assertEqual(
            response.status_code,
            503,
        )

        self.assertEqual(
            response.json()["detail"],
            (
                "Your account was created, but the verification email "
                "could not be sent. Please try again later."
            ),
        )

        db = TestSessionLocal()

        try:
            user = db.query(User).filter_by(
                email="email-failure@example.com"
            ).one()

            self.assertFalse(
                user.is_email_verified,
            )

        finally:
            db.close()
    
    def test_valid_verification_token_returns_200_and_verifies_user(self) -> None:
        with patch(
            "app.api.routes.auth.email_service.send_verification_email"
        ) as mock_send_email:
            registration_response = self.client.post(
                "/auth/register",
                json={
                    "first_name": "Verify",
                    "last_name": "User",
                    "email": "verify-api@example.com",
                    "password": "secure-test-password",
                    "organization_name": "Verification API Organization",
                },
            )

        self.assertEqual(registration_response.status_code, 201)
        mock_send_email.assert_called_once()

        verification_url = mock_send_email.call_args.kwargs[
            "verification_url"
        ]

        raw_token = verification_url.split(
            "token=",
            1,
        )[1]

        response = self.client.get(
            "/auth/verify-email",
            params={
                "token": raw_token,
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.json(),
            {
                "message": "Email address verified successfully.",
            },
        )

        db = TestSessionLocal()

        try:
            user = db.query(User).filter_by(
                email="verify-api@example.com"
            ).one()

            verification_token = db.query(
                EmailVerificationToken
            ).filter_by(
                user_id=user.id,
            ).one()

            self.assertTrue(
                user.is_email_verified,
            )

            self.assertIsNotNone(
                verification_token.used_at,
            )

            self.assertEqual(
                verification_token.token_hash,
                hash_token(raw_token),
            )

        finally:
            db.close()

    def test_invalid_verification_token_returns_400(self) -> None:
        response = self.client.get(
            "/auth/verify-email",
            params={
                "token": "invalid-verification-token",
            },
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertEqual(
            response.json()["detail"],
            "Invalid or expired email verification link.",
        )

    def test_used_verification_token_returns_400(self) -> None:
        with patch(
            "app.api.routes.auth.email_service.send_verification_email"
        ) as mock_send_email:
            registration_response = self.client.post(
                "/auth/register",
                json={
                    "first_name": "Used",
                    "last_name": "Token",
                    "email": "used-token@example.com",
                    "password": "secure-test-password",
                    "organization_name": "Used Token Organization",
                },
            )

        self.assertEqual(
            registration_response.status_code,
            201,
        )

        raw_token = mock_send_email.call_args.kwargs[
            "verification_url"
        ].split(
            "token=",
            1,
        )[1]

        first_response = self.client.get(
            "/auth/verify-email",
            params={
                "token": raw_token,
            },
        )

        self.assertEqual(
            first_response.status_code,
            200,
        )

        second_response = self.client.get(
            "/auth/verify-email",
            params={
                "token": raw_token,
            },
        )

        self.assertEqual(
            second_response.status_code,
            400,
        )

        self.assertEqual(
            second_response.json()["detail"],
            "Invalid or expired email verification link.",
        )


if __name__ == "__main__":
    unittest.main()