# Infomation Manager Validation Criteria 轻量方案（目标：覆盖率 >=90%）

## 1. 只保留三个目标
- 覆盖率达到并维持 >=90%。
- 高风险需求（P0）覆盖率 100%。
- 方案可长期执行：每周只维护一组小矩阵。

## 2. 覆盖率口径（固定不变）

最小验证单位：AVR（原子可验证需求）。

计算公式：
- Overall Coverage = Validated / Total * 100%
- P0 Coverage = Validated(P0) / Total(P0) * 100%

通过标准：
- Overall Coverage >= 90%
- P0 Coverage = 100%

状态仅保留 4 个：
- Defined
- Validated
- Failed
- Blocked

说明：只有 Validated 计入覆盖率。

## 3. 最小矩阵模板（核心）

Validation Matrix 只保留 6 列：

| ID | Priority | Test Scenario | Expected Output | Status | Owner |
|---|---|---|---|---|---|

填写规则：
- 每个 AVR 一行。
- Priority 仅用 P0/P1/P2。
- Test Scenario 写“动作+条件”，Expected Output 写“可判定结果”。

## 4. AVR 数量建议（简化版）

首版建议 40 条 AVR（控制维护成本）：
- P0：16 条（必须全通过）
- P1：18 条
- P2：6 条

达到 90% 的最低要求：
- 40 条中至少 36 条为 Validated。
- 且 16 条 P0 全部 Validated。

## 5. P0 最小清单（长期不轻易改）

- 登录成功/失败
- token 刷新
- 越权访问拦截
- 用户新增/编辑/查询
- 逻辑删除
- 回收站恢复
- 回收站批量物理删除
- CSV 批量导入仅新增
- 角色权限变更生效
- 教师名单查询
- 待选课名单查询
- 校历查询
- 选课学生名单查询
- 培养方案查询（含课程ID列表）
- version 或 snapshotTime 返回校验
- 高风险操作审计日志可检索

## 6. 按功能分类维护（替代单一大矩阵）

不维护一张大矩阵，改为多个小矩阵，按功能域分组，便于长期维护与责任划分。

建议分为 4 个矩阵：
- Matrix-A（认证与权限）：登录、token、越权拦截、角色权限变更
- Matrix-B（用户与回收站）：用户增查改、逻辑删除、恢复、批量物理删除、CSV导入
- Matrix-C（基础信息与数据提供）：教师名单、待选课名单、校历、选课学生名单、培养方案
- Matrix-D（审计与非功能）：审计日志、安全、性能、可靠性、可追溯字段

维护规则：
- 每个矩阵独立统计覆盖率。
- 总覆盖率按 4 个矩阵汇总计算。
- P0 可分散在各矩阵，但总体仍要求 100% 覆盖。

## 7. 长期推进节奏（每周固定）

每周只做三件事：
1. 更新各分类矩阵状态（Validated/Failed/Blocked）。
2. 计算两个指标（Overall、P0）。
3. 处理前三个失败或阻塞项。

每周输出模板：
- Total
- Validated
- Failed
- Blocked
- Overall Coverage
- P0 Coverage
- Top 3 Risks

## 8. 立即执行步骤（本周）

1. 按上面的 6 列创建 4 个分类矩阵（A/B/C/D）。
2. 先录入 16 条 P0 AVR，按功能分配到对应矩阵。
3. 再补充 24 条 P1/P2 AVR，凑满 40 条。
4. 先冲到 36/40（90%），再持续维持。

## 9. 来源范围（不扩散）

仅依据以下文档分解 AVR：
- requirement-spec.md
- design.md
- use_cases/use-cases-basic.md
- use_cases/use-cases-detailed.md
- data_flow/data_flow_level0.mmd
- data_flow/data_flow_level1.mmd
- data_flow/data_flow_level2.mmd
- state_diagram/state_diagram.md

说明：后续新增需求，按同样规则增量加入矩阵，不重写整份方案。
