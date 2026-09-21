import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.core.security import create_access_token
from app.db.session import get_db
from app.main import app
from app.models import (
    Organization,
    OrganizationMembership,
    OrganizationMembershipRole,
    OrganizationMembershipStatus,
    OrganizationRole,
    Permission,
    RolePermission,
)
from app.models.organization import OrganizationStatus
from app.models.user import User, UserStatus
from app.services.auth_service import register_user


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


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


EXPECTED_PERMISSIONS = sorted([
    "organization.view",
    "organization.manage",
    "members.view",
    "members.manage",
    "roles.view",
    "roles.manage",
    "documents.view",
    "documents.upload",
    "documents.delete",
    "documents.review",
    "documents.approve",
    "documents.reject",
    "collections.view",
    "collections.manage",
    "audit_logs.view",
    "settings.view",
    "settings.manage",
])

OWNER_PERMISSIONS = sorted(EXPECTED_PERMISSIONS)
ADMIN_PERMISSIONS = sorted(EXPECTED_PERMISSIONS)
MEMBER_PERMISSIONS = sorted([
    "organization.view",
    "members.view",
    "roles.view",
    "documents.view",
    "collections.view",
    "settings.view",
])
VIEWER_PERMISSIONS = sorted([
    "organization.view",
    "documents.view",
    "collections.view",
])

SYSTEM_ROLES = ["owner", "admin", "member", "viewer"]


class RbacStep2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.client.close()

    def setUp(self) -> None:
        self.db = TestSessionLocal()
        self._clear_test_data()

        app.dependency_overrides = {
            get_db: override_get_db,
        }
        self.client.cookies.clear()

    def tearDown(self) -> None:
        app.dependency_overrides.clear()
        try:
            self.db.rollback()
        except Exception:
            pass
        try:
            self.db.close()
        except Exception:
            pass

    def _clear_test_data(self) -> None:
        self.db.execute(
            text(
                """
                TRUNCATE TABLE
                    role_permissions,
                    organization_roles,
                    permissions,
                    organization_memberships,
                    organizations,
                    users
                RESTART IDENTITY CASCADE
                """
            )
        )
        self.db.commit()

    def _create_user(self, email: str) -> User:
        user = User(
            email=email,
            password_hash="test-password-hash",
            first_name="Test",
            last_name="User",
            is_email_verified=True,
            status=UserStatus.ACTIVE,
        )
        self.db.add(user)
        self.db.flush()
        return user

    def _create_organization(self, name: str) -> Organization:
        organization = Organization(
            name=name,
            slug=name.lower().replace(" ", "-"),
            description="Organization description",
            logo_url="logo.png",
            settings={},
            status=OrganizationStatus.ACTIVE,
        )
        self.db.add(organization)
        self.db.flush()
        return organization

    def _get_role_permissions(self, role: OrganizationRole) -> list[str]:
        return [
            p.name
            for p in self.db.query(Permission)
            .join(RolePermission, Permission.id == RolePermission.permission_id)
            .filter(RolePermission.role_id == role.id)
            .order_by(Permission.name)
            .all()
        ]

    def test_expected_17_permissions_exist(self) -> None:
        self.assertEqual(len(EXPECTED_PERMISSIONS), 17)

    def test_permission_names_are_globally_unique(self) -> None:
        self.assertEqual(len(set(EXPECTED_PERMISSIONS)), len(EXPECTED_PERMISSIONS))

    def test_owner_receives_all_17_permissions(self) -> None:
        org = self._create_organization("Test Org")
        for role_name in SYSTEM_ROLES:
            role = OrganizationRole(
                organization_id=org.id,
                name=role_name,
                is_system=True,
            )
            self.db.add(role)
            self.db.flush()
            for perm_name in OWNER_PERMISSIONS:
                perm = self.db.query(Permission).filter_by(name=perm_name).one_or_none()
                if perm is None:
                    perm = Permission(name=perm_name)
                    self.db.add(perm)
                    self.db.flush()
                rp = RolePermission(role_id=role.id, permission_id=perm.id)
                self.db.add(rp)
        self.db.commit()
        owner_role = self.db.query(OrganizationRole).filter_by(
            organization_id=org.id, name="owner"
        ).one()
        permissions = self._get_role_permissions(owner_role)
        self.assertEqual(sorted(permissions), OWNER_PERMISSIONS)

    def test_admin_receives_all_17_permissions(self) -> None:
        org = self._create_organization("Test Org")
        for role_name in SYSTEM_ROLES:
            role = OrganizationRole(
                organization_id=org.id,
                name=role_name,
                is_system=True,
            )
            self.db.add(role)
            self.db.flush()
            perms_for_role = ADMIN_PERMISSIONS if role_name == "admin" else []
            for perm_name in perms_for_role:
                perm = self.db.query(Permission).filter_by(name=perm_name).one_or_none()
                if perm is None:
                    perm = Permission(name=perm_name)
                    self.db.add(perm)
                    self.db.flush()
                rp = RolePermission(role_id=role.id, permission_id=perm.id)
                self.db.add(rp)
        self.db.commit()
        admin_role = self.db.query(OrganizationRole).filter_by(
            organization_id=org.id, name="admin"
        ).one()
        permissions = self._get_role_permissions(admin_role)
        self.assertEqual(sorted(permissions), ADMIN_PERMISSIONS)

    def test_member_receives_exact_permissions(self) -> None:
        org = self._create_organization("Test Org")
        for role_name in SYSTEM_ROLES:
            role = OrganizationRole(
                organization_id=org.id,
                name=role_name,
                is_system=True,
            )
            self.db.add(role)
            self.db.flush()
            perms_for_role = MEMBER_PERMISSIONS if role_name == "member" else []
            for perm_name in perms_for_role:
                perm = self.db.query(Permission).filter_by(name=perm_name).one_or_none()
                if perm is None:
                    perm = Permission(name=perm_name)
                    self.db.add(perm)
                    self.db.flush()
                rp = RolePermission(role_id=role.id, permission_id=perm.id)
                self.db.add(rp)
        self.db.commit()
        member_role = self.db.query(OrganizationRole).filter_by(
            organization_id=org.id, name="member"
        ).one()
        permissions = self._get_role_permissions(member_role)
        self.assertEqual(sorted(permissions), MEMBER_PERMISSIONS)

    def test_viewer_receives_exact_permissions(self) -> None:
        org = self._create_organization("Test Org")
        for role_name in SYSTEM_ROLES:
            role = OrganizationRole(
                organization_id=org.id,
                name=role_name,
                is_system=True,
            )
            self.db.add(role)
            self.db.flush()
            perms_for_role = VIEWER_PERMISSIONS if role_name == "viewer" else []
            for perm_name in perms_for_role:
                perm = self.db.query(Permission).filter_by(name=perm_name).one_or_none()
                if perm is None:
                    perm = Permission(name=perm_name)
                    self.db.add(perm)
                    self.db.flush()
                rp = RolePermission(role_id=role.id, permission_id=perm.id)
                self.db.add(rp)
        self.db.commit()
        viewer_role = self.db.query(OrganizationRole).filter_by(
            organization_id=org.id, name="viewer"
        ).one()
        permissions = self._get_role_permissions(viewer_role)
        self.assertEqual(sorted(permissions), VIEWER_PERMISSIONS)

    def test_no_duplicate_role_permission_rows(self) -> None:
        org = self._create_organization("Test Org")
        role = OrganizationRole(
            organization_id=org.id,
            name="owner",
            is_system=True,
        )
        perm = Permission(name="organization.view")
        self.db.add(role)
        self.db.add(perm)
        self.db.flush()
        rp1 = RolePermission(role_id=role.id, permission_id=perm.id)
        self.db.add(rp1)
        self.db.commit()
        rp2 = RolePermission(role_id=role.id, permission_id=perm.id)
        self.db.add(rp2)
        with self.assertRaises(Exception) as ctx:
            self.db.commit()
        self.db.rollback()

    def test_existing_organizations_have_expected_mappings(self) -> None:
        org = self._create_organization("Test Org")
        for role_name in SYSTEM_ROLES:
            role = OrganizationRole(
                organization_id=org.id,
                name=role_name,
                is_system=True,
            )
            self.db.add(role)
            self.db.flush()
        for perm_name in EXPECTED_PERMISSIONS:
            perm = Permission(name=perm_name)
            self.db.add(perm)
        self.db.flush()
        for role_name in SYSTEM_ROLES:
            role = self.db.query(OrganizationRole).filter_by(
                organization_id=org.id, name=role_name,
            ).one()
            if role_name == "owner":
                expected = OWNER_PERMISSIONS
            elif role_name == "admin":
                expected = ADMIN_PERMISSIONS
            elif role_name == "member":
                expected = MEMBER_PERMISSIONS
            else:
                expected = VIEWER_PERMISSIONS
            for perm_name in expected:
                perm = self.db.query(Permission).filter_by(name=perm_name).one()
                rp = RolePermission(role_id=role.id, permission_id=perm.id)
                self.db.add(rp)
        self.db.commit()
        for role_name in SYSTEM_ROLES:
            role = self.db.query(OrganizationRole).filter_by(
                organization_id=org.id, name=role_name,
            ).one()
            permissions = self._get_role_permissions(role)
            if role_name in ("owner", "admin"):
                self.assertEqual(sorted(permissions), OWNER_PERMISSIONS)
            elif role_name == "member":
                self.assertEqual(sorted(permissions), MEMBER_PERMISSIONS)
            else:
                self.assertEqual(sorted(permissions), VIEWER_PERMISSIONS)

    def test_registration_creates_all_four_system_roles(self) -> None:
        result = register_user(
            self.db,
            email="step2@example.com",
            password="secure-test-password",
            first_name="Step",
            last_name="Two",
            organization_name="Step 2 Org",
        )
        self.db.refresh(result.organization)
        roles = (
            self.db.query(OrganizationRole)
            .filter_by(organization_id=result.organization.id)
            .order_by(OrganizationRole.name)
            .all()
        )
        self.assertEqual(len(roles), 4)
        role_names = {r.name for r in roles}
        self.assertEqual(role_names, set(SYSTEM_ROLES))
        self.assertTrue(all(r.is_system for r in roles))

    def test_registration_creates_correct_permission_mappings(self) -> None:
        result = register_user(
            self.db,
            email="perm-mappings@example.com",
            password="secure-test-password",
            first_name="Perm",
            last_name="Mappings",
            organization_name="Perm Mappings Org",
        )
        self.db.refresh(result.organization)
        for role_name, expected_permissions in [
            ("owner", OWNER_PERMISSIONS),
            ("admin", ADMIN_PERMISSIONS),
            ("member", MEMBER_PERMISSIONS),
            ("viewer", VIEWER_PERMISSIONS),
        ]:
            role = self.db.query(OrganizationRole).filter_by(
                organization_id=result.organization.id,
                name=role_name,
            ).one()
            permissions = self._get_role_permissions(role)
            self.assertEqual(sorted(permissions), expected_permissions)

    def test_registration_user_gets_owner_role(self) -> None:
        result = register_user(
            self.db,
            email="owner-role@example.com",
            password="secure-test-password",
            first_name="Owner",
            last_name="Role",
            organization_name="Owner Role Org",
        )
        self.db.refresh(result.user)
        membership = (
            self.db.query(OrganizationMembership)
            .filter_by(
                user_id=result.user.id,
                organization_id=result.organization.id,
            )
            .one()
        )
        self.assertIsNotNone(membership.organization_role_id)
        self.assertEqual(membership.role, OrganizationMembershipRole.OWNER)
        owner_role = self.db.query(OrganizationRole).filter_by(
            organization_id=result.organization.id,
            name="owner",
        ).one()
        self.assertEqual(membership.organization_role_id, owner_role.id)

    def test_legacy_membership_role_unchanged(self) -> None:
        result = register_user(
            self.db,
            email="legacy-role@example.com",
            password="secure-test-password",
            first_name="Legacy",
            last_name="Role",
            organization_name="Legacy Role Org",
        )
        self.db.refresh(result.user)
        membership = (
            self.db.query(OrganizationMembership)
            .filter_by(
                user_id=result.user.id,
                organization_id=result.organization.id,
            )
            .one()
        )
        self.assertEqual(membership.role, OrganizationMembershipRole.OWNER)

    def test_organization_get_and_patch_still_work(self) -> None:
        user = self._create_user("org-get-patch@example.com")
        organization = self._create_organization("Existing Org")
        self.db.flush()
        org_role = OrganizationRole(
            organization_id=organization.id,
            name="owner",
            is_system=True,
        )
        self.db.add(org_role)
        self.db.flush()
        membership = OrganizationMembership(
            user_id=user.id,
            organization_id=organization.id,
            role=OrganizationMembershipRole.OWNER,
            status=OrganizationMembershipStatus.ACTIVE,
            organization_role_id=org_role.id,
        )
        self.db.add(membership)
        self.db.commit()
        token = create_access_token(user.id)
        self.client.cookies.clear()
        self.client.cookies.set(settings.auth_cookie_name, token)
        get_response = self.client.get(f"/organizations/{organization.id}")
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.json()["name"], "Existing Org")
        patch_response = self.client.patch(
            f"/organizations/{organization.id}",
            json={"name": "Updated Org"},
        )
        self.assertEqual(patch_response.status_code, 200)
        self.assertEqual(patch_response.json()["name"], "Updated Org")


if __name__ == "__main__":
    unittest.main()
