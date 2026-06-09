# STSS 信息管理子系统

STSS 大组 P2-A 子系统 — 教务信息管理系统，负责认证授权（Auth Service）、基础数据管理（Info Service）和前端管理界面（Vue 3 SPA）。

## 技术栈

| 组件 | 选型 | 说明 |
|------|------|------|
| 语言 | Python 3.12+ | — |
| 框架 | FastAPI | async |
| ORM | SQLModel | Pydantic v2 + SQLAlchemy |
| 数据库 | SQLite → PostgreSQL | 原型 → 生产 |
| 迁移 | Alembic | 三条独立迁移链（见 `docs/alembic-guide.md`） |
| 认证 | JWT HS256 / RS256 | 默认 HS256；生产推荐 RS256（env 配置，Auth 内验签） |
| 包管理 | uv | — |
| Lint | ruff | — |
| 测试 | pytest + pytest-asyncio | — |
| 容器 | Docker + Compose | — |

## 前置条件

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)（Python 包管理器）
- Docker & Docker Compose（可选，用于容器化运行）

## 快速开始

```bash
# 1. 克隆仓库
git clone <repo-url>
cd group1-base

# 2. 安装依赖
uv sync --group dev

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env，将 TOKEN_SECRET_KEY 改为随机字符串

# 5. 启动服务
# 方式一：本地运行
uv run uvicorn auth_service.main:app --port 8001 --reload
uv run uvicorn info_service.main:app --port 8002 --reload
uv run python -m scripts.seed_data

# 方式二：Docker Compose
docker-compose up -d

# 6. 验证
# 浏览器访问 Swagger 文档
# http://localhost:8001/docs  (Auth Service)
# http://localhost:8002/docs  (Info Service)
```

## 运行测试

```bash
# 全部测试
uv run pytest

# 仅冒烟测试（快速验证基础设施）
uv run pytest -m smoke

# 覆盖率报告
uv run pytest --cov
```

## 项目结构

```
group1-base/
├── auth_service/          # 认证授权服务（端口 8001）
│   ├── api/v1/            # 路由层：auth.py、internal.py
│   ├── services/          # 业务层
│   ├── crud/              # 数据访问层
│   ├── models/            # SQLModel 实体
│   ├── schemas/           # Pydantic Schema
│   ├── core/              # 配置、安全
│   └── main.py            # 入口
├── info_service/          # 信息管理服务（端口 8002）
│   ├── api/v1/            # 12 个端点模块
│   ├── services/          # 7 个服务
│   ├── crud/              # 12 个 CRUD 模块
│   ├── models/            # 13 个实体
│   ├── schemas/           # 12 个 Schema 模块
│   └── main.py            # 入口
├── scripts/               # 数据库初始化脚本仓库
├── shared/                # 共用库（异常、响应、安全工具、日志）
├── tests/                 # 测试代码
├── docs/
│   ├── design/v2/         # 架构设计文档（9 份）
│   └── require-spec/      # 需求规格 + 验证矩阵
├── data/                  # SQLite 数据库文件（运行时生成）
├── logs/                  # 日志文件
├── uploads/               # 上传文件存储（运行时生成）
├── pyproject.toml         # 项目配置
├── docker-compose.yml     # Docker 编排
├── .env.example           # 环境变量模板
├── CLAUDE.md              # Agent 入口文件
└── TEAM_GUIDE.md          # 团队协作指南
```

## 服务概览

| 服务 | 端口 | 入口 | 说明 |
|------|------|------|------|
| Auth Service | 8001 | `/docs` | 认证（login/logout/refresh/change-password）+ 系统登录 + 内部验证 |
| Info Service | 8002 | `/docs` | 用户/课程/排课/日历/培养方案/基础信息/回收站/文件/审计/数据供给 |
| Frontend | 5173 | `/` | Vue 3 管理后台，9 个模块管理界面 |

## 开发指南

| 文档 | 用途 |
|------|------|
| [CLAUDE.md](CLAUDE.md) | Agent 编码入口，含架构约束、代码规范 |
| [TEAM_GUIDE.md](TEAM_GUIDE.md) | 团队协作流程，含分支策略、PR 模板、任务分工 |
| [docs/BRANCH_STRATEGY.md](docs/BRANCH_STRATEGY.md) | 分支管理详细规范 |
| [docs/design/v2/README.md](docs/design/v2/README.md) | 架构设计文档索引 |
| [docs/auth-jwt-keys.md](docs/auth-jwt-keys.md) | JWT HS256/RS256 配置与换密钥（env + 重启） |
| [docs/require-spec/](docs/require-spec/) | 需求规格 + 验证矩阵 |

### 架构硬约束

- **单向依赖**：Router → Service → CRUD → Model，禁止反向引用
- **数据库独立**：Auth 和 Info 各有独立数据库，通过 `userId` 逻辑关联，无外键
- **身份传递**：Gateway → `/internal/verify` → Header（`X-User-Id`、`X-User-Role`、`X-User-Permissions`）→ 下游服务
- **统一响应**：所有端点使用 `APIResponse[T]` 格式

## Auth 开发与联调

| 项 | 说明 |
|----|------|
| JWT | `JWT_SUPPORT_HS256` / `JWT_SUPPORT_RS256` + `JWT_SIGNING_ALGORITHM`（见 [docs/auth-jwt-keys.md](docs/auth-jwt-keys.md)） |
| 验签 | 均在 Auth 内完成（`/internal/verify`）；**无** `/auth/public-key` 端点 |
| Token 存储 | DB 仅存 `token_hash`（SHA-256），不存 JWT 明文 |
| 种子数据 | `uv run python -m scripts.seed_data` |
| 内部 API | `POST /api/v1/internal/users` 返回 **201**；`DELETE .../users/{id}` 返回 **204** |
| 服务登录 | `POST /api/v1/auth/sys/login`，凭据见 `SERVICE_CLIENT_*` 环境变量 |

更多约束见 [CLAUDE.md](CLAUDE.md) 与 [docs/design/v2/04-security-architecture.md](docs/design/v2/04-security-architecture.md)。
