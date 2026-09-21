"""seed permissions and system role-permission mappings

Revision ID: a1b2c3d4e5f6
Revises: 1816d04d00b4
Create Date: 2026-09-20 00:00:00.000000

"""
import uuid
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "1816d04d00b4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ---------------------------------------------------------------------------
# Permission catalogue
# ---------------------------------------------------------------------------
PERMISSIONS = [
    # Organization
    ("organization.view", "Allows viewing organization details and profile."),
    ("organization.manage", "Allows managing organization settings and configuration."),
    # Members
    ("members.view", "Allows viewing organization members and their roles."),
    ("members.manage", "Allows managing organization members (invite, remove, change roles)."),
    # Roles
    ("roles.view", "Allows viewing organization roles and their permission assignments."),
    ("roles.manage", "Allows managing organization roles and permission assignments."),
    # Documents
    ("documents.view", "Allows viewing documents within the organization."),
    ("documents.upload", "Allows uploading new documents."),
    ("documents.delete", "Allows deleting documents."),
    ("documents.review", "Allows reviewing documents (e.g., review workflow)."),
    ("documents.approve", "Allows approving documents."),
    ("documents.reject", "Allows rejecting documents."),
    # Collections
    ("collections.view", "Allows viewing collections within the organization."),
    ("collections.manage", "Allows managing collections (create, edit, delete)."),
    # Audit
    ("audit_logs.view", "Allows viewing audit logs for the organization."),
    # Settings
    ("settings.view", "Allows viewing organization settings."),
    ("settings.manage", "Allows managing organization settings."),
]


# ---------------------------------------------------------------------------
# Role-permission mapping: role_name -> list of permission names
# ---------------------------------------------------------------------------
ROLE_PERMISSIONS = {
    "owner": [name for name, _ in PERMISSIONS],
    "admin": [name for name, _ in PERMISSIONS],
    "member": [
        "organization.view",
        "members.view",
        "roles.view",
        "documents.view",
        "collections.view",
        "settings.view",
    ],
    "viewer": [
        "organization.view",
        "documents.view",
        "collections.view",
    ],
}


def _insert_permissions(connection) -> dict:
    """Insert all permissions if they do not already exist.

    Returns a mapping of permission name -> permission id.
    """
    permission_ids = {}

    for name, description in PERMISSIONS:
        existing = connection.execute(
            sa.text(
                "SELECT id FROM permissions WHERE name = :name"
            ),
            {"name": name},
        ).mappings().one_or_none()

        if existing is not None:
            permission_ids[name] = existing["id"]
        else:
            new_id = str(uuid.uuid4())
            connection.execute(
                sa.text(
                    """
                    INSERT INTO permissions
                        (id, name, description, created_at, updated_at)
                    VALUES
                        (:id, :name, :description, now(), now())
                    """
                ),
                {
                    "id": new_id,
                    "name": name,
                    "description": description,
                },
            )
            permission_ids[name] = new_id

    return permission_ids


def _create_role_permission_mappings(connection, permission_ids: dict) -> None:
    """Create RolePermission mappings for all organizations' system roles.

    Uses INSERT ... SELECT ... WHERE NOT EXISTS to avoid duplicates.
    """
    for role_name, perm_names in ROLE_PERMISSIONS.items():
        for perm_name in perm_names:
            perm_id = permission_ids[perm_name]

            connection.execute(
                sa.text(
                    """
                    INSERT INTO role_permissions (role_id, permission_id)
                    SELECT or2.id, :permission_id
                    FROM organization_roles or2
                    WHERE or2.name = :role_name
                      AND NOT EXISTS (
                          SELECT 1
                          FROM role_permissions rp
                          WHERE rp.role_id = or2.id
                            AND rp.permission_id = :permission_id
                      )
                    """
                ),
                {
                    "permission_id": perm_id,
                    "role_name": role_name,
                },
            )


def upgrade() -> None:
    connection = op.get_bind()

    permission_ids = _insert_permissions(connection)

    _create_role_permission_mappings(connection, permission_ids)


def downgrade() -> None:
    """Remove the permission seed and role-permission mappings.

    Only deletes RolePermission rows that reference permissions created
    by this migration, and removes the permissions themselves. Existing
    organizations, memberships, and roles are preserved.
    """
    connection = op.get_bind()

    permission_names = [name for name, _ in PERMISSIONS]

    # Delete role_permissions referencing any of the seeded permissions.
    connection.execute(
        sa.text(
            """
            DELETE FROM role_permissions
            WHERE permission_id IN (
                SELECT id FROM permissions WHERE name = ANY(:names)
            )
            """
        ),
        {"names": permission_names},
    )

    # Delete the seeded permissions.
    connection.execute(
        sa.text(
            "DELETE FROM permissions WHERE name = ANY(:names)"
        ),
        {"names": permission_names},
    )