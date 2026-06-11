# STSS 信息管理系统 — 架构设计文档（V3）

> 本目录包含 STSS 大组中 **子系统 A（信息管理）** 的完整架构设计。
> 设计基于 [需求规格](../../require-spec/requirement-spec.md) 展开，遵循 Clean Architecture 与 DDD 分层原则。
>
> **V3 变更**：项目已转为**纯后端**架构，移除前端相关设计；修正 V2 与代码实现之间的差异；新增测试设计方法论指导文档；新增 Redis/PostgreSQL 未来演进路线图。

## 文档索引

| 编号 | 文档 | 内容 | 与 V2 差异 |
|------|------|------|------------|
| 01 | [系统总体架构](01-system-overview.md) | 系统上下文、STSS 大组定位、服务边界、技术栈决策、未来演进目标 | 移除前端技术栈；新增 Redis/PG 未来目标 |
| 02 | [模块架构](02-module-architecture.md) | 分层架构（Router → Service → CRUD → Model）、Auth/Info 服务内部模块设计 | 修正实际目录结构（classrooms、deps、auth_client）；修正 shared 模块描述 |
| 03 | [数据架构](03-data-architecture.md) | 数据库分库设计、ER 图、跨库一致性策略、Alembic 迁移 | 修正实际表名与模型名；补充索引策略 |
| 04 | [安全架构](04-security-architecture.md) | 认证流程、RBAC+资源级授权、JWT 密钥管理、安全防护 | 补充缺失的内部端点；移除前端 CORS 引用 |
| 05 | [API 架构](05-api-architecture.md) | API 设计规范、完整端点清单、错误码体系 | 新增 classrooms 端点；新增 prerequisites 端点；新增 role/batch 内部端点 |
| 06 | [业务流程设计](06-business-flows.md) | 用户创建/删除/恢复、批量导入、数据提供、角色同步 | 新增角色同步流程；更新跨服务调用细节 |
| 07 | [可观测性设计](07-observability.md) | 日志体系、审计日志、链路追踪 | 微调与实际实现对齐 |
| 08 | [部署架构](08-deployment.md) | Docker Compose 编排、端口规划、环境配置 | 更新 docker-compose 匹配实际（healthcheck、seed 服务） |
| 09 | [测试设计指导](09-test-design-guide.md) | **新增**：测试设计方法论 — 如何制定测试策略、设计测试架构、规划覆盖率 | V2 无此文档 |
| 10 | [未来演进路线图](10-future-roadmap.md) | **新增**：Redis 缓存层、PostgreSQL 迁移方案（均标注暂未实现） | V2 无此文档 |

## 与 V2 的主要变更

### 项目范围调整
- **V2**：包含前端管理端（Vue 3 + Element Plus）的完整设计
- **V3**：项目已确定为纯后端，移除所有前端相关内容（原 09-frontend-architecture.md 不再保留）

### 实现差异修正
V2 设计文档中存在多处与实际代码实现不一致的地方，V3 已全部修正：

| 差异项 | V2 描述 | 实际实现 | V3 修正 |
|--------|---------|----------|---------|
| Auth 内部端点 | 4 个端点 | 7 个端点（新增 role sync、batch roles、verify） | 已补充 |
| Info classrooms | 未列入 API 清单 | 完整 CRUD 端点 | 已补充 |
| Info prerequisites | 未列入 API 清单 | 嵌套端点 | 已补充 |
| shared/security.py | 描述为"JWT 工具" | 实际为身份 Header 读取 + 权限校验 | 已修正 |
| Info services 结构 | 仅有粗粒度服务 | auth_client + auth_http_client 拆分 | 已修正 |
| Docker Compose | 简化版（无 healthcheck、seed） | 完整版（healthcheck、seed、depends_on） | 已更新 |

### 新增内容
- **测试设计指导文档**（09）：填补 V2 在测试设计方法论层面的空白
- **未来演进路线图**（10）：明确 Redis 缓存层和 PostgreSQL 迁移的目标、方案、前置条件

## V2 → V3 迁移说明

- **V2 文档保留**：`docs/design/v2/` 作为历史参考，不做删除
- **新开发参考 V3**：Agent 编码前应阅读 V3 对应章节
- **V3 中的"暂未实现"标记**：第 10 号文档中的 Redis 和 PostgreSQL 方案仅供设计参考，当前代码库未实现

## 阅读顺序建议

1. **首次阅读**：按编号顺序 01 → 10，建立完整架构认知。
2. **实现参考**：直接跳转到对应章节，各文档独立自包含。
3. **评审关注**：重点阅读 03（数据架构）、04（安全架构）、05（API 架构）、10（未来演进）。

## 设计原则

- **单向依赖**：Router → Service → CRUD → Model，禁止反向引用。
- **职责分离**：Auth Service（认证/授权）与 Info Service（业务数据）独立部署、独立数据库。
- **默认拒绝**：所有接口默认要求鉴权，显式授权访问。
- **最终一致**：跨服务写操作优先保证主写成功，同步调用失败通过补偿机制处理。
- **原型可演进**：SQLite → PostgreSQL 切换仅需修改连接配置；Redis 缓存层预留集成接口。

## 与需求文档的对应

| 需求文档 | 对应设计文档 |
|----------|-------------|
| [requirement-spec.md](../../require-spec/requirement-spec.md) | 01, 04, 05 |
| [class-definition-detailed.md](../../require-spec/class_definition/class-definition-detailed.md) | 03 |
| [use-cases-detailed.md](../../require-spec/use_cases/use-cases-detailed.md) | 05, 06 |
| [group_bus_L0_L1_L2_integrated.md](../../require-spec/data_flow/group_bus_L0_L1_L2_integrated.md) | 01, 06 |
| [design.md](../../require-spec/design.md)（设计基线） | 01, 04, 08 |
| [validation_matrices/](../../require-spec/validation_matrices/) | 09 |
