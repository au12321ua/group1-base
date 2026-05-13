# 09 — 前端架构（管理端）

## 1. 技术栈

| 组件 | 选择 | 用途 |
|------|------|------|
| 框架 | Vue 3 + Composition API | 组件化开发 |
| 语言 | TypeScript | 类型安全 |
| UI 库 | Element Plus | 管理后台组件（Table、Form、Dialog 等） |
| 构建 | Vite | 快速 HMR 与打包 |
| 状态管理 | Pinia | 轻量状态管理 |
| 路由 | Vue Router 4 | SPA 路由 + 导航守卫 |
| HTTP | Axios | 请求拦截、Token 续期 |

## 2. 页面结构

```
登录页 (/login)
│
└─ 管理端布局 (/)
   ├─ 侧边导航
   │   ├─ 用户管理 (/users)
   │   │   ├─ 用户列表
   │   │   ├─ 用户详情 (/users/:id)
   │   │   ├─ 新增用户 (/users/create)
   │   │   └─ 批量导入 (/users/import)
   │   ├─ 课程管理 (/courses)
   │   ├─ 开课管理 (/offerings)
   │   ├─ 排课管理 (/schedules)
   │   ├─ 校历管理 (/calendars)
   │   ├─ 培养方案 (/training-programs)
   │   ├─ 基础信息 (/base-info)
   │   ├─ 回收站 (/recycle-bin)
   │   └─ 审计日志 (/audit-logs)
   ├─ 顶部栏
   │   ├─ 当前用户信息
   │   └─ 个人中心 → 修改密码
   └─ 403 页 (/403)
```

## 3. 路由设计

### 3.1 路由表

```typescript
const routes = [
  { path: "/login", component: LoginPage, meta: { guest: true } },
  {
    path: "/",
    component: AdminLayout,
    meta: { requiresAuth: true },
    children: [
      { path: "users", component: UserListPage, meta: { permission: "user:read" } },
      { path: "users/create", component: UserCreatePage, meta: { permission: "user:create" } },
      { path: "users/:id", component: UserDetailPage, meta: { permission: "user:read" } },
      { path: "users/import", component: UserImportPage, meta: { permission: "user:create" } },
      { path: "courses", component: CourseListPage, meta: { permission: "course:read" } },
      { path: "offerings", component: OfferingListPage, meta: { permission: "offering:read" } },
      { path: "schedules", component: ScheduleListPage, meta: { permission: "schedule:read" } },
      { path: "calendars", component: CalendarListPage, meta: { permission: "calendar:read" } },
      { path: "training-programs", component: TrainingProgramPage, meta: { permission: "training:read" } },
      { path: "base-info", component: BaseInfoPage, meta: { permission: "base-info:read" } },
      { path: "recycle-bin", component: RecycleBinPage, meta: { permission: "recycle:read" } },
      { path: "audit-logs", component: AuditLogPage, meta: { permission: "audit:read" } },
      { path: "403", component: ForbiddenPage },
    ],
  },
];
```

### 3.2 路由守卫

```typescript
router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore();

  // 未登录 → 跳转登录页
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return next("/login");
  }

  // 已登录访问登录页 → 跳转首页
  if (to.meta.guest && authStore.isAuthenticated) {
    return next("/");
  }

  // 权限校验
  if (to.meta.permission && !authStore.hasPermission(to.meta.permission as string)) {
    return next("/403");
  }

  next();
});
```

## 4. 状态管理（Pinia）

### 4.1 useAuthStore

```typescript
interface AuthState {
  token: string | null;
  refreshToken: string | null;
  user: UserInfo | null;
  permissions: string[];
}

// Actions
- login(username, password)
- logout()
- refreshAccessToken()
- fetchCurrentUser()
- hasPermission(code: string): boolean
```

### 4.2 useUserStore

```typescript
interface UserState {
  list: User[];
  current: User | null;
  pagination: Pagination;
  filters: UserFilters;
}

// Actions
- fetchUsers(params)
- fetchUserDetail(id)
- createUser(data)
- updateUser(id, data)
- deleteUser(id)
- batchImport(file)
```

### 4.3 useCourseStore

```typescript
interface CourseState {
  list: Course[];
  current: Course | null;
  pagination: Pagination;
}

// Actions — 同理覆盖开课、排课、校历、培养方案等
```

## 5. Axios 拦截器

### 5.1 请求拦截

```typescript
axios.interceptors.request.use((config) => {
  const authStore = useAuthStore();
  if (authStore.token) {
    config.headers.Authorization = `Bearer ${authStore.token}`;
  }
  return config;
});
```

### 5.2 响应拦截（Token 自动续期）

```typescript
axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // 401 + 未重试过 → 尝试刷新 Token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const authStore = useAuthStore();
      try {
        await authStore.refreshAccessToken();
        originalRequest.headers.Authorization = `Bearer ${authStore.token}`;
        return axios(originalRequest);
      } catch {
        authStore.logout();
        router.push("/login");
        return Promise.reject(error);
      }
    }

    // 统一错误提示
    ElMessage.error(error.response?.data?.message || "请求失败");
    return Promise.reject(error);
  }
);
```

## 6. 按钮级权限控制

通过自定义指令 `v-permission` 控制按钮显隐：

```typescript
// directives/permission.ts
app.directive("permission", (el, binding) => {
  const authStore = useAuthStore();
  if (!authStore.hasPermission(binding.value)) {
    el.parentNode?.removeChild(el);
  }
});
```

```html
<!-- 使用示例 -->
<el-button v-permission="'user:create'" @click="openCreateDialog">
  新增用户
</el-button>
<el-button v-permission="'user:delete'" @click="handleDelete">
  删除
</el-button>
```

## 7. 通用组件

| 组件 | 用途 |
|------|------|
| `SearchBar` | 通用搜索栏（keyword + 额外过滤字段） |
| `DataTable` | 封装 Element Plus Table，统一分页、排序、选择 |
| `DetailDrawer` | 详情侧滑面板 |
| `FormDialog` | 新增/编辑弹出表单 |
| `StatusTag` | 状态标签（ACTIVE/DISABLED/DELETED） |
| `ConfirmButton` | 危险操作确认按钮（删除、物理删除等） |

## 8. 与后端 API 的对应

前端通过 Axios 实例统一访问后端 API（`/api/v1/`）：

| 前端操作 | API 调用 | 权限 |
|----------|----------|------|
| 登录 | `POST /auth/login` | 无 |
| 退出 | `POST /auth/logout` | 需认证 |
| 用户列表 | `GET /users` | `user:read` |
| 新增用户 | `POST /users` | `user:create` |
| 编辑用户 | `PUT/PATCH /users/{id}` | `user:update` |
| 删除用户 | `DELETE /users/{id}` | `user:delete` |
| 批量导入 | `POST /users/import` | `user:create` |
| 回收站列表 | `GET /recycle-bin` | `recycle:read` |
| 恢复用户 | `POST /recycle-bin/{id}/restore` | `recycle:restore` |
| 物理删除 | `DELETE /recycle-bin/{id}` | `recycle:delete` |
| 审计日志 | `GET /audit-logs` | `audit:read` |
