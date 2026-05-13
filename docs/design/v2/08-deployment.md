# 08 — 部署架构

## 1. 服务端口规划

| 服务 | 端口 | 负责方 | 说明 |
|------|------|--------|------|
| Nginx Gateway | 8000 | 其他组 | 统一入口、路由、限流 |
| **Auth Service** | 8001 | **本组** | 认证授权 |
| **Info Service** | 8002 | **本组** | 业务信息管理 |

> 本组仅负责 Auth Service（8001）和 Info Service（8002），不部署 Gateway。

## 2. 容器化部署

### 2.1 Docker Compose 编排

```yaml
# docker-compose.yml
version: "3.9"

services:
  auth_service:
    build:
      context: ./auth_service
      dockerfile: Dockerfile
    ports:
      - "8001:8001"
    env_file:
      - .env
    volumes:
      - auth_data:/app/data        # Auth DB 持久化
      - ./auth_service:/app        # 开发热重载
    command: uvicorn main:app --host 0.0.0.0 --port 8001 --reload

  info_service:
    build:
      context: ./info_service
      dockerfile: Dockerfile
    ports:
      - "8002:8002"
    env_file:
      - .env
    volumes:
      - info_data:/app/data        # Info DB 持久化
      - uploads:/app/uploads       # 上传文件目录
      - logs:/app/logs             # 日志文件目录
      - ./info_service:/app        # 开发热重载
    command: uvicorn main:app --host 0.0.0.0 --port 8002 --reload

volumes:
  auth_data:
  info_data:
  uploads:
  logs:
```

### 2.2 Dockerfile（多阶段构建）

```dockerfile
# auth_service/Dockerfile (info_service 同理)
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
EXPOSE 8001
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

### 2.3 数据卷挂载

| 卷名 | 挂载路径 | 内容 |
|------|----------|------|
| `auth_data` | `/app/data` | Auth DB（auth.db） |
| `info_data` | `/app/data` | Info DB（info.db） |
| `uploads` | `/app/uploads` | 用户上传文件 |
| `logs` | `/app/logs` | 应用日志 + 审计日志（audit.db） |

## 3. 环境配置

### 3.1 环境变量（.env）

```ini
# ===== 公共 =====
ENV=development
LOG_LEVEL=DEBUG

# ===== Auth Service =====
AUTH_DATABASE_URL=sqlite:///data/auth.db
TOKEN_SECRET_KEY=change-me-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=15
ADMIN_ACCESS_TOKEN_EXPIRE_MINUTES=5
REFRESH_TOKEN_EXPIRE_DAYS=7
SERVICE_TOKEN_EXPIRE_HOURS=8
MAX_LOGIN_ATTEMPTS=5
ACCOUNT_LOCK_MINUTES=10
BCRYPT_COST_FACTOR=12

# ===== Info Service =====
INFO_DATABASE_URL=sqlite:///data/info.db
AUDIT_DATABASE_URL=sqlite:///logs/audit.db
AUTH_SERVICE_URL=http://auth_service:8001
UPLOAD_DIR=/app/uploads
MAX_UPLOAD_SIZE_MB=10
ALLOWED_UPLOAD_TYPES=jpg,jpeg,png,pdf,csv
```

### 3.2 多环境策略

| 文件 | 用途 | 加载方式 |
|------|------|----------|
| `.env` | 开发环境默认值 | 自动加载（Pydantic Settings） |
| `.env.prod` | 生产环境覆盖 | `ENV=prod` 时加载 |

```python
# core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    env: str = "development"
    auth_database_url: str = "sqlite:///data/auth.db"
    # ...

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }

# 生产环境：通过环境变量 ENV=prod 触发加载 .env.prod
# Docker 启动时：docker compose --env-file .env.prod up
```

## 4. 开发环境

### 4.1 本地直接启动

```bash
# 终端 1 — Auth Service
cd auth_service
uvicorn main:app --port 8001 --reload

# 终端 2 — Info Service
cd info_service
uvicorn main:app --port 8002 --reload
```

### 4.2 Docker Compose 一键启动

```bash
docker compose up -d
```

### 4.3 开发流程

1. 克隆仓库 → 复制 `.env.example` 为 `.env`。
2. 初始化数据库：`alembic upgrade head`（每个服务独立执行）。
3. 导入种子数据（角色 + 权限 + 初始管理员）。
4. 启动服务 → 访问 `http://localhost:8001/docs`（Auth）/ `http://localhost:8002/docs`（Info）查看 Swagger 文档。

## 5. 网络拓扑

```
                    ┌──────────────┐
                    │   Browser    │
                    │  (管理端 SPA) │
                    └──────┬───────┘
                           │ :8000
                    ┌──────▼───────┐
                    │ Nginx Gateway│ (其他组)
                    │    :8000     │
                    └──┬────────┬──┘
                       │        │
              :8001    │        │    :8002
            ┌──────────▼──┐ ┌──▼──────────┐
            │ Auth Service│ │ Info Service│
            │    :8001    │ │    :8002    │
            └──────┬──────┘ └──┬────┬─────┘
                   │           │    │
            ┌──────▼──┐  ┌────▼──┐ ┌▼──────┐
            │ Auth DB │  │Info DB│ │Log DB │
            │(auth.db)│  │(info. │ │(audit.│
            │         │  │ db)   │ │ db)   │
            └─────────┘  └───────┘ └───────┘
```

### 5.1 通信方式

| 通信方向 | 协议 | 说明 |
|----------|------|------|
| Browser → Gateway | HTTP/HTTPS | 管理端前端请求 |
| Gateway → Auth | HTTP（内部网络） | Gateway 调用 Auth `/internal/verify` 验签并提取身份信息 |
| Gateway → Info | HTTP（内部网络） | 透传身份 Header（X-User-Id、X-User-Role、X-User-Permissions） |
| Auth ↔ Info | HTTP（内部网络） | 跨服务同步调用（Docker 内部 DNS `auth_service:8001`） |

## 6. 部署检查清单

- [ ] 生产环境 `.env.prod` 已配置（TOKEN_SECRET_KEY 必须更换）
- [ ] 管理员初始密码已设置
- [ ] CORS 白名单已限定为管理端域名
- [ ] 数据库文件目录已设置适当的文件系统权限
- [ ] 日志目录磁盘空间充足（预估 500MB+ 预留）
- [ ] Docker 数据卷已配置备份策略
