# 测试设计文档

## 1. 文档目标

测试要求：

1. 测试基础设施（`conftest.py`、fixture、mock client、测试 DB、测试设计文档）
2. Auth 测试（登录/登出/刷新/改密/验签，含安全边界）
3. 用户域测试（CRUD、批量导入、回收站、跨服务补偿）
4. 课程域测试（课程/开课/排课/校历/培养方案/基础信息）
5. 文件+审计+数据提供测试（上传下载、搜索导出、数据快照）

## 2. 测试策略（单元 vs 集成边界）

### 2.1 分层策略

1. 单元测试（快、定位清晰）
- 目标：纯逻辑函数、权限判断、数据转换、CRUD 轻逻辑。
- 重点模块：
  - `shared/security.py`、`info_service/core/security.py`
  - 各 `crud/*_crud.py` 的查询条件与异常分支
  - 各 `services/*.py` 的业务决策与补偿流程

2. 集成测试（主战场）
- 目标：以 API 为入口验证请求-响应契约、权限、数据一致性、审计副作用。
- 重点模块：
  - `auth_service/api/v1/*.py`
  - `info_service/api/v1/*.py`
- 判定标准：
  - HTTP 状态码、`APIResponse` 结构（`code/message/data/errors`）
  - 数据库状态变化（新增、更新、逻辑删除、恢复、物理删除）
  - 高风险行为审计日志可检索（D-001）

### 2.2 测试目录

```text
tests/
  conftest.py
  factories/
    user_factory.py
    course_factory.py
    calendar_factory.py
  auth_service/
    test_auth.py
    test_internal.py
    test_security.py
  info_service/
    test_users.py
    test_recycle_bin.py
    test_courses.py
    test_calendars.py
    test_files.py
    test_audit.py
    test_data_provision.py
```

## 3. Mock 策略（跨服务调用与环境隔离）

### 3.1 Auth Service 跨服务调用 mock

Info Service 对 Auth Service 的典型调用（创建用户、禁用/启用、角色同步、删除）统一 mock：

1. 单元层：
- 对 `services/user_management_service.py`、`services/recycle_bin_service.py` 中的跨服务客户端方法使用 `monkeypatch` 替换。
- 模拟成功、超时、4xx、5xx，验证补偿与错误传播。

2. 集成层：
- 不访问真实网络。
- 在测试依赖注入中替换 Auth client（fake client），返回固定响应体。

### 3.2 数据库隔离策略

1. 每个测试会话创建独立测试库：
- Auth: `sqlite+aiosqlite:///:memory:` 或临时文件库
- Info: `sqlite+aiosqlite:///:memory:` 或临时文件库
- Audit: `sqlite+aiosqlite:///:memory:` 或临时文件库

2. 每条测试用例事务回滚或重建 schema，保证无状态污染。

3. 迁移策略：
- 需要验证迁移时，先 `alembic upgrade head` 到临时库再执行测试。

### 3.3 文件系统隔离策略

文件测试统一写入 `tmp_path`：

- `upload_dir` 在 fixture 中重定向到临时目录
- 用例结束后自动清理
- 校验 DB 元数据与物理文件一致性

## 4. 数据工厂

### 4.1 命名规范

- 基础 fixture：`seed_*`
- 请求体构造器：`build_*_payload`
- 已登录上下文：`as_admin_headers`、`as_teacher_headers`

### 4.2 用户域 fixture 模板

```python
def build_user_payload(
    user_no: str = "20260001",
    username: str = "alice",
    role_ids: list[int] | None = None,
) -> dict:
    return {
        "user_no": user_no,
        "username": username,
        "role_ids": role_ids or [2],
        "full_name": "Alice Zhang",
        "gender": "F",
        "email": "alice@example.com",
        "phone": "13800000000",
    }
```

### 4.3 课程域 fixture 模板

```python
def build_course_payload(code: str = "CS101") -> dict:
    return {
        "course_code": code,
        "course_name": "Intro to CS",
        "credit": 3,
        "capacity": 80,
        "assessment_method": "exam",
    }
```

### 4.4 校历 fixture 模板

```python
def build_calendar_payload(term_code: str = "2026-FALL") -> dict:
    return {
        "term_code": term_code,
        "term_name": "2026 Fall",
        "start_date": "2026-09-01",
        "end_date": "2027-01-20",
        "version": "1.0",
    }
```

## 5. 参数化矩阵（正常/边界/异常）

### 5.1 用例 ID 规则

- `A-*`：认证与权限
- `B-*`：用户与回收站
- `C-*`：基础信息与数据提供
- `D-*`：审计与非功能

新增 API 细粒度用例建议命名：`<域>-<模块>-<序号>-<类型>`
- 类型：`ok` / `edge` / `err`

### 5.2 参数化模板

```python
@pytest.mark.parametrize(
    "payload, expected_code, expected_http",
    [
        (valid_payload, 0, 200),      # 正常
        (edge_payload, 0, 200),       # 边界
        (invalid_payload, 1001, 400), # 异常
    ],
)
async def test_xxx(payload, expected_code, expected_http, client):
    resp = await client.post("/api/v1/xxx", json=payload)
    assert resp.status_code == expected_http
    body = resp.json()
    assert body["code"] == expected_code
```

### 5.3 按域最小覆盖清单

1. Matrix-A（认证与权限）
- 登录成功/失败
- token 刷新
- 越权拦截
- 角色变更后权限即时生效

2. Matrix-B（用户与回收站）
- 用户新增/编辑/查询
- 逻辑删除与恢复
- 回收站批量物理删除
- CSV 导入仅新增（重复数据不覆盖）
- 跨服务失败补偿（Info 创建成功但 Auth 创建失败时回滚）

3. Matrix-C（基础信息与数据提供）
- 教师名单、待选课名单、校历、选课学生名单、培养方案
- 快照字段 `version` / `snapshot_time` 必返
- 排课冲突检测与教师分配子资源

4. Matrix-D（审计与非功能）
- 高风险操作审计可检索（D-001）
- 密码不明文存储（D-002）
- 性能基线（D-003/D-004）
- 统一错误码与错误提示（D-005）

## 6. CI 集成方案（pytest + SQLite）

### 6.1 本地与 CI 统一命令

```bash
uv run ruff check .
uv run pytest -q
```

### 6.2 分阶段执行

1. 快速集（PR 必跑，<3 分钟）
- `tests/auth_service/test_security.py`
- 用户域与课程域的 P0 核心用例

2. 全量集（合并前或夜间任务）
- `tests/` 全量执行
- 输出覆盖统计与失败用例清单

### 6.3 环境变量

CI 中覆盖默认配置，指向临时 SQLite 与临时上传目录：

```bash
ENV=test
AUTH_DATABASE_URL=sqlite+aiosqlite:///:memory:
INFO_DATABASE_URL=sqlite+aiosqlite:///:memory:
AUDIT_DATABASE_URL=sqlite+aiosqlite:///:memory:
UPLOAD_DIR=/tmp/stss-uploads
```

