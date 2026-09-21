import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
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


class RbacFoundationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
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
        self.db.execute(
            text(
                """
                TRUNCATE TABLE
                    organization_roles,
                    permissions,
                    role_permissions,
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

    def _create_membership(
        self,
        user: User,
        organization: Organization,
        role: OrganizationMembershipRole = OrganizationMembershipRole.MEMBER,
    ) -> OrganizationMembership:
        role_map = {
            OrganizationMembershipRole.OWNER: "owner",
            OrganizationMembershipRole.ADMIN: "admin",
            OrganizationMembershipRole.MEMBER: "member",
            OrganizationMembershipRole.VIEWER: "viewer",
        }
        system_role_name = role_map[role]
        system_role = self.db.query(OrganizationRole).filter_by(
            organization_id=organization.id,
            name=system_role_name,
        ).one_or_none()
        membership = OrganizationMembership(
            user_id=user.id,
            organization_id=organization.id,
            status=OrganizationMembershipStatus.ACTIVE,
            role=role,
            organization_role_id=system_role.id if system_role else None,
        )
        self.db.add(membership)
        self.db.flush()
        return membership

    def _create_system_roles(self, organization: Organization) -> None:
        for role_name in ["owner", "admin", "member", "viewer"]:
            role = OrganizationRole(
                organization_id=organization.id,
                name=role_name,
                is_system=True,
            )
            self.db.add(role)
        self.db.flush()

    def test_organization_role_can_be_associated_with_organization(self) -> None:
        org = self._create_organization("Test Org")
        role = OrganizationRole(
            organization_id=org.id,
            name="manager",
            is_system=False,
        )
        self.db.add(role)
        self.db.commit()

        self.db.refresh(role)
        self.assertIsNotNone(role.id)
        self.assertEqual(role.organization_id, org.id)
        self.assertEqual(role.name, "manager")
        self.assertFalse(role.is_system)

    def test_organization_role_name_uniqueity_is_organization_scoped(self) -> None:
        org = self._create_organization("Test Org")
        role = OrganizationRole(
            organization_id=org.id,
            name="manager",
            is_system=False,
        )
        self.db.add(role)
        self.db.commit()

        duplicate = OrganizationRole(
            organization_id=org.id,
            name="manager",
            is_system=False,
        )
        self.db.add(duplicate)

        with self.assertRaises(Exception) as ctx:
            self.db.commit()

        self.db.rollback()

    def test_same_role_name_can_exist_in_different_organizations(self) -> None:
        org_a = self._create_organization("Org A")
        org_b = self._create_organization("Org B")

        role_a = OrganizationRole(
            organization_id=org_a.id,
            name="manager",
            is_system=False,
        )
        role_b = OrganizationRole(
            organization_id=org_b.id,
            name="manager",
            is_system=False,
        )
        self.db.add(role_a)
        self.db.add(role_b)
        self.db.commit()

        self.assertIsNotNone(role_a.id)
        self.assertIsNotNone(role_b.id)
        self.assertNotEqual(role_a.id, role_b.id)
        self.assertEqual(role_a.name, "manager")
        self.assertEqual(role_b.name, "manager")

    def test_permission_name_is_globally_unique(self) -> None:
        permission_a = Permission(name="view members", description="Can view members")
        permission_b = Permission(name="view members", description="Duplicate")
        self.db.add(permission_a)
        self.db.add(permission_b)

        with self.assertRaises(Exception) as ctx:
            self.db.commit()

        self.db.rollback()

    def test_role_permission_prevents_duplicate_role_permission_pairs(self) -> None:
        org = self._create_organization("Test Org")
        role = OrganizationRole(
            organization_id=org.id,
            name="manager",
            is_system=False,
        )
        permission = Permission(name="view members")
        self.db.add(role)
        self.db.add(permission)
        self.db.flush()

        rp1 = RolePermission(role_id=role.id, permission_id=permission.id)
        rp2 = RolePermission(role_id=role.id, permission_id=permission.id)
        self.db.add(rp1)
        self.db.add(rp2)

        with self.assertRaises(Exception) as ctx:
            self.db.commit()

        self.db.rollback()

    def test_organization_membership_can_reference_organization_role_id(self) -> None:
        org = self._create_organization("Test Org")
        self._create_system_roles(org)
        user = self._create_user("member@test.com")
        role = self.db.query(OrganizationRole).filter_by(
            organization_id=org.id, name="member"
        ).one()

        membership = OrganizationMembership(
            user_id=user.id,
            organization_id=org.id,
            role=OrganizationMembershipRole.MEMBER,
            organization_role_id=role.id,
        )
        self.db.add(membership)
        self.db.commit()

        self.db.refresh(membership)
        self.assertIsNotNone(membership.organization_role_id)
        self.assertEqual(membership.organization_role_id, role.id)

    def test_existing_membership_role_remains_available(self) -> None:
        org = self._create_organization("Test Org")
        self._create_system_roles(org)
        user = self._create_user("member@test.com")
        membership = self._create_membership(
            user, org, role=OrganizationMembershipRole.ADMIN
        )
        self.db.commit()

        self.db.refresh(membership)
        self.assertEqual(membership.role, OrganizationMembershipRole.ADMIN)

    def test_system_roles_created_for_each_organization(self) -> None:
        org = self._create_organization("Test Org")
        self._create_system_roles(org)
        self.db.commit()

        roles = (
            self.db.query(OrganizationRole)
            .filter_by(organization_id=org.id)
            .order_by(OrganizationRole.name)
            .all()
        )

        self.assertEqual(len(roles), 4)
        role_names = {r.name for r in roles}
        self.assertEqual(role_names, {"owner", "admin", "member", "viewer"})
        self.assertTrue(all(r.is_system for r in roles))

    def test_memberships_mapped_to_correct_system_role(self) -> None:
        org = self._create_organization("Test Org")
        self._create_system_roles(org)
        owner_role = self.db.query(OrganizationRole).filter_by(
            organization_id=org.id, name="owner"
        ).one()
        admin_role = self.db.query(OrganizationRole).filter_by(
            organization_id=org.id, name="admin"
        ).one()
        viewer_role = self.db.query(OrganizationRole).filter_by(
            organization_id=org.id, name="viewer"
        ).one()

        owner_user = self._create_user("owner@test.com")
        admin_user = self._create_user("admin@test.com")
        viewer_user = self._create_user("viewer@test.com")

        owner_membership = self._create_membership(
            owner_user, org, role=OrganizationMembershipRole.OWNER
        )
        admin_membership = self._create_membership(
            admin_user, org, role=OrganizationMembershipRole.ADMIN
        )
        viewer_membership = self._create_membership(
            viewer_user, org, role=OrganizationMembershipRole.VIEWER
        )

        owner_membership.organization_role_id = owner_role.id
        admin_membership.organization_role_id = admin_role.id
        viewer_membership.organization_role_id = viewer_role.id
        self.db.commit()

        self.assertEqual(owner_membership.organization_role_id, owner_role.id)
        self.assertEqual(admin_membership.organization_role_id, admin_role.id)
        self.assertEqual(viewer_membership.organization_role_id, viewer_role.id)

    def test_organization_membership_survives_migration_preserves_relationships(self) -> None:
        org = self._create_organization("Migration Test Org")
        self._create_system_roles(org)
        user = self._create_user("migration@test.com")
        owner_role = self.db.query(OrganizationRole).filter_by(
            organization_id=org.id, name="owner"
        ).one()

        membership = self._create_membership(
            user, org, role=OrganizationMembershipRole.OWNER
        )
        membership.organization_role_id = owner_role.id
        self.db.commit()
        self.db.refresh(membership)

        self.assertIsNotNone(membership.organization_role_id)
        self.assertEqual(membership.organization_role_id, owner_role.id)
        self.assertEqual(membership.role, OrganizationMembershipRole.OWNER)
        self.assertEqual(membership.status, OrganizationMembershipStatus.ACTIVE)

    def test_organization_role_relationship_on_organization(self) -> None:
        org = self._create_organization("Relationship Test Org")
        role = OrganizationRole(
            organization_id=org.id,
            name="custom_role",
            is_system=False,
        )
        self.db.add(role)
        self.db.commit()
        self.db.refresh(org)

        self.assertIn(role.id, [r.id for r in org.roles])

    def test_organization_role_relationship_on_membership(self) -> None:
        org = self._create_organization("Membership Relation Test Org")
        self._create_system_roles(org)
        user = self._create_user("relay@test.com")
        role = self.db.query(OrganizationRole).filter_by(
            organization_id=org.id, name="member"
        ).one()

        membership = OrganizationMembership(
            user_id=user.id,
            organization_id=org.id,
            role=OrganizationMembershipRole.MEMBER,
            organization_role_id=role.id,
        )
        self.db.add(membership)
        self.db.commit()
        self.db.refresh(membership)

        self.assertIsNotNone(membership.organization_role)
        self.assertEqual(membership.organization_role.id, role.id)
        self.assertEqual(membership.organization_role.name, "member")

    def test_organization_membership_unique_constraint_preserved(self) -> None:
        org = self._create_organization("Unique Constraint Test Org")
        user = self._create_user("unique@test.com")
        self._create_system_roles(org)
        role = self.db.query(OrganizationRole).filter_by(
            organization_id=org.id, name="member"
        ).one()

        membership = OrganizationMembership(
            user_id=user.id,
            organization_id=org.id,
            role=OrganizationMembershipRole.MEMBER,
            organization_role_id=role.id,
        )
        self.db.add(membership)
        self.db.commit()

        duplicate = OrganizationMembership(
            user_id=user.id,
            organization_id=org.id,
            role=OrganizationMembershipRole.VIEWER,
            organization_role_id=role.id,
        )
        self.db.add(duplicate)

        with self.assertRaises(Exception) as ctx:
            self.db.commit()

        self.db.rollback()

    def test_permissions_relationship_on_role(self) -> None:
        org = self._create_organization("Permission Relation Test Org")
        role = OrganizationRole(
            organization_id=org.id,
            name="manager",
            is_system=False,
        )
        permission = Permission(name="view documents")
        self.db.add(role)
        self.db.add(permission)
        self.db.flush()

        rp = RolePermission(role_id=role.id, permission_id=permission.id)
        self.db.add(rp)
        self.db.commit()
        self.db.refresh(role)

        self.assertIn(permission.id, [p.id for p in role.permissions])

    def test_role_permissions_relationship_on_permission(self) -> None:
        org = self._create_organization("Permission Relation Test Org")
        role = OrganizationRole(
            organization_id=org.id,
            name="manager",
            is_system=False,
        )
        permission = Permission(name="edit documents")
        self.db.add(role)
        self.db.add(permission)
        self.db.flush()

        rp = RolePermission(role_id=role.id, permission_id=permission.id)
        self.db.add(rp)
        self.db.commit()
        self.db.refresh(permission)

        self.assertIn(role.id, [r.id for r in permission.roles])

    def test_organization_role_description_is_optional(self) -> None:
        org = self._create_organization("Test Org")
        role_no_desc = OrganizationRole(
            organization_id=org.id,
            name="no_desc_role",
            is_system=False,
        )
        role_with_desc = OrganizationRole(
            organization_id=org.id,
            name="with_desc_role",
            description="A role with a description",
            is_system=False,
        )
        self.db.add(role_no_desc)
        self.db.add(role_with_desc)
        self.db.commit()

        self.assertIsNone(role_no_desc.description)
        self.assertEqual(role_with_desc.description, "A role with a description")


if __name__ == "__main__":
    unittest.main()
