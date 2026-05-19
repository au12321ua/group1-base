# 测试文档

## 概述

本项目使用 pytest + pytest-asyncio 进行异步测试。测试按服务（auth_service、info_service、shared）组织，按范围（smoke、unit、integration、regression）分类。

- **覆盖率目标**：总体 >= 90%，P0 = 100%（详见 `docs/require-spec/validation_matrices/`）
- **测试数据隔离**：每个测试函数使用独立的 in-memory SQLite，测试间无状态泄漏
- **HTTP 测试**：通过 httpx `ASGITransport` 直连 FastAPI app，无网络开销

## 测试分类

| 标记 | 用途 | 典型耗时 | 运行时机 |
|------|------|----------|----------|
| `smoke` | 验证测试基础设施正确连接（app 可达、DB 可读写、工具函数正确） | < 2s | 每次提交前 |
| `unit` | 隔离测试单个组件，不依赖外部服务 | < 10s | 每次提交前 |
| `integration` | 测试完整 Router → Service → CRUD → Model 链路 | < 60s | 合并前 |
| `regression` | 针对已修复 bug 的测试，防止问题复发 | 不定 | CI 常驻 |

## 快速开始

```bash
# 运行全部测试
uv run pytest

# 仅冒烟测试
uv run pytest -m smoke

# 仅单元测试（不含冒烟）
uv run pytest -m unit

# 单元 + 集成（排除冒烟）
uv run pytest -m "not smoke"

# 指定文件
uv run pytest tests/info_service/test_deps.py

# 指定单个测试
uv run pytest tests/info_service/test_deps.py::TestGetCurrentUser::test_raises_when_user_id_missing

# 覆盖率
uv run pytest --cov=. --cov-report=term-missing
```

## 关键文件

| 文件 | 说明 |
|------|------|
| `tests/conftest.py` | 定义所有共享 fixture，修改前需确认消费者 |
| `tests/utils.py` | `build_identity_headers`、`build_auth_header`、`make_user_payload` |
| `pyproject.toml` | `[tool.pytest.ini_options]` 中的 pytest 配置 |

## 验证矩阵

测试用例应覆盖 `docs/require-spec/validation_matrices/` 中的 AVR（原子可验证需求）：

| 矩阵 | 领域 |
|------|------|
| `matrix-a-auth-permission.md` | 认证与权限 |
| `matrix-b-user-recyclebin.md` | 用户与回收站 |
| `matrix-c-baseinfo-data-provision.md` | 基础信息与数据提供 |
| `matrix-d-audit-nfr.md` | 审计与非功能需求 |

## 相关文档

- [测试编写指南](test-guide.md) — Agent 和开发者编写测试的完整参考
- [测试基础设施计划](../test/test-infra-plan.md) — 原始设计方案
- [任务拆解](../TASK_BREAKDOWN.md) — 测试任务分配
