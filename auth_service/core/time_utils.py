"""UTC 时间工具（与 fix(time) 模型 default_factory 对齐；SQLite 读回常为 naive）。"""

from datetime import UTC, datetime


def utc_now() -> datetime:
    """当前 UTC 时刻（aware）。"""
    return datetime.now(UTC)


def as_utc(dt: datetime) -> datetime:
    """将 naive 或 aware 时间统一为 UTC aware，便于比较与断言。"""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)
