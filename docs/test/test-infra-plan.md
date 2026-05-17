# 测试基础设施搭建计划

## 1. 概述

为 Auth Service 和 Info Service 搭建统一的测试基础设施，包括数据库 fixture、HTTP 客户端 fixture、测试工具函数，以及一个验证基础设施正确性的空测试。

## 2. 目录结构

```
tests/
├── conftest.py              # 顶层共享 fixture（日志、事件循环配置）
├── utils.py                 # 测试工具函数（身份 header 构建、数据工厂等）
├── test_infra.py            # 基础设施正确性验证测试
├── auth_service/
│   └── conftest.py          # Auth Service 专用 fixture（client + db）
└── info_service/
    └── conftest.py          # Info Service 专用 fixture（client + db）
```

## 3. 技术方案

### 3.1 数据库 Fixture

**方案**：每个服务使用独立的 in-memory SQLite 数据库（`sqlite+aiosqlite://`）。

- `auth_db_engine` / `auth_db_session`：Auth Service 模型的数据库引擎和会话
- `info_db_engine` / `info_db_session`：Info Service 模型的数据库引擎和会话
- `audit_db_engine` / `audit_db_session`：审计日志模型的数据库引擎和会话

**实现要点**：
- 使用 `sqlalchemy.ext.asyncio.create_async_engine` 创建异步引擎
- 各引擎只创建本服务所属的表（按 `__tablename__` 过滤 `SQLModel.metadata.sorted_tables`），保持 auth.db / info.db / audit.db 三库分离
- 每个 fixture 作用域为 `function`（每个测试独立的 in-memory 数据库）
- 隔离策略：引擎为函数级 scope，每个测试获得全新的数据库实例，无需手动事务回滚

### 3.2 异步 HTTP 客户端 Fixture

**方案**：使用 `httpx.AsyncClient` + `httpx.ASGITransport` 直接连接 FastAPI app。

- `async_client_auth`：连接 `auth_service.main.app`
- `async_client_info`：连接 `info_service.main.app`

**实现要点**：
- 使用 `ASGITransport(app=app)` 避免实际网络调用
- `base_url="http://test"` 作为测试基准 URL
- 每个测试独立客户端实例

### 3.3 配置覆盖

测试环境下覆盖以下配置：
- 数据库 URL → in-memory SQLite（避免磁盘文件）
- `TOKEN_SECRET_KEY` → 固定测试密钥
- `LOG_LEVEL` → WARNING（减少测试输出噪音）
- `ENV` → "test"

通过 `monkeypatch.setenv` 或直接 patch `get_*_settings()` 函数实现。

### 3.4 测试工具函数（tests/utils.py）

- `build_identity_headers(user_id, role, permissions)`：构建 Gateway 透传的身份 Header（`X-User-Id`、`X-User-Role`、`X-User-Permissions`）
- `build_auth_header(token)`：构建携带 Bearer Token 的认证 Header（`Authorization: Bearer <token>`）
- `make_user_payload(**kwargs)`：生成测试用户数据载荷（含 username、user_no、role_ids 等默认字段）

## 4. pytest 配置

在 `pyproject.toml` 中已有配置：

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

无需额外变更。

## 5. 依赖项

已在 `pyproject.toml` 的 `dev` 依赖中：
- `pytest>=8.3.0`
- `pytest-asyncio>=0.24.0`
- `httpx>=0.28.0`（含 `ASGITransport`）

无需新增依赖。

## 6. 实现步骤

1. 创建 `tests/conftest.py` — 顶层 pytest 配置
2. 创建 `tests/utils.py` — 测试工具函数
3. 创建 `tests/auth_service/conftest.py` — Auth 专用 fixture
4. 创建 `tests/info_service/conftest.py` — Info 专用 fixture
5. 创建 `tests/test_infra.py` — 基础设施验证测试
6. 运行 `ruff check . && pytest` 自检

## 7. 验证标准

- `pytest` 成功执行且 `tests/test_infra.py` 通过
- `ruff check .` 零错误
- 数据库 fixture 正确创建所有表
- HTTP 客户端 fixture 可以访问 FastAPI app
