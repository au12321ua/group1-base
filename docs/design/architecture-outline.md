# 架构设计大纲（V2）

> 本文档为新一版架构设计的大纲，列出预计要做的设计内容。
> 基于 `require-spec/` 下的需求分析成果与 [data_flow](../require-spec/data_flow/group_bus_L0_L1_L2_integrated.md) 数据流分析，对 `design/design.md` 初版设计进行升级。
> 用户回答已整合到各节，不再单独标注 Q&A。

---

## 1. 系统总体架构

### 1.1 在 STSS 大组中的定位
- STSS 大组共 6 个子系统（A~F），本系统为 **A 信息管理（Information Management）**。
- 统一网关/总线由其他组负责（Nginx），本组**不实现** Gateway。
- 本组仅实现 **Auth Service** + **Info Service** 两个独立服务。
- 跨子系统通信：Auth Service 签发 Token → 总线透传身份 → 各子系统本地验签。
- 本系统向 B（排课）、C（选课）、F（成绩）提供主数据消费接口。

### 1.2 服务职责与边界
| 服务 | 负责方 | 职责 |
|------|--------|------|
| Gateway/Bus | 其他组（Nginx） | 统一入口、路由转发、限流 |
| **Auth Service** | **本组** | 认证、令牌签发/续期/撤销、公钥分发、身份提取、权限定义 |
| **Info Service** | **本组** | 用户管理、课程管理、基础信息管理、回收站、校历、培养方案、文件存储、主数据快照发布、审计日志写入 |
| 日志查询 | **本组** | 独立存储，统一检索入口（可作为 Info Service 子模块） |

### 1.3 技术栈定版
| 组件 | 选择 | 说明 |
|------|------|------|
| 后端框架 | Python FastAPI | 异步高性能，自动 OpenAPI 文档 |
| ORM | SQLModel | 与 FastAPI 适配 |
| 数据库 | SQLite（原型）/ PostgreSQL（后续） | 通过 Alembic 管理迁移 |
| 数据库迁移 | Alembic | 为后期切换 PostgreSQL 做准备 |
| 认证 | JWT（HS256） | 对称密钥，环境变量管理 |
| 跨服务通信 | HTTP 同步调用 + 补偿重试 | 原型阶段不引入 MQ，但预留事件发布接口 |
| 容器化 | Docker + Docker Compose | |
| 前端 | Vue 3 + TypeScript + Element Plus + Vite + Pinia + Vue Router | 仅实现管理端 |

---

## 2. 服务内部模块架构

### 2.1 分层架构（Layer-driven）
统一采用 `Router → Service → CRUD → Model` 单向依赖。

```
project/
├── auth_service/
│   ├── api/v1/           # Router 层
│   ├── services/          # Service 层
│   ├── crud/              # CRUD/Repository 层
│   ├── models/            # SQLModel 实体
│   ├── schemas/           # Pydantic 请求/响应 Schema
│   └── core/              # 配置、异常、安全工具
├── info_service/
│   ├── api/v1/            # Router 层
│   ├── services/          # Service 层（含数据提供、回收站、文件服务）
│   ├── crud/              # CRUD/Repository 层
│   ├── models/            # SQLModel 实体
│   ├── schemas/           # Pydantic 请求/响应 Schema
│   └── core/              # 配置、异常、通用工具
├── shared/                # 跨服务共享代码
│   ├── exceptions.py      # 统一异常定义
│   ├── response.py        # 统一响应格式
│   ├── security.py        # JWT 工具（验签、身份提取）
│   └── logging.py         # 日志封装
├── docker-compose.yml
└── .env / .env.prod
```

### 2.2 Auth Service 内部模块
- **api/v1/**: `/auth/login`、`/auth/sys/login`、`/auth/logout`、`/auth/refresh`、`/auth/me`、`/auth/change-password`、`/auth/public-key`
- **services/**: AuthService（登录、令牌签发/续期/撤销）、KeyService（密钥管理）、IdentityService（身份提取）
- **crud/**: CredentialCRUD、TokenCRUD、SessionCRUD、RoleCRUD、PermissionCRUD
- **models/**: Credential、Token、AuthenticationSession、Role、Permission、UserRole、RolePermission、User（最小字段集：userId、username、status）

### 2.3 Info Service 内部模块
- **api/v1/**: `/users`、`/courses`、`/offerings`、`/schedules`、`/enrollments`、`/calendars`、`/training-programs`、`/base-info`、`/recycle-bin`、`/files`、`/audit-logs`、`/data-provision/*`
- **services/**:
  - UserManagementService（用户增删改查、角色变更、状态管理）
  - CourseManagementService（课程、开课、排课 CRUD）
  - EnrollmentService（选课、退课、冲突校验）
  - DataProvisionService（向 B/C/F 提供主数据快照，含 snapshotTime/version）
  - RecycleBinService（逻辑删除、恢复、物理删除）
  - FileStorageService（文件上传、校验、存储、访问地址生成）
  - AuditService（审计日志写入与检索）
- **crud/**: UserCRUD、UserProfileCRUD、CourseCRUD、OfferingCRUD、ScheduleCRUD、EnrollmentCRUD、ClassroomCRUD、AcademicCalendarCRUD、TrainingProgramCRUD、BaseInfoCRUD、FileResourceCRUD、AuditLogCRUD
- **models/**: User、UserProfile、Course、CourseOffering、CourseSchedule、Classroom、Enrollment、TeacherAssignment、CoursePrerequisite、AcademicCalendar、TrainingProgram、BaseInfoItem、FileResource、AuditLog、OperationLog

---

## 3. 数据架构

### 3.1 数据库分库设计
**Auth DB**（独立 SQLite 文件）：
- `users`（最小字段：userId、username、status，通过 userId 与 Info DB 关联）
- `credentials`、`tokens`、`authentication_sessions`
- `roles`、`permissions`、`user_roles`、`role_permissions`

**Info DB**（独立 SQLite 文件）：
- `users_info`（用户主表，含 userNo、username、roleIds 等）
- `user_profiles`、`course`、`course_offerings`、`course_schedules`、`classrooms`
- `student_course_enrollments`、`teacher_course_assignments`、`course_prerequisites`
- `academic_calendars`、`training_programs`、`base_info_items`
- `file_resources`、`audit_logs`、`operation_logs`

**Log DB**（独立 SQLite 文件）：
- `audit_logs`、`operation_logs`（与 Info DB 分离，独立存储）

> 两个服务各自独立数据库，通过 `userId` 关联。跨库写操作通过 HTTP 同步调用 + 补偿重试保证最终一致。

### 3.2 跨库数据一致性
- **用户创建**：Info Service 先写 → 成功 → HTTP 调用 Auth Service 创建认证账号 → 失败则 Info Service 补偿删除。
- **角色/状态变更**：Info Service 变更 → HTTP 调用 Auth Service 同步角色/禁用/启用。
- **删除/恢复**：Info Service 逻辑删除/恢复 → HTTP 同步 Auth Service 禁用/启用。
- **物理删除**：Info Service 物理删除 → HTTP 同步 Auth Service 清理认证数据。
- 所有同步调用失败时记录异常日志，触发告警，支持人工介入重试。

### 3.3 数据模型（ER 图级别）
基于 `require-spec/class_definition/class-definition-detailed.md` 落地为表结构：
- **用户与权限域**：users_info、user_profiles、roles、permissions、user_roles、role_permissions
- **课程域**：courses、course_offerings、course_schedules、course_prerequisites
- **教学资源域**：classrooms、teacher_course_assignments
- **选课域**：student_course_enrollments
- **基础数据域**：academic_calendars、training_programs、base_info_items
- **辅助域**：file_resources、audit_logs、operation_logs

### 3.4 数据迁移管理
- 使用 **Alembic** 管理数据库版本。
- 每个服务独立维护自己的迁移链。
- 原型阶段 SQLite，后续切换 PostgreSQL 仅需修改连接字符串 + 重建迁移。

---

## 4. 安全架构

### 4.1 认证流程
1. 用户 → Nginx Gateway → Auth Service `/auth/login`。
2. Auth Service 验证凭据 → 签发 Access Token + Refresh Token。
3. 后续请求：Gateway 透传 Authorization Header → 各子系统本地验签并提取 `sub`/`role`。
4. Token 刷新：Access Token 过期 → 用 Refresh Token 换新 Token 对。
5. 登出：撤销 Refresh Token，Access Token 自然过期。

### 4.2 授权模型：RBAC + 资源级权限
- **基础层 RBAC**：Role（STUDENT、TEACHER、ACADEMIC_ADMIN、SYS_ADMIN）→ Permission 多对多。
- **资源级补充**：对隐含归属关系的操作，增加资源级校验。例如：
  - 教师只能修改自己授课班级的成绩/信息
  - 学生只能查看/操作自己的选课记录
  - 用户只能编辑自己的个人信息
- 权限校验链路：Auth Service 负责角色级粗粒度 → Info Service 负责资源级细粒度（Owner/Scope 校验）。

### 4.3 权限点编码规范
采用 `resource:action` 格式：
- `user:read`、`user:create`、`user:update`、`user:delete`
- `course:read`、`course:create`、`course:update`、`course:delete`
- `offering:read/create/update/delete`、`schedule:read/create/update/delete`
- `enrollment:read`、`enrollment:create`、`enrollment:update`、`enrollment:delete`、`enrollment:grade`
- `calendar:read/create/update/delete`、`training:read/create/update/delete`
- `audit:read`、`recycle:read/restore/delete`

### 4.4 JWT 密钥管理
- 原型：对称密钥 HS256，通过 `TOKEN_SECRET_KEY` 环境变量管理。
- 密钥轮换：Auth Service 提供 `/auth/public-key` 接口（当前返回 JWKS 格式的公钥集）。
- 跨子系统校验：各子系统从公钥接口获取密钥，本地完成验签。

### 4.5 安全防护
- 密码：bcrypt 带盐哈希。
- 登录保护：连续失败 5 次 → 锁定 10 分钟 → 自动解除或管理员强制解除。
- 管理员：密码复杂度高于普通用户，Access Token 有效期短于普通用户。
- 接口保护：全量鉴权，默认拒绝，显式授权。
- 敏感操作审计：删除、权限变更、批量导入写审计日志。

---

## 5. API 架构

### 5.1 API 设计规范（继承初版）
- 前缀：`/api/v1/`
- RESTful 风格，统一响应格式（code、message、data）。
- 通用 Query 参数：page、page_size、sort_by、sort_order、keyword、status。
- 幂等约定：PUT/DELETE 幂等，POST 非幂等。
- 关系型 API：嵌套路径（如 `/schedules/{id}/teachers`）用于纯关联，独立资源（如 `/enrollments/{id}`）用于含业务属性的关系。

### 5.2 完整 API 清单

#### Auth Service
| 路径 | 方法 | 说明 |
|------|------|------|
| `/auth/login` | POST | 用户登录 |
| `/auth/sys/login` | POST | 系统服务登录（service token） |
| `/auth/logout` | POST | 用户登出 |
| `/auth/refresh` | POST | 刷新 token |
| `/auth/me` | GET | 获取当前用户 public 信息 |
| `/auth/change-password` | POST | 修改密码 |
| `/auth/public-key` | GET | 获取 JWKS 公钥集 |

#### Info Service — 用户管理
| 路径 | 方法 | 说明 |
|------|------|------|
| `/users` | GET/POST | 列表 / 新增 |
| `/users/{id}` | GET/PUT/PATCH/DELETE | 详情 / 全量更新 / 局部更新 / 逻辑删除 |
| `/users/import` | POST | 批量导入（CSV） |

#### Info Service — 课程
| 路径 | 方法 | 说明 |
|------|------|------|
| `/courses` | GET/POST | 列表 / 新增 |
| `/courses/{id}` | GET/PUT/PATCH/DELETE | 详情 / 更新 / 局部更新 / 删除 |

#### Info Service — 开课
| 路径 | 方法 | 说明 |
|------|------|------|
| `/offerings` | GET/POST | 列表 / 新增 |
| `/offerings/{id}` | GET/PUT/PATCH/DELETE | 详情 / 更新 / 局部更新 / 删除 |

#### Info Service — 排课
| 路径 | 方法 | 说明 |
|------|------|------|
| `/schedules` | GET/POST | 列表 / 新增 |
| `/schedules/{id}` | GET/PUT/PATCH/DELETE | 详情 / 更新 / 局部更新 / 删除 |
| `/schedules/{id}/teachers` | GET/PUT/POST | 教师列表 / 全量覆盖 / 增量添加 |
| `/schedules/{id}/teachers/{tid}` | PUT/DELETE | 单条分配 / 解除 |

#### Info Service — 选课
| 路径 | 方法 | 说明 |
|------|------|------|
| `/enrollments` | GET/POST | 列表 / 选课 |
| `/enrollments/{id}` | GET/PUT/PATCH/DELETE | 详情 / 状态更新 / 局部更新 / 退选 |

#### Info Service — 校历
| 路径 | 方法 | 说明 |
|------|------|------|
| `/calendars` | GET/POST | 列表 / 新增 |
| `/calendars/{id}` | GET/PUT/PATCH/DELETE | 详情 / 更新 / 局部更新 / 删除 |
| `/calendars/by-term` | GET | 按学期查询（`?term_code=xxx`） |

#### Info Service — 培养方案
| 路径 | 方法 | 说明 |
|------|------|------|
| `/training-programs` | GET/POST | 列表 / 新增 |
| `/training-programs/{id}` | GET/PUT/PATCH/DELETE | 详情 / 更新 / 局部更新 / 删除 |
| `/training-programs/by-major` | GET | 按专业/年级/版本查询 |

#### Info Service — 基础信息
| 路径 | 方法 | 说明 |
|------|------|------|
| `/base-info` | GET/POST | 列表 / 新增 |
| `/base-info/{id}` | GET/PUT/PATCH/DELETE | 详情 / 更新 / 局部更新 / 删除 |

#### Info Service — 回收站
| 路径 | 方法 | 说明 |
|------|------|------|
| `/recycle-bin` | GET | 逻辑删除用户列表 |
| `/recycle-bin/{id}/restore` | POST | 恢复用户 |
| `/recycle-bin/{id}` | DELETE | 物理删除单个（需二次确认） |
| `/recycle-bin/batch-delete` | POST | 批量物理删除（需二次确认） |

#### Info Service — 文件
| 路径 | 方法 | 说明 |
|------|------|------|
| `/files` | POST | 上传文件 |
| `/files/{id}` | GET/DELETE | 下载 / 删除文件 |

#### Info Service — 审计日志
| 路径 | 方法 | 说明 |
|------|------|------|
| `/audit-logs` | GET | 检索审计日志（按时间/用户/操作类型） |
| `/audit-logs/export` | GET | CSV 导出审计日志 |

#### Info Service — 数据提供（面向 B/C/F）
| 路径 | 方法 | 说明 | 消费方 |
|------|------|------|--------|
| `/data-provision/teachers` | GET | 教师名单（含分页、snapshotTime） | B 排课 |
| `/data-provision/candidate-students` | GET | 待选课名单（含分页、snapshotTime） | B 排课 |
| `/data-provision/calendars` | GET | 校历（含 version、snapshotTime） | B 排课 |
| `/data-provision/training-programs` | GET | 培养方案（含 requiredCourseIds、version） | C 选课 |
| `/data-provision/selected-students` | GET | 选课学生名单（代理查询，不落库，含 snapshotTime） | B 排课 |

> `selected-students` 接口为代理查询：Info Service 透传调用 C 选课系统接口，组装结果后统一返回。不持久化选课数据。

### 5.3 错误码体系
| HTTP 状态码 | 业务码 | 场景 |
|-------------|--------|------|
| 400 | — | 请求参数错误 |
| 401 | — | 缺少或无效 Token |
| 403 | — | 权限不足 |
| 404 | — | 资源不存在 |
| 409 | — | 资源冲突（唯一约束） |
| 422 | 4221 | 选课人数已满 |
| 422 | 4222 | 时间冲突 |
| 422 | 4223 | 先修课程未完成 |
| 422 | 4224 | 学分超限 |
| 423 | 4231 | 课程已关闭选课 |
| 423 | 4232 | 成绩已锁定无法修改 |
| 429 | — | 请求频率限制 |
| 500 | — | 服务器内部错误 |

---

## 6. 关键业务流程设计

### 6.1 用户创建流程（跨服务）
```
管理员 → Info Service POST /users
  → Info 校验 → 写入 users_info + user_profiles
  → HTTP POST Auth Service /internal/users → 创建 credentials + user_roles
  → 成功 → 返回用户信息
  → Auth 创建失败 → Info 补偿删除本地记录 → 返回失败
```

### 6.2 用户删除与恢复流程
- **逻辑删除**：Info Service 标记 isDeleted → HTTP 调用 Auth Service 禁用账号 → 用户进入回收站。
- **恢复**：回收站 → Info Service 清除 isDeleted → HTTP 调用 Auth Service 启用账号。
- **物理删除**：需要二次确认 → Info Service 物理删除 → HTTP 调用 Auth Service 清理认证数据 → 写审计日志。

### 6.3 批量导入流程
- 管理员上传 CSV → 解析校验 → 逐条 Info Service 建档 → 逐条调用 Auth Service 创建认证 → 汇总成功/失败统计 → 返回结果。

### 6.4 数据提供流程（向 B/C）
```
B/C 系统 → 携带 service token → Nginx Gateway 透传
  → Info Service 本地验签 → 校验 scope 权限
  → 查询主数据 → 附加 snapshotTime/version → 返回结果
  → 写入操作日志（调用方、查询条件、版本号）
```

### 6.5 选课冲突校验
- 课程容量校验：当前选课人数 < 课程容量。
- 时间冲突校验：新选课程时间段与已有课程不重叠。
- 先修课程校验：先修课程已修且成绩合格。
- 学分上限校验：本学期已选学分 + 新选学分 ≤ 上限。

### 6.6 系统间调用（透传用户 Token）
参考 `require-spec/design.md` 3.3 节 JWT 验证标准：用户 Token 透传到 Info Service → 本地验签 → 提取 sub/role → 资源级授权判定。

---

## 7. 日志与可观测性

### 7.1 日志体系
- **应用日志**：AppLogger 封装，DEBUG/INFO/WARN/ERROR 四级，统一 JSON 格式输出。
- **审计日志**：高风险操作写入独立 Log DB，包含 operatorUserId、targetType、targetId、action、result、requestId、createdAt。
- **请求日志**：每个请求记录 request_id（X-Request-ID 透传）、method、path、status_code、duration_ms。

### 7.2 日志存储
- 应用日志：控制台 + 文件（按天轮转）。
- 审计日志：独立 SQLite Log DB（`logs/audit.db`），与业务数据隔离。
- 后续可迁移至集中式日志系统（ELK/Loki）。

### 7.3 链路追踪
- X-Request-ID 全链路透传（Gateway 生成 → Auth Service → Info Service → 日志记录）。
- 原型阶段通过 request_id 串联日志排查，后续可接入 OpenTelemetry。

---

## 8. 部署架构

### 8.1 服务端口规划
| 服务 | 端口 | 说明 |
|------|------|------|
| Nginx Gateway | 8000 | 其他组负责 |
| Auth Service | 8001 | 本组 |
| Info Service | 8002 | 本组 |

### 8.2 容器化部署
- 每个服务独立 Dockerfile（多阶段构建）。
- Docker Compose 编排：Auth Service + Info Service。
- 环境变量分离：`.env`（开发）、`.env.prod`（生产）。
- 数据卷挂载：SQLite 数据库文件、上传文件目录、日志文件目录。

### 8.3 开发环境
- 本地直接启动：`uvicorn main:app --port 8001`（Auth）/ `uvicorn main:app --port 8002`（Info）。
- 或通过 Docker Compose 一键启动。

---

## 9. 前端架构（管理端）

### 9.1 页面结构
- 登录页
- 管理员工作台
  - 用户管理（列表、详情、新增、编辑、批量导入）
  - 课程管理（列表、详情、新增、编辑、删除）
  - 开课/排课管理
  - 校历管理
  - 培养方案管理
  - 基础信息管理
  - 回收站（列表、恢复、物理删除）
  - 审计日志查询
- 个人中心（修改密码）

### 9.2 路由与权限
- 路由守卫：未登录 → 登录页；已登录无权限 → 403 页。
- 按钮级权限：基于后端返回的 permissions 列表控制操作按钮显隐。
- Axios 拦截器：自动附带 Authorization Header、Token 过期自动续期、统一错误提示。

### 9.3 状态管理（Pinia）
- `useAuthStore`：登录状态、Token、用户信息、权限列表。
- `useUserStore`：用户列表、当前编辑用户。
- `useCourseStore`：课程列表、开课/排课数据。

---

## 10. 与 data_flow 的对齐

本架构对齐 [group_bus_L0_L1_L2_integrated.md](../require-spec/data_flow/group_bus_L0_L1_L2_integrated.md) 中 **子系统 A（P2 信息管理）** 的 L2 分解：

| L2 过程 | 对应模块 | 说明 |
|---------|----------|------|
| P2.1 请求解析与鉴权上下文 | Info Service Router + shared/security.py | 请求上下文构建、身份提取 |
| P2.2 用户与档案维护 | UserManagementService | 用户增删改查、档案管理 |
| P2.3 课程校历培养方案维护 | CourseManagementService + DataProvisionService | 课程/校历/培养方案 CRUD |
| P2.4 权限变更与回收站处理 | UserManagementService + RecycleBinService | 角色变更、删除/恢复 |
| P2.5 主数据快照发布与审计写入 | DataProvisionService + AuditService | 快照输出（HTTP）、审计日志写入 |

> L2 图中使用事件总线（MQ）发布主数据快照，原型阶段改为 HTTP 同步提供（`/data-provision/*` 接口），但保留事件发布接口定义，便于后期切换到 MQ。

---

## 11. 设计文档中预计包含的图表

| 图表 | 类型 | 覆盖内容 |
|------|------|----------|
| 系统上下文图 | Mermaid Flowchart | STSS 大组 6 子系统 + 本系统 Auth/Info 服务 |
| 服务拓扑图 | Mermaid Flowchart | Auth/Info 服务与 Gateway/外部系统的通信关系 |
| 分层架构图 | ASCII/Mermaid | Router → Service → CRUD → Model 层次结构 |
| 数据库 ER 图 | Mermaid ER | 三库全部表结构与关联关系 |
| 认证流程时序图 | Mermaid Sequence | 登录 → 签发 → 透传 → 验签 → 授权 |
| 跨服务用户创建时序图 | Mermaid Sequence | Info → Auth HTTP 同步 + 补偿 |
| 数据提供流程时序图 | Mermaid Sequence | B/C → Info Service → 快照返回 |
| 安全架构图 | Mermaid Flowchart | JWT 签发/验签/透传链路 + 权限模型 |
| 部署架构图 | ASCII Table/Mermaid | Docker Compose 编排 + 端口映射 |

---

## 12. 后续步骤

1. 用户确认本大纲已覆盖所有设计要点。
2. 根据大纲输出完整架构设计文档 → `design/architecture-v2.md`。
