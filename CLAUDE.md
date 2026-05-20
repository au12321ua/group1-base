# STSS 信息管理子系统

> **一句话**：教务信息管理系统（Auth Service + Info Service），作为 STSS 大组的 P2-A 子系统，负责认证授权和基础数据管理。
>
> **本仓库范围**：Auth Service（8001）、Info Service（8002）、前端管理界面（Vite 5173）。Gateway/Bus 由其他组负责。

## 技术栈

| 组件 | 选择 | 版本要求 |
|------|------|----------|
| 语言 | Python | 3.12+ |
| 框架 | FastAPI | async |
| ORM | SQLModel | Pydantic v2 + SQLAlchemy |
| 数据库 | SQLite → PostgreSQL | 原型 → 生产 |
| 迁移 | Alembic | — |
| 认证 | JWT HS256 | 预留 RS256 扩展 |
| 包管理 | uv | — |
| Lint | ruff | — |
| 测试 | pytest + pytest-asyncio + pytest-cov | — |
| 容器 | Docker + Compose | — |
| 前端 | Vue 3 + TS + Element Plus + Pinia | Node 18+, npm |

## 目录结构

```
group1-base/
├── docs/
│   ├── design/v2/              ← 架构设计（9 份编号文档 + README，Agent 编码前必读）
│   ├── require-spec/           ← 需求规格（验收标准来源）
│   ├── tests/                  ← 测试文档：README 概览 + 完整编写指南
│   ├── BRANCH_STRATEGY.md      ← 分支管理策略（GitHub Flow）
│   └── TASK_BREAKDOWN.md       ← 任务分工建议（4 Dev + 1 QA）
├── shared/                     ← 共用库（异常、响应、安全工具、日志）
├── auth_service/               ← 认证授权服务（端口 8001）
│   ├── api/v1/                 # 端点：auth.py、internal.py
│   ├── services/               # 业务：auth、key、identity
│   ├── crud/                   # 数据访问：credential、token、session、role、permission
│   ├── models/                 # SQLModel：user、credential、token、session、role、permission
│   ├── schemas/                # Pydantic：auth_schema、user_schema
│   └── migrations/             # Alembic 迁移链 → auth.db（8 表）
├── info_service/               ← 信息管理服务（端口 8002）
│   ├── api/v1/                 # 12 个端点模块（user、course、offering、schedule、calendar、training_program、base_info、recycle_bin、files、audit_logs、data_provision）
│   ├── services/               # 7 个服务
│   ├── crud/                   # 12 个 CRUD + base
│   ├── models/                 # 13 个 SQLModel 实体
│   ├── schemas/                # 12 个 Schema 模块
│   └── migrations/             # Alembic 迁移链
│       ├── info/               #   → info.db（12 表）
│       └── audit/              #   → audit.db（3 表）
├── tests/                      ← 自动化测试（smoke / unit / integration / regression）
│   ├── conftest.py             # 根级 fixture：DB 引擎、HTTP 客户端
│   ├── utils.py                # 测试工具：身份 Header 构建、数据工厂
│   ├── test_infra.py           # 冒烟测试
│   ├── auth_service/           # Auth Service 测试
│   ├── info_service/           # Info Service 测试
│   └── shared/                 # 共用库测试（数据库、错误处理、应用 wiring）
├── frontend/                   ← Vue 3 管理后台（端口 5173）
│   ├── src/
│   │   ├── api/client.ts       # Axios 实例（拦截器、Token 续期）
│   │   ├── components/         # 共享组件（StatusTag 等）
│   │   ├── directives/         # 自定义指令（v-permission）
│   │   ├── layouts/            # 布局组件（AdminLayout）
│   │   ├── router/             # 路由表 + beforeEach 导航守卫
│   │   ├── stores/auth.ts      # Pinia 认证 Store
│   │   └── views/              # 页面组件（12 个占位页 — 无业务逻辑）
│   ├── package.json
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   └── vite.config.ts          # Vite 配置（@ 别名、API 代理）
├── .github/
│   └── workflows/
│       └── ci.yml              # CI：ruff check + pytest（PR / push to main）
├── pyproject.toml
├── docker-compose.yml
└── .env.example
```

## 架构硬约束

### 分层规则（不可违反）
```
Router → Service → CRUD → Model
  薄路由        厚业务     纯数据     实体
```
- **单向依赖，禁止反向引用**。CRUD 不可导入 Service，Service 不可导入 Router。
- Schemas 和 Core 是横切关注点，所有层可依赖。

### 服务边界
- **Auth Service 只存最小用户字段**（userId、username、status），不持有业务数据。
- **Info Service 不签发 Token**，认证统一走 Auth Service。
- 两个服务的数据库独立，通过 `userId` 逻辑关联，**无外键约束**。

### 身份传递（关键！）
```
Gateway → Auth Service /internal/verify → X-User-Id, X-User-Role, X-User-Permissions Header → 下游服务
```
- **Info Service 不持有 JWT 密钥**，信任 Gateway 透传的身份 Header。
- 跨服务调用使用 Service Token（通过 `/auth/sys/login` 签发）。

### 数据库
- 3 个独立数据库：`auth.db`（Auth Service）、`info.db`（Info Service）、`audit.db`（审计日志）
- 跨库操作需**补偿机制**：主写成功 → 跨服务调用 → 失败则补偿回滚

### 数据库迁移（Alembic）
- **3 条独立迁移链**，每条链有独立的 `alembic.ini`、`env.py`、`versions/`
- **Alembic 使用同步驱动**（`sqlite:///`），与运行时异步驱动（`sqlite+aiosqlite:///`）不同但指向同一数据库文件
- **info_service 有两条链**：info 链和 audit 链。因为所有表共用一个 `SQLModel.metadata`，env.py 通过 `table.tometadata()` 将目标表复制到独立 `MetaData` 实例来隔离 autogenerate
- **`alembic.ini` 中 `script_location = %(here)s`**：确保从任意工作目录通过 `-c` 指定配置文件时都能正确找到 env.py
- **所有迁移命令从项目根目录运行**，使用 `-c` 指定配置文件路径
- 迁移文件纳入版本控制，ruff 对 versions 目录豁免 E501（行长度）
- 完整指南见 `docs/alembic-guide.md`

### 权限模型
- 权限码格式：`resource:action`（如 `user:read`、`course:create`）
- 四种角色：STUDENT、TEACHER、ACADEMIC_ADMIN、SYS_ADMIN
- Auth Service 负责 RBAC，Info Service 负责资源级授权（检查访问者是否为资源所有者等）

## 代码规范

- **所有函数签名必须有完整类型注解**
- **所有端点使用 `shared.response.APIResponse[T]` 统一响应格式**
- **docstring 用中文，变量/函数名用英文**
- **异步接口**：`async def` + `await` 数据库操作
- **未实现功能**：用 `warnings.warn("TODO: ...")` + `raise NotImplementedError`
- **异常**：使用 `shared/exceptions.py` 中的异常类，不要直接 `raise HTTPException`
- **ruff 配置**在 `pyproject.toml` 中，提交前必须 `ruff check .` 通过

## 测试

测试按服务组织（`auth_service/`、`info_service/`、`shared/`），按范围标记分类。4 个 pytest 标记定义在 `pyproject.toml` 中：

| 标记 | 用途 | 典型耗时 | 建议频率 |
|------|------|----------|----------|
| `smoke` | 验证测试基础设施（app 可达、DB 可读写） | < 2s | 每次提交 |
| `unit` | 隔离测试单个组件 | < 10s | 每次提交 |
| `integration` | 完整 Router → Service → CRUD → Model 链路 | < 60s | 合并前 |
| `regression` | 已修复 bug 的回归防护 | 不定 | CI 常驻 |

覆盖率目标：总体 >= 90%，P0 功能 100%。通过 `pytest-cov` 收集，配置项在 `pyproject.toml` 的 `[tool.coverage.*]` 中。详细指导见 `docs/tests/README.md` 和 `docs/tests/test-guide.md`。

## 开发工作流

1. 从 `main` 创建分支：`feat/xxx`、`fix/xxx`、`chore/xxx`
2. 让 Agent 先阅读 `docs/design/v2/` 下对应设计文档
3. 编写实现（Agent 生成或手写）
4. 本地验证：
   - 后端完整检查：`uv run ruff check . && uv run pytest`
   - 快速检查（跳过集成测试）：`uv run pytest -m "not integration"`
   - 按标记运行：`uv run pytest -m smoke`、`uv run pytest -m unit`
   - 覆盖率报告：`uv run pytest --cov=. --cov-report=term-missing`
   - 前端类型检查：`cd frontend && npx vue-tsc --noEmit`
   - 数据库迁移（如需）：`uv run python -m alembic -c <service>/migrations/<chain>/alembic.ini upgrade head`
5. 提交 PR（`gh pr create`）
6. CI 自动 lint + test，至少 1 人 Review
7. Squash Merge 到 main

## 快速启动

```bash
git clone <repo-url> && cd group1-base
uv sync --group dev
cp .env.example .env   # 填入开发用密钥
docker-compose up -d    # 或手动 uvicorn auth_service.main:app --port 8001 & info_service...

# 前端
cd frontend && npm install && npm run dev   # http://localhost:5173

# 测试
uv run pytest
```

## 设计文档索引

启动 Agent 开发前，根据任务类型选择阅读：

| 任务类型 | 必读文档 |
|----------|----------|
| Auth 相关 | `docs/design/v2/04-security-architecture.md`、`02-module-architecture.md` |
| CRUD 接口 | `docs/design/v2/05-api-architecture.md`、`03-data-architecture.md` |
| 业务流程 | `docs/design/v2/06-business-flows.md` |
| 部署/环境 | `docs/design/v2/08-deployment.md` |
| 数据库迁移 | `docs/alembic-guide.md` |
| 前端开发 | `docs/frontend/README.md`、`docs/frontend/development-guide.md` |
| 全部 | `docs/design/v2/README.md`（索引入口） |

完整需求规格在 `docs/require-spec/`，测试矩阵在 `docs/require-spec/validation_matrices/`。

## 关键文件路径

- 环境变量模板：`.env.example`
- Docker 编排：`docker-compose.yml`
- 包配置：`pyproject.toml`
- CI 工作流：`.github/workflows/ci.yml`
- 团队协作指南：`TEAM_GUIDE.md`
- 分支管理策略：`docs/BRANCH_STRATEGY.md`
- Alembic 迁移指南：`docs/alembic-guide.md`
