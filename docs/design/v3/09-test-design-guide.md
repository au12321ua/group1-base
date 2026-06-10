# 09 — 测试设计指导

> **文档定位**：本文档是"指导如何设计测试的文档"，即测试设计的**方法论与规范**。
> 它不描述具体测试用例，而是定义测试设计的流程、原则、模式和产出标准。
>
> **与已有测试文档的关系**：
> - `docs/tests/README.md` — 测试文档入口，描述测试分类和快速开始
> - `docs/tests/test-guide.md` — 测试编写指南，描述具体写法（fixture 参考、命名约定、代码示例）
> - `docs/test/test-design.md` — 测试基础设施设计方案（测试策略、Mock 策略、数据工厂）
> - **本文档** — 测试设计的**方法论**：如何制定测试策略、如何设计测试架构、如何规划覆盖率

## 1. 测试设计流程

### 1.1 设计阶段

测试设计应在功能设计完成之后、编码之前进行，遵循以下流程：

```
需求分析 → 测试策略制定 → 测试架构设计 → 用例设计 → 数据设计 → 评审 → 编码
```

| 阶段 | 输入 | 输出 | 参与角色 |
|------|------|------|----------|
| 需求分析 | 需求规格、API 设计文档 | 测试范围矩阵 | Dev + QA |
| 策略制定 | 测试范围矩阵、架构设计文档 | 测试策略文档（分层/分范围） | QA |
| 架构设计 | 测试策略、项目结构 | 测试目录结构、fixture 设计、Mock 策略 | Dev + QA |
| 用例设计 | API 端点清单、业务流程图 | 参数化矩阵（正常/边界/异常） | Dev + QA |
| 数据设计 | 数据模型、业务规则 | 数据工厂定义、种子数据方案 | Dev |
| 评审 | 以上全部 | 评审意见、修改项 | Dev + QA |
| 编码 | 评审通过的设计 | 测试代码 | Dev |

### 1.2 设计原则

1. **先策略后用例**：确定测什么、测到什么程度，再设计具体用例。
2. **分层覆盖**：不同层用不同级别的测试（单元 → CRUD，集成 → API）。
3. **边界优先**：每个功能至少覆盖正常路径、边界条件和异常路径。
4. **独立可重复**：每个测试用例可独立运行，不依赖执行顺序。
5. **数据隔离**：测试数据在测试结束后不留痕迹。
6. **可维护性**：测试代码与业务代码同等重要，需要 review 和重构。

## 2. 测试策略制定

### 2.1 测试范围决策矩阵

对于每个功能模块，回答以下问题确定测试级别和深度：

| 决策问题 | 纯单元 | 单元为主 | 集成为主 | 全栈 |
|----------|--------|----------|----------|------|
| 是否有外部依赖（DB、HTTP）？ | 否 | 少量 | 是 | 是 |
| 业务逻辑复杂度？ | 低 | 中 | 高 | 高 |
| 失败影响范围？ | 低 | 中 | 高 | 极高 |
| 是否 P0 功能？ | 否 | 否 | 是 | 是 |

**推荐策略**：

| 模块类型 | 测试策略 | 单元:集成比例 |
|----------|----------|---------------|
| CRUD 层 | 单元测试为主（in-memory SQLite） | 90:10 |
| Service 层 | 单元测试（mock CRUD）+ 关键路径集成测试 | 60:40 |
| API 端点 | 集成测试为主（完整 HTTP 请求周期） | 10:90 |
| 工具函数 | 纯单元测试 | 100:0 |
| 跨服务调用 | 集成测试（fake client）+ 单元测试（mock） | 50:50 |

### 2.2 优先级分级

| 优先级 | 覆盖范围 | 测试要求 |
|--------|----------|----------|
| P0 | 核心认证流程、用户 CRUD、权限校验 | 100% 覆盖率，正常+边界+异常全覆盖 |
| P1 | 课程/开课/排课 CRUD、回收站 | 90% 覆盖率，正常+关键异常覆盖 |
| P2 | 校历/培养方案/教室/基础信息 | 80% 覆盖率，正常路径为主 |
| P3 | 文件上传/下载、数据提供 | 70% 覆盖率，核心功能覆盖 |

### 2.3 风险驱动补充

以下场景需要**额外补充测试**（即使不在基本覆盖率范围内）：

- 并发冲突（如同 userId 同时操作）
- 大数据量分页（边界：空、单页、跨页）
- 补偿机制异常（跨服务调用失败后的补偿操作失败）
- Token 过期边界（过期前一秒、刚过期）
- 输入注入攻击（SQL 注入、XSS）

## 3. 测试架构设计

### 3.1 目录结构设计原则

```
tests/
├── conftest.py              # 全局 fixture（所有测试共用）
├── utils.py                 # 全局工具函数（数据工厂、Header 构建）
├── test_infra.py            # 基础设施冒烟测试
├── <service>/               # 按服务组织
│   ├── conftest.py          # 服务级 fixture
│   ├── test_<module>.py     # 按模块组织测试文件
│   └── ...
└── cross_service/           # 跨服务集成测试
    └── test_<scenario>.py
```

**设计要点**：
- `conftest.py` 分级：根级定义 DB 引擎/HTTP 客户端，服务级定义领域 fixture
- 每个服务目录自包含：该服务的测试不依赖其他服务的 fixture
- 跨服务测试独立目录：明确标注跨服务依赖

### 3.2 Fixture 设计模式

**模式 1：DB 引擎隔离（function 作用域）**

每个测试函数获得独立的 in-memory SQLite 数据库，测试间零污染。

```python
@pytest.fixture(scope="function")
async def auth_db_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield engine
    await engine.dispose()
```

**设计要点**：
- 使用 `scope="function"` 确保隔离
- 每次创建全新引擎（非复用）
- 仅创建该服务所需的表（不跨 DB 创建）

**模式 2：HTTP 客户端直连**

通过 `httpx.ASGITransport` 直连 FastAPI app，无网络开销。

```python
@pytest.fixture(scope="function")
async def async_client_auth():
    from auth_service.main import app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
```

**设计要点**：
- 覆盖依赖注入：通过 app.dependency_overrides 替换真实依赖
- 每个测试独立 transport

**模式 3：跨服务 Fake Client**

集成测试中不访问真实网络，替换为 fake client 返回固定响应。

```python
@pytest.fixture
def fake_auth_client():
    return FakeAuthServiceClient(responses={
        "create_user": {"status": "created", "user_id": "u1"},
        "disable_user": {"status": "disabled"},
    })
```

**设计要点**：
- 预设成功和失败两种响应
- 记录调用历史（验证是否调用了正确的端点）
- 可注入延迟模拟超时

### 3.3 Mock 边界设计

| Mock 对象 | 测试级别 | Mock 方式 |
|-----------|----------|-----------|
| 外部 HTTP 服务 | 单元 + 集成 | Fake client / monkeypatch |
| 文件系统 | 单元 + 集成 | tmp_path fixture |
| 时间 | 单元 | freezegun / time_machine |
| 随机数 | 单元 | seed / mock |
| 真实数据库 | 集成 | in-memory SQLite（不 mock） |

**原则**：Mock 仅用于外部边界，数据库不 mock（用 in-memory SQLite 替代真实 SQLite）。

## 4. 用例设计方法

### 4.1 参数化矩阵模板

每个 API 端点至少覆盖三类场景：

| 场景类型 | 输入特征 | 预期结果 | 用例 ID 后缀 |
|----------|----------|----------|-------------|
| 正常（ok） | 合法参数、正常状态 | 200/201，data 非空 | `-ok` |
| 边界（edge） | 空列表、单条、最大值、临界时间 | 200，返回空/单条/截断 | `-edge` |
| 异常（err） | 缺失必填、无效格式、越权访问 | 400/401/403/404 | `-err` |

### 4.2 用例 ID 命名规范

```
<领域代码>-<模块代码>-<序号>-<类型>
```

| 领域代码 | 说明 |
|----------|------|
| A | 认证与权限（Auth） |
| B | 用户与回收站（User & Recycle Bin） |
| C | 课程与教学（Course & Teaching） |
| D | 基础信息与数据提供（Base Info & Data Provision） |
| E | 审计与非功能（Audit & NFR） |

示例：`B-user-001-ok` = 用户模块第 1 个用例，正常场景

### 4.3 断言设计

每个测试用例的断言应覆盖三个维度：

```
1. HTTP 层：状态码、Content-Type
2. 业务层：APIResponse.code、APIResponse.message、data 结构
3. 副作用：数据库状态变更、审计日志写入、文件系统变更
```

**示例**：
```python
async def test_create_user_success(client, db_session):
    # Arrange
    payload = make_user_payload()
    # Act
    resp = await client.post("/api/v1/info/users", json=payload)
    # Assert — HTTP 层
    assert resp.status_code == 201
    # Assert — 业务层
    body = resp.json()
    assert body["code"] == 0
    assert body["data"]["username"] == payload["username"]
    # Assert — 副作用（DB）
    user = await db_session.get(UserInfo, body["data"]["id"])
    assert user is not None
    assert user.user_no == payload["user_no"]
```

## 5. 测试数据设计

### 5.1 数据工厂模式

数据工厂函数应满足：
- **有意义的默认值**：所有字段有合理默认值，调用方可只覆盖关心的字段
- **幂等性**：支持通过参数控制唯一字段值，避免冲突
- **语义化命名**：使用描述性值和命名模式

```python
# 好的数据工厂
def make_user_payload(
    user_no: str = "S2026001",
    username: str = "alice",
    full_name: str = "Alice Zhang",
    role_ids: list[int] | None = None,
) -> dict:
    return {
        "user_no": user_no,
        "username": username,
        "full_name": full_name,
        "role_ids": role_ids or [STUDENT_ROLE_ID],
        ...
    }

# 使用时只覆盖需要区分的字段
payload1 = make_user_payload(user_no="S2026001", username="alice")
payload2 = make_user_payload(user_no="S2026002", username="bob")
```

### 5.2 种子数据设计

种子数据（seed data）用于集成测试提供基础上下文：

- **角色与权限**：固定数据，所有集成测试共用（STUDENT、TEACHER、ACADEMIC_ADMIN、SYS_ADMIN）
- **初始管理员**：固定 admin 账号，用于鉴权测试
- **参考数据**：校历、教室等基础数据

设计原则：
- 种子数据量最小化（满足测试即可）
- 可重复执行（幂等）
- 与生产种子数据一致（结构与 scripts/seed_*.py 对齐）

## 6. 覆盖率规划

### 6.1 覆盖率目标

| 指标 | 总体 | P0 功能 | P1 功能 |
|------|------|---------|---------|
| 行覆盖率 | ≥ 90% | 100% | ≥ 90% |
| 分支覆盖率 | ≥ 85% | ≥ 95% | ≥ 85% |

### 6.2 覆盖率缺口分析

当覆盖率未达标时，按以下优先级补充：

1. **未覆盖的异常分支**：错误处理路径最容易遗漏
2. **未覆盖的边界条件**：if/else 分支中只有一个被测试
3. **未覆盖的补偿逻辑**：跨服务失败处理
4. **未覆盖的配置路径**：不同环境配置下的行为

### 6.3 覆盖率报告解读

```bash
uv run pytest --cov=. --cov-report=term-missing
```

关注：
- `models/` — 通常覆盖率低但可接受（纯数据结构）
- `core/config.py` — 通常覆盖率低但可接受（配置加载）
- `services/` — **必须高覆盖**（业务逻辑核心）
- `api/v1/` — **必须高覆盖**（集成测试应覆盖所有端点）

## 7. 测试文档产出标准

### 7.1 测试设计文档模板

新功能或模块的测试设计应产出以下文档（可放在 `docs/test/` 目录下）：

```markdown
# [功能名称] 测试设计

## 1. 测试范围
- 涉及端点/函数
- 优先级（P0/P1/P2/P3）

## 2. 测试策略
- 单元测试覆盖：[列出]
- 集成测试覆盖：[列出]
- Mock 策略：[列出需要 mock 的依赖]

## 3. 用例矩阵

| ID | 场景 | 输入 | 预期 | 级别 |
|----|------|------|------|------|
| ... | ... | ... | ... | unit/integration |

## 4. 数据工厂
- 需要的种子数据
- 需要的工厂函数

## 5. 特殊考虑
- 并发问题
- 性能基线
- 已知风险
```

### 7.2 与验证矩阵的关系

测试用例 ID 应与 `docs/require-spec/validation_matrices/` 中的 AVR（原子可验证需求）对应：

- 每个 AVR 应至少有一个测试用例覆盖
- 用例 ID 应包含对应的 AVR 编号引用

## 8. 测试质量评审清单

评审测试设计时，检查以下各项：

- [ ] 测试策略是否与功能优先级匹配？
- [ ] 参数化矩阵是否覆盖正常、边界、异常三类？
- [ ] 断言是否覆盖 HTTP 层、业务层和副作用三个维度？
- [ ] Fixture 是否按正确的作用域设计？
- [ ] Mock 边界是否合理（不过度 mock）？
- [ ] 数据工厂是否有意义的默认值？
- [ ] 用例 ID 是否遵循命名规范？
- [ ] 是否有测试顺序依赖？
- [ ] 是否依赖外部网络？
- [ ] CI 中是否能稳定运行？

## 9. 与 V2 测试文档的关系

| 文档 | 类型 | 本文档如何补充 |
|------|------|---------------|
| `docs/test/test-design.md` | 测试基础设施设计（实例） | 本文档提供"如何产生这样的设计"的方法论 |
| `docs/tests/test-guide.md` | 测试编写指南（操作手册） | 本文档提供编写之前的"设计阶段"指导 |
| `docs/tests/README.md` | 测试文档入口 | 本文档补充了测试设计流程和架构决策 |
| `docs/require-spec/validation_matrices/` | 验证矩阵（需求到用例映射） | 本文档定义了用例 ID 体系与矩阵的对应关系 |
