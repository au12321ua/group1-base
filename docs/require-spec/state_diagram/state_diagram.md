# 状态图（State Diagram）

## 第一步：筛选需要绘制状态图的类

仅对“具有明确生命周期、状态可迁移且会影响业务规则”的类绘制状态图。

需要绘制：
- UserProfile：存在 ACTIVE、DISABLED、DELETED 等状态与恢复流程。
- Credential：存在失败次数累计、锁定、解锁等状态迁移。
- Token：存在签发、生效、过期、撤销等状态迁移。
- AuthenticationSession：存在 ACTIVE、ENDED、EXPIRED 等会话状态迁移。

不优先绘制（或不绘制）：
- Course：根据最新确认，不绘制状态图。
- User、Role、Permission、AuditLog、AppLogger、各 Service 类：当前定义更偏“关系/能力描述”，缺少清晰的状态机事件与状态边界。

## 第二步：分别绘制状态图

### 1) UserProfile
（包含了物理删除的二次确认与状态流转约定）

```mermaid
stateDiagram-v2
    [*] --> 正常

    正常 --> 禁用: 管理员禁用(同步禁用Credential)
    禁用 --> 正常: 管理员启用(同步启用Credential)

    正常 --> 已逻辑删除: 管理员删除用户
    禁用 --> 已逻辑删除: 管理员删除用户

    已逻辑删除 --> 正常: 回收站恢复用户
    已逻辑删除 --> 待物理删除确认: 选中并点击物理删除
    
    待物理删除确认 --> 已逻辑删除: 取消/驳回
    待物理删除确认 --> [*]: 二次确认后执行物理删除
```

### 2) Credential
（按照失败5次锁定10分钟，不支持指数退避，支持管理员强制解除绘制）

```mermaid
stateDiagram-v2
    [*] --> 可用

    可用 --> 可用: 登录成功/修改密码/重置密码
    可用 --> 锁定: 连续登录失败达到5次

    锁定 --> 可用: 满10分钟自动解除 / 管理员强制解锁
    锁定 --> 锁定: 锁定期间尝试登录(不累计时间)
    
    可用 --> 禁用: 同步自 UserProfile 禁用
    锁定 --> 禁用: 同步自 UserProfile 禁用
    禁用 --> 可用: 同步自 UserProfile 启用
    
    禁用 --> [*]: 随档案被物理删除
```

### 3) Token
（明确 Access 仅自然过期，Refresh 可被撤销）

```mermaid
stateDiagram-v2
    [*] --> 已签发
    已签发 --> 有效: 下发给客户端

    有效 --> 过期: 到达 expiresAt(Access/Refresh均会发生)
    有效 --> 已撤销: 主动登出/安全策略撤销(仅作用于 Refresh Token)

    过期 --> [*]
    已撤销 --> [*]
```

### 4) AuthenticationSession
（明确仅通过 Refresh Token 的失效来判定 Session 过期）

```mermaid
stateDiagram-v2
    [*] --> 活跃

    活跃 --> 活跃: 请求访问 / 刷新访问令牌(Access)
    活跃 --> 已结束: 用户主动退出登录(撤销 Refresh Token)
    活跃 --> 已过期: Refresh Token 达到过期时间

    已结束 --> [*]
    已过期 --> [*]
```

## 业务规则说明（基于确认信息的补充）
1. **账号锁定与解锁**：连续失败5次后锁定10分钟，不支持指数退避。满10分钟后自动解除，同时允许管理员强制解除锁定状态。
2. **账号生命周期联动**：UserProfile 状态变更为“禁用”或“启用”时，需同步联动到对应的 Credential 禁用/启用（如状态图所示）。
3. **退出的 Token 更新机制**：主动退出或结束会话时，仅作废 Refresh Token。下发在客户端既有的 Access Token 等待其自然到期，实现轻量级注销。
4. **Session 状态判定**：AuthenticationSession 的生命与终结，统一以 Refresh Token 失效为准。
5. **物理删除保护**：对用户的物理删除属于高危操作，强制要求系统进入“二次确认”阶段，以防误删。
