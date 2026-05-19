# 前端开发指南

本文档覆盖日常开发中的常见任务：添加页面、配置路由、调用 API、使用 Store 和指令。

## 目录

- [代码规范](#代码规范)
- [添加新页面](#添加新页面)
- [添加新路由](#添加新路由)
- [调用 API](#调用-api)
- [使用 Auth Store](#使用-auth-store)
- [权限控制](#权限控制)
- [使用组件](#使用组件)
- [新增 API 模块](#新增-api-模块)

---

## 代码规范

### SFC 结构

所有 `.vue` 文件使用 `<script setup lang="ts">`，按以下顺序组织：

```vue
<template>
  <!-- 模板 -->
</template>

<script setup lang="ts">
// 逻辑
</script>

<style scoped>
/* 局部样式 */
</style>
```

### 类型注解

- 所有函数参数和返回值必须有类型注解
- Props 使用 `defineProps<T>()` 泛型语法
- Emits 使用 `defineEmits<T>()` 泛型语法

### 命名约定

| 类别 | 规则 | 示例 |
|------|------|------|
| 变量/函数 | camelCase | `userList`, `handleSubmit` |
| 组件文件 | PascalCase | `UserList.vue` |
| 目录 | kebab-case | `audit-logs/` |
| 路由名 | PascalCase | `UserList` |
| 路由路径 | kebab-case | `/training-programs` |
| 接口/类型 | PascalCase | `UserInfo` |

### 文档字符串

- 使用中文注释说明用途
- 注释放在所描述代码的上方
- 组件逻辑用 `/** */`，行内逻辑用 `//`

---

## 添加新页面

以添加「数据报表」页面为例。

### 1. 创建页面组件

```vue
<!-- src/views/reports/ReportList.vue -->
<template>
  <div class="page">
    <h2>数据报表</h2>
    <!-- 页面内容 -->
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";

const loading = ref(false);
// 业务逻辑
</script>

<style scoped>
.page {
  padding: 20px;
}
</style>
```

### 2. 注册路由

在 `src/router/index.ts` 的 `AdminLayout.children` 中添加：

```typescript
{
  path: "reports",
  name: "ReportList",
  component: () => import("@/views/reports/ReportList.vue"),
  meta: { permission: "report:read" },
}
```

### 3. 添加侧边栏菜单项

在 `src/layouts/AdminLayout.vue` 的 `<el-menu>` 中添加：

```vue
<el-menu-item index="/reports">
  <el-icon><DataAnalysis /></el-icon>
  <span>数据报表</span>
</el-menu-item>
```

同时在 `<script setup>` 中导入对应图标。

---

## 添加新路由

路由定义在 `src/router/index.ts`，遵循以下模式：

```typescript
{
  path: "/",                       // 根路由
  name: "Admin",
  component: AdminLayout,
  meta: { requiresAuth: true },    // 需要登录
  children: [
    {
      path: "users",               // 子路由路径（相对父级）
      name: "UserList",            // 命名路由
      component: () => import("@/views/users/UserList.vue"),
      meta: { permission: "user:read" },  // 所需权限码
    },
  ],
}
```

### meta 字段说明

| meta 字段 | 类型 | 说明 |
|-----------|------|------|
| `requiresAuth` | `boolean` | 需要登录，未登录跳转到 `/login` |
| `guest` | `boolean` | 仅未登录可访问（如 `/login`） |
| `permission` | `string` | 需要的权限码，缺失跳转到 `/403` |

> 导航守卫逻辑在 `router.beforeEach` 中，顺序为：认证检查 → 访客检查 → 权限检查。

---

## 调用 API

### 使用封装好的 apiClient

```typescript
import apiClient from "@/api/client";

// GET
const res = await apiClient.get("/api/users", { params: { page: 1 } });

// POST
const res = await apiClient.post("/api/users", { username: "test" });

// PUT
const res = await apiClient.put("/api/users/123", { username: "new" });

// DELETE
const res = await apiClient.delete("/api/users/123");
```

### 关于 apiClient

`src/api/client.ts` 提供了预配置的 Axios 实例：

- **请求拦截器** 自动附加 `Authorization: Bearer <token>`
- **响应拦截器** 自动处理 401 → Token 刷新 → 重试原请求
- **错误处理** 自动弹出 `ElMessage.error` 显示错误信息

响应数据结构遵循后端 `APIResponse` 格式：

```typescript
interface APIResponse<T> {
  code: number;
  message: string;
  data: T;
}
```

### 不使用 apiClient 的场景

登录和刷新 Token 接口不要用 `apiClient`（会触发循环依赖），直接使用 `axios`。

---

## 使用 Auth Store

```typescript
import { useAuthStore } from "@/stores/auth";

const authStore = useAuthStore();

// 读取状态
console.log(authStore.token);
console.log(authStore.user?.username);
console.log(authStore.isAuthenticated);  // computed

// 登录
await authStore.login(username, password);

// 退出
await authStore.logout();

// 权限检查
if (authStore.hasPermission("user:create")) {
  // 显示新建按钮
}
```

### Store 字段一览

| 字段 | 类型 | 说明 |
|------|------|------|
| `token` | `string \| null` | Access Token |
| `refreshToken` | `string \| null` | Refresh Token |
| `user` | `UserInfo \| null` | 当前用户信息 |
| `permissions` | `string[]` | 用户权限码列表 |
| `isAuthenticated` | `ComputedRef<boolean>` | 是否已登录 |
| `hasPermission(code)` | `(code: string) => boolean` | 检查是否拥有权限 |

---

## 权限控制

### 路由级

在路由 `meta` 中声明 `permission`，导航守卫自动拦截：

```typescript
{ path: "users", meta: { permission: "user:read" } }
```

### 元素级

使用 `v-permission` 指令控制按钮/元素的可见性：

```vue
<el-button v-permission="'user:create'" type="primary" @click="handleCreate">
  新增
</el-button>
```

> 无权限时元素会被从 DOM 中移除（`parentNode.removeChild`）。

### 编程式

在逻辑中根据返回值决定行为：

```typescript
if (!authStore.hasPermission("user:delete")) {
  ElMessage.warning("无操作权限");
  return;
}
```

---

## 使用组件

### StatusTag

```vue
<StatusTag status="ACTIVE" />
```

| status 值 | 显示效果 |
|-----------|----------|
| `ACTIVE` | 绿色 `success` 标签 |
| `DISABLED` | 橙色 `warning` 标签 |
| `DELETED` | 红色 `danger` 标签 |
| 其他 | 灰色 `info` 标签 |

---

## 新增 API 模块

在 `src/api/` 下按领域新建文件，通过 `apiClient` 封装接口：

```typescript
// src/api/user.ts
import apiClient from "./client";

export interface User {
  userId: string;
  username: string;
  status: string;
}

/** 获取用户列表 */
export function fetchUserList(page: number, size: number) {
  return apiClient.get<{ items: User[]; total: number }>("/api/users", {
    params: { page, size },
  });
}

/** 创建用户 */
export function createUser(data: { username: string; password: string }) {
  return apiClient.post("/api/users", data);
}
```

页面组件中直接调用：

```typescript
import { fetchUserList } from "@/api/user";

const users = ref<User[]>([]);
const res = await fetchUserList(1, 20);
users.value = res.data.data.items;
```
