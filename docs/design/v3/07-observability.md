# 07 — 可观测性设计

## 1. 日志体系

### 1.1 架构概览

```
┌─────────────────────────────────────────────────┐
│                    日志系统                       │
├─────────────────┬───────────────────────────────┤
│   应用日志       │         审计日志               │
│  (AppLogger)    │       (AuditService)          │
│                 │                               │
│ ▪ 控制台输出     │  ▪ 独立 Audit DB (audit.db)     │
│ ▪ 文件按天轮转   │  ▪ 高风险操作 + 数据提供记录   │
│ ▪ JSON 格式     │  ▪ 不可抵赖                    │
│ ▪ 四级分级       │  ▪ 支持检索 + CSV 导出         │
└─────────────────┴───────────────────────────────┘
```

### 1.2 日志级别定义

| 级别 | 用途 | 示例 |
|------|------|------|
| DEBUG | 开发调试信息 | SQL 语句、函数入参/出参 |
| INFO | 关键业务流程节点 | 用户登录成功、数据创建、Token 签发 |
| WARN | 需关注但非致命的异常 | 登录失败（未锁定）、补偿重试 |
| ERROR | 错误与异常 | 跨服务调用失败、补偿操作失败、未处理异常 |

### 1.3 AppLogger 设计

`shared/logging.py` 提供统一的日志基础设施：

- **`AppLogger`**：统一日志封装，JSON 格式输出，自动注入 `request_id`、`timestamp`、`service_name`
- **`LoggingService`**：服务级日志管理器
- **`RequestIDMiddleware`**：FastAPI 中间件，读取/生成 `X-Request-ID` 并存入 `ContextVar`
- **`RequestLoggingMiddleware`**：FastAPI 中间件，记录每个 HTTP 请求的 method、path、status_code、duration_ms

**JSON 输出格式**：
```json
{
  "timestamp": "2026-05-12T10:30:00.123Z",
  "level": "INFO",
  "service": "info_service",
  "logger": "user_management",
  "message": "User created successfully",
  "request_id": "req_9aef8a7d",
  "user_id": "42",
  "target_id": "100"
}
```

### 1.4 日志配置

```python
# 开发环境
LOG_LEVEL = "DEBUG"
LOG_OUTPUT = "console"        # 控制台
LOG_FORMAT = "json"

# 生产环境
LOG_LEVEL = "INFO"
LOG_OUTPUT = "file"           # 文件
LOG_DIR = "/var/log/stss/"
LOG_ROTATION = "daily"        # 按天轮转
LOG_RETENTION = 30            # 保留 30 天
```

## 2. 审计日志

### 2.1 审计日志模型

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | int | 主键 |
| `operator_user_id` | string | 操作者 userId |
| `operator_role` | string | 操作者角色 |
| `target_type` | string | 操作目标类型（user, course, role 等） |
| `target_id` | string | 操作目标 ID |
| `action` | string | 操作类型（create, update, delete, import 等） |
| `result` | string | 操作结果（success / failed） |
| `reason` | string | 操作原因/备注 |
| `request_id` | string | 关联请求 ID |
| `created_at` | datetime | 记录时间 |

### 2.2 需审计的操作

| 操作类别 | 具体操作 | target_type |
|----------|----------|-------------|
| 用户管理 | 创建用户、批量导入 | user |
| 用户管理 | 逻辑删除、物理删除 | user |
| 用户管理 | 角色变更、状态变更 | user |
| 权限管理 | 密码重置 | credential |
| 课程管理 | 创建/删除课程 | course |
| 数据提供 | 查询教师名单、校历等 | data_provision |
| 回收站 | 恢复、物理删除 | recycle_bin |

### 2.3 审计日志检索

- 支持过滤条件：时间范围、操作者、操作类型、目标类型、结果。
- 支持分页。
- 支持 CSV 导出（`/audit-logs/export`）。
- 访问控制：仅 `audit:read` 权限可查询（SYS_ADMIN）。

## 3. 链路追踪

### 3.1 X-Request-ID 全链路透传

```
Client → Nginx Gateway → Auth Service → Info Service
   │           │                │              │
   └── 生成 X-Request-ID ──────┴──────────────┘
        (若无则生成 UUID)      透传不修改      透传不修改
```

- **生成**：Gateway 在请求入口生成 `X-Request-ID`（UUID v4），若上游已传则透传。
- **透传**：Auth Service 和 Info Service 的 `RequestIDMiddleware` 读取并透传，所有日志自动注入 `request_id`。
- **存储**：通过 Python `contextvars.ContextVar` 存储，确保异步安全。

### 3.2 请求日志

每个 HTTP 请求由 `RequestLoggingMiddleware` 记录一条 INFO 日志：

```json
{
  "timestamp": "2026-05-12T10:30:00.123Z",
  "level": "INFO",
  "service": "info_service",
  "message": "Request completed",
  "request_id": "req_9aef8a7d",
  "method": "GET",
  "path": "/api/v1/info/users",
  "status_code": 200,
  "duration_ms": 45,
  "user_id": "42"
}
```

### 3.3 错误追踪

- ERROR 级别日志务必包含：`exception_type`、`traceback`、`request_id`。
- 跨服务调用失败：同时记录 `target_service`、`target_url`、`response_status`。
- 补偿操作失败：记录完整 `payload`，写入 `dead_letter_queue` 表。

## 4. 可观测性演进路线

| 阶段 | 能力 | 说明 |
|------|------|------|
| 原型（当前） | JSON 日志 + request_id 串联 | 通过 `grep request_id` 手动排查 |
| 中期 | ELK / Loki 集中日志 | 结构化查询、自动聚合 |
| 远期 | OpenTelemetry 全链路 | Trace + Metrics + Logs 三位一体 |

> 原型阶段基础设施简单，优先保证日志结构化与 request_id 透传，确保出问题时能快速定位。两个中间件（`RequestIDMiddleware`、`RequestLoggingMiddleware`）已实现并注册到 FastAPI app。
