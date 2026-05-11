# Matrix-D 审计与非功能

| ID | Priority | Test Scenario | Expected Output | Status | Owner |
|---|---|---|---|---|---|
| D-001 | P0 | 执行高风险操作（删除、权限变更、批量导入）后查询审计日志 | 审计日志可检索，包含时间、操作者、对象、结果 | Defined | TBD |
| D-002 | P0 | 用户密码入库存储检查 | 不存在明文密码，仅存储带盐哈希 | Defined | TBD |
| D-003 | P1 | 常规查询接口性能测试 | 90% 请求响应时间 <= 500ms | Defined | TBD |
| D-004 | P1 | 登录接口性能测试 | 常规并发下响应时间 <= 800ms | Defined | TBD |
| D-005 | P1 | 异常场景错误码与提示校验 | 返回统一错误码与可读提示 | Defined | TBD |
