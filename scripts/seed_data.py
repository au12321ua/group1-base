"""Seed data CLI entry point.

Usage:
    uv run seed                 # minimal mode (roles + permissions + admin)
    uv run seed --full          # full mode (includes sample data)
    uv run seed --reset         # delete all existing data first
    uv run seed --env-file .env.prod
"""

import argparse
import os
import sys
from pathlib import Path


def _resolve_env_file(env_file: str) -> str:
    """Resolve env file path relative to project root."""
    path = Path(env_file)
    if path.is_absolute():
        return str(path)
    project_root = Path(__file__).resolve().parent.parent
    return str(project_root / env_file)


def _load_env(env_file: str) -> None:
    """Load environment variables from a .env file (if it exists)."""
    env_path = _resolve_env_file(env_file)
    if Path(env_path).exists():
        # Use python-dotenv if available, otherwise fall back to manual parsing
        try:
            from dotenv import load_dotenv
            load_dotenv(env_path)
        except ImportError:
            _load_env_manual(env_path)
        print(f"[ENV] 已加载: {env_path}")
    else:
        print(f"[ENV] 文件不存在，使用当前环境变量: {env_path}")


def _load_env_manual(env_path: str) -> None:
    """Minimal .env parser — sets os.environ for KEY=VALUE lines."""
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key not in os.environ:
                os.environ[key] = value


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Seed STSS databases with initial data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    uv run seed                     minimal mode (default)
    uv run seed --full              include sample data
    uv run seed --reset             clear all data first
    uv run seed --reset --full      full reset and seed
        """,
    )
    parser.add_argument(
        "--full",
        action="store_true",
        default=False,
        help="Include sample data (departments, classrooms, calendars)",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        default=False,
        help="Drop and recreate all tables before seeding",
    )
    parser.add_argument(
        "--env-file",
        default=".env",
        help="Path to .env file relative to project root (default: .env)",
    )
    return parser.parse_args()


def main() -> None:
    """Entry point for `uv run seed`."""
    args = _parse_args()

    # Ensure project root is on sys.path
    project_root = str(Path(__file__).resolve().parent.parent)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # Load env
    _load_env(args.env_file)

    # Import project modules after path setup
    from scripts.seed_utils import (
        clear_all_tables,
        create_sync_engine,
        print_header,
        print_step,
    )

    # Read config from environment
    auth_db_url = os.environ.get(
        "AUTH_DATABASE_URL", "sqlite+aiosqlite:///./data/auth.db"
    )
    info_db_url = os.environ.get(
        "INFO_DATABASE_URL", "sqlite+aiosqlite:///./data/info.db"
    )
    audit_db_url = os.environ.get(
        "AUDIT_DATABASE_URL", "sqlite+aiosqlite:///./data/audit.db"
    )
    admin_username = os.environ.get("SEED_ADMIN_USERNAME", "admin")
    admin_password = os.environ.get("SEED_ADMIN_PASSWORD", "Admin123!")
    admin_user_no = os.environ.get("SEED_ADMIN_USER_NO", "STSS-ADMIN-001")
    admin_full_name = os.environ.get("SEED_ADMIN_FULL_NAME", "系统管理员")

    mode = "完整模式 (--full)" if args.full else "最小模式 (--minimal)"
    print_header(f"STSS 数据库种子脚本 — {mode}")

    # Create sync engines
    print_step(f"Auth DB: {auth_db_url}")
    print_step(f"Info DB: {info_db_url}")
    print_step(f"Audit DB: {audit_db_url}")

    auth_engine = create_sync_engine(auth_db_url)
    info_engine = create_sync_engine(info_db_url)
    audit_engine = create_sync_engine(audit_db_url)

    # Import all models so SQLModel.metadata is populated
    import auth_service.models  # noqa: F401
    import info_service.models  # noqa: F401
    import shared.models.audit_log  # noqa: F401

    # Reset if requested
    if args.reset:
        print_header("重置数据库")
        clear_all_tables(auth_engine)
        clear_all_tables(info_engine)
        clear_all_tables(audit_engine)

    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)

    # ── Auth DB ──────────────────────────────────────────────────────────────
    print_header("Auth DB 种子数据")

    from scripts.seed_auth import (
        seed_admin_user,
        seed_permissions,
        seed_role_permissions,
        seed_roles,
    )

    role_map = seed_roles(auth_engine)
    perm_map = seed_permissions(auth_engine)
    seed_role_permissions(auth_engine, role_map, perm_map)
    seed_admin_user(auth_engine, password=admin_password, username=admin_username)

    # ── Info DB ──────────────────────────────────────────────────────────────
    print_header("Info DB 种子数据")

    from scripts.seed_info import seed_admin_user_info

    seed_admin_user_info(
        info_engine,
        username=admin_username,
        user_no=admin_user_no,
        full_name=admin_full_name,
    )

    if args.full:
        from scripts.seed_info import (
            seed_academic_calendars,
            seed_base_info_items,
            seed_classrooms,
        )

        seed_base_info_items(info_engine)
        seed_classrooms(info_engine)
        seed_academic_calendars(info_engine)

    # ── Cleanup ──────────────────────────────────────────────────────────────
    auth_engine.dispose()
    info_engine.dispose()
    audit_engine.dispose()

    print_header("完成")
    print(f"  管理员用户名: {admin_username}")
    print(f"  管理员密码:   {admin_password}")
    print(f"  角色数量:     {len(role_map)}")
    print(f"  权限数量:     {len(perm_map)}")
    print()


if __name__ == "__main__":
    main()
