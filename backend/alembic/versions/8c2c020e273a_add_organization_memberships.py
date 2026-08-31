"""add organization memberships

Revision ID: 8c2c020e273a
Revises: cdcea0ace309
Create Date: 2026-08-23 16:35:00.581168

"""
import uuid
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8c2c020e273a"
down_revision: Union[str, Sequence[str], None] = "cdcea0ace309"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create memberships and preserve existing user-organization links."""
    op.create_table(
        "organization_memberships",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column(
            "role",
            sa.Enum(
                "OWNER",
                "ADMIN",
                "MEMBER",
                "VIEWER",
                name="organization_membership_role",
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "ACTIVE",
                "SUSPENDED",
                "REMOVED",
                name="organization_membership_status",
            ),
            nullable=False,
        ),
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
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "organization_id",
            name="uq_organization_memberships_user_organization",
        ),
    )
    op.create_index(
        op.f("ix_organization_memberships_organization_id"),
        "organization_memberships",
        ["organization_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_organization_memberships_user_id"),
        "organization_memberships",
        ["user_id"],
        unique=False,
    )

    connection = op.get_bind()
    existing_memberships = connection.execute(
        sa.text("SELECT id, organization_id FROM users"),
    ).mappings().all()
    if existing_memberships:
        connection.execute(
            sa.text(
                """
                INSERT INTO organization_memberships
                    (id, user_id, organization_id, role, status)
                VALUES
                    (:id, :user_id, :organization_id, 'MEMBER', 'ACTIVE')
                """,
            ),
            [
                {
                    "id": uuid.uuid4(),
                    "user_id": user["id"],
                    "organization_id": user["organization_id"],
                }
                for user in existing_memberships
            ],
        )

    op.drop_index(op.f("ix_users_organization_id"), table_name="users")
    op.drop_constraint(
        op.f("users_organization_id_fkey"),
        "users",
        type_="foreignkey",
    )
    op.drop_column("users", "organization_id")


def downgrade() -> None:
    """Restore the legacy single-organization association for each user."""
    op.add_column(
        "users",
        sa.Column("organization_id", sa.Uuid(), nullable=True),
    )

    # A legacy users row can represent one organization only. If a user has
    # multiple memberships, restore its earliest membership deterministically.
    connection = op.get_bind()
    connection.execute(
        sa.text(
            """
            UPDATE users
            SET organization_id = selected_membership.organization_id
            FROM (
                SELECT DISTINCT ON (user_id) user_id, organization_id
                FROM organization_memberships
                ORDER BY user_id, created_at, id
            ) AS selected_membership
            WHERE users.id = selected_membership.user_id
            """,
        ),
    )

    op.alter_column("users", "organization_id", nullable=False)
    op.create_foreign_key(
        op.f("users_organization_id_fkey"),
        "users",
        "organizations",
        ["organization_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index(
        op.f("ix_users_organization_id"),
        "users",
        ["organization_id"],
        unique=False,
    )
    op.drop_index(
        op.f("ix_organization_memberships_user_id"),
        table_name="organization_memberships",
    )
    op.drop_index(
        op.f("ix_organization_memberships_organization_id"),
        table_name="organization_memberships",
    )
    op.drop_table("organization_memberships")
    sa.Enum(
        "ACTIVE",
        "SUSPENDED",
        "REMOVED",
        name="organization_membership_status",
    ).drop(op.get_bind(), checkfirst=True)
    sa.Enum(
        "OWNER",
        "ADMIN",
        "MEMBER",
        "VIEWER",
        name="organization_membership_role",
    ).drop(op.get_bind(), checkfirst=True)
