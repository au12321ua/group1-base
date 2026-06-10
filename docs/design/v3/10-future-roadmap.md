# 10 — 未来演进路线图

> ⚠️ **状态说明**：本文档中描述的所有功能均为**未来规划**，当前代码库**暂未实现**。
> 每个章节开头的状态标记指示该功能的实现状态。

## 1. 演进概览

```
原型阶段（当前）           中期（v1.x）              远期（v2.x）
──────────────────────────────────────────────────────────
SQLite (3 DB)      →     PostgreSQL (3 DB)    →    PostgreSQL + 读写分离
无缓存              →     Redis 查询缓存       →    Redis 集群
HTTP 同步补偿        →     HTTP + 补偿重试      →    MQ 异步 (RabbitMQ)
Model-First 建表    →     Alembic 迁移          →    CI/CD 自动迁移
单机部署             →     Docker Compose       →    K8s 容器编排
```

## 2. Redis 缓存层

> **状态**：🔴 暂未实现

### 2.1 目标

引入 Redis 作为缓存层，加速热点数据查询，减少数据库压力。

### 2.2 缓存策略

#### 2.2.1 候选缓存数据

| 数据 | 缓存模式 | TTL | 失效策略 | 优先级 |
|------|----------|-----|----------|--------|
| 用户基本信息（UserInfo + UserProfile） | Cache-Aside | 5 min | 写操作时主动失效 | P0 |
| 角色与权限映射（Role → Permissions） | 启动预加载 + 写时刷新 | 30 min | 角色变更时刷新 | P0 |
| 课程列表（热点查询） | Cache-Aside | 10 min | 课程变更时失效 | P1 |
| 校历数据 | Cache-Aside | 1 hour | 校历更新时失效 | P2 |
| 基础信息条目 | Cache-Aside | 30 min | 条目更新时失效 | P2 |
| Token 黑名单（Access Token 即时撤销） | Write-Through | =Token 剩余有效期 | 自动过期 | P1 |

#### 2.2.2 缓存模式

**Cache-Aside（旁路缓存）— 主要模式**：

```
读取路径：
  1. 查询 Redis → 命中则返回
  2. 未命中 → 查询 DB → 写入 Redis（设 TTL）→ 返回

写入路径：
  1. 更新 DB
  2. 删除 Redis 对应缓存（invalidate）
```

**Write-Through（写穿）— 用于 Token 黑名单**：

```
写入路径：
  1. 同时写入 Redis + DB
  2. Redis 设 TTL 自动过期
```

### 2.3 架构设计

```
┌──────────────────────────────────────────┐
│               Info Service                │
│                                           │
│  ┌──────────┐    ┌──────────────────┐    │
│  │  Router   │ →  │     Service      │    │
│  └──────────┘    └───────┬──────────┘    │
│                          │               │
│              ┌───────────┼───────────┐   │
│              ▼           ▼           ▼   │
│        ┌─────────┐ ┌─────────┐ ┌───────┐│
│        │ Cache   │ │  CRUD   │ │ Auth  ││
│        │ Layer   │ │  Layer  │ │ Client││
│        └────┬────┘ └────┬────┘ └───────┘│
│             │           │                │
└─────────────┼───────────┼────────────────┘
              │           │
        ┌─────▼───┐  ┌───▼──────┐
        │  Redis  │  │ PostgreSQL│
        └─────────┘  └──────────┘
```

### 2.4 实现方案

#### 2.4.1 依赖

```toml
# pyproject.toml
[project.dependencies]
redis = { version = ">=5.0", optional = true }
hiredis = { version = ">=2.0", optional = true }

[project.optional-dependencies]
redis = ["redis", "hiredis"]
```

#### 2.4.2 配置

```python
# shared/config.py
class SharedSettings(BaseSettings):
    # Redis 配置（暂未启用）
    redis_enabled: bool = False
    redis_url: str = "redis://localhost:6379/0"
    redis_cache_ttl_default: int = 300  # 5 min

# 环境变量
REDIS_ENABLED=false
REDIS_URL=redis://redis:6379/0
```

#### 2.4.3 缓存装饰器接口（预留）

```python
# info_service/services/cache.py（预留给未来实现）
from functools import wraps
from typing import Callable, TypeVar

T = TypeVar("T")

class CacheLayer:
    """Redis 缓存层 — 暂未实现，接口预留"""

    def __init__(self, redis_client):
        self.redis = redis_client

    async def get(self, key: str) -> bytes | None:
        """从缓存获取数据"""
        raise NotImplementedError("TODO: Redis 缓存暂未实现")

    async def set(self, key: str, value: bytes, ttl: int) -> None:
        """写入缓存"""
        raise NotImplementedError("TODO: Redis 缓存暂未实现")

    async def delete(self, key: str) -> None:
        """删除缓存"""
        raise NotImplementedError("TODO: Redis 缓存暂未实现")

    async def delete_pattern(self, pattern: str) -> None:
        """按模式删除缓存"""
        raise NotImplementedError("TODO: Redis 缓存暂未实现")


def cached(key_pattern: str, ttl: int = 300):
    """缓存装饰器 — 暂未实现，接口预留。
    
    用于 Service 层方法，自动处理 Cache-Aside 模式。
    
    Usage:
        @cached("user:{user_id}", ttl=300)
        async def get_user(self, user_id: str) -> UserResponse:
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # TODO: 检查 Redis 缓存
            # TODO: 命中 → 返回缓存数据
            # TODO: 未命中 → 调用原函数 → 写入缓存 → 返回
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

### 2.5 Docker Compose 补充

```yaml
# 未来添加到 docker-compose.yml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
    restart: unless-stopped

volumes:
  redis_data:
```

### 2.6 切换步骤

1. 添加 `redis` 和 `hiredis` 可选依赖
2. 实现 `CacheLayer` 类（`info_service/services/cache.py`）
3. 在各 Service 方法上添加 `@cached` 装饰器
4. 在写操作中调用 `cache.delete()` 主动失效
5. 更新 `docker-compose.yml` 添加 Redis 服务
6. 设置 `REDIS_ENABLED=true` 启用

### 2.7 注意事项

- **缓存一致性**：写操作必须先更新 DB，再删除缓存（避免缓存雪崩）
- **缓存穿透**：对不存在的数据缓存空值（短 TTL）
- **缓存击穿**：热点数据过期时使用互斥锁防止并发查询 DB
- **降级策略**：Redis 不可用时自动 fallback 到直接查询 DB
- **监控**：缓存命中率、延迟、内存使用

---

## 3. PostgreSQL 数据库切换

> **状态**：🔴 暂未实现

### 3.1 目标

从 SQLite 切换到 PostgreSQL，获得以下能力：
- 真正的并发写入支持（SQLite 单写锁限制）
- 生产级性能和可靠性
- 高级查询功能（JSON 字段、全文搜索、窗口函数）
- 连接池管理

### 3.2 当前准备状态

| 准备项 | 状态 | 说明 |
|--------|------|------|
| SQLModel 模型定义 | ✅ 已就绪 | 使用标准 SQLModel 类型，无需修改 |
| Alembic 配置 | ✅ 已保留 | 3 条迁移链（auth/info/audit）配置完整 |
| 数据库连接配置 | ✅ 已支持 | 通过环境变量切换 URL 即可 |
| 数据迁移方案 | ⬜ 待制定 | 需 SQLite → PostgreSQL 数据迁移工具 |
| 连接池配置 | ⬜ 待添加 | 需要配置 SQLAlchemy 连接池参数 |

### 3.3 切换方案

#### 3.3.1 配置变更

```ini
# .env — 仅需修改数据库 URL
# SQLite（当前）
AUTH_DATABASE_URL=sqlite+aiosqlite:///auth_service/data/auth.db
INFO_DATABASE_URL=sqlite+aiosqlite:///info_service/data/info.db
AUDIT_DATABASE_URL=sqlite+aiosqlite:///data/audit.db

# PostgreSQL（未来切换）
AUTH_DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/auth_db
INFO_DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/info_db
AUDIT_DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/audit_db
```

#### 3.3.2 依赖

```toml
# pyproject.toml
[project.dependencies]
asyncpg = { version = ">=0.29", optional = true }

[project.optional-dependencies]
postgresql = ["asyncpg"]
```

#### 3.3.3 SQLAlchemy 引擎配置（需调整）

```python
# shared/database.py — 当前实现（SQLite）
def create_engine(database_url: str):
    return create_async_engine(
        database_url,
        echo=False,
    )

# shared/database.py — PostgreSQL 切换后
def create_engine(database_url: str):
    is_postgres = database_url.startswith("postgresql")
    return create_async_engine(
        database_url,
        echo=False,
        pool_size=20 if is_postgres else None,        # PG 连接池
        max_overflow=10 if is_postgres else None,      # 溢出连接
        pool_pre_ping=True if is_postgres else False,  # 连接健康检查
    )
```

### 3.4 Alembic 迁移流程

```
原型状态：                        PostgreSQL 切换后：
                                  
SQLModel.metadata.create_all()    1. 生成初始迁移
       ↓                          2. alembic revision --autogenerate
  自动建表（3 条链）               3. alembic upgrade head（初始基准）
       ↓                          4. 数据迁移（SQLite → PG）
  无版本历史                      5. 后续增量迁移
                                  6. CI/CD 自动执行迁移
```

#### 迁移命令参考

```bash
# Auth 迁移链
cd auth_service
alembic -c migrations/alembic.ini revision --autogenerate -m "initial"
alembic -c migrations/alembic.ini upgrade head

# Info 迁移链
cd info_service
alembic -c migrations/info/alembic.ini revision --autogenerate -m "initial"
alembic -c migrations/info/alembic.ini upgrade head

# Audit 迁移链
alembic -c migrations/audit/alembic.ini revision --autogenerate -m "initial"
alembic -c migrations/audit/alembic.ini upgrade head
```

### 3.5 Docker Compose 补充

```yaml
# 未来添加到 docker-compose.yml
services:
  postgres:
    image: postgres:16-alpine
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: stss
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-stss_dev}
      POSTGRES_DB: postgres
    volumes:
      - pg_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U stss"]
      interval: 5s
    restart: unless-stopped

volumes:
  pg_data:
```

### 3.6 初始化 SQL 脚本

```sql
-- scripts/init-db.sql（未来使用）
CREATE DATABASE auth_db OWNER stss;
CREATE DATABASE info_db OWNER stss;
CREATE DATABASE audit_db OWNER stss;
```

### 3.7 潜在不兼容项

SQLite 与 PostgreSQL 的差异需要在切换前检查：

| 差异项 | SQLite 行为 | PostgreSQL 行为 | 影响 |
|--------|-------------|-----------------|------|
| 自增主键 | `INTEGER PRIMARY KEY` 自动自增 | 需 `SERIAL` 或 `IDENTITY` | SQLModel 已处理 |
| 日期类型 | 无原生 DATE，存为 TEXT | 原生 `DATE` 类型 | Pydantic 序列化可能不同 |
| 布尔类型 | INTEGER (0/1) | 原生 `BOOLEAN` | SQLModel 已处理 |
| LIKE 大小写 | 默认不区分 | 默认区分（需 `ILIKE`） | 搜索功能可能受影响 |
| 并发写入 | 单写锁 | MVCC 多版本 | 性能大幅提升 |
| 外键约束 | 默认关闭 | 默认开启 | 需确保代码不依赖 SQLite 宽松行为 |

### 3.8 数据迁移方案

```bash
# 方案 A：使用 pgloader（推荐）
pgloader sqlite:///auth.db postgresql://user:pass@localhost/auth_db
pgloader sqlite:///info.db postgresql://user:pass@localhost/info_db
pgloader sqlite:///audit.db postgresql://user:pass@localhost/audit_db

# 方案 B：Python 脚本逐表导出导入
uv run python scripts/migrate_sqlite_to_pg.py
```

### 3.9 切换步骤

1. **准备阶段**：
   - 添加 `asyncpg` 依赖
   - 更新 `docker-compose.yml` 添加 PostgreSQL 服务
   - 创建初始化 SQL 脚本
2. **配置阶段**：
   - 更新 `.env` 中的数据库 URL
   - 配置连接池参数
3. **迁移阶段**：
   - 启用 Alembic，生成初始迁移
   - 执行 `alembic upgrade head` 建表
4. **数据迁移**：
   - 使用 pgloader 或自定义脚本迁移数据
   - 验证数据完整性（行数、关联关系）
5. **验证阶段**：
   - 全量测试套件通过
   - 性能基准测试
6. **上线**：
   - 切换生产环境配置
   - 监控数据库性能

---

## 4. 其他未来演进项

### 4.1 消息队列（MQ）

> **状态**：🔴 暂未实现

- **目标**：跨服务异步通信，替代当前 HTTP 同步调用
- **候选**：Redis Pub/Sub（轻量）→ RabbitMQ（生产级）
- **影响**：06 号文档中的跨服务流程将从"HTTP 同步 + 补偿"变为"事件发布 + 订阅"
- **预留接口**：Python Protocol `EventPublisher`，各 Service 通过依赖注入获取

### 4.2 API 版本管理

> **状态**：🔴 暂未实现

- **目标**：`/api/v1/` → `/api/v2/` 平滑升级
- **策略**：URL 前缀版本 + Deprecation Header 通知
- **当前约定**：全部端点使用 `/api/v1/` 前缀

### 4.3 监控与告警

> **状态**：🔴 暂未实现

- **目标**：Prometheus Metrics + Grafana Dashboard
- **指标**：请求延迟（p50/p95/p99）、错误率、DB 查询耗时、缓存命中率
- **当前替代**：结构化 JSON 日志 + `grep` 手动排查

---

## 5. 优先级与时间线

| 阶段 | 内容 | 优先级 | 预估工作量 | 前置条件 |
|------|------|--------|-----------|----------|
| v1.0（当前） | 原型稳定、测试完善 | — | — | — |
| v1.1 | PostgreSQL 切换 | P0 | 3-5 天 | 测试覆盖率 ≥ 90% |
| v1.2 | Redis 缓存层 | P1 | 3-5 天 | PostgreSQL 切换完成 |
| v1.3 | Token 黑名单（Redis） | P1 | 1-2 天 | Redis 可用 |
| v2.0 | MQ 异步通信 | P2 | 5-7 天 | 业务稳定、跨服务调用频繁 |
| v2.1 | 监控与告警 | P2 | 3-5 天 | 生产环境运行 |
| v2.2 | Kubernetes 部署 | P3 | 5-7 天 | 容器化稳定运行 |
