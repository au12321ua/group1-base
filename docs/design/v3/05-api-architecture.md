# 05 — API 架构

## 1. 设计规范

### 1.1 通用约定

| 约定 | 规则 |
|------|------|
| 前缀 | 对外：`/api/v1/`（Auth: `/api/v1/auth/*`；Info: `/api/v1/info/*`）；内部：`/api/v1/internal/*` |
| 风格 | RESTful |
| 请求格式 | `application/json`（文件上传除外：`multipart/form-data`） |
| 响应格式 | 统一 `{code, message, data}` |
| 认证 | Bearer Token（`Authorization: Bearer <token>`） |
| 链路追踪 | `X-Request-ID` Header 全链路透传 |

### 1.2 通用 Query 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `page` | int | 1 | 页码，从 1 开始 |
| `page_size` | int | 20 | 每页数量，最大 100 |
| `sort_by` | string | — | 排序字段名 |
| `sort_order` | string | asc | asc / desc |
| `keyword` | string | — | 模糊搜索关键词 |
| `status` | string | — | 状态过滤 |

### 1.3 响应格式

**列表响应**：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [...],
    "pagination": {"total": 100, "page": 1, "page_size": 20}
  }
}
```

**单体响应**：
```json
{
  "code": 0,
  "message": "success",
  "data": { "id": 1, "name": "张三" }
}
```

**错误响应**：
```json
{
  "code": 1001,
  "message": "Authentication failed",
  "errors": [{"field": "password", "message": "Password is incorrect"}]
}
```

### 1.4 幂等约定

| 方法 | 幂等性 | 说明 |
|------|--------|------|
| GET | 是 | 查询不产生副作用 |
| PUT | 是 | 全量更新，重复调用结果一致 |
| DELETE | 是 | 重复删除返回成功（204） |
| POST | 否 | 创建/批量追加可能产生重复资源 |
| PATCH | 否 | 局部更新可能依赖当前状态 |

### 1.5 关联关系 API 设计

- **纯关系**（如教师-排课）：嵌套路径 `/schedules/{id}/teachers`。
- **含业务属性**：独立资源路径。
- 关系查询过滤优先使用主列表 + Query 参数。

## 2. API 端点清单

### 2.1 Auth Service — 公开端点

| 路径 | 方法 | 说明 | 鉴权 |
|------|------|------|------|
| `/auth/login` | POST | 用户登录，返回 Token 对 | 无 |
| `/auth/sys/login` | POST | 系统服务登录，返回 Service Token | client_id/client_secret |
| `/auth/logout` | POST | 登出，撤销 Refresh Token | Access Token |
| `/auth/refresh` | POST | 刷新 Token 对 | Refresh Token |
| `/auth/me` | GET | 当前用户信息 | Access Token（仅 user access） |
| `/auth/change-password` | POST | 修改密码 | Access Token |

### 2.2 Auth Service — 内部端点（/internal/*）

> 所有内部端点要求 Service Token 鉴权。

| 路径 | 方法 | 说明 | 调用方 |
|------|------|------|--------|
| `/internal/verify` | POST | 验证 JWT，返回身份信息 | Gateway |
| `/internal/users` | POST | 创建认证用户（credentials + 角色） | Info Service |
| `/internal/users/{user_id}/disable` | POST | 禁用用户 | Info Service |
| `/internal/users/{user_id}/enable` | POST | 启用用户 | Info Service |
| `/internal/users/{user_id}/roles` | POST | 同步角色（替换全部角色分配） | Info Service |
| `/internal/users/roles/batch` | POST | 批量查询用户角色 | Info Service |
| `/internal/users/{user_id}` | DELETE | 物理删除所有认证数据 | Info Service |

### 2.3 Info Service — 用户管理

| 路径 | 方法 | 说明 | 权限 |
|------|------|------|------|
| `/users` | GET | 用户列表（分页、搜索） | `user:read` |
| `/users` | POST | 创建用户（跨服务同步） | `user:create` |
| `/users/{id}` | GET | 用户详情（含档案） | `user:read` |
| `/users/{id}` | PUT | 全量更新用户 | `user:update` |
| `/users/{id}` | PATCH | 局部更新用户 | `user:update` |
| `/users/{id}` | DELETE | 逻辑删除 → 回收站 | `user:delete` |
| `/users/import` | POST | CSV 批量导入 | `user:create` |

### 2.4 Info Service — 课程

| 路径 | 方法 | 说明 | 权限 |
|------|------|------|------|
| `/courses` | GET | 课程列表 | `course:read` |
| `/courses` | POST | 创建课程 | `course:create` |
| `/courses/{id}` | GET | 课程详情 | `course:read` |
| `/courses/{id}` | PUT | 全量更新 | `course:update` |
| `/courses/{id}` | PATCH | 局部更新 | `course:update` |
| `/courses/{id}` | DELETE | 删除课程（软删除） | `course:delete` |
| `/courses/{id}/prerequisites` | GET | 先修课程列表 | `course:read` |
| `/courses/{id}/prerequisites` | POST | 添加先修课程 | `course:update` |
| `/courses/{id}/prerequisites/{prereq_id}` | DELETE | 移除先修课程 | `course:update` |

### 2.5 Info Service — 开课

| 路径 | 方法 | 说明 | 权限 |
|------|------|------|------|
| `/offerings` | GET | 开课列表 | `offering:read` |
| `/offerings` | POST | 创建开课 | `offering:create` |
| `/offerings/{id}` | GET | 开课详情 | `offering:read` |
| `/offerings/{id}` | PUT | 全量更新 | `offering:update` |
| `/offerings/{id}` | PATCH | 局部更新 | `offering:update` |
| `/offerings/{id}` | DELETE | 删除开课 | `offering:delete` |

### 2.6 Info Service — 排课

| 路径 | 方法 | 说明 | 权限 |
|------|------|------|------|
| `/schedules` | GET | 排课列表 | `schedule:read` |
| `/schedules` | POST | 创建排课 | `schedule:create` |
| `/schedules/{id}` | GET | 排课详情 | `schedule:read` |
| `/schedules/{id}` | PUT | 全量更新 | `schedule:update` |
| `/schedules/{id}` | PATCH | 局部更新 | `schedule:update` |
| `/schedules/{id}` | DELETE | 删除排课 | `schedule:delete` |
| `/schedules/{id}/teachers` | GET | 教师列表 | `schedule:read` |
| `/schedules/{id}/teachers` | PUT | 全量替换教师 | `schedule:update` |
| `/schedules/{id}/teachers` | POST | 增量添加教师 | `schedule:update` |
| `/schedules/{id}/teachers/{tid}` | PUT | 单条分配 | `schedule:update` |
| `/schedules/{id}/teachers/{tid}` | DELETE | 单条解除 | `schedule:update` |

### 2.7 Info Service — 教室

| 路径 | 方法 | 说明 | 权限 |
|------|------|------|------|
| `/classrooms` | GET | 教室列表 | `classroom:read` |
| `/classrooms` | POST | 创建教室 | `classroom:create` |
| `/classrooms/{id}` | GET | 教室详情 | `classroom:read` |
| `/classrooms/{id}` | PUT | 全量更新 | `classroom:update` |
| `/classrooms/{id}` | PATCH | 局部更新 | `classroom:update` |
| `/classrooms/{id}` | DELETE | 删除教室 | `classroom:delete` |

> **注意**：教室端点（classrooms）在 V2 设计文档中未列出，V3 补充。教室资源被排课（schedules）引用。

### 2.8 Info Service — 校历

| 路径 | 方法 | 说明 | 权限 |
|------|------|------|------|
| `/calendars` | GET | 校历列表 | `calendar:read` |
| `/calendars` | POST | 创建校历 | `calendar:create` |
| `/calendars/{id}` | GET | 校历详情 | `calendar:read` |
| `/calendars/{id}` | PUT | 全量更新 | `calendar:update` |
| `/calendars/{id}` | PATCH | 局部更新 | `calendar:update` |
| `/calendars/{id}` | DELETE | 删除校历 | `calendar:delete` |
| `/calendars/by-term` | GET | 按学期查询 | `calendar:read` |

### 2.9 Info Service — 培养方案

| 路径 | 方法 | 说明 | 权限 |
|------|------|------|------|
| `/training-programs` | GET | 培养方案列表 | `training:read` |
| `/training-programs` | POST | 创建培养方案 | `training:create` |
| `/training-programs/{id}` | GET | 方案详情 | `training:read` |
| `/training-programs/{id}` | PUT | 全量更新 | `training:update` |
| `/training-programs/{id}` | PATCH | 局部更新 | `training:update` |
| `/training-programs/{id}` | DELETE | 删除方案 | `training:delete` |
| `/training-programs/by-major` | GET | 按专业/年级/版本查询 | `training:read` |

### 2.10 Info Service — 基础信息

| 路径 | 方法 | 说明 | 权限 |
|------|------|------|------|
| `/base-info` | GET | 基础信息列表 | `base-info:read` |
| `/base-info` | POST | 新增条目 | `base-info:create` |
| `/base-info/{id}` | GET | 条目详情 | `base-info:read` |
| `/base-info/{id}` | PUT | 全量更新 | `base-info:update` |
| `/base-info/{id}` | PATCH | 局部更新 | `base-info:update` |
| `/base-info/{id}` | DELETE | 删除条目 | `base-info:delete` |

### 2.11 Info Service — 回收站

| 路径 | 方法 | 说明 | 权限 |
|------|------|------|------|
| `/recycle-bin` | GET | 已删除用户列表 | `recycle:read` |
| `/recycle-bin/{id}/restore` | POST | 恢复单个用户 | `recycle:restore` |
| `/recycle-bin/{id}` | DELETE | 物理删除单个 | `recycle:delete` |
| `/recycle-bin/batch-delete` | POST | 批量物理删除 | `recycle:delete` |

### 2.12 Info Service — 文件

| 路径 | 方法 | 说明 | 权限 |
|------|------|------|------|
| `/files` | POST | 上传文件 | 需认证 |
| `/files/{id}` | GET | 文件元数据 | 需认证 |
| `/files/{id}/download` | GET | 下载文件 | 需认证 |
| `/files/{id}` | DELETE | 删除文件 | 拥有者或管理员 |

### 2.13 Info Service — 审计日志

| 路径 | 方法 | 说明 | 权限 |
|------|------|------|------|
| `/audit-logs` | GET | 检索审计日志 | `audit:read` |
| `/audit-logs/export` | GET | CSV 导出 | `audit:read` |

### 2.14 Info Service — 数据提供（面向 B/C/F）

| 路径 | 方法 | 说明 | 消费方 | 鉴权 |
|------|------|------|--------|------|
| `/data-provision/teachers` | GET | 教师名单 | B 排课 | Service Token |
| `/data-provision/candidate-students` | GET | 待选课名单 | B 排课 | Service Token |
| `/data-provision/calendars` | GET | 校历 | B 排课 | Service Token |
| `/data-provision/training-programs` | GET | 培养方案 | C 选课 | Service Token |

> `/data-provision/*` 接口返回均含 `snapshotTime` 或 `version` 字段，供消费方做数据版本比对。

## 3. 错误码体系

| HTTP 状态码 | 业务码 | 场景 |
|-------------|--------|------|
| 400 | — | 请求参数格式/校验错误 |
| 401 | — | 缺少 Token、Token 无效、Token 过期 |
| 403 | — | 权限不足（角色或资源级） |
| 404 | — | 资源不存在 |
| 409 | — | 资源冲突（唯一约束违反） |
| 423 | 4233 | 账号已锁定（登录保护） |
| 429 | — | 请求频率限制 |
| 500 | — | 服务器内部错误 |

### 3.1 Auth Service 业务码

| 业务码 | 说明 |
|--------|------|
| 1001 | 用户名或密码错误 |
| 1002 | 账号已被禁用 |
| 1003 | 账号已锁定（请稍后重试） |
| 1004 | Refresh Token 无效或已过期 |
| 1005 | 旧密码错误 |
| 1006 | 新密码不符合策略 |
| 1007 | Service 凭据无效 |
| 1008 | 网关身份头缺失（X-User-Id/X-User-Role/X-User-Permissions）|
