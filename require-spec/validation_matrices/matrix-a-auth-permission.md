# Matrix-A 认证与权限

| ID | Priority | Test Scenario | Expected Output | Status | Owner |
|---|---|---|---|---|---|
| A-001 | P0 | 普通用户使用正确账号密码登录 | 返回 access/refresh token，登录成功 | Defined | TBD |
| A-002 | P0 | 普通用户使用错误密码登录 | 返回明确失败提示，不暴露敏感信息 | Defined | TBD |
| A-003 | P0 | access token 过期后使用 refresh token 续期 | 返回新 access token，会话继续可用 | Defined | TBD |
| A-004 | P0 | 普通用户访问管理员受保护接口 | 被拒绝并返回无权限错误 | Defined | TBD |
| A-005 | P0 | 管理员调整用户角色后再次访问受限接口 | 新权限立即生效，授权结果符合新角色 | Defined | TBD |
