"""add rbac foundation tables

Revision ID: 1816d04d00b4
Revises: 4ad57e06053d
Create Date: 2026-09-15 12:00:00.000000

"""
import uuid
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1816d04d00b4"
down_revision: Union[str, Sequence[str], None] = "4ad57e06053d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


SYSTEM_ROLE_NAMES = ["owner", "admin", "member", "viewer"]


def _insert_system_roles(connection) -> None:
    organizations = connection.execute(
        sa.text("SELECT id FROM organizations")
    ).mappings().all()

    for org in organizations:
        org_id = org["id"]
        for role_name in SYSTEM_ROLE_NAMES:
            connection.execute(
                sa.text(
                    """
                    INSERT INTO organization_roles
                        (id, organization_id, name, is_system, created_at, updated_at)
                    VALUES
                        (:id, :organization_id, :name, true, now(), now())
                    """
                ),
                {
                    "id": str(uuid.uuid4()),
                    "organization_id": org_id,
                    "name": role_name,
                },
            )


def _map_memberships_to_roles(connection) -> None:
    connection.execute(
        sa.text(
            """
            UPDATE organization_memberships om
            SET organization_role_id = (
                SELECT or2.id
                FROM organization_roles or2
                WHERE or2.organization_id = om.organization_id
                  AND or2.name = LOWER(om.role::text)
            )
            """
        )
    )


def upgrade() -> None:
    connection = op.get_bind()

    op.create_table(
        "organization_roles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_system", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "organization_id",
            "name",
            name="uq_organization_roles_organization_name",
        ),
    )
    op.create_index(
        op.f("ix_organization_roles_organization_id"),
        "organization_roles",
        ["organization_id"],
        unique=False,
    )

    op.create_table(
        "permissions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="uq_permissions_name"),
    )
    op.create_index(
        op.f("ix_permissions_name"),
        "permissions",
        ["name"],
        unique=True,
    )

    op.create_table(
        "role_permissions",
        sa.Column("role_id", sa.Uuid(), nullable=False),
        sa.Column("permission_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["organization_roles.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["permission_id"],
            ["permissions.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "role_id",
            "permission_id",
            name="pk_role_permissions",
        ),
    )

    op.add_column(
        "organization_memberships",
        sa.Column(
            "organization_role_id",
            sa.Uuid(),
            nullable=True,
        ),
    )
    op.create_index(
        op.f("ix_organization_memberships_organization_role_id"),
        "organization_memberships",
        ["organization_role_id"],
        unique=False,
    )

    _insert_system_roles(connection)

    _map_memberships_to_roles(connection)

    op.alter_column(
        "organization_memberships",
        "organization_role_id",
        existing_type=sa.Uuid(),
        nullable=False,
    )

    op.create_foreign_key(
        "fk_organization_memberships_organization_role_id",
        "organization_memberships",
        "organization_roles",
        ["organization_role_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_organization_memberships_organization_role_id",
        "organization_memberships",
        type_="foreignkey",
    )

    op.drop_index(
        op.f("ix_organization_memberships_organization_role_id"),
        table_name="organization_memberships",
    )

    op.drop_column("organization_memberships", "organization_role_id")

    op.drop_table("role_permissions")
    op.drop_table("permissions")
    op.drop_table("organization_roles")
