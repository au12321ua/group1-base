# 06 — 业务流程设计

## 1. 用户创建流程（跨服务）

```mermaid
sequenceDiagram
    actor Admin as 管理员
    participant Info as Info Service
    participant InfoDB as Info DB
    participant Auth as Auth Service
    participant AuthDB as Auth DB
    participant Audit as 审计日志

    Admin->>Info: POST /users {user_data}
    Info->>Info: 校验必填字段 + 唯一性
    Info->>InfoDB: BEGIN TRANSACTION
    Info->>InfoDB: INSERT users_info
    Info->>InfoDB: INSERT user_profiles
    Info->>InfoDB: COMMIT

    Info->>Auth: POST /internal/users {userId, username, roleIds}
    Auth->>AuthDB: INSERT credentials (初始密码)
    Auth->>AuthDB: INSERT user_roles

    alt Auth 创建成功
        Auth-->>Info: 201 Created
        Info->>Audit: 写审计日志 (action=user_created, result=success)
        Info-->>Admin: 201 用户创建成功
    else Auth 创建失败
        Auth-->>Info: 500 创建失败
        Info->>InfoDB: DELETE users_info (补偿)
        Info->>InfoDB: DELETE user_profiles (补偿)
        Info->>Audit: 写审计日志 (action=user_created, result=failed)
        Info-->>Admin: 500 用户创建失败，已回滚
    end
```

## 2. 用户删除与恢复流程

### 2.1 逻辑删除

```mermaid
sequenceDiagram
    actor Admin as 管理员
    participant Info as Info Service
    participant Auth as Auth Service
    participant Audit as 审计日志

    Admin->>Info: DELETE /users/{id}
    Info->>Info: 校验目标用户存在且未被删除
    Info->>Info: UPDATE users_info SET is_deleted=true, deleted_at=now
    Info->>Auth: POST /internal/users/{id}/disable
    Auth->>Auth: UPDATE users SET status=DISABLED
    Auth-->>Info: 200 OK
    Info->>Audit: 写审计日志 (action=user_deleted_logical)
    Info-->>Admin: 200 用户已移入回收站
```

### 2.2 回收站恢复

```mermaid
sequenceDiagram
    actor Admin as 管理员
    participant Info as Info Service
    participant Auth as Auth Service

    Admin->>Info: POST /recycle-bin/{id}/restore
    Info->>Info: 校验存在且 isDeleted=true
    Info->>Info: UPDATE users_info SET is_deleted=false, deleted_at=null
    Info->>Auth: POST /internal/users/{id}/enable
    Auth->>Auth: UPDATE users SET status=ACTIVE
    Auth-->>Info: 200 OK
    Info-->>Admin: 200 用户已恢复
```

### 2.3 物理删除

```mermaid
sequenceDiagram
    actor Admin as 管理员
    participant Info as Info Service
    participant Auth as Auth Service
    participant Audit as 审计日志

    Admin->>Info: DELETE /recycle-bin/{id} (二次确认)
    Info->>Info: 校验 isDeleted=true
    Info->>Info: DELETE FROM users_info
    Info->>Info: DELETE FROM user_profiles
    Info->>Auth: DELETE /internal/users/{id}
    Auth->>Auth: DELETE credentials, tokens, sessions
    Auth->>Auth: DELETE user_roles
    Auth-->>Info: 204 No Content
    Info->>Audit: 写审计日志 (action=user_deleted_permanent)
    Info-->>Admin: 204 用户已永久删除
```

## 3. 批量导入流程

```mermaid
sequenceDiagram
    actor Admin as 管理员
    participant Info as Info Service
    participant Auth as Auth Service

    Admin->>Info: POST /users/import (CSV 文件)
    Info->>Info: 解析 CSV → 逐行校验
    Info->>Info: 过滤已存在用户（按 userNo/username）
    loop 每条有效记录
        Info->>Info: INSERT users_info + user_profiles
        Info->>Auth: POST /internal/users (创建认证)
        alt 成功
            Info->>Info: success_count++
        else 失败
            Info->>Info: 补偿删除 Info 记录
            Info->>Info: failed_count++, 记录错误原因
        end
    end
    Info-->>Admin: 200 {total, success_count, failed_count, errors: [...]}
```

## 4. 数据提供流程（向 B/C 系统）

```mermaid
sequenceDiagram
    actor B as B 排课系统
    participant Gateway as Nginx Gateway
    participant Auth as Auth Service
    participant Info as Info Service
    participant Log as 操作日志

    B->>Auth: POST /auth/sys/login {client_id, client_secret}
    Auth-->>B: {service_token}
    B->>Gateway: GET /data-provision/teachers?page=1 (Authorization: Bearer <service_token>)
    Gateway->>Auth: POST /internal/verify (service_token)
    Auth->>Auth: 验签 Service Token，校验 scope
    Auth-->>Gateway: 200 {client_id, scope, permissions}
    Gateway->>Info: 透传 + Header {X-Client-Id, X-Request-ID}
    Info->>Info: 信任 Gateway Header 中的调用方身份
    Info->>Info: 查询教师主数据
    Info->>Info: 附加 snapshotTime
    Info->>Log: 记录调用方 + 查询条件 + 版本号
    Info-->>Gateway: 200 {items, pagination, snapshotTime}
    Gateway-->>B: 教师名单（含版本）
```

## 5. 角色变更流程

```mermaid
sequenceDiagram
    actor Admin as 管理员
    participant Info as Info Service
    participant Auth as Auth Service
    participant Audit as 审计日志

    Admin->>Info: PATCH /users/{id} {role_ids: [...]}
    Info->>Info: 校验操作者权限
    Info->>Info: UPDATE users_info SET role_ids
    Info->>Auth: POST /internal/users/{id}/roles {role_ids}
    Auth->>Auth: 删除旧 user_roles
    Auth->>Auth: 插入新 user_roles
    alt 成功
        Auth-->>Info: 200 OK
        Info->>Audit: 写审计日志 (action=role_changed)
        Info-->>Admin: 200 角色更新成功
    else 失败
        Auth-->>Info: 500
        Info->>Info: 回滚 role_ids
        Info-->>Admin: 500 角色更新失败
    end
```

## 6. 与 data_flow 的 L2 对齐

本系统对应 [data_flow](../../require-spec/data_flow/group_bus_L0_L1_L2_integrated.md) 中 **子系统 A（P2 信息管理）** 的 L2 分解：

| L2 过程 | 实现模块 | 关键逻辑 |
|---------|----------|----------|
| P2.1 请求解析与鉴权上下文 | Router + shared/security.py | 读取 Gateway 透传的身份 Header（X-User-Id、X-User-Role、X-User-Permissions），构建鉴权上下文 |
| P2.2 用户与档案维护 | UserManagementService | CRUD + 跨服务同步 |
| P2.3 课程校历培养方案维护 | CourseManagementService | 课程/开课/排课/校历/方案 CRUD |
| P2.4 权限变更与回收站处理 | UserManagementService + RecycleBinService | 角色同步 + 逻辑/物理删除 |
| P2.5 主数据快照发布与审计 | DataProvisionService + AuditService | HTTP 快照提供 + 审计写入 |

> L2 数据流图中使用事件总线（MQ）发布主数据快照。原型阶段改为 HTTP 同步提供（`/data-provision/*`），但预留 `EventPublisher` 接口（Python Protocol），后续可替换为 MQ 实现。
