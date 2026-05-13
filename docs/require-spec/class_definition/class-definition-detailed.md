# 类详细定义（第2步）

## 说明
- 本文档基于第1步收敛后的基础类清单，补全每个类的核心属性与操作。
- 目标是直接支撑后续 Class Diagram、CRC Cards、State Diagram、Data Flow Diagram 的绘制。
- 本文档以原型阶段可实现为准，避免过度细化。

## 总体约定
- 主键统一使用 id（UUID 或自增整型，原型阶段可先用整型）。
- 时间字段统一使用 createdAt、updatedAt（UTC）。
- 逻辑删除统一使用 isDeleted + deletedAt（需要时）。
- 枚举可先用字符串实现，后续再固化为 enum。

## 1. 用户与授权域

### 1.1 User
职责：统一用户主体，连接登录身份、角色与个人档案。

核心属性：
- id
- userNo（学号或工号，唯一）
- username（登录名，唯一）
- roleIds
- profileId
- credentialId
- createdAt
- updatedAt

核心操作：
- addRole(roleId)
- removeRole(roleId)
- bindProfile(profileId)
- bindCredential(credentialId)
- isAdmin()

### 1.2 UserProfile
职责：保存用户档案与可编辑信息，并承载用户状态。

核心属性：
- id
- userId
- fullName
- gender
- birthDate
- contactPhone
- email
- emergencyContact
- avatarFileId
- enrollmentOrHireDate
- status（ACTIVE、DISABLED、DELETED）
- isDeleted
- deletedAt
- createdAt
- updatedAt

核心操作：
- updateEditableFields(phone, email, emergencyContact)
- updateAvatar(fileId)
- disable()
- enable()
- markDeleted()
- restoreFromRecycle()

### 1.3 Role
职责：描述角色及其权限边界。

核心属性：
- id
- code（STUDENT、TEACHER、ACADEMIC_ADMIN、SYS_ADMIN）
- name
- PermissionIds
- description
- isActive
- createdAt
- updatedAt

核心操作：
- bindPermission(permissionId)
- unbindPermission(permissionId)
- listPermissions()
- can(permissionCode)

### 1.4 Permission
职责：定义可授权的最小权限点。

核心属性：
- id
- code（如 USER_READ、USER_WRITE、COURSE_MANAGE）
- name
- resource
- action
- description
- createdAt
- updatedAt

核心操作：
- matches(resource, action)

## 2. 认证与会话域

### 2.1 Credential
职责：保存认证信息并提供密码相关能力。

核心属性：
- id
- userId
- username
- passwordHash
- passwordSalt
- passwordUpdatedAt
- failedLoginCount
- lockedUntil
- createdAt
- updatedAt

核心操作：
- verifyPassword(rawPassword)
- updatePassword(oldPassword, newPassword)
- resetPassword(newPassword)
- increaseFailedCount()
- clearFailedCount()
- isLocked()

### 2.2 Token
职责：统一表示 access 与 refresh 令牌，通过 type 区分。

核心属性：
- id
- userId
- type（ACCESS、REFRESH）
- tokenValue
- issuedAt
- expiresAt
- revokedAt
- createdAt

核心操作：
- isExpired(now)
- revoke()
- isRevoked()
- isValid(now)

### 2.3 AuthenticationSession
职责：描述一次登录会话及其令牌对。

核心属性：
- id
- userId
- accessTokenId
- refreshTokenId
- clientIp
- userAgent
- startedAt
- lastActiveAt
- endedAt
- status（ACTIVE、ENDED、EXPIRED）

核心操作：
- start(accessTokenId, refreshTokenId)
- refresh(newAccessTokenId, newRefreshTokenId)
- touch()
- end()
- isActive()

## 3. 基础信息域

### 3.1 Course
职责：维护课程主数据。

核心属性：
- id
- courseCode（唯一）
- courseName
- credit
- capacity
- assessmentMethod
- isActive
- isDeleted
- deletedAt
- createdAt
- updatedAt

核心操作：
- createCourse(data)
- updateCourse(data)
- deactivate()
- activate()
- markDeleted()

### 3.2 BaseInfoItem
职责：承载通用基础信息条目（非课程类）。

核心属性：
- id
- category（如 DEPARTMENT、MAJOR、ACADEMIC_CALENDAR）
- itemCode
- itemName
- description
- sortOrder
- isActive
- createdAt
- updatedAt

核心操作：
- createItem(data)
- updateItem(data)
- activate()
- deactivate()

### 3.3 AcademicCalendar
职责：维护学年学期、教学周、节假日与补课安排等校历信息。

核心属性：
- id
- termCode
- termName
- startDate
- endDate
- teachingWeekRule
- holidayRules
- makeUpClassRules
- version
- snapshotTime
- isActive
- createdAt
- updatedAt

核心操作：
- createCalendar(data)
- updateCalendar(calendarId, data)
- publishCalendar(calendarId)
- getCalendarByTerm(termCode)

### 3.4 TrainingProgram
职责：维护培养方案主信息。

核心属性：
- id
- programCode
- programName
- majorCode
- grade
- version
- effectiveFrom
- effectiveTo
- status
- requiredCourseIds（课程ID列表）
- snapshotTime
- createdAt
- updatedAt

核心操作：
- createProgram(data)
- updateProgram(programId, data)
- publishProgram(programId)
- getProgram(majorCode, grade, version)

## 4. 文件与日志域

### 4.1 FileResource
职责：统一文件资源元数据（头像、照片、导入文件）。

核心属性：
- id
- ownerUserId
- fileName
- fileType
- fileSize
- storagePath
- accessUrl
- checksum
- createdAt

核心操作：
- validateType(allowedTypes)
- validateSize(maxSize)
- generateAccessUrl()

### 4.2 AuditLog
职责：记录不可抵赖的高风险操作。

核心属性：
- id
- operatorUserId
- operatorRole
- targetType
- targetId
- action
- result
- reason
- requestId
- createdAt

核心操作：
- record(action, targetType, targetId, result)

### 4.3 AppLogger
职责：对常用 logging 库做轻量封装，统一日志格式与输出级别。

核心属性：
- loggerName
- logLevel（DEBUG、INFO、WARN、ERROR）
- outputTarget（console、file）

核心操作：
- debug(message, context)
- info(message, context)
- warn(message, context)
- error(message, context)
- setLevel(level)

## 5. 服务类候选

### 5.1 AuthService
职责：登录鉴权、令牌签发、续期、退出，并向网关/业务服务提供公钥与身份提取能力。

核心操作：
- login(username, password)
- validateToken(tokenValue)
- extractIdentity(tokenValue)
- getPublicKey()
- refreshToken(refreshTokenValue)
- logout(sessionId)
- logoutAll(userId)

### 5.2 UserManagementService
职责：用户查询、新增、编辑、删除、恢复、权限调整。

核心操作：
- createUser(userData, credentialData)
- getUserDetail(userId)
- searchUsers(condition, page)
- listTeachers(condition, page)
- updateUserProfile(userId, editableData)
- changeUserRole(userId, roleId)
- disableUser(userId)
- enableUser(userId)
- logicalDeleteUser(userId)
- restoreUser(userId)
- batchImportUsers(csvFileId)

### 5.3 CourseManagementService
职责：课程与其他基础信息管理。

核心操作：
- createCourse(courseData)
- updateCourse(courseId, courseData)
- deleteCourse(courseId)
- listCourses(condition, page)
- createBaseInfoItem(data)
- updateBaseInfoItem(itemId, data)
- getAcademicCalendar(termCode)
- createAcademicCalendar(data)
- updateAcademicCalendar(calendarId, data)
- getTrainingProgram(majorCode, grade, version)
- listCandidateStudents(termCode, majorCode, grade, page)
- querySelectedStudents(condition, page)

### 5.4 LoggingService
职责：统一日志入口。普通日志通过 AppLogger 输出；高风险操作写入 AuditLog 并提供检索。

核心操作：
- debug(message, context)
- info(message, context)
- warn(message, context)
- error(message, context)
- writeAuditLog(logData)
- searchAuditLogs(condition, page)

### 5.5 FileStorageService
职责：文件上传、校验、存储、访问地址生成。

核心操作：
- uploadFile(ownerUserId, file)
- deleteFile(fileId)
- getFile(fileId)
- generateFileUrl(fileId)

## 6. 关键关系（用于类图落地）
- User 1..1 UserProfile
- User 1..1 Credential
- User n..1 Role
- Role n..n Permission
- User 1..n Token
- AuthenticationSession 1..1 User
- AuthenticationSession 1..1 Token（access）
- AuthenticationSession 1..1 Token（refresh）
- UserProfile 0..1 FileResource（头像）
- User 1..n AuditLog（operator）
- LoggingService 1..1 AppLogger
- LoggingService 1..n AuditLog

## 7. CRC Cards 最小落地建议
- 先为实体类准备责任与协作者：User、UserProfile、Role、Credential、Token、Course、AcademicCalendar、TrainingProgram、AuditLog。
- 再为服务类补协作关系：AuthService、UserManagementService、CourseManagementService、LoggingService。
- 原型阶段先覆盖高频用例：登录、查看/修改个人信息、管理员用户管理、课程管理、受保护资源访问、跨业务组数据提供。