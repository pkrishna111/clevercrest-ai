import unittest
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.api.dependencies import (
    get_current_user,
    get_current_organization_membership,
)
from app.models.organization import Organization
from app.models.organization_membership import (
    OrganizationMembership,
    OrganizationMembershipRole,
    OrganizationMembershipStatus,
)
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
    return create_engine(database_url, pool_pre_ping=True)


test_engine = create_test_engine()
TestSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


class DependencyTests(unittest.TestCase):
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

    def _create_user(self, email: str, status=UserStatus.ACTIVE) -> User:
        user = User(
            email=email,
            password_hash="hashed",
            first_name="Test",
            last_name="User",
            is_email_verified=True,
            status=status,
        )
        self.db.add(user)
        self.db.flush()
        return user

    def _create_organization(self, name: str) -> Organization:
        org = Organization(
            name=name,
            slug=name.lower().replace(" ", "-"),
            settings={},
        )
        self.db.add(org)
        self.db.flush()
        return org

    def _create_membership(
        self,
        user: User,
        organization: Organization,
        role=OrganizationMembershipRole.MEMBER,
        status=OrganizationMembershipStatus.ACTIVE,
    ) -> OrganizationMembership:
        membership = OrganizationMembership(
            user_id=user.id,
            organization_id=organization.id,
            role=role,
            status=status,
        )
        self.db.add(membership)
        self.db.flush()
        return membership

    def test_get_current_organization_membership_returns_active_membership(
        self,
    ) -> None:
        user = self._create_user("member@example.com")
        org = self._create_organization("Member Org")
        self._create_membership(user, org)

        self.db.commit()

        membership = get_current_organization_membership(
            organization_id=org.id,
            current_user=user,
            db=self.db,
        )

        self.assertEqual(membership.user_id, user.id)
        self.assertEqual(membership.organization_id, org.id)
        self.assertEqual(membership.status, OrganizationMembershipStatus.ACTIVE)

    def test_get_current_organization_membership_returns_403_for_suspended_membership(
        self,
    ) -> None:
        user = self._create_user("suspended-member@example.com")
        org = self._create_organization("Suspended Member Org")
        self._create_membership(
            user,
            org,
            status=OrganizationMembershipStatus.SUSPENDED,
        )

        self.db.commit()

        with self.assertRaises(HTTPException) as ctx:
            get_current_organization_membership(
                organization_id=org.id,
                current_user=user,
                db=self.db,
            )

        self.assertEqual(ctx.exception.status_code, 403)
        self.assertIn("suspended", ctx.exception.detail.lower())

    def test_get_current_organization_membership_returns_403_for_removed_membership(
        self,
    ) -> None:
        user = self._create_user("removed-member@example.com")
        org = self._create_organization("Removed Member Org")
        self._create_membership(
            user,
            org,
            status=OrganizationMembershipStatus.REMOVED,
        )

        self.db.commit()

        with self.assertRaises(HTTPException) as ctx:
            get_current_organization_membership(
                organization_id=org.id,
                current_user=user,
                db=self.db,
            )

        self.assertEqual(ctx.exception.status_code, 403)
        self.assertIn("removed", ctx.exception.detail.lower())

    def test_get_current_organization_membership_returns_403_when_no_membership(
        self,
    ) -> None:
        user = self._create_user("no-member@example.com")
        org = self._create_organization("No Member Org")

        self.db.commit()

        with self.assertRaises(HTTPException) as ctx:
            get_current_organization_membership(
                organization_id=org.id,
                current_user=user,
                db=self.db,
            )

        self.assertEqual(ctx.exception.status_code, 403)
        self.assertIn("do not have access", ctx.exception.detail.lower())

    def test_get_current_user_rejects_missing_cookie(self) -> None:
        with self.assertRaises(HTTPException) as ctx:
            get_current_user(access_token=None, db=self.db)

        self.assertEqual(ctx.exception.status_code, 401)

    def test_get_current_user_rejects_invalid_token(self) -> None:
        with self.assertRaises(HTTPException) as ctx:
            get_current_user(access_token="not-a-valid-token", db=self.db)

        self.assertEqual(ctx.exception.status_code, 401)

    def test_get_current_user_rejects_nonexistent_user(self) -> None:
        from app.core.security import create_access_token

        fake_token = create_access_token(uuid4())

        with self.assertRaises(HTTPException) as ctx:
            get_current_user(access_token=fake_token, db=self.db)

        self.assertEqual(ctx.exception.status_code, 401)
        self.assertIn("not found", ctx.exception.detail.lower())

    def test_get_current_user_rejects_inactive_user(self) -> None:
        from app.core.security import create_access_token

        user = self._create_user("inactive-dep@example.com", UserStatus.INACTIVE)
        token = create_access_token(user.id)
        self.db.commit()

        with self.assertRaises(HTTPException) as ctx:
            get_current_user(access_token=token, db=self.db)

        self.assertEqual(ctx.exception.status_code, 403)

    def test_get_current_user_rejects_suspended_user(self) -> None:
        from app.core.security import create_access_token

        user = self._create_user("suspended-dep@example.com", UserStatus.SUSPENDED)
        token = create_access_token(user.id)
        self.db.commit()

        with self.assertRaises(HTTPException) as ctx:
            get_current_user(access_token=token, db=self.db)

        self.assertEqual(ctx.exception.status_code, 403)


if __name__ == "__main__":
    unittest.main()
