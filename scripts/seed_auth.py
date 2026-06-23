"""Seed Auth DB with roles, permissions, role-permission assignments, and admin user."""

from datetime import UTC, datetime

from sqlalchemy.engine import Engine
from sqlmodel import Session

from scripts.seed_utils import is_table_empty, print_step

# ── Roles ──────────────────────────────────────────────────────────────────────

_ROLES: list[dict] = [
    {"code": "STUDENT", "name": "学生", "description": "默认学生角色，拥有基础查看权限"},
    {"code": "TEACHER", "name": "教师", "description": "教师角色，拥有课程与排课相关权限"},
    {
        "code": "ACADEMIC_ADMIN",
        "name": "教务管理员",
        "description": "教务管理员，拥有除系统管理外的全部权限",
    },
    {"code": "SYS_ADMIN", "name": "系统管理员", "description": "系统管理员，拥有全部权限"},
]


def seed_roles(engine: Engine) -> dict[str, int]:
    """Insert roles into the roles table. Returns {code: id} mapping."""
    from auth_service.models.role import Role

    if not is_table_empty(engine, "roles"):
        print_step("roles 表非空，跳过")
        with Session(engine) as session:
            roles = session.query(Role).all()
            return {r.code: r.id for r in roles}

    with Session(engine) as session:
        role_map: dict[str, int] = {}
        for r in _ROLES:
            role = Role(
                code=r["code"],
                name=r["name"],
                description=r["description"],
                is_active=True,
                created_at=datetime.now(UTC),
            )
            session.add(role)
            session.flush()
            role_map[role.code] = role.id
        session.commit()
    print_step(f"已创建 {len(_ROLES)} 个角色: {', '.join(role_map.keys())}")
    return role_map


# ── Permissions ────────────────────────────────────────────────────────────────

# (code, name, resource, action)
_PERMISSIONS: list[tuple[str, str, str, str]] = [
    # user
    ("user:read", "查看用户", "user", "read"),
    ("user:create", "创建用户", "user", "create"),
    ("user:update", "更新用户", "user", "update"),
    ("user:delete", "删除用户", "user", "delete"),
    # course
    ("course:read", "查看课程", "course", "read"),
    ("course:create", "创建课程", "course", "create"),
    ("course:update", "更新课程", "course", "update"),
    ("course:delete", "删除课程", "course", "delete"),
    # offering
    ("offering:read", "查看开课", "offering", "read"),
    ("offering:create", "创建开课", "offering", "create"),
    ("offering:update", "更新开课", "offering", "update"),
    ("offering:delete", "删除开课", "offering", "delete"),
    # schedule
    ("schedule:read", "查看排课", "schedule", "read"),
    ("schedule:create", "创建排课", "schedule", "create"),
    ("schedule:update", "更新排课", "schedule", "update"),
    ("schedule:delete", "删除排课", "schedule", "delete"),
    # calendar
    ("calendar:read", "查看校历", "calendar", "read"),
    ("calendar:create", "创建校历", "calendar", "create"),
    ("calendar:update", "更新校历", "calendar", "update"),
    ("calendar:delete", "删除校历", "calendar", "delete"),
    # training
    ("training:read", "查看培养方案", "training", "read"),
    ("training:create", "创建培养方案", "training", "create"),
    ("training:update", "更新培养方案", "training", "update"),
    ("training:delete", "删除培养方案", "training", "delete"),
    # base-info
    ("base-info:read", "查看基础数据", "base-info", "read"),
    ("base-info:create", "创建基础数据", "base-info", "create"),
    ("base-info:update", "更新基础数据", "base-info", "update"),
    ("base-info:delete", "删除基础数据", "base-info", "delete"),
    # classroom
    ("classroom:read", "查看教室", "classroom", "read"),
    ("classroom:create", "创建教室", "classroom", "create"),
    ("classroom:update", "更新教室", "classroom", "update"),
    ("classroom:delete", "删除教室", "classroom", "delete"),
    # recycle
    ("recycle:read", "查看回收站", "recycle", "read"),
    ("recycle:restore", "恢复数据", "recycle", "restore"),
    ("recycle:delete", "彻底删除", "recycle", "delete"),
    # file
    ("file:read", "查看文件", "file", "read"),
    ("file:create", "上传文件", "file", "create"),
    ("file:delete", "删除文件", "file", "delete"),
    # audit
    ("audit:read", "查看审计日志", "audit", "read"),
    # data-provision
    ("data-provision:read", "查看数据供给", "data-provision", "read"),
    # role
    ("role:read", "查看角色", "role", "read"),
    ("role:assign", "分配角色", "role", "assign"),
    # permission
    ("permission:read", "查看权限", "permission", "read"),
]


def seed_permissions(engine: Engine) -> dict[str, int]:
    """Insert permissions into the permissions table. Returns {code: id} mapping."""
    from auth_service.models.permission import Permission

    if not is_table_empty(engine, "permissions"):
        print_step("permissions 表非空，跳过")
        with Session(engine) as session:
            perms = session.query(Permission).all()
            return {p.code: p.id for p in perms}

    with Session(engine) as session:
        perm_map: dict[str, int] = {}
        for code, name, resource, action in _PERMISSIONS:
            perm = Permission(
                code=code,
                name=name,
                resource=resource,
                action=action,
                created_at=datetime.now(UTC),
            )
            session.add(perm)
            session.flush()
            perm_map[code] = perm.id
        session.commit()
    print_step(f"已创建 {len(_PERMISSIONS)} 条权限")
    return perm_map


# ── Role-Permission assignments ────────────────────────────────────────────────

# Which permission codes each role gets
_ROLE_PERMISSION_MAP: dict[str, list[str]] = {
    "SYS_ADMIN": [
        # all permissions (resolved at runtime via perm_map.keys())
    ],
    "ACADEMIC_ADMIN": [
        "user:read", "user:create", "user:update", "user:delete",
        "course:read", "course:create", "course:update", "course:delete",
        "offering:read", "offering:create", "offering:update", "offering:delete",
        "schedule:read", "schedule:create", "schedule:update", "schedule:delete",
        "classroom:read", "classroom:create", "classroom:update", "classroom:delete",
        "calendar:read", "calendar:create", "calendar:update", "calendar:delete",
        "training:read", "training:create", "training:update", "training:delete",
        "base-info:read", "base-info:create", "base-info:update", "base-info:delete",
        "recycle:read", "recycle:restore", "recycle:delete",
        "file:read", "file:create", "file:delete",
        # audit:read intentionally omitted — only SYS_ADMIN per §2.4
        "data-provision:read",
    ],
    "TEACHER": [
        # self-profile
        "user:read", "user:update",
        # read-only resources
        "course:read",
        "classroom:read",
        "calendar:read", "training:read",
        "base-info:read",
        # offering & schedule — can mutate assigned ones (resource-level check)
        "offering:read", "offering:update", "offering:delete",
        "schedule:read", "schedule:update", "schedule:delete",
        # files — own uploads only (resource-level check)
        "file:read", "file:create", "file:delete",
    ],
    "STUDENT": [
        # self-profile
        "user:read", "user:update",
        # read-only resources
        "course:read", "offering:read", "schedule:read",
        "classroom:read",
        "calendar:read", "training:read",
        "base-info:read",
        # files — own uploads only (resource-level check)
        "file:read", "file:create", "file:delete",
    ],
}


def seed_role_permissions(
    engine: Engine,
    role_map: dict[str, int],
    perm_map: dict[str, int],
) -> None:
    """Assign permissions to roles based on _ROLE_PERMISSION_MAP."""
    from auth_service.models.permission import RolePermission

    if not is_table_empty(engine, "role_permissions"):
        print_step("role_permissions 表非空，跳过")
        return

    with Session(engine) as session:
        count = 0
        for role_code, perm_codes in _ROLE_PERMISSION_MAP.items():
            role_id = role_map[role_code]
            # "SYS_ADMIN" gets ALL permissions
            resolved = (
                list(perm_map.keys()) if role_code == "SYS_ADMIN" else perm_codes
            )
            for pc in resolved:
                perm_id = perm_map.get(pc)
                if perm_id is None:
                    print(f"    [WARN] 权限码 {pc} 未找到，跳过")
                    continue
                session.add(RolePermission(role_id=role_id, permission_id=perm_id))
                count += 1
        session.commit()
    print_step(f"已分配 {count} 条角色-权限关联")


# ── Admin user ─────────────────────────────────────────────────────────────────

def seed_admin_user(
    engine: Engine,
    password: str,
    username: str = "admin",
) -> str:
    """Create admin user with SYS_ADMIN role. Returns user_id."""
    from auth_service.core.security import get_password_hash
    from auth_service.models.credential import Credential
    from auth_service.models.role import Role, UserRole
    from auth_service.models.user import User, UserStatus

    if not is_table_empty(engine, "users"):
        print_step("users 表非空，跳过")
        with Session(engine) as session:
            user = session.query(User).filter(User.username == username).first()
            if user:
                return user.user_id
            return ""

    with Session(engine) as session:
        # Get SYS_ADMIN role
        admin_role = session.query(Role).filter(Role.code == "SYS_ADMIN").first()
        if not admin_role:
            raise RuntimeError("SYS_ADMIN 角色未找到，请先运行 seed_roles")

        # Generate a deterministic user_id for admin
        user_id = "admin-001"
        user = User(
            user_id=user_id,
            username=username,
            status=UserStatus.ACTIVE,
            created_at=datetime.now(UTC),
        )
        session.add(user)
        session.flush()

        # Create credential
        password_hash, password_salt = get_password_hash(password)
        cred = Credential(
            user_id=user_id,
            username=username,
            password_hash=password_hash,
            password_salt=password_salt,
            failed_login_count=0,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        session.add(cred)

        # Assign SYS_ADMIN role
        session.add(UserRole(user_id=user_id, role_id=admin_role.id))

        session.commit()
    print_step(f"已创建管理员用户: username={username}, user_id={user_id}")
    return user_id
