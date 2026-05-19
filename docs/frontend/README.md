# STSS 管理前端

Vue 3 管理后台单页应用，提供用户管理、课程管理、开课管理等 9 个模块的管理界面。

## 技术栈

| 组件 | 选择 | 版本 |
|------|------|------|
| 框架 | Vue 3 (Composition API) | ^3.4 |
| 语言 | TypeScript | ~5.4 |
| 构建 | Vite | ^5.3 |
| UI 库 | Element Plus | ^2.7 |
| 路由 | Vue Router 4 | ^4.3 |
| 状态管理 | Pinia | ^2.1 |
| HTTP 客户端 | Axios | ^1.7 |

## 目录结构

```
frontend/
├── public/
│   └── vite.svg              # 网站图标
├── src/
│   ├── api/
│   │   └── client.ts         # Axios 实例（拦截器、Token 续期）
│   ├── components/
│   │   └── StatusTag.vue     # 状态标签（ACTIVE/DISABLED/DELETED）
│   ├── directives/
│   │   └── permission.ts     # v-permission 权限指令
│   ├── layouts/
│   │   └── AdminLayout.vue   # 管理布局（侧边栏 + 顶栏 + 内容区）
│   ├── router/
│   │   └── index.ts          # 路由表 + 导航守卫
│   ├── stores/
│   │   └── auth.ts           # 认证 Store（登录/退出/Token 刷新/权限）
│   ├── views/
│   │   ├── Login.vue         # 登录页
│   │   ├── Forbidden.vue     # 403 页
│   │   ├── users/            # 用户管理（列表/新增/详情/批量导入）
│   │   ├── courses/          # 课程管理
│   │   ├── offerings/        # 开课管理
│   │   ├── schedules/        # 排课管理
│   │   ├── calendars/        # 校历管理
│   │   ├── training/         # 培养方案
│   │   ├── base-info/        # 基础信息
│   │   ├── recycle-bin/      # 回收站
│   │   └── audit-logs/       # 审计日志
│   ├── App.vue               # 根组件
│   ├── env.d.ts              # 类型声明
│   └── main.ts               # 入口（注册 Element Plus / Pinia / Router）
├── index.html
├── package.json
├── tsconfig.json
├── tsconfig.node.json
└── vite.config.ts
```

## 快速启动

```bash
cd frontend
npm install
npm run dev
```

浏览器打开 `http://localhost:5173`。

> 后端服务需同时在 `localhost:8001`（Auth）和 `localhost:8002`（Info）运行，前端通过 Vite proxy 转发 `/auth` 和 `/api` 请求。

## 脚本

| 命令 | 说明 |
|------|------|
| `npm run dev` | 启动开发服务器（热更新） |
| `npm run build` | 类型检查 + 生产构建 |
| `npm run preview` | 预览生产构建产物 |

## 代理配置

开发环境下，Vite 自动代理以下路径：

| 前缀 | 目标 |
|------|------|
| `/auth` | `http://localhost:8001` |
| `/api` | `http://localhost:8002` |

配置位于 `vite.config.ts` → `server.proxy`。

## 路由一览

| 路径 | 页面 | 权限 |
|------|------|------|
| `/login` | 登录页 | 访客 |
| `/users` | 用户列表 | `user:read` |
| `/users/create` | 新增用户 | `user:create` |
| `/users/:id` | 用户详情 | `user:read` |
| `/users/import` | 批量导入 | `user:create` |
| `/courses` | 课程管理 | `course:read` |
| `/offerings` | 开课管理 | `offering:read` |
| `/schedules` | 排课管理 | `schedule:read` |
| `/calendars` | 校历管理 | `calendar:read` |
| `/training-programs` | 培养方案 | `training:read` |
| `/base-info` | 基础信息 | `base-info:read` |
| `/recycle-bin` | 回收站 | `recycle:read` |
| `/audit-logs` | 审计日志 | `audit:read` |
| `/403` | 无权限 | — |

## 相关文档

- [开发指南](./development-guide.md) — 如何添加页面、调用 API、使用 Store 等
- [设计文档](../design/v2/09-frontend-architecture.md) — 前端架构设计
- [后端总览](../../CLAUDE.md) — 后端技术栈与架构
