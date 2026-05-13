# STSS 信息管理系统 — 架构设计文档（V2）

> 本目录包含 STSS 大组中 **子系统 A（信息管理）** 的完整架构设计。
> 设计基于 [需求规格](../../require-spec/requirement-spec.md) 与 [架构大纲](../architecture-outline.md) 展开，遵循 Clean Architecture 与 DDD 分层原则。

## 文档索引

| 编号 | 文档 | 内容 |
|------|------|------|
| 01 | [系统总体架构](01-system-overview.md) | 系统上下文、STSS 大组定位、服务边界、技术栈决策 |
| 02 | [模块架构](02-module-architecture.md) | 分层架构（Router → Service → CRUD → Model）、Auth/Info 服务内部模块设计 |
| 03 | [数据架构](03-data-architecture.md) | 数据库分库设计、ER 图、跨库一致性策略、Alembic 迁移 |
| 04 | [安全架构](04-security-architecture.md) | 认证流程、RBAC+资源级授权、JWT 密钥管理、安全防护 |
| 05 | [API 架构](05-api-architecture.md) | API 设计规范、完整端点清单、错误码体系 |
| 06 | [业务流程设计](06-business-flows.md) | 用户创建/删除/恢复、批量导入、数据提供、角色变更 |
| 07 | [可观测性设计](07-observability.md) | 日志体系、审计日志、链路追踪 |
| 08 | [部署架构](08-deployment.md) | Docker Compose 编排、端口规划、环境配置 |
| 09 | [前端架构](09-frontend-architecture.md) | Vue 3 管理端、路由权限、状态管理 |

## 阅读顺序建议

1. **首次阅读**：按编号顺序 01 → 09，建立完整架构认知。
2. **实现参考**：直接跳转到对应章节，各文档独立自包含。
3. **评审关注**：重点阅读 03（数据架构）、04（安全架构）、05（API 架构）。

## 设计原则

- **单向依赖**：Router → Service → CRUD → Model，禁止反向引用。
- **职责分离**：Auth Service（认证/授权）与 Info Service（业务数据）独立部署、独立数据库。
- **默认拒绝**：所有接口默认要求鉴权，显式授权访问。
- **最终一致**：跨服务写操作优先保证主写成功，同步调用失败通过补偿机制处理。
- **原型可演进**：SQLite → PostgreSQL 切换仅需修改连接配置，预留 MQ 接口便于后续升级。

## 与需求文档的对应

| 需求文档 | 对应设计文档 |
|----------|-------------|
| [requirement-spec.md](../../require-spec/requirement-spec.md) | 01, 04, 05 |
| [class-definition-detailed.md](../../require-spec/class_definition/class-definition-detailed.md) | 03 |
| [use-cases-detailed.md](../../require-spec/use_cases/use-cases-detailed.md) | 05, 06 |
| [group_bus_L0_L1_L2_integrated.md](../../require-spec/data_flow/group_bus_L0_L1_L2_integrated.md) | 01, 06 |
| [design.md](../../require-spec/design.md)（设计基线） | 01, 04, 08 |
| [validation_matrices/](../../require-spec/validation_matrices/) | 全文档 |
