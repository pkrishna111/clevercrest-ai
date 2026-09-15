import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.security import create_access_token
from app.db.session import get_db
from app.main import app
from app.models.organization import Organization, OrganizationStatus
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


class OrganizationApiTests(unittest.TestCase):
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
            get_db: override_get_db,
        }
        self.client.cookies.clear()

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def _clear_test_data(self) -> None:
        self.db.execute(text("DELETE FROM email_verification_tokens"))
        self.db.execute(text("DELETE FROM password_reset_tokens"))
        self.db.execute(text("DELETE FROM organization_invitations"))
        self.db.execute(text("DELETE FROM organization_memberships"))
        self.db.execute(text("DELETE FROM users"))
        self.db.execute(text("DELETE FROM organizations"))
        self.db.commit()

    def _create_user(
        self,
        email: str,
        user_status: UserStatus = UserStatus.ACTIVE,
    ) -> User:
        user = User(
            email=email,
            password_hash="test-password-hash",
            first_name="Test",
            last_name="User",
            is_email_verified=True,
            status=user_status,
        )
        self.db.add(user)
        self.db.flush()
        return user

    def _create_organization(
        self,
        name: str,
        organization_status: OrganizationStatus = OrganizationStatus.ACTIVE,
        settings_value: dict | None = None,
    ) -> Organization:
        organization = Organization(
            name=name,
            slug=name.lower().replace(" ", "-"),
            description="Organization description",
            logo_url="logo.png",
            settings=settings_value or {"private": "not-public"},
            status=organization_status,
        )
        self.db.add(organization)
        self.db.flush()
        return organization

    def _create_membership(
        self,
        user: User,
        organization: Organization,
        membership_status: OrganizationMembershipStatus = OrganizationMembershipStatus.ACTIVE,
        role: OrganizationMembershipRole = OrganizationMembershipRole.MEMBER,
    ) -> OrganizationMembership:
        membership = OrganizationMembership(
            user_id=user.id,
            organization_id=organization.id,
            status=membership_status,
            role=role,
        )
        self.db.add(membership)
        self.db.flush()
        return membership

    def _authenticate(self, user: User) -> None:
        self.client.cookies.clear()
        self.client.cookies.set(
            settings.auth_cookie_name,
            create_access_token(user.id),
        )

    def test_active_member_can_retrieve_organization_profile(self) -> None:
        user = self._create_user("owner@example.com")
        organization = self._create_organization(
            "Profile Org",
            settings_value={"private": "must-not-be-exposed"},
        )
        self._create_membership(
            user,
            organization,
            role=OrganizationMembershipRole.OWNER,
        )
        self.db.commit()
        self._authenticate(user)

        response = self.client.get(f"/organizations/{organization.id}")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(
            set(body),
            {
                "id",
                "name",
                "slug",
                "description",
                "logo_url",
                "status",
                "created_at",
                "updated_at",
            },
        )
        self.assertEqual(body["id"], str(organization.id))
        self.assertEqual(body["name"], organization.name)
        self.assertEqual(body["slug"], organization.slug)
        self.assertEqual(body["description"], organization.description)
        self.assertEqual(body["logo_url"], organization.logo_url)
        self.assertEqual(body["status"], organization.status.value)
        self.assertEqual(body["created_at"], organization.created_at.isoformat())
        self.assertEqual(body["updated_at"], organization.updated_at.isoformat())
        self.assertNotIn("settings", body)
        self.assertNotIn("role", body)

    def test_unauthenticated_user_cannot_retrieve_organization(self) -> None:
        organization = self._create_organization("Unauthenticated Org")
        self.db.commit()

        response = self.client.get(f"/organizations/{organization.id}")

        self.assertEqual(response.status_code, 401)

    def test_non_member_cannot_retrieve_organization(self) -> None:
        user = self._create_user("member@example.com")
        user_organization = self._create_organization("Member Org")
        other_organization = self._create_organization("Other Org")
        self._create_membership(user, user_organization)
        self.db.commit()
        self._authenticate(user)

        response = self.client.get(f"/organizations/{other_organization.id}")

        self.assertEqual(response.status_code, 403)

    def test_suspended_membership_cannot_retrieve_organization(self) -> None:
        user = self._create_user("suspended-member@example.com")
        organization = self._create_organization("Suspended Membership Org")
        self._create_membership(
            user,
            organization,
            membership_status=OrganizationMembershipStatus.SUSPENDED,
        )
        self.db.commit()
        self._authenticate(user)

        response = self.client.get(f"/organizations/{organization.id}")

        self.assertEqual(response.status_code, 403)

    def test_removed_membership_cannot_retrieve_organization(self) -> None:
        user = self._create_user("removed-member@example.com")
        organization = self._create_organization("Removed Membership Org")
        self._create_membership(
            user,
            organization,
            membership_status=OrganizationMembershipStatus.REMOVED,
        )
        self.db.commit()
        self._authenticate(user)

        response = self.client.get(f"/organizations/{organization.id}")

        self.assertEqual(response.status_code, 403)

    def test_inactive_organization_cannot_be_retrieved(self) -> None:
        user = self._create_user("inactive-org-member@example.com")
        organization = self._create_organization(
            "Inactive Org",
            organization_status=OrganizationStatus.INACTIVE,
        )
        self._create_membership(user, organization)
        self.db.commit()
        self._authenticate(user)

        response = self.client.get(f"/organizations/{organization.id}")

        self.assertEqual(response.status_code, 403)

    def test_suspended_organization_cannot_be_retrieved(self) -> None:
        user = self._create_user("suspended-org-member@example.com")
        organization = self._create_organization(
            "Suspended Org",
            organization_status=OrganizationStatus.SUSPENDED,
        )
        self._create_membership(user, organization)
        self.db.commit()
        self._authenticate(user)

        response = self.client.get(f"/organizations/{organization.id}")

        self.assertEqual(response.status_code, 403)

    def test_invalid_organization_uuid_returns_422(self) -> None:
        user = self._create_user("invalid-uuid@example.com")
        organization = self._create_organization("Valid Org")
        self._create_membership(user, organization)
        self.db.commit()
        self._authenticate(user)

        response = self.client.get("/organizations/not-a-valid-uuid")

        self.assertEqual(response.status_code, 422)

    def test_user_cannot_retrieve_another_tenant_organization(self) -> None:
        user_a = self._create_user("user-a@example.com")
        organization_a = self._create_organization("Tenant A")
        self._create_membership(user_a, organization_a)

        user_b = self._create_user("user-b@example.com")
        organization_b = self._create_organization("Tenant B")
        self._create_membership(user_b, organization_b)
        self.db.commit()
        self._authenticate(user_a)

        response = self.client.get(f"/organizations/{organization_b.id}")

        self.assertEqual(response.status_code, 403)


if __name__ == "__main__":
    unittest.main()
