import { createRouter, createWebHistory, type RouteRecordRaw } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { PERM } from "@/constants/permissions";

/** 占位页面工厂 —— 各管理页面仅为占位，仅显示标题 */
const LoginPage = () => import("@/views/Login.vue");
const ForbiddenPage = () => import("@/views/Forbidden.vue");
const AdminLayout = () => import("@/layouts/AdminLayout.vue");
const ChangePasswordPage = () => import("@/views/ChangePassword.vue");

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
      { path: "change-password", name: "ChangePassword", component: ChangePasswordPage, meta: { requiresAuth: true } },
      { path: "users", name: "UserList", component: UserListPage, meta: { permission: PERM.USER_READ } },
      { path: "users/create", name: "UserCreate", component: UserCreatePage, meta: { permission: PERM.USER_CREATE } },
      { path: "users/:id", name: "UserDetail", component: UserDetailPage, meta: { permission: PERM.USER_READ } },
      { path: "users/import", name: "UserImport", component: UserImportPage, meta: { permission: PERM.USER_CREATE } },
      { path: "courses", name: "CourseList", component: CourseListPage, meta: { permission: PERM.COURSE_READ } },
      { path: "offerings", name: "OfferingList", component: OfferingListPage, meta: { permission: PERM.OFFERING_READ } },
      { path: "schedules", name: "ScheduleList", component: ScheduleListPage, meta: { permission: PERM.SCHEDULE_READ } },
      { path: "calendars", name: "CalendarList", component: CalendarListPage, meta: { permission: PERM.CALENDAR_READ } },
      { path: "training-programs", name: "TrainingProgram", component: TrainingProgramPage, meta: { permission: PERM.TRAINING_READ } },
      { path: "base-info", name: "BaseInfo", component: BaseInfoPage, meta: { permission: PERM.BASE_INFO_READ } },
      { path: "recycle-bin", name: "RecycleBin", component: RecycleBinPage, meta: { permission: PERM.RECYCLE_READ } },
      { path: "audit-logs", name: "AuditLog", component: AuditLogPage, meta: { permission: PERM.AUDIT_READ } },
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

  // 权限校验 —— 仅当权限数据已加载时才校验（空列表时放行，后端 API 层负责最终鉴权）
  if (to.meta.permission && authStore.permissions.length > 0 && !authStore.hasPermission(to.meta.permission)) {
    return next("/403");
  }

  next();
});

export default router;
