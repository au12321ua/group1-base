# 基本类识别（第1步，收敛版）

## 说明
- 本文件只做基础类识别，不展开属性、操作与详细关系。
- 本版按原型开发优先级进行收敛，删除不必要抽象，避免过度设计。
- 目标是给后续 Class Diagram、CRC Cards、State Diagram、Data Flow Diagram 提供稳定原材料。

## 本次收敛调整
- 将 UserStatus 取消独立成类，相关状态字段并入 UserProfile。
- 取消 PasswordPolicy 类，密码策略差异在实现中通过 Role 判定。
- 将 AccessToken 与 RefreshToken 合并为统一 Token 类，通过 type 字段区分用途。
- 取消批量操作任务类与回收站条目类，不为批量流程单独建模。
- 取消变更记录类（ProfileChangeRecord、AccountStatusChangeRecord），原型阶段不强制要求。
- 取消 AdminUser 独立类，管理员通过 User + Role 组合表达。
- 取消 Avatar 独立类，统一并入 FileResource。

## 收敛后基础类清单

### 1. 用户与授权域
- User：系统统一用户主体，承载账号标识与角色关联。
- UserProfile：用户档案信息（包含状态字段，如启用/禁用/逻辑删除）。
- Role：角色定义（学生、教师、教务管理员、系统管理员等）。
- Permission：权限点定义，用于表达资源访问与操作授权。

### 2. 认证与会话域
- Credential：认证凭据（账号、密码哈希等）。
- Token：统一令牌实体，通过 type 区分 access 与 refresh。
- AuthenticationSession：登录会话对象。

### 3. 基础信息域
- Course：课程基础信息实体。
- BaseInfoItem：其他基础信息通用实体（预留给非课程主数据）。
- AcademicCalendar：校历实体，描述学期、教学周、节假日与补课安排。
- TrainingProgram：培养方案主信息实体（包含 requiredCourseIds 课程ID列表）。

### 4. 文件与日志域
- FileResource：文件资源（头像、个人照片、导入文件等）。
- AuditLog：审计日志（高风险操作记录）。
- OperationLog：一般操作日志（查询、编辑、导入等过程记录）。

### 5. 服务类候选
- AuthService：鉴权与会话服务。
- UserManagementService：用户与权限管理服务。
- CourseManagementService：课程与基础信息管理服务。
- AuditService：日志写入与检索服务。
- FileStorageService：文件存储服务。

## 边界说明（当前阶段）
- 批量导入、批量删除、回收站恢复等流程优先建模为服务操作，不单独抽象流程类。
- 用户状态使用 UserProfile 中的状态字段表达，不额外增加状态实体。
- 密码复杂度、有效期差异通过 Role 分支控制，不单独建策略类。
- 令牌使用统一 Token 类建模，通过 type 与过期时间表达不同令牌行为。
- 原型阶段只保留必要日志类，不额外要求结构化变更记录实体。
- 名单类与方案类查询优先建模为服务操作，不额外抽象查询任务类。
- 校历与培养方案采用版本化字段（version/snapshotTime）支持跨系统口径追溯。

## 下一步（第2步）
- 为收敛后的每个类补齐属性与操作。
- 明确关键关联关系（如 User-Role、User-UserProfile、User-Credential）。
- 基于定稿类模型输出 Class Diagram 与 CRC Cards，再衔接状态图和数据流图。
- 重点补齐跨业务组数据提供链路：教师名单、待选课名单、选课学生名单、校历、培养方案。