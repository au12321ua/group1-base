# 任务分工建议

> 4 开发 + 1 测试，按模块拆分。每个人独立分支工作，通过 PR 合入 main。

---

## 1. 模块总览

### Dev-A：Auth Service（认证授权）— 1 人

| 层 | 文件 | 说明 |
|-----|------|------|
| Core | `core/security.py` | JWT 签发/验签、密码哈希 |
| Core | `core/config.py` | 已完成 |
| CRUD | `crud/credential_crud.py` | 凭据增删改查 |
| CRUD | `crud/token_crud.py` | Token 记录管理 |
| CRUD | `crud/session_crud.py` | 会话管理 |
| CRUD | `crud/role_crud.py` | 角色 CRUD + 用户角色关联 |
| CRUD | `crud/permission_crud.py` | 权限查询 |
| Service | `services/auth_service.py` | 登录/登出/刷新/改密 |
| Service | `services/key_service.py` | JWKS 公钥发布 |
| Service | `services/identity_service.py` | 内部验签 |
| API | `api/v1/auth.py` | 7 个公开端点 |
| API | `api/v1/internal.py` | 6 个内部端点 |
| Test | `tests/auth_service/` | 13 个端点 + 安全测试 |

**13 个端点** · 建议顺序：Core → CRUD → Service → API

### Dev-B：Info Service — 用户域 — 1 人

| 层 | 文件 | 说明 |
|-----|------|------|
| CRUD | `crud/user_crud.py` | 用户 CRUD + 逻辑删除 |
| CRUD | `crud/user_profile_crud.py` | 用户档案 |
| Service | `services/user_management_service.py` | 创建用户（含跨服务同步+补偿）、更新/删除/批量导入 |
| Service | `services/recycle_bin_service.py` | 回收站操作（含恢复时的跨服务调用） |
| API | `api/v1/users.py` | 8 个端点 |
| API | `api/v1/recycle_bin.py` | 4 个端点 |
| Test | `tests/info_service/test_users.py` | 用户 CRUD + 导入 |
| Test | `tests/info_service/test_recycle_bin.py` | 回收站 |

**12 个端点** · 关键难点：跨服务同步 Auth Service（创建用户时调用 `/internal/users`，失败需补偿回滚）

### Dev-C：Info Service — 课程域 — 1 人

| 层 | 文件 | 说明 |
|-----|------|------|
| CRUD | `crud/course_crud.py` | 课程 CRUD |
| CRUD | `crud/offering_crud.py` | 课程开课 |
| CRUD | `crud/schedule_crud.py` | 排课时间 + 冲突检测 |
| CRUD | `crud/classroom_crud.py` | 教室管理 |
| CRUD | `crud/calendar_crud.py` | 校历 |
| CRUD | `crud/training_program_crud.py` | 培养方案 |
| Service | `services/course_management_service.py` | 30+ 方法，覆盖课程/开课/排课/教师分配/校历/培养方案/基础信息 |
| API | `api/v1/courses.py` | 6 个端点 |
| API | `api/v1/offerings.py` | 6 个端点 |
| API | `api/v1/schedules.py` | 11 个端点（含教师分配子资源） |
| API | `api/v1/calendars.py` | 7 个端点 |
| API | `api/v1/training_programs.py` | 7 个端点 |
| API | `api/v1/base_info.py` | 6 个端点 |
| Test | `tests/info_service/test_courses.py` | 课程/开课/排课 |
| Test | `tests/info_service/test_calendars.py` | 校历/培养方案/基础信息 |

**43 个端点** · 关键难点：排课时间冲突检测、教师分配子资源嵌套

### Dev-D：Info Service — 文件/数据提供/基础设施 — 1 人

| 层 | 文件 | 说明 |
|-----|------|------|
| CRUD | `crud/base_info_crud.py` | 基础信息项 |
| CRUD | `crud/file_resource_crud.py` | 文件资源 |
| CRUD | `crud/audit_log_crud.py` | 审计日志写入/查询 |
| Service | `services/file_storage_service.py` | 文件上传/下载/删除 |
| Service | `services/audit_service.py` | 审计日志搜索/导出 |
| Service | `services/data_provision_service.py` | 数据快照提供（给 B/C/F 系统） |
| API | `api/v1/files.py` | 3 个端点 |
| API | `api/v1/audit_logs.py` | 2 个端点 |
| API | `api/v1/data_provision.py` | 5 个端点 |
| Test | `tests/info_service/test_files.py` | 文件上传/下载/删除 |
| Test | `tests/info_service/test_audit.py` | 审计日志 |
| Test | `tests/info_service/test_data_provision.py` | 数据提供 |

**10 个端点** · 关键难点：文件存储路径管理、审计日志独立数据库读写

**此角色同时负责**：Alembic 迁移脚本、`shared/` 库的补充维护。

---

## 2. 测试拆解（QA-1）

| 阶段 | 产出 | 覆盖范围 |
|------|------|----------|
| 1 | 测试基础设施 | `conftest.py`（fixture、mock client、测试 DB）、测试设计文档 |
| 2 | Auth 测试 | 登录/登出/刷新/改密/验签，含安全边界（锁定、过期、越权） |
| 3 | 用户域测试 | 用户 CRUD + 批量导入 + 回收站恢复/删除，含跨服务补偿场景 |
| 4 | 课程域测试 | 课程/开课/排课/校历/培养方案/基础信息，含排课冲突、嵌套资源 |
| 5 | 文件+审计+数据提供测试 | 文件上传下载、审计搜索导出、数据快照 |

### 测试设计文档大纲

```
1. 测试策略：单元 vs 集成测试边界
2. Mock 策略：Auth Service 调用如何 mock、数据库如何隔离
3. 数据工厂：测试用户/课程/校历的 fixture 模板
4. 参数化矩阵：每个端点的正常/边界/异常路径
5. CI 集成：pytest 如何在 CI 中运行（SQLite 内存库）
```

直接参考 `docs/require-spec/validation_matrices/` 下的 4 份验证矩阵来写用例。

---

## 3. 分工总览

| 角色 | 模块 | 端点 | 工作量评估 |
|------|------|------|-----------|
| **Dev-A** | Auth Service 全部 | 13 | 中等（安全敏感，逻辑密度高） |
| **Dev-B** | Info Service 用户域 | 12 | 中等（跨服务通信是唯一难点） |
| **Dev-C** | Info Service 课程域 | 43 | 较大（端点最多，但模式重复） |
| **Dev-D** | Info Service 文件/审计/数据提供 + 基础设施 | 10 + CI | 中等（领域分散但每个都简单） |
| **QA-1** | 全量测试 | 覆盖 78 端点 | 测试设计 → 逐模块跟进 |
