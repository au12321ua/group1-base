# 测试报告

## 1. 报告范围

- 报告日期：2026-06-09
- 当前分支：`test/integration`
- 基线提交：`af7372a`（同步自最新 `origin/main` 后创建测试分支）
- 测试框架：`pytest` + `pytest-asyncio` + `pytest-cov`
- 测试边界：按 Router、Service、CRUD、Model 分层统计
- 覆盖对象：`auth_service`、`info_service`、`shared`
- 跨服务场景：`tests/cross_service`

## 2. 参考依据

- `docs/tests/README.md`
- `docs/tests/test-guide.md`
- `docs/TASK_BREAKDOWN.md`
- `docs/test/test-design.md`
- `docs/require-spec/validation_matrices/`
- `docs/design/v2/04-security-architecture.md`
- `docs/design/v2/05-api-architecture.md`

## 3. 测试策略

本项目测试按服务与层次组织。

Router 层使用 ASGI 客户端发起 HTTP 请求，验证请求解析、依赖注入、权限守卫、响应格式和错误响应。

Service 层覆盖业务规则、补偿回滚、跨服务同步、状态流转和异常路径。

CRUD 层使用 SQLite in-memory 数据库，验证查询、分页、过滤、软删除、唯一性和关联数据处理。

Model 与 Schema 层覆盖默认值、枚举、字段校验和序列化行为。

回归测试聚焦已修复问题，包括审计日志 ORM 序列化、用户恢复补偿、跨服务用户生命周期等场景。

## 4. 执行命令

| 目标 | 命令 |
|------|------|
| 收集用例 | `uv run pytest --collect-only -qq` |
| 全量测试 | `uv run pytest` |
| 冒烟测试 | `uv run pytest -m smoke` |
| 单元测试 | `uv run pytest -m unit` |
| 集成测试 | `uv run pytest -m integration` |
| 回归测试 | `uv run pytest -m regression` |
| 覆盖率 | `uv run pytest --cov=auth_service --cov=info_service --cov=shared --cov-report=term-missing` |
| Ruff | `uv run ruff check .` |

## 5. 本地执行记录

| 命令 | 结果 | 备注 |
|------|------|------|
| `UV_CACHE_DIR=/tmp/uv-cache uv run pytest --collect-only -qq` | 通过 | 收集到 402 条测试样例，耗时约 9.24s |
| `UV_CACHE_DIR=/tmp/uv-cache uv run pytest --cov=auth_service --cov=info_service --cov=shared --cov-report=term-missing` | 未完成 | 当前受限沙箱中卡在 Auth API 首个集成用例，已终止 |
| `UV_CACHE_DIR=/tmp/uv-cache BCRYPT_COST_FACTOR=4 timeout 60 uv run pytest tests/auth_service/test_auth_api.py::TestAuthAPI::test_internal_create_login_me_and_verify -vv -s` | 超时 | 降低 bcrypt cost 后仍超时，需在本机或 CI 环境复验 |

说明：本报告的样例数量来自 pytest collection。当前沙箱未产出可信覆盖率结果，因此最终通过数和覆盖率以后续 CI 或本机环境运行结果为准。

## 6. 测试分类汇总

| 范围 | 用例数 | 覆盖重点 |
|------|--------|----------|
| Auth Service | 79 | 登录、登出、刷新、改密、内部用户、Service Token、JWT、RBAC、Token/Session CRUD |
| Info Service | 251 | 用户、课程、开课、排课、校历、基础信息、文件、审计、回收站、数据供给 |
| Shared | 55 | 数据库依赖、错误处理、路由挂载、安全上下文 |
| Cross Service | 1 | Auth 与 Info 用户生命周期联动 |
| Smoke / Infra | 16 | App 可达、OpenAPI、DB、测试工具函数 |
| 合计 | 402 | pytest 可收集测试样例总数 |

## 7. 按文件汇总的测试样例

本节不逐条展开全部 402 个 nodeid，改为按测试文件汇总。完整 nodeid 可通过 `uv run pytest --collect-only -qq` 重新生成。

### Auth Service

| 测试文件 | 用例数 | 主要场景 |
|----------|--------|----------|
| `tests/auth_service/test_auth_api.py` | 22 | Auth HTTP API、内部接口、Service Token 鉴权边界 |
| `tests/auth_service/test_auth_service.py` | 11 | 登录、锁定、刷新、登出、内部用户生命周期 |
| `tests/auth_service/test_credential_crud.py` | 4 | 凭据查询、失败计数、锁定、密码更新、删除 |
| `tests/auth_service/test_exceptions.py` | 1 | 异常模块 re-export |
| `tests/auth_service/test_identity_service.py` | 3 | access/service token 身份解析 |
| `tests/auth_service/test_models.py` | 3 | Auth 模型默认值和关联持久化 |
| `tests/auth_service/test_password_policy.py` | 10 | 管理员和普通用户密码策略 |
| `tests/auth_service/test_permission_crud.py` | 2 | 权限查询和角色权限映射 |
| `tests/auth_service/test_role_crud.py` | 4 | 角色查询、激活过滤、用户角色分配 |
| `tests/auth_service/test_security.py` | 11 | JWT、密码哈希、过期、篡改、密钥 ID |
| `tests/auth_service/test_session_crud.py` | 4 | 会话创建、结束、过期、用户级删除 |
| `tests/auth_service/test_token_crud.py` | 4 | Token 创建、撤销、哈希存储、用户级删除 |

### Info Service

| 测试文件 | 用例数 | 主要场景 |
|----------|--------|----------|
| `tests/info_service/test_audit_logs_api.py` | 2 | 审计日志查询、导出 |
| `tests/info_service/test_audit_service.py` | 6 | 审计写入、过滤查询、CSV 导出 |
| `tests/info_service/test_auth_http_client.py` | 5 | Auth HTTP 客户端 token 缓存和内部路径封装 |
| `tests/info_service/test_base_crud.py` | 1 | 基础 CRUD 排序 |
| `tests/info_service/test_base_info_api.py` | 4 | 基础信息 CRUD、重复校验、权限、分页校验 |
| `tests/info_service/test_base_info_crud.py` | 11 | 基础信息创建、查询、分页、分类、更新、删除 |
| `tests/info_service/test_base_info_service.py` | 9 | 基础信息 Service 层 CRUD 与分类过滤 |
| `tests/info_service/test_calendar_api.py` | 5 | 校历 API 校验、权限、更新、删除 |
| `tests/info_service/test_calendar_crud.py` | 14 | 校历 CRUD、term/date 查询、边界日期 |
| `tests/info_service/test_calendar_service.py` | 9 | 校历 Service 层创建、查询、更新、删除 |
| `tests/info_service/test_classroom_api.py` | 4 | 教室 CRUD、过滤、重复 room_no、分页校验 |
| `tests/info_service/test_classroom_crud.py` | 3 | 教室按房间号查询、过滤、删除 |
| `tests/info_service/test_course_api.py` | 9 | 课程 CRUD、先修课、软删除后编码复用、权限 |
| `tests/info_service/test_course_crud.py` | 7 | 课程查询、过滤、逻辑删除、先修课 |
| `tests/info_service/test_course_management_service.py` | 11 | 课程、开课、排课、教师分配服务规则 |
| `tests/info_service/test_data_provision_api.py` | 4 | 教师、候选学生、校历、培养方案数据供给 |
| `tests/info_service/test_data_provision_service.py` | 3 | 数据供给过滤、分页、培养方案课程解析 |
| `tests/info_service/test_deps.py` | 6 | Gateway 身份头解析和默认 request id |
| `tests/info_service/test_file_api.py` | 4 | 文件上传、元数据、下载、删除、权限 |
| `tests/info_service/test_file_resource_crud.py` | 5 | 文件资源 CRUD 与 owner 查询 |
| `tests/info_service/test_file_storage_service.py` | 10 | 文件类型、大小、路径、读取、删除权限 |
| `tests/info_service/test_offering_api.py` | 7 | 开课 CRUD、重复身份、教师访问控制 |
| `tests/info_service/test_offering_crud.py` | 3 | 开课过滤、课程学期查询、删除 |
| `tests/info_service/test_offering_route_units.py` | 9 | 开课路由辅助函数、审计记录、响应组装 |
| `tests/info_service/test_recycle_bin_api.py` | 3 | 回收站恢复、批量物理删除、回滚回归 |
| `tests/info_service/test_recycle_bin_service.py` | 7 | 已删除用户列表、恢复、物理删除、批量删除 |
| `tests/info_service/test_reexports.py` | 2 | 模块 re-export |
| `tests/info_service/test_schedule_api.py` | 12 | 排课 CRUD、冲突检测、教师分配、访问控制 |
| `tests/info_service/test_schedule_crud.py` | 2 | 排课排序和冲突检测 |
| `tests/info_service/test_schedule_route_units.py` | 16 | 排课路由辅助函数、审计记录、教师分配响应 |
| `tests/info_service/test_security_utils.py` | 6 | 权限头解析和资源访问判断 |
| `tests/info_service/test_training_program_api.py` | 5 | 培养方案 CRUD、未知课程、权限 |
| `tests/info_service/test_training_program_crud.py` | 3 | 培养方案编码、专业年级、过滤 |
| `tests/info_service/test_user_api.py` | 12 | 用户 CRUD、导入、Auth 同步回滚、访问控制 |
| `tests/info_service/test_user_crud.py` | 17 | 用户和 profile CRUD、软删除、恢复、物理删除 |
| `tests/info_service/test_user_management_service.py` | 15 | 用户 Service 创建、更新、删除、导入、补偿回滚 |

### Cross Service / Shared / Infra

| 测试文件 | 用例数 | 主要场景 |
|----------|--------|----------|
| `tests/cross_service/test_user_lifecycle.py` | 1 | 用户创建、禁用、恢复、物理删除的 Auth/Info 联动 |
| `tests/shared/test_database.py` | 6 | DB session、commit、rollback、engine 隔离 |
| `tests/shared/test_error_handlers.py` | 26 | 统一异常到 APIResponse 的状态码、错误体、兜底 |
| `tests/shared/test_main_wiring.py` | 10 | Auth/Info 路由注册、lifespan、错误处理挂载 |
| `tests/shared/test_security.py` | 13 | 身份头依赖、权限检查器、IdentityContext |
| `tests/test_infra.py` | 16 | App 可达、OpenAPI、Auth/Info/Audit DB、工具函数 |

## 8. 关键覆盖场景

| 领域 | 覆盖场景 |
|------|----------|
| 认证授权 | 登录、刷新、登出、改密、Service Token、Access Token 冒用内部接口 |
| 内部同步 | Info 创建/删除用户时同步 Auth，失败时验证补偿回滚 |
| 用户管理 | 用户 CRUD、批量导入、软删除、恢复、物理删除、角色同步 |
| 课程管理 | 课程 CRUD、先修课、开课、排课冲突、教师分配 |
| 基础数据 | 校历、教室、基础信息、培养方案、数据供给 |
| 文件 | 上传、下载、删除、类型校验、大小校验、owner/admin 权限 |
| 审计 | 写入、查询、导出、ORM 响应序列化回归 |
| 共享能力 | 统一错误响应、DB session、OpenAPI 路由挂载 |

## 9. 风险与复验建议

- 在 CI 或本机非沙箱环境运行全量测试和覆盖率，确认最终通过数与覆盖率。
- 若 Auth API 集成用例继续超时，优先检查 `async_client_auth`、内部用户创建接口、审计 DB 依赖和 ASGI 请求生命周期。
- 网关联调测试应在 `STSS-gateway` 仓库通过 Compose 启动 gateway、auth_service、info_service、seed 后，从 `http://localhost:8000` 入口验证。
- 测试报告不替代 CI 结果；PR 合并前仍应以 CI 运行结果作为准入依据。

## 10. 验证矩阵映射

| 验证矩阵 | 对应测试范围 | 代表性测试文件 |
|----------|--------------|----------------|
| `matrix-a-auth-permission.md` | 登录、token、权限、内部接口鉴权 | `tests/auth_service/test_auth_api.py`、`tests/auth_service/test_security.py`、`tests/shared/test_security.py` |
| `matrix-b-user-recyclebin.md` | 用户 CRUD、导入、软删除、恢复、物理删除 | `tests/info_service/test_user_api.py`、`tests/info_service/test_recycle_bin_api.py`、`tests/cross_service/test_user_lifecycle.py` |
| `matrix-c-baseinfo-data-provision.md` | 课程、开课、排课、校历、基础信息、数据供给 | `tests/info_service/test_course_api.py`、`tests/info_service/test_schedule_api.py`、`tests/info_service/test_data_provision_api.py` |
| `matrix-d-audit-nfr.md` | 审计、错误响应、基础设施、非功能行为 | `tests/info_service/test_audit_logs_api.py`、`tests/shared/test_error_handlers.py`、`tests/test_infra.py` |

## 11. 分层覆盖明细

| 层次 | 覆盖方式 | 关注点 |
|------|----------|--------|
| Router | `async_client_auth`、`async_client_info` HTTP 请求 | 路由注册、依赖注入、状态码、统一响应体 |
| Service | 直接调用服务对象，必要时 mock 外部依赖 | 业务规则、补偿回滚、状态流转 |
| CRUD | in-memory SQLite + `AsyncSession` | 查询条件、分页、排序、唯一性、软删除 |
| Model / Schema | 模型实例化和响应序列化 | 默认值、枚举、字段校验、ORM 转换 |
| Cross Service | Auth ASGI bridge + Info API | 用户生命周期跨服务一致性 |
| Infra | OpenAPI、DB fixture、工具函数 | 测试基础设施可用性 |

## 12. 提交前复验清单

| 检查项 | 命令 | 预期 |
|--------|------|------|
| 收集全部用例 | `uv run pytest --collect-only -qq` | 能收集到当前分支全部测试 |
| 冒烟测试 | `uv run pytest -m smoke` | App、DB、工具函数均通过 |
| 单元测试 | `uv run pytest -m unit` | CRUD、Service、工具函数通过 |
| 集成测试 | `uv run pytest -m integration` | Router 到 DB 链路通过 |
| 回归测试 | `uv run pytest -m regression` | 已修复问题不复发 |
| 全量测试 | `uv run pytest` | 全部测试通过 |
| 覆盖率 | `uv run pytest --cov=auth_service --cov=info_service --cov=shared --cov-report=term-missing` | 覆盖率满足 CI gate |
| Ruff | `uv run ruff check .` | 无 lint 错误 |
| 网关联调 | `STSS-gateway` 中通过 Compose 启动服务 | `http://localhost:8000/api/v1/health` 可访问 |
| PR 文档 | 检查测试报告和 PR 描述 | 风险、命令、结果说明完整 |

## 13. 后续维护建议

- 新增业务接口时，同步补充 Router 集成测试和 Service 层边界测试。
- 修复线上或 CI 问题时，补充 `regression` 标记测试，避免问题回归。
- 修改共享 fixture 前，先搜索消费者，避免破坏跨服务测试。
- 报告中的测试数量应随 `pytest --collect-only -qq` 结果更新。
- 覆盖率最终值应以 CI 或本机非沙箱环境为准。

## 14. 结论

当前分支可收集 402 条 pytest 测试样例，覆盖 Auth Service、Info Service、Shared 和跨服务用户生命周期。

测试体系已覆盖主要 P0/P1 链路：认证授权、用户同步、课程排课、基础数据、文件、审计和回收站。

本报告已压缩为按文件汇总的测试索引，避免逐条列出 402 个 nodeid，同时保留完整覆盖范围和复验路径。
