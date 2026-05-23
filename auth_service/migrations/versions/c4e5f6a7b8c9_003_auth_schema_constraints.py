"""003_auth_schema_constraints

Revision ID: c4e5f6a7b8c9
Revises: b2c3d4e5f6a7
Create Date: 2026-05-23 12:00:00.000000

补充 Auth 表索引与唯一约束（对齐模型与 PR Review）：
- tokens.token_value 唯一索引
- credentials.username 非唯一索引（登录 lookup）
- user_roles (user_id, role_id) 唯一
- role_permissions (role_id, permission_id) 唯一
"""
from collections.abc import Sequence

from alembic import op

revision: str = "c4e5f6a7b8c9"
down_revision: str | None = "b2c3d4e5f6a7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index(
        op.f("ix_credentials_username"),
        "credentials",
        ["username"],
        unique=False,
    )
    op.create_index(
        op.f("ix_tokens_token_value"),
        "tokens",
        ["token_value"],
        unique=True,
    )
    op.create_unique_constraint(
        "uq_user_roles_user_id_role_id",
        "user_roles",
        ["user_id", "role_id"],
    )
    op.create_unique_constraint(
        "uq_role_permissions_role_id_permission_id",
        "role_permissions",
        ["role_id", "permission_id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_role_permissions_role_id_permission_id",
        "role_permissions",
        type_="unique",
    )
    op.drop_constraint("uq_user_roles_user_id_role_id", "user_roles", type_="unique")
    op.drop_index(op.f("ix_tokens_token_value"), table_name="tokens")
    op.drop_index(op.f("ix_credentials_username"), table_name="credentials")
