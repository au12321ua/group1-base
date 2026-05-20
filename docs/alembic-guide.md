# Alembic 迁移指南

## 概述

项目使用 Alembic 管理三个独立数据库的 schema 变更，每个数据库有独立的迁移链：

```
auth_service/migrations/          → auth.db（8 表：认证授权）
info_service/migrations/info/     → info.db（12 表：业务主数据）
info_service/migrations/audit/    → audit.db（3 表：审计日志 + 死信队列 + 操作日志）
```

每个迁移链包含：
- `alembic.ini` — 数据库连接（同步 `sqlite:///`，Alembic 不需要异步驱动）
- `env.py` — 环境配置，导入模型并过滤目标表
- `script.py.mako` — 新迁移脚本模板
- `versions/` — 迁移版本文件

## 常用命令

所有命令从**项目根目录**运行：

```bash
# 生成新迁移（自动检测模型变更）
uv run alembic -c auth_service/migrations/alembic.ini revision --autogenerate -m "描述"
uv run alembic -c info_service/migrations/info/alembic.ini revision --autogenerate -m "描述"
uv run alembic -c info_service/migrations/audit/alembic.ini revision --autogenerate -m "描述"

# 执行迁移（升级到最新）
uv run alembic -c auth_service/migrations/alembic.ini upgrade head
uv run alembic -c info_service/migrations/info/alembic.ini upgrade head
uv run alembic -c info_service/migrations/audit/alembic.ini upgrade head

# 回滚
uv run alembic -c auth_service/migrations/alembic.ini downgrade -1

# 查看当前版本
uv run alembic -c auth_service/migrations/alembic.ini current

# 查看未应用的迁移
uv run alembic -c auth_service/migrations/alembic.ini heads

# 生成 SQL 脚本（不实际执行）
uv run alembic -c auth_service/migrations/alembic.ini upgrade head --sql
```

> **注意**：若 `uv run alembic`无法使用，可以使用等价形式`uv run python -m alembic`。

## 添加新模型后的工作流

1. 在 `*_service/models/` 中定义或修改 SQLModel 模型
2. 确保模型的 `__init__.py` 已 import 新模块
3. 运行 `revision --autogenerate` 生成迁移脚本
4. 检查生成的迁移脚本是否正确（特别注意：多数据库场景下表是否落在正确的迁移链中）
5. 运行 `upgrade head` 应用迁移
6. 运行 `uv run pytest` 确保无回归

## 设计决策

### 为什么使用同步数据库 URL？

Alembic 执行的是 DDL 操作（CREATE/ALTER TABLE），不需要异步 I/O。使用同步 `sqlite:///` 驱动比异步 `sqlite+aiosqlite:///` 更简单可靠。两者指向同一个数据库文件。

### 为什么 info_service 有两条迁移链？

info_service 管理两个物理数据库（info.db 和 audit.db），两个库的表定义在同一个 `info_service.models` 中。Alembic 的 autogenerate 会比较 `target_metadata` 与数据库当前状态，如果两条链共享同一个 metadata，会出现表重复的问题。

解决方案：每条链的 `env.py` 用 `table.tometadata()` 将属于当前数据库的表复制到独立的 `MetaData` 实例中，autogenerate 只看到目标库的表。

### 为什么 `script_location = %(here)s`？

`%(here)s` 是 Alembic 的内置变量，指向 `alembic.ini` 所在目录。使用它（而非 `.`）确保从任何工作目录通过 `-c` 指定配置文件时，都能正确找到 `env.py`。

### ruff 配置

迁移文件的自动生成代码行较长，在 `pyproject.toml` 中配置了豁免：

```toml
[tool.ruff.lint.per-file-ignores]
"**/migrations/**/versions/*.py" = ["E501"]
```

## 原型阶段注意事项

- **SQLite → PostgreSQL 切换时**：修改连接字符串 → 删除旧迁移链 → 重新生成初始迁移
- **迁移文件纳入版本控制**，与代码同步提交
- `data/` 目录由应用 lifespan 自动创建，Alembic env.py 不负责创建目录
