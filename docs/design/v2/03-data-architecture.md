# 03 — 数据架构

## 1. 数据库分库设计

系统使用 **3 个独立 SQLite 数据库**，分别服务于认证、业务和审计日志。

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Auth DB      │     │    Info DB      │     │    Log DB       │
│  (auth.db)      │     │  (info.db)      │     │  (audit.db)     │
│                 │     │                 │     │                 │
│ ▪ users (最小)  │     │ ▪ users_info    │     │ ▪ audit_logs    │
│ ▪ credentials   │     │ ▪ user_profiles │     │ ▪ dead_letter   │
│ ▪ tokens        │     │ ▪ courses       │     │   _queue        │
│ ▪ sessions      │     │ ▪ offerings     │     │ ▪ operation_logs│
│ ▪ roles         │     │ ▪ schedules     │     │                 │
│ ▪ permissions   │     │ ▪ classrooms    │     │                 │
│ ▪ user_roles    │     │ ▪ teacher_      │     │                 │
│ ▪ role_perms    │     │   assignments   │     │                 │
│                 │     │ ▪ course_       │     │                 │
│                 │     │   prerequisites │     │                 │
│                 │     │ ▪ calendars     │     │                 │
│                 │     │ ▪ training_progs│     │                 │
│                 │     │ ▪ training_     │     │                 │
│                 │     │   program_      │     │                 │
│                 │     │   courses       │     │                 │
│                 │     │ ▪ base_info     │     │                 │
│                 │     │ ▪ file_resources│     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
       ↑ 8001                  ↑ 8002                ↑ 8001 + 8002
   Auth Service           Info Service         Auth + Info Service
                                              (共享写入)
```

### 1.1 分库原则

- **Auth DB**：仅存认证授权相关数据，由 Auth Service 独占。
- **Info DB**：存全部业务主数据，由 Info Service 独占。
- **Log DB**：存审计日志与操作日志，与业务数据物理隔离，满足审计独立存储要求。由 Auth Service 和 Info Service 共享写入，两个服务各自启动独立的 audit.db 引擎，共享同一个 audit.db 文件。
- **跨库关联**：通过 `userId` 逻辑关联，不建立数据库级外键。

### 1.2 各库表清单

#### Auth DB

| 表名 | 职责 | 关键字段 |
|------|------|----------|
| `users` | 最小用户标识 | id, userId, username, status, created_at |
| `credentials` | 认证凭据 | id, user_id, password_hash, password_salt, failed_login_count, locked_until |
| `tokens` | Token 记录 | id, user_id, type, token_value, issued_at, expires_at, revoked_at |
| `authentication_sessions` | 登录会话 | id, user_id, access_token_id, refresh_token_id, status, client_ip |
| `roles` | 角色定义 | id, code, name, description, is_active |
| `permissions` | 权限点定义 | id, code, name, resource, action |
| `user_roles` | 用户-角色关联 | id, user_id, role_id |
| `role_permissions` | 角色-权限关联 | id, role_id, permission_id |

#### Info DB

| 域 | 表名 | 关键字段 |
|----|------|----------|
| 用户 | `users_info` | id, user_no, username, is_deleted, deleted_at, created_at, updated_at |
| 用户 | `user_profiles` | id, user_id, full_name, gender, email, phone, status, avatar_file_id |
| 课程 | `courses` | id, course_code, course_name, credit, capacity, assessment_method, is_active, is_deleted |
| 课程 | `course_offerings` | id, course_id, term_code, class_no, capacity, status |
| 课程 | `course_schedules` | id, offering_id, classroom_id, day_of_week, start_period, end_period, week_range |
| 课程 | `course_prerequisites` | id, course_id, prerequisite_course_id, min_grade |
| 教学 | `classrooms` | id, room_no, building, capacity, type |
| 教学 | `teacher_course_assignments` | id, teacher_id, offering_id, role_type |
| 教学 | `training_program_courses` | id, program_id, course_id |
| 基础 | `academic_calendars` | id, term_code, term_name, start_date, end_date, version, snapshot_time |
| 基础 | `training_programs` | id, program_code, major_code, grade, version, snapshot_time |
| 基础 | `base_info_items` | id, category, item_code, item_name, description, is_active |
| 文件 | `file_resources` | id, owner_user_id, file_name, file_type, file_size, storage_path, checksum |

#### Log DB

| 表名 | 关键字段 |
|------|----------|
| `audit_logs` | id, operator_user_id, operator_role, target_type, target_id, action, result, reason, request_id, created_at |
| `dead_letter_queue` | id, target_service, operation, payload, error_message, retry_count, max_retries, created_at, last_retry_at |
| `operation_logs` | id, caller_id, query_condition, snapshot_version, created_at |

## 2. 实体关系图（ER）

```mermaid
erDiagram
    UserInfo ||--|| UserProfile : "has"
    Course ||--o{ CourseOffering : "offered_as"
    CourseOffering ||--o{ CourseSchedule : "scheduled"
    CourseOffering ||--o{ TeacherCourseAssignment : "assigned"
    Classroom ||--o{ CourseSchedule : "located"
    Course ||--o{ CoursePrerequisite : "requires"
    UserInfo ||--o{ FileResource : "owns"
    UserInfo ||--o{ AuditLog : "triggers"
    TrainingProgram ||--o{ TrainingProgramCourse : "contains"
    Course ||--o{ TrainingProgramCourse : "required_by"

    UserInfo {
        int id PK
        string user_no UK
        string username UK
        bool is_deleted
        datetime deleted_at
        datetime created_at
        datetime updated_at
    }

    UserProfile {
        int id PK
        int user_id FK
        string full_name
        string gender
        string email
        string phone
        string status
    }

    Course {
        int id PK
        string course_code UK
        string course_name
        int credit
        int capacity
        string assessment_method
        bool is_active
        bool is_deleted
    }

    CourseOffering {
        int id PK
        int course_id FK
        string term_code
        string class_no
        int capacity
        string status
    }

    CourseSchedule {
        int id PK
        int offering_id FK
        int classroom_id FK
        int day_of_week
        int start_period
        int end_period
        string week_range
    }

    TeacherCourseAssignment {
        int id PK
        string teacher_id
        int offering_id FK
        string role_type
    }

    CoursePrerequisite {
        int id PK
        int course_id FK
        int prerequisite_course_id FK
        string min_grade
    }

    AcademicCalendar {
        int id PK
        string term_code UK
        string term_name
        date start_date
        date end_date
        string version
        datetime snapshot_time
    }

    TrainingProgram {
        int id PK
        string program_code UK
        string major_code
        string grade
        string version
        datetime snapshot_time
    }

    TrainingProgramCourse {
        int id PK
        int program_id FK
        int course_id FK
        datetime created_at
    }

    AuditLog {
        int id PK
        string operator_user_id
        string operator_role
        string target_type
        string target_id
        string action
        string result
        string reason
        string request_id
        datetime created_at
    }
```

> 注：Auth DB 中的 User、Credential、Token、Role、Permission 等表通过 userId 与 Info DB 逻辑关联，不在 ER 图中重复绘制。

## 3. 跨库数据一致性

### 3.1 一致性策略

原型阶段采用 **HTTP 同步调用 + 补偿重试** 模式：

```
Info Service（主写方）                     Auth Service（从写方）
      │                                         │
      │  ① 写 Info DB（事务内）                  │
      │  ② HTTP POST /internal/users            │
      │ ──────────────────────────────────────→ │
      │                                         │  ③ 写 Auth DB
      │  ④ 成功 ←──────────────────────────── │
      │                                         │
      │  若 ②/③ 失败：                          │
      │  ⑤ 补偿删除 Info DB 记录                │
      │  ⑥ 记录异常日志                          │
```

### 3.2 场景覆盖

| 场景 | 主操作（Info） | 同步操作（Auth） | 补偿动作 |
|------|---------------|-----------------|----------|
| 用户创建 | 写 users_info + user_profiles | POST /internal/users 创建 credentials | 补偿删除 Info 记录 |
| 逻辑删除 | 标记 isDeleted=true | POST /internal/users/{id}/disable 禁用账号 | Info 清除 isDeleted |
| 恢复用户 | 清除 isDeleted | POST /internal/users/{id}/enable 启用账号 | Info 重新标记 isDeleted |
| 物理删除 | DELETE users_info + profiles | DELETE /internal/users/{id} 清理认证数据 | 记录失败日志，人工介入 |
| 批量导入 | 逐条 Info 建档 | 逐条创建 Auth 账号 | 汇总失败明细，不补偿已成功的 |

### 3.3 异常处理

- 所有 HTTP 同步调用失败时：记录 ERROR 日志（含完整请求上下文）、触发告警。
- 补偿操作本身失败时：写入 `dead_letter_queue` 表（Info DB），支持后续人工或自动重试。
- 补偿失败不影响已有成功数据，宁可保留未同步状态也不丢失主数据。

## 4. 数据迁移管理

### 4.1 Model-First 模式（原型阶段）

原型阶段采用 **Model-First** 模式：SQLModel 模型定义即为数据库 schema 的唯一真实来源，应用启动时通过 `SQLModel.metadata.create_all()` 自动建表。

- **无迁移文件**：原型阶段不维护 Alembic migration chain，快速迭代模型定义。
- **Alembic 配置保留**：`alembic.ini` 和 `env.py` 作为模板保留，生产切换时可随时启用。
- **建表时机**：FastAPI lifespan 中调用 `create_all()`，确保所有注册模型对应的表已创建。
- **表注册**：每个服务的 `models/__init__.py` 导入所有模型模块，确保 `SQLModel.metadata` 包含完整表集合。

### 4.2 生产演进路径

- SQLite → PostgreSQL 切换时：修改连接字符串 → 启用 Alembic → 生成初始迁移 → 后续增量迁移。
- Alembic 配置结构（保留作为模板）：

```
auth_service/migrations/    # Auth 链（alembic.ini + env.py）
info_service/migrations/
├── info/                   # Info 链（alembic.ini + env.py）
└── audit/                  # Audit 链（alembic.ini + env.py）
```

### 4.3 索引策略

原型阶段建立以下索引（SQLite 自动为主键和 UNIQUE 约束创建索引）：

| 表 | 索引字段 | 用途 |
|----|----------|------|
| users_info | username, user_no | 登录查询、学号查询 |
| user_profiles | user_id | 档案关联 |
| courses | course_code, is_active | 课程检索 |
| course_offerings | course_id, term_code | 开课查询 |
| course_offerings | (course_id, term_code, class_no) UNIQUE | 防重复开课 |
| course_schedules | offering_id, classroom_id | 排课关联查询 |
| course_prerequisites | course_id, prerequisite_course_id | 先修课程查询 |
| course_prerequisites | (course_id, prerequisite_course_id) UNIQUE | 防重复先修关系 |
| teacher_course_assignments | teacher_id, offering_id | 教师分配查询 |
| teacher_course_assignments | (offering_id, teacher_id, role_type) UNIQUE | 防重复分配 |
| training_program_courses | program_id, course_id | 方案课程查询 |
| training_program_courses | (program_id, course_id) UNIQUE | 防重复关联 |
| base_info_items | category | 基础信息分类查询 |
| base_info_items | (category, item_code) UNIQUE | 防重复条目 |
| training_programs | program_code, major_code | 方案检索 |
| audit_logs | operator_user_id, target_type, action, created_at | 审计检索 |
| audit_logs | (target_type, action, created_at) COMPOSITE | 审计组合查询 |
| dead_letter_queue | target_service, retry_count | 死信队列查询 |
| authentication_sessions | user_id, access_token_id, refresh_token_id | 会话关联查询 |
