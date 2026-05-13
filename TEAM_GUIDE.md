# STSS 团队协作指导手册

> 本文档面向 STSS 信息管理子系统（Auth Service + Info Service）的 4 位开发与 1 位测试。
> 所有成员均使用 AI Agent（Claude Code 或同类工具）辅助开发。

---

## 1. 让 Agent 快速了解项目

Agent 的工作质量取决于它对项目的理解程度。你需要让 Agent **在每次对话开始时**就能获取关键上下文。

### 1.1 CLAUDE.md（Agent 入口文件）

Claude Code 会在启动时自动加载项目根目录的 `CLAUDE.md`。这是 Agent 了解项目最重要（也是最容易被忽略）的文件。

**CLAUD.md 应该包含：**

- 项目一句话概述（这是什么、有哪些服务）
- 技术栈（Python 3.12 + FastAPI + SQLModel + SQLite）
- 目录结构速览（哪个文件夹干什么）
- 架构约束（单向依赖、Auth/Info 分离、跨服务通信方式）
- 代码规范（ruff 配置、命名约定、类型注解要求）
- 当前开发阶段和优先级

**建议**：每个组员在自己的工作分支上 `@import` 设计文档到 CLAUDE.md，让 Agent 在编码前先理解相关设计。

### 1.2 设计文档作为 Agent 知识库

```
design/v2/           ← 架构设计（Agent 编码前必读）
require-spec/        ← 需求规格（验收标准来源）
```

**推荐做法：**

| 场景 | Agent 应该读什么 |
|------|-----------------|
| 开发 Auth 相关功能 | `design/v2/04-security-architecture.md` + `design/v2/02-module-architecture.md` |
| 开发 CRUD 接口 | `design/v2/05-api-architecture.md` + `design/v2/03-data-architecture.md` |
| 写测试 / QA 验证 | `require-spec/validation_matrices/` 下对应矩阵 |
| 理解业务流程 | `design/v2/06-business-flows.md` + `require-spec/use_cases/` |

### 1.3 保证开发质量的实践

1. **设计先行**：让 Agent 先读设计文档，再写代码。不要在 Agent 不了解上下文时直接让它写实现。
2. **小步验证**：每完成一个函数/类就让 Agent 跑一次测试，不要批量实现后才发现问题。
3. **跨服务影响检查**：修改 Auth Service 的接口时，必须让 Agent 同时检查 Info Service 的调用方（跨服务 HTTP 调用）。
4. **安全红线**：在给 Agent 的 prompt 中明确禁止行为——不要硬编码密钥、不要在日志中打印 token、不要信任未验证的输入。
5. **Agent 生成的代码必须通过 CI**：lint (ruff) + test (pytest) 是底线。

---

## 2. 协作策略

### 2.1 分支策略（GitHub Flow）

采用简化版 GitHub Flow，适合小团队 + Agent 开发：

```
main          ← 生产就绪（只通过 PR 合并，禁止直接推送）
  └─ feat/<功能名>   ← 功能开发分支
  └─ fix/<问题描述>  ← Bug 修复分支
  └─ chore/<内容>    ← 基础设施/文档/配置
```

**分支命名约定：**

```
feat/user-import-endpoint
fix/token-expiry-check
chore/ci-setup
```

**规则：**

| 规则 | 说明 |
|------|------|
| `main` 分支保护 | 禁止直接 push，必须通过 PR |
| 每分支一人 | 一个功能分支由一个人负责（减少冲突） |
| 提交粒度 | 每完成一个有意义的变更就提交，提交信息用中文 |
| Rebase 优先 | 合并前先 `git fetch origin main && git rebase origin/main` |

### 2.2 PR 流程

```
1. 开发完成 → 本地跑 ruff + pytest 通过
2. 推送到 GitHub → 创建 PR
3. CI 自动运行 lint + test
4. 至少 1 人 Review（可以用 Agent 辅助 Review）
5. 合并到 main（使用 Squash Merge）
```

**PR 描述模板**（建议保存为 `.github/PULL_REQUEST_TEMPLATE.md`）：

```markdown
## 变更说明
-

## 关联设计文档
- design/v2/xx-xxx.md（如有）

## 测试说明
- [ ] 单元测试通过
- [ ] 新增测试覆盖了核心逻辑

## Agent 辅助记录（如适用）
- 使用的 Agent 工具：[Claude Code / 其他]
- 关键 Prompt 摘要：
```

### 2.3 CI/CD（GitHub Actions）

**推荐的最小 CI 流程**（`.github/workflows/ci.yml`）：

```yaml
# 触发条件：push 到任意分支 + PR 到 main
# 步骤：
#   1. uv sync --group dev
#   2. ruff check .
#   3. pytest --cov
```

**CD 策略（暂缓）**：
- 原型阶段使用 `docker-compose up -d` 手动部署
- 进入稳定阶段后再配置 GitHub Actions 自动构建镜像 + 部署

### 2.4 任务分配建议

当前角色未定，建议按**服务边界**划分（减少冲突）：

| 模块 | 建议人数 | 原因 |
|------|---------|------|
| Auth Service（认证/授权） | 1 人 | 相对独立，安全敏感，适合一人深入 |
| Info Service（业务 CRUD） | 2 人 | 接口最多（60+），可以按领域再分（用户/课程/文件/审计） |
| 共用库（shared/） + 基础设施 | 1 人 | 配置、Docker、CI/CD、共用类型 |
| 测试 | 1 人 | 独立验证，编写集成测试，维护验证矩阵 |

---

## 3. design/ 与 require-spec/ 管理

### 3.1 定位

| 目录 | 定位 | 修改规则 |
|------|------|---------|
| `design/v2/` | **当前版本的架构设计** | 只读参考。修改需全组讨论 + 更新 README.md 索引 |
| `require-spec/` | **需求规格基线** | 原则上冻结。发现矛盾时先沟通，不直接修改 |
| `design/v1/`（如有） | 历史版本，保留备查 | 不修改 |

### 3.2 版本管理建议

- 两个目录都纳入 Git 版本控制（它们是项目的"宪法"）
- 当设计发生重大变更时，创建 `design/v3/` 而非覆盖 v2
- 在 `design/v2/README.md` 中已经维护了与 `require-spec/` 的对应关系表，保持更新

### 3.3 日常开发中的使用

- Agent prompt 中引用设计文档路径，例如：`请根据 design/v2/05-api-architecture.md 中的端点定义实现 POST /users 接口`
- Code Review 时对照设计文档检查实现是否偏离
- 测试根据 `require-spec/validation_matrices/` 编写测试用例

---

## 4. 快速启动清单（新组员入职）

- [ ] 克隆仓库：`git clone <repo-url> && cd STSS`
- [ ] 安装依赖：`uv sync --group dev`
- [ ] 复制环境变量：`cp .env.example .env`（然后填入开发用密钥）
- [ ] 阅读 `CLAUDE.md`（了解项目全貌）
- [ ] 阅读 `design/v2/README.md`（了解设计文档索引）
- [ ] 阅读 `design/v2/01-system-overview.md`（理解系统定位）
- [ ] 启动服务：`docker-compose up -d` 或 `uv run uvicorn auth_service.main:app --port 8001`
- [ ] 运行测试确认环境正常：`uv run pytest`
- [ ] 配置 IDE 的 ruff 集成（自动格式化）

---

## 5. 团队约定

| 事项 | 约定 |
|------|------|
| 提交信息语言 | 中文 |
| 代码注释语言 | 中文（docstring 用中文，变量名用英文） |
| Python 版本 | 3.12+ |
| 类型注解 | 所有函数签名必须有完整类型注解 |
| Lint 工具 | ruff（配置在 pyproject.toml） |
| 测试框架 | pytest + pytest-asyncio |
| 数据库 | 原型阶段 SQLite，通过 Alembic 管理迁移 |
| 接口风格 | RESTful，JSON 格式，统一响应结构 `APIResponse[T]` |
