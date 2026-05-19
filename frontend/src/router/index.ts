import { createRouter, createWebHistory, type RouteRecordRaw } from "vue-router";
import { useAuthStore } from "@/stores/auth";

/** 占位页面工厂 —— 各管理页面仅为占位，仅显示标题 */
const LoginPage = () => import("@/views/Login.vue");
const ForbiddenPage = () => import("@/views/Forbidden.vue");
const AdminLayout = () => import("@/layouts/AdminLayout.vue");

const UserListPage = () => import("@/views/users/UserList.vue");
const UserCreatePage = () => import("@/views/users/UserCreate.vue");
const UserDetailPage = () => import("@/views/users/UserDetail.vue");
const UserImportPage = () => import("@/views/users/UserImport.vue");
const CourseListPage = () => import("@/views/courses/CourseList.vue");
const OfferingListPage = () => import("@/views/offerings/OfferingList.vue");
const ScheduleListPage = () => import("@/views/schedules/ScheduleList.vue");
const CalendarListPage = () => import("@/views/calendars/CalendarList.vue");
const TrainingProgramPage = () => import("@/views/training/TrainingProgramList.vue");
const BaseInfoPage = () => import("@/views/base-info/BaseInfoList.vue");
const RecycleBinPage = () => import("@/views/recycle-bin/RecycleBinList.vue");
const AuditLogPage = () => import("@/views/audit-logs/AuditLogList.vue");

/** 路由表 —— 与设计文档 3.1 节一致 */
const routes: RouteRecordRaw[] = [
  {
    path: "/login",
    name: "Login",
    component: LoginPage,
    meta: { guest: true },
  },
  {
    path: "/",
    name: "Admin",
    component: AdminLayout,
    meta: { requiresAuth: true },
    children: [
      { path: "users", name: "UserList", component: UserListPage, meta: { permission: "user:read" } },
      { path: "users/create", name: "UserCreate", component: UserCreatePage, meta: { permission: "user:create" } },
      { path: "users/:id", name: "UserDetail", component: UserDetailPage, meta: { permission: "user:read" } },
      { path: "users/import", name: "UserImport", component: UserImportPage, meta: { permission: "user:create" } },
      { path: "courses", name: "CourseList", component: CourseListPage, meta: { permission: "course:read" } },
      { path: "offerings", name: "OfferingList", component: OfferingListPage, meta: { permission: "offering:read" } },
      { path: "schedules", name: "ScheduleList", component: ScheduleListPage, meta: { permission: "schedule:read" } },
      { path: "calendars", name: "CalendarList", component: CalendarListPage, meta: { permission: "calendar:read" } },
      { path: "training-programs", name: "TrainingProgram", component: TrainingProgramPage, meta: { permission: "training:read" } },
      { path: "base-info", name: "BaseInfo", component: BaseInfoPage, meta: { permission: "base-info:read" } },
      { path: "recycle-bin", name: "RecycleBin", component: RecycleBinPage, meta: { permission: "recycle:read" } },
      { path: "audit-logs", name: "AuditLog", component: AuditLogPage, meta: { permission: "audit:read" } },
      { path: "403", name: "Forbidden", component: ForbiddenPage },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

/** 全局导航守卫 —— 认证与权限校验 */
router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore();

  // 未登录访问需认证页面 → 跳转登录
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return next("/login");
  }

  // 已登录访问访客页面 → 跳转首页
  if (to.meta.guest && authStore.isAuthenticated) {
    return next("/");
  }

  // 权限校验
  if (to.meta.permission && !authStore.hasPermission(to.meta.permission as string)) {
    return next("/403");
  }

  next();
});

export default router;
