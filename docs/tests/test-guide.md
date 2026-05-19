# 测试编写指南

面向 Agent 和开发者的测试编写参考文档。

## 1. 项目分层与测试边界

项目遵循严格分层：**Router → Service → CRUD → Model**。不同层适合不同级别的测试：

| 层 | 测试级别 | 示例 |
|----|----------|------|
| Router | integration | 完整 HTTP 请求/响应周期 |
| Service | unit 或 integration | 业务逻辑 + mock CRUD / 真实 CRUD |
| CRUD | unit | 数据库查询 + in-memory SQLite |
| Model | unit | 字段校验、序列化、约束 |

## 2. 文件组织与命名

### 命名约定

- **文件名**：`test_<模块名>.py`（如 `test_database.py`、`test_deps.py`）
- **类名**：`Test<功能或模块>`（如 `TestGetCurrentUser`、`TestAuthDB`）
- **方法名**：`test_<场景>` 或 `test_<动作>_<预期结果>`（如 `test_raises_when_user_id_missing`、`test_create_and_read_user`）

## 3. 标记分类规则

每个测试类**必须**有且仅有一个范围标记。回归测试可额外添加 `regression` 标记。

### `@pytest.mark.smoke`

**使用场景**：
- 验证测试基础设施是否正确连接（app 可达、DB 可读写、工具函数正确）
- 不涉及任何业务逻辑
- 失败原因通常是配置或 fixture 问题，而非代码 bug

**位置**：类级别。`test_infra.py` 中所有测试均为冒烟测试。

### `@pytest.mark.unit`

**使用场景**：
- 隔离测试单个函数、类或模块
- 外部依赖（DB、HTTP）使用 in-memory 或 mock 替代
- 不经过完整的 Router → Service → CRUD 链路

**示例**：测试 CRUD 函数（in-memory SQLite）、测试依赖函数（直接调用）、测试错误处理器（合成 app）

### `@pytest.mark.integration`

**使用场景**：
- 测试完整 Router → Service → CRUD → Model 链路
- 通过 `async_client_*` 发送真实 HTTP 请求
- 使用真实数据库（in-memory SQLite 可接受）

**示例**：`POST /api/v1/auth/login`、`GET /api/v1/users`

### `@pytest.mark.regression`

**使用场景**：
- 针对已修复 bug 的测试
- docstring 必须引用 bug 编号或问题链接
- 通常与 `unit` 或 `integration` 标记叠加使用

**示例**：
```python
@pytest.mark.unit
@pytest.mark.regression
class TestBugFix123:
    """回归测试：修复 issue #123 — 空权限列表导致 500 错误。"""
```

## 4. Fixture 参考

以下 fixture 定义在 `tests/conftest.py` 中，所有测试可直接使用。

### 数据库引擎（function 作用域，每测试独立）

| Fixture | 包含的表 |
|---------|----------|
| `auth_db_engine` | users, credentials, roles, user_roles, permissions, role_permissions, tokens, authentication_sessions |
| `info_db_engine` | users_info, user_profiles, courses, course_offerings, course_prerequisites, course_schedules, teacher_course_assignments, classrooms, training_programs, academic_calendars, base_info_items, file_resources |
| `audit_db_engine` | audit_logs, dead_letter_queue, operation_logs |

### 数据库会话（function 作用域）

| Fixture | 对应引擎 |
|---------|----------|
| `auth_db_session` | `auth_db_engine` |
| `info_db_session` | `info_db_engine` |
| `audit_db_session` | `audit_db_engine` |

### HTTP 客户端

| Fixture | 连接目标 |
|---------|----------|
| `async_client_auth` | `auth_service.main.app`（端口 8001 的 app） |
| `async_client_info` | `info_service.main.app`（端口 8002 的 app） |

### 添加新 fixture

- 跨服务共享 → 添加到 `tests/conftest.py`
- 服务专用 → 添加到 `tests/<service>/conftest.py`
- 默认使用 `scope="function"` 确保隔离
- 必须写 docstring

## 5. 编写异步测试

项目配置了 `asyncio_mode = "auto"`，所有 `async def test_*` 自动作为异步测试运行。

```python
@pytest.mark.integration
class TestUserEndpoints:
    async def test_get_users_returns_list(self, async_client_info):
        response = await async_client_info.get("/api/v1/users")
        assert response.status_code == 200
        body = response.json()
        assert "data" in body
```

**规则**：
- 异步操作必须 `await`
- 使用 `pytest.raises` 断言异常
- 不要使用 `event_loop` fixture（pytest-asyncio 自动管理）

## 6. 编写参数化测试

```python
@pytest.mark.parametrize(
    "user_id, role, expected_status",
    [
        pytest.param("u1", "SYS_ADMIN", 200, id="admin-can-access"),
        pytest.param("u2", "STUDENT", 403, id="student-cannot-access"),
        pytest.param("", "TEACHER", 401, id="empty-user-id-rejected"),
    ],
)
async def test_access_control(self, async_client_info, user_id, role, expected_status):
    headers = build_identity_headers(user_id=user_id, role=role)
    response = await async_client_info.get("/api/v1/admin/users", headers=headers)
    assert response.status_code == expected_status
```

**规则**：
- 使用 `pytest.param` 并设置 `id=` 以获得清晰的测试名称
- 覆盖正常路径、边界条件和异常路径

## 7. 数据库操作模式

```python
@pytest.mark.unit
class TestCourseCrud:
    async def test_create_course(self, info_db_session):
        from info_service.models.course import Course

        course = Course(
            course_code="CS101",
            course_name="计算机科学导论",
            credit=3,
            capacity=100,
            assessment_method="考试",
            is_active=True,
            is_deleted=False,
        )
        info_db_session.add(course)
        await info_db_session.flush()

        assert course.id is not None
        assert course.course_code == "CS101"
```

**注意**：
- `flush()` 足以在同一会话内验证 —— `commit()` 不需要（每测试独立 DB）
- 需要跨会话验证（如测试 commit/rollback 行为）时才使用 `commit()`
- 不要在一个测试中混用不同服务的 session（如 `auth_db_session` 访问 Info 表会报错）

## 8. 测试错误响应

```python
async def test_login_with_wrong_password(self, async_client_auth):
    response = await async_client_auth.post(
        "/api/v1/auth/login",
        json={"username": "alice", "password": "wrong"},
    )
    assert response.status_code == 401
    body = response.json()
    assert body["code"] != 0
    assert "message" in body
```

## 9. 使用测试工具函数

```python
from tests.utils import build_identity_headers, build_auth_header, make_user_payload

# 构建 Gateway 身份 Header（用于 Info Service 测试）
headers = build_identity_headers(
    user_id="user-001",
    role="TEACHER",
    permissions=["course:read", "offering:read"],
)
# → {"X-User-Id": "user-001", "X-User-Role": "TEACHER", ...}

# 构建 Bearer Token Header（用于 Auth Service 测试）
auth_headers = build_auth_header("my-token")
# → {"Authorization": "Bearer my-token"}

# 生成用户创建 payload
payload = make_user_payload(user_no="S2026002", username="newuser")
# → {"user_no": "S2026002", "username": "newuser", ...}
```

## 10. 最佳实践

### 隔离性

- 每个测试必须**独立可运行**，不能依赖测试执行顺序
- 使用 `scope="function"` 的 fixture 确保每个测试获得全新状态
- 不在测试间共享可变状态

### 确定性

- 使用固定、明确的值，不使用随机生成器
- 显式测试边界条件（空字符串、None、极大值）

### 速度

- 冒烟 + 单元测试应在 10 秒内完成
- 集成测试应在 60 秒内完成
- 需要生产级数据库的测试放入单独的 CI 阶段

### 可读性

- 遵循 Arrange-Act-Assert（AAA）模式，用空行分隔三个阶段
- 类和方法使用中文 docstring（项目约定）
- 变量名使用描述性英文

### 标记

- 每个测试类**必须**有范围标记（smoke/unit/integration）
- 回归测试额外添加 `regression` 标记（可与范围标记叠加）
- 不得无故使用 `@pytest.mark.skip`，如需跳过必须注明原因和 issue 引用

## 11. Docstring 约定

```python
@pytest.mark.unit
class TestGetCurrentUser:
    """测试 get_current_user 依赖 — 从 Gateway 请求头解析 IdentityContext。"""

    async def test_returns_identity_context_with_valid_headers(self):
        """当所有请求头都存在时，应返回包含正确字段的 IdentityContext。"""
        ...

    async def test_raises_when_user_id_missing(self):
        """当 X-User-Id 为 None 或空时，应抛出 AuthenticationError。"""
        ...
```

- 类 docstring：表述测试目标
- 方法 docstring：表述场景和预期行为（"当...时，应..."）
- 使用中文（项目约定）

## 12. CI 集成

```bash
# CI 中分层运行：
uv run pytest -m smoke       # 最快，最先运行
uv run pytest -m unit        # 次快
uv run pytest -m integration # 较慢，可并行
```

项目 CI 配置位于 `.github/workflows/ci.yml`。

## 13. 覆盖率要求

- 总体覆盖率 >= 90%
- P0 AVR 覆盖率 = 100%（定义在 `docs/require-spec/validation_matrices/`）

```bash
uv run pytest --cov=. --cov-report=term-missing
```

## 14. 新测试检查清单

编写新测试时确认以下各项：

- [ ] 类级别正确应用了标记（smoke / unit / integration）
- [ ] 回归测试额外添加了 `@pytest.mark.regression` 并引用 bug 编号
- [ ] 测试类名符合 `Test<功能或模块>` 格式
- [ ] 测试方法名描述场景：`test_<动作>_<预期>`
- [ ] 类和方法的 docstring 使用中文
- [ ] 正确使用 fixture，未重复定义已有 fixture
- [ ] 遵循 AAA 模式
- [ ] 测试可独立运行：`uv run pytest tests/path/to/test.py::TestClass::test_method`
- [ ] 无测试顺序依赖
- [ ] 无网络调用（通过 `async_client_*` fixture 的调用除外）
- [ ] 无磁盘 I/O（in-memory DB 除外）
