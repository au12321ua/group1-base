"""002_seed_roles_permissions_admin

Revision ID: b2c3d4e5f6a7
Revises: aaff2418abc3
Create Date: 2026-05-21 12:00:00.000000

导入 RBAC 种子数据（对齐 docs/design/v2/04-security-architecture.md）：
- 4 个角色、权限点及 role_permissions 映射
- 初始系统管理员 sys-admin-001 / admin（默认密码 ChangeMe123）
"""
from collections.abc import Sequence
from datetime import UTC, datetime

import bcrypt
import sqlalchemy as sa
from alembic import op

revision: str = "b2c3d4e5f6a7"
down_revision: str | None = "aaff2418abc3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# 权限点定义：(code, name, resource, action)
_PERMISSIONS: list[tuple[str, str, str, str]] = [
    ("user:read", "查看用户", "user", "read"),
    ("user:create", "创建用户", "user", "create"),
    ("user:update", "更新用户", "user", "update"),
    ("user:delete", "删除用户", "user", "delete"),
    ("course:read", "查看课程", "course", "read"),
    ("course:create", "创建课程", "course", "create"),
    ("course:update", "更新课程", "course", "update"),
    ("course:delete", "删除课程", "course", "delete"),
    ("offering:read", "查看开课", "offering", "read"),
    ("offering:create", "创建开课", "offering", "create"),
    ("offering:update", "更新开课", "offering", "update"),
    ("offering:delete", "删除开课", "offering", "delete"),
    ("schedule:read", "查看排课", "schedule", "read"),
    ("schedule:create", "创建排课", "schedule", "create"),
    ("schedule:update", "更新排课", "schedule", "update"),
    ("schedule:delete", "删除排课", "schedule", "delete"),
    ("calendar:read", "查看校历", "calendar", "read"),
    ("calendar:create", "创建校历", "calendar", "create"),
    ("calendar:update", "更新校历", "calendar", "update"),
    ("calendar:delete", "删除校历", "calendar", "delete"),
    ("training:read", "查看培养方案", "training", "read"),
    ("training:create", "创建培养方案", "training", "create"),
    ("training:update", "更新培养方案", "training", "update"),
    ("training:delete", "删除培养方案", "training", "delete"),
    ("base-info:read", "查看基础信息", "base-info", "read"),
    ("base-info:create", "创建基础信息", "base-info", "create"),
    ("base-info:update", "更新基础信息", "base-info", "update"),
    ("base-info:delete", "删除基础信息", "base-info", "delete"),
    ("audit:read", "查看审计日志", "audit", "read"),
    ("recycle:read", "查看回收站", "recycle", "read"),
    ("recycle:restore", "恢复回收站条目", "recycle", "restore"),
    ("recycle:delete", "永久删除回收站条目", "recycle", "delete"),
]

_ROLES: list[tuple[str, str, str]] = [
    ("STUDENT", "学生", "查看个人信息与课程相关数据"),
    ("TEACHER", "教师", "管理授课班级与个人信息"),
    ("ACADEMIC_ADMIN", "教务管理员", "管理用户、课程、校历与基础信息"),
    ("SYS_ADMIN", "系统管理员", "最高权限，含角色分配与系统配置"),
]

_READ_PERMISSIONS = (
    "user:read",
    "course:read",
    "offering:read",
    "schedule:read",
    "calendar:read",
    "training:read",
    "base-info:read",
)

_ACADEMIC_WRITE = (
    "user:read",
    "user:create",
    "user:update",
    "user:delete",
    "course:read",
    "course:create",
    "course:update",
    "course:delete",
    "offering:read",
    "offering:create",
    "offering:update",
    "offering:delete",
    "schedule:read",
    "schedule:create",
    "schedule:update",
    "schedule:delete",
    "calendar:read",
    "calendar:create",
    "calendar:update",
    "calendar:delete",
    "training:read",
    "training:create",
    "training:update",
    "training:delete",
    "base-info:read",
    "base-info:create",
    "base-info:update",
    "base-info:delete",
    "recycle:read",
    "recycle:restore",
    "recycle:delete",
)

_ROLE_PERMISSION_CODES: dict[str, frozenset[str]] = {
    "STUDENT": frozenset(_READ_PERMISSIONS),
    "TEACHER": frozenset(_READ_PERMISSIONS),
    "ACADEMIC_ADMIN": frozenset(_ACADEMIC_WRITE),
    "SYS_ADMIN": frozenset(code for code, *_ in _PERMISSIONS),
}

_ADMIN_USER_ID = "sys-admin-001"
_ADMIN_USERNAME = "admin"
_DEFAULT_ADMIN_PASSWORD = "ChangeMe123"


def _hash_password(password: str) -> tuple[str, str]:
    salt = bcrypt.gensalt(rounds=12)
    password_hash = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
    return password_hash, salt.decode("utf-8")


def upgrade() -> None:
    bind = op.get_bind()
    now = datetime.now(UTC)

    roles_table = sa.table(
        "roles",
        sa.column("code", sa.String),
        sa.column("name", sa.String),
        sa.column("description", sa.String),
        sa.column("is_active", sa.Boolean),
        sa.column("created_at", sa.DateTime),
    )
    op.bulk_insert(
        roles_table,
        [
            {
                "code": code,
                "name": name,
                "description": desc,
                "is_active": True,
                "created_at": now,
            }
            for code, name, desc in _ROLES
        ],
    )

    perms_table = sa.table(
        "permissions",
        sa.column("code", sa.String),
        sa.column("name", sa.String),
        sa.column("resource", sa.String),
        sa.column("action", sa.String),
        sa.column("created_at", sa.DateTime),
    )
    op.bulk_insert(
        perms_table,
        [
            {
                "code": code,
                "name": name,
                "resource": resource,
                "action": action,
                "created_at": now,
            }
            for code, name, resource, action in _PERMISSIONS
        ],
    )

    role_rows = bind.execute(sa.text("SELECT id, code FROM roles")).fetchall()
    perm_rows = bind.execute(sa.text("SELECT id, code FROM permissions")).fetchall()
    role_id_by_code = {row.code: row.id for row in role_rows}
    perm_id_by_code = {row.code: row.id for row in perm_rows}

    rp_table = sa.table(
        "role_permissions",
        sa.column("role_id", sa.Integer),
        sa.column("permission_id", sa.Integer),
    )
    rp_rows: list[dict[str, int]] = []
    for role_code, perm_codes in _ROLE_PERMISSION_CODES.items():
        role_id = role_id_by_code[role_code]
        for perm_code in perm_codes:
            rp_rows.append({"role_id": role_id, "permission_id": perm_id_by_code[perm_code]})
    op.bulk_insert(rp_table, rp_rows)

    password_hash, password_salt = _hash_password(_DEFAULT_ADMIN_PASSWORD)
    users_table = sa.table(
        "users",
        sa.column("user_id", sa.String),
        sa.column("username", sa.String),
        sa.column("status", sa.Enum("ACTIVE", "DISABLED", name="userstatus")),
        sa.column("created_at", sa.DateTime),
    )
    op.bulk_insert(
        users_table,
        [
            {
                "user_id": _ADMIN_USER_ID,
                "username": _ADMIN_USERNAME,
                "status": "ACTIVE",
                "created_at": now,
            }
        ],
    )

    cred_table = sa.table(
        "credentials",
        sa.column("user_id", sa.String),
        sa.column("username", sa.String),
        sa.column("password_hash", sa.String),
        sa.column("password_salt", sa.String),
        sa.column("failed_login_count", sa.Integer),
        sa.column("created_at", sa.DateTime),
        sa.column("updated_at", sa.DateTime),
    )
    op.bulk_insert(
        cred_table,
        [
            {
                "user_id": _ADMIN_USER_ID,
                "username": _ADMIN_USERNAME,
                "password_hash": password_hash,
                "password_salt": password_salt,
                "failed_login_count": 0,
                "created_at": now,
                "updated_at": now,
            }
        ],
    )

    sys_admin_role_id = role_id_by_code["SYS_ADMIN"]
    ur_table = sa.table(
        "user_roles",
        sa.column("user_id", sa.String),
        sa.column("role_id", sa.Integer),
    )
    op.bulk_insert(
        ur_table,
        [{"user_id": _ADMIN_USER_ID, "role_id": sys_admin_role_id}],
    )


def downgrade() -> None:
    bind = op.get_bind()
    bind.execute(
        sa.text("DELETE FROM user_roles WHERE user_id = :uid"),
        {"uid": _ADMIN_USER_ID},
    )
    bind.execute(
        sa.text("DELETE FROM credentials WHERE user_id = :uid"),
        {"uid": _ADMIN_USER_ID},
    )
    bind.execute(
        sa.text("DELETE FROM users WHERE user_id = :uid"),
        {"uid": _ADMIN_USER_ID},
    )
    bind.execute(sa.text("DELETE FROM role_permissions"))
    bind.execute(sa.text("DELETE FROM permissions"))
    bind.execute(sa.text("DELETE FROM roles"))
