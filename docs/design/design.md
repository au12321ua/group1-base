# 项目设计

## 需求描述

主要负责管理整个教学服务系统的用户、权限、课程等基础信息，并能够提供一定程度的系统安全性保证。用户主要分学生、教师、教务管理人员和系统管理员等。具体功能如下：
- 用户基本信息管理：教务管理人员能够添加、编辑、删除学生和教师用户，搜索与查看学生和教师信息，设置用户类别，管理用户权限，修改用户信息。
- 不同类型用户登录系统后的功能：可管理个人信息，填写或修改部分内容，上传照片等。
- 课程基本信息管理：包括课程名称，课程学分，课程容量，课程考核方式等基本信息。
- 用户权限管理：主要体现在后续的各个子系统，不同类型用户在各个子系统中拥有不同类型的权限，系统能够保证用户不越权访问，其中系统管理员具有最高的权限。 系统安全管理负责对整个系统的安全性进行管理，包括用户注册信息的安全、用户密码的安全管理，防入侵管理，系统日志的记录与管理等。

## 技术栈规划

### 后端技术栈
**Python FastAPI + SQLite**

| 组件 | 选择 | 理由 |
|------|------|------|
| **后端框架** | FastAPI | 异步高性能，自动API文档|
| **数据库** | SQLite | 简单轻量，便于部署 |
| **ORM** | SQLModel | 与FastAPI适配，学习曲线较缓 |
| **认证授权** | JWT | 无状态认证，支持令牌撤销 |
| **容器化** | Docker + Docker Compose | 环境一致性，简化部署 |

### 前端技术栈
**Vue 3 + TypeScript + Element Plus + Vite**

| 组件 | 选择 | 版本 | 理由 |
|------|------|------|------|
| **框架** | Vue 3 + Composition API | 最新 | 学习曲线平缓，适合前端经验有限团队 |
| **语言** | TypeScript | 最新 | 类型安全，减少运行时错误 |
| **UI组件库** | Element Plus | 最新 | 完整的管理后台组件，减少UI开发 |
| **构建工具** | Vite | 最新 | 快速构建和热重载，开发体验好 |
| **状态管理** | Pinia | 最新 | 轻量级状态管理，替代Vuex |
| **路由** | Vue Router | 4.x | 官方路由解决方案 |
| **HTTP客户端** | Axios | 最新 | 成熟的HTTP客户端库 |

> 备注：不太了解前端，直接使用大模型推荐的技术栈

## 数据库设计

见[数据库设计](./db_design.md)。

## api设计

统一以`/api/v1/`作为前缀，采用Restful设计风格。


### 通用的Header、Query参数规范

#### 1.1 通用Header参数
| Header名称 | 类型 | 必填 | 说明 | 示例 |
|-----------|------|------|------|------|
| Authorization | string | 是 | Bearer Token格式 | `Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...` |
| X-Request-ID | string | 否 | 请求唯一标识，用于链路追踪 | `req_9aef8a7d-f5c1-4ab8-9b6d-1e3421d91821` |
| X-Client-Version | string | 否 | 客户端版本号 | `1.0.0` |
| X-Client-Type | string | 否 | 客户端类型（web/app） | `web` |
| Content-Type | string | 是 | 请求体类型 | `application/json` |
| Accept | string | 否 | 期望的响应类型 | `application/json` |

#### 1.2 通用Query参数
| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| page | integer | 否 | 页码，从1开始 | `page=1` |
| page_size | integer | 否 | 每页数量，默认20，最大100 | `page_size=20` |
| sort_by | string | 否 | 排序字段 | `sort_by=created_at` |
| sort_order | string | 否 | 排序方向（asc/desc） | `sort_order=desc` |
| keyword | string | 否 | 关键词搜索 | `keyword=计算机` |
| status | string | 否 | 状态过滤 | `status=active` |
| start_date | string | 否 | 开始日期（ISO格式） | `start_date=2024-03-01` |
| end_date | string | 否 | 结束日期（ISO格式） | `end_date=2024-03-31` |

### 统一的请求、响应与异常JSON格式

#### 2.1 统一请求格式

所有POST、PUT、PATCH请求应该使用JSON格式，直接包含请求的业务数据即可，具体根据API端点而定。

**示例 - 创建用户请求：**
```json
{
  "username": "john_doe",
  "password": "SecurePass123",
  "name": "John Doe",
  "email": "john@example.com",
  "department": "计算机学院"
}
```

#### 2.2 成功响应格式

列表请求，如`GET /users`：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [ { "id": 1, "name": "张三" }, ... ],
    "pagination": { "total": 100, "page": 1, "page_size": 20 } // 暂时只包括这些参数
  }
}
```

单体请求，如`GET /users/1`

```json
{
  "code": 0,
  "message": "success",
  "data": { "id": 1, "name": "张三" } // 直接返回对象，无 pagination 字段
}
```

#### 2.3 错误响应格式
```json
{
  "code": 1001,
  "message": "Authentication failed",
  "errors": [
    {
      "field": "password",
      "message": "Password is incorrect"
    }
  ]
}
```

### JWT Token设计

#### 3.1 Token Payload结构

```python
{
  "sub": "user_id",           # 用户ID（唯一主体标识）
  "jti": "uuid",              # token唯一ID（用于撤销）
  "type": "access",           # token类型（access/refresh）
  "iat": 1648300800,           # 签发时间
  "exp": 1648302600            # 过期时间（建议15-30分钟）
}
```

如果是sys access token，过期时间设置1-24h，且必须增加以下参数：

- `client_id`：调用方系统标识。
- `scope`：调用权限范围（粗粒度，如`enrollment:read enrollment:update`）。

**Refresh Token Payload：**
```python
{
  "sub": "user_id",           # 用户ID
  "jti": "uuid",              # refresh token唯一ID
  "type": "refresh",          # token类型
  "iat": 1648300800,           # 签发时间
  "exp": 1648905600            # 过期时间（建议7天）
}
```

#### 3.2 Token配置参数
```python
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7
TOKEN_SECRET_KEY = "your-secret-key-change-in-production"
```

#### 3.3 跨子系统JWT验证标准

为支持不同技术栈（Python/Node.js/Java等）子系统独立做认证中间件，定义统一JWT验证标准如下：

1. 适用范围
- 所有子系统对外API都必须校验Access Token。
- 每个子系统本地完成Token校验，不依赖调用认证服务的`/auth/me`。

2. Access Token必备声明（Claims）
- `sub`：用户唯一标识。
- `jti`：Token唯一ID，用于撤销校验。
- `type`：固定为`access`。
- `iat`：签发时间（Unix时间戳，秒）。
- `exp`：过期时间（Unix时间戳，秒）。

3. Service Token必备声明（Claims）
- `sub`：服务主体标识（建议为`client_id`）。
- `type`：固定为`service`。
- `iat`：签发时间（Unix时间戳，秒）。
- `exp`：过期时间（Unix时间戳，秒）。
- `aud`：目标受众（被调用子系统标识）。
- `client_id`：调用方系统标识。
- `scope`：调用权限范围（如`enrollment:read enrollment:update`）。

4. 中间件最小校验规则（所有语言一致）
- 验证签名算法与签名有效性。
- 校验`exp`未过期，`iat`不晚于当前时间（允许60秒时钟偏差）。
- 根据场景校验`type`：用户请求必须为`access`，系统间调用可为`service`。
- `service` token必须校验`client_id`、`scope`、`aud`。
- 目前暂不做`jti`黑名单校验；后续如引入撤销能力，再恢复`jti`强校验。

5. 失败响应规范
- 缺少或无效Token：返回`401 Unauthorized`。
- Token有效但权限不足：返回`403 Forbidden`。
- 子系统鉴权/鉴权后授权失败时必须拒绝请求，不得降级放行。
- 错误响应格式遵循本文“2.3 错误响应格式”。

6. 密钥与轮换建议
- 单体/小规模：可使用对称密钥（HS256），但必须通过环境变量管理密钥。
- 多子系统/长期演进：建议改为非对称密钥（RS256/ES256）+ JWKS发布公钥。
- 密钥轮换期间至少保留“当前Key + 上一版本Key”，避免正在生效的Token瞬时失效。

7. 关于`/auth/me`的定位
- `GET /auth/me`仅用于“获取当前用户public信息”（如前端页面初始化）。
- 不作为其他子系统的认证中间件校验接口。
- `GET /auth/me`仅接受用户`access token`（`type=access`），拒绝`service token`。

8. Token使用边界
- 与用户无关的系统间调用：使用`service token`（通过`/auth/sys/login`签发）。
- 与用户有关的调用：透传用户`access token`，由被调用子系统本地完成验签与权限判断。
- 如被调用子系统返回`403 Forbidden`，调用方应直接拒绝该次请求，不得忽略或二次放宽权限。

### API路径设计

基于数据库实体设计的Restful API端点（以`/api/v1/`为前缀）：

接口统一约定：
- read接口统一返回资源的全部public信息，不再单独设计“仅返回部分字段/子集信息”的GET子接口。
- 关联关系查询优先通过主列表接口 + Query参数过滤实现（例如`/enrollments?student_id=xxx`）。
- 局部更新统一使用PATCH，且不对具体更新字段做接口层限制（由服务端权限与业务校验控制）。

#### 4.1 认证相关API
| 路径 | 方法 | 说明 | 权限要求 |
|------|------|------|----------|
| `/auth/login` | POST | 用户登录 | 无 |
| `/auth/sys/login` | POST | 系统服务登录并签发service token | 无（使用`client_id/client_secret`） |
| `/auth/logout` | POST | 用户登出 | 需要认证 |
| `/auth/refresh` | POST | 刷新token | 需要refresh_token |
| `/auth/me` | GET | 获取当前用户public信息（仅user access token，非中间件校验接口） | 需要认证 |
| `/auth/change-password` | POST | 修改密码 | 需要认证 |

#### 4.2 用户管理API
| 路径 | 方法 | 说明 | 权限要求 |
|------|------|------|----------|
| `/users` | GET | 获取用户列表 | `user:read` |
| `/users` | POST | 创建用户 | `user:create` |
| `/users/{user_id}` | GET | 获取用户详情 | `user:read` |
| `/users/{user_id}` | PUT | 更新用户信息 | `user:update` |
| `/users/{user_id}` | PATCH | 局部更新用户信息（任意允许字段） | `user:update` |
| `/users/{user_id}` | DELETE | 删除用户 | `user:delete` |


#### 4.3 课程管理API
| 路径 | 方法 | 说明 | 权限要求 |
|------|------|------|----------|
| `/courses` | GET | 获取课程列表 | `course:read` |
| `/courses` | POST | 创建课程 | `course:create` |
| `/courses/{course_id}` | GET | 获取课程详情 | `course:read` |
| `/courses/{course_id}` | PUT | 更新课程 | `course:update` |
| `/courses/{course_id}` | PATCH | 局部更新课程信息（任意允许字段） | `course:update` |
| `/courses/{course_id}` | DELETE | 删除课程 | `course:delete` |

#### 4.4 课程开设API
| 路径 | 方法 | 说明 | 权限要求 |
|------|------|------|----------|
| `/offerings` | GET | 获取开设列表 | `offering:read` |
| `/offerings` | POST | 创建开设实例 | `offering:create` |
| `/offerings/{offering_id}` | GET | 获取开设详情 | `offering:read` |
| `/offerings/{offering_id}` | PUT | 更新开设信息 | `offering:update` |
| `/offerings/{offering_id}` | PATCH | 局部更新开设信息（任意允许字段） | `offering:update` |
| `/offerings/{offering_id}` | DELETE | 删除开设实例 | `offering:delete` |

#### 4.5 排课管理API
| 路径 | 方法 | 说明 | 权限要求 |
|------|------|------|----------|
| `/schedules` | GET | 获取排课列表 | `schedule:read` |
| `/schedules` | POST | 创建排课 | `schedule:create` |
| `/schedules/{schedule_id}` | GET | 获取排课详情 | `schedule:read` |
| `/schedules/{schedule_id}` | PUT | 更新排课 | `schedule:update` |
| `/schedules/{schedule_id}` | PATCH | 局部更新排课信息（任意允许字段） | `schedule:update` |
| `/schedules/{schedule_id}` | DELETE | 删除排课 | `schedule:delete` |
| `/schedules/{schedule_id}/teachers` | GET | 获取该排课关联的教师列表 | `schedule:read` |
| `/schedules/{schedule_id}/teachers` | PUT | 批量替换该排课的授课教师（全量覆盖） | `schedule:update` |
| `/schedules/{schedule_id}/teachers` | POST | 批量新增授课教师（增量添加，不覆盖） | `schedule:update` |
| `/schedules/{schedule_id}/teachers/{teacher_id}` | PUT | 为该排课分配单个教师（幂等） | `schedule:update` |
| `/schedules/{schedule_id}/teachers/{teacher_id}` | DELETE | 解除该排课与单个教师关系（幂等） | `schedule:update` |

#### 4.6 选课管理API
| 路径 | 方法 | 说明 | 权限要求 |
|------|------|------|----------|
| `/enrollments` | GET | 获取选课列表 | `enrollment:read` |
| `/enrollments` | POST | 学生选课 | `enrollment:create` |
| `/enrollments/{enrollment_id}` | GET | 获取选课详情 | `enrollment:read` |
| `/enrollments/{enrollment_id}` | PUT | 更新选课状态 | `enrollment:update` |
| `/enrollments/{enrollment_id}` | PATCH | 局部更新选课信息（任意允许字段） | `enrollment:update` |
| `/enrollments/{enrollment_id}` | DELETE | 退选课程 | `enrollment:delete` |

#### 4.7 关系型表API设计思路（适用于多对多/关联实体）

1. 纯关系表与关系实体分开建模
- 若关系表仅表达“关联本身”（例如教师-排课），优先使用嵌套路径设计（如`/schedules/{schedule_id}/teachers/{teacher_id}`），不强制暴露关系主键。
- 若关系表包含明确业务属性（例如选课状态、成绩、选课时间），应提升为独立资源（如`/enrollments/{enrollment_id}`）。

2. 语义与方法对齐
- `GET`：查询关系。
- `PUT`：幂等建立关系或幂等全量替换关系集合。
- `POST`：非幂等创建或“增量添加集合”。
- `DELETE`：幂等解除关系。

3. 单条关系与批量关系并存
- 单条关系用于精确控制：`PUT/DELETE /schedules/{schedule_id}/teachers/{teacher_id}`。
- 批量关系用于管理端高效维护：
  - `PUT /schedules/{schedule_id}/teachers`：全量覆盖。
  - `POST /schedules/{schedule_id}/teachers`：增量追加。

4. 幂等与冲突处理约定
- 对幂等接口（单条`PUT`、单条`DELETE`、批量`PUT`）重复调用应返回成功（通常`204`）。
- 若出现业务冲突（如教师时间冲突、跨院系限制、容量规则冲突），返回`422`并在错误体中给出可定位信息。
- 缺少认证返回`401`，权限不足返回`403`，目标资源不存在返回`404`。

5. 权限粒度建议
- 关系查询与主资源读取权限保持一致（如`schedule:read`）。
- 关系变更与主资源更新权限保持一致（如`schedule:update`）。
- 带敏感业务字段的关系子接口单独权限控制（如`enrollment:grade`）。

### 跨子系统调用示例（以“本人选课信息”场景说明）

#### 示例A：获取用户自己的选课列表

流程：
1. 用户在论坛子系统登录后，论坛拿到用户`access token`。
2. 论坛调用信息管理子系统：`GET /api/v1/enrollments?student_id={sub}`，请求头透传`Authorization: Bearer <user_access_token>`。
3. 信息管理子系统本地校验JWT，并校验该用户是否具备`enrollment:read:self`（或等价规则）。
4. 若通过，返回该用户选课数据；若权限不足，返回`403 Forbidden`。
5. 论坛收到`403`后必须拒绝该请求，不得改用服务token重试同一“用户态”请求。

#### 示例B：更新用户自己的选课状态（如退选）

流程：
1. 用户在论坛发起“退选课程”。
2. 论坛调用信息管理子系统：`PATCH /api/v1/enrollments/{enrollment_id}`，请求头仍使用用户`access token`。
3. 信息管理子系统完成两类校验：
  - 身份校验：token有效、`type=access`、未过期。
  - 业务授权：该`enrollment_id`确实属于当前`sub`，且用户具备`enrollment:update:self`。
4. 任一校验失败返回`403 Forbidden`（或token无效时`401 Unauthorized`）。
5. 论坛收到失败响应后直接向前端返回失败，不做权限绕过。

#### 服务token的适用边界补充
- 仅用于与具体用户无关的系统级任务（如定时同步、批处理统计）。
- 不用于代替用户执行“本人数据读写”。
- 若确需系统代办，必须走明确的受控机制（如审计记录、显式代理权限）。

### 特殊HTTP响应码设计

| 状态码 | 名称 | 使用场景 | 说明 |
|--------|------|----------|------|
| 400 | Bad Request | 请求参数错误 | 通用参数验证失败 |
| 401 | Unauthorized | 未认证 | 缺少或无效的token |
| 403 | Forbidden | 权限不足 | 用户没有访问权限 |
| 404 | Not Found | 资源不存在 | 请求的资源不存在 |
| 409 | Conflict | 资源冲突 | 创建时资源已存在，或违反唯一约束 |
| 422 | Unprocessable Entity | 业务逻辑错误 | 如选课人数已满、时间冲突等 |
| 423 | Locked | 资源被锁定 | 如课程已关闭选课 |
| 429 | Too Many Requests | 请求频率限制 | API调用频率超限 |
| 500 | Internal Server Error | 服务器内部错误 | 未处理的异常 |
| 503 | Service Unavailable | 服务不可用 | 维护中或过载 |

**特殊业务状态码（在422和423基础上扩展）：**
- `4221`: 选课人数已满
- `4222`: 时间冲突
- `4223`: 先修课程未完成
- `4224`: 学分超限
- `4231`: 课程已关闭选课
- `4232`: 成绩已锁定无法修改

## 项目组织

1. 项目目录结构如何分包？ 
  - 建议方案 ： 按层划分 (Layer-driven) 。即 api/ 、 services/ 、 crud/ 、 models/ 平行。模块在各层内部通过文件区分（如 services/user_service.py ）。这样可以严格控制单向依赖： Router -> Service -> CRUD -> Model ，避免循环引用，也是目前 Python/FastAPI 圈内企业级应用最认可的方式。
2. Router 如何组织？ 
  - 建议方案 ：使用 APIRouter 分模块，在 api/v1/router.py 中进行统一聚合与版本控制。
  - 示例： api_router.include_router(users.router, prefix="/users", tags=["Users"]) 。主应用 main.py 中只挂载 api_router 并设置全局前缀 app.include_router(api_router, prefix="/api/v1") 。
3. Service/Repository/CRUD 的划分方式 (薄 Router，厚 Service) 
  - 薄 Router ：代码行数极少，只负责接收请求、调用 Service 层方法、返回 Pydantic Schema。 坚决不在路由中写 if-else 的业务逻辑 。
  - 厚 Service ：承载业务，比如“自动排课系统请求查询教师信息”，Service 层要负责校验请求方是否有权、数据清洗等。
  - Repository/CRUD ：只负责和 SQLAlchemy 交互，如 db.query(User).filter(...) ，不包含任何业务。
4. 配置管理 (Pydantic Settings & 多环境) 
  - 建议方案 ：在 core/config.py 中继承 pydantic_settings.BaseSettings 。
  - 使用类属性 Config 中的 env_file = ".env" 来加载。在 Docker 或 CI/CD 启动时，通过注入环境变量 ENV=prod 动态读取 .env.prod 文件，覆盖默认配置。
