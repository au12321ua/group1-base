<template>
  <el-container class="admin-container">
    <!-- 左侧导航 -->
    <el-aside width="220px" class="admin-aside">
      <div class="logo">STSS 管理系统</div>
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409eff"
      >
        <el-menu-item index="/users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        <el-menu-item index="/courses">
          <el-icon><Reading /></el-icon>
          <span>课程管理</span>
        </el-menu-item>
        <el-menu-item index="/offerings">
          <el-icon><Notebook /></el-icon>
          <span>开课管理</span>
        </el-menu-item>
        <el-menu-item index="/schedules">
          <el-icon><Timer /></el-icon>
          <span>排课管理</span>
        </el-menu-item>
        <el-menu-item index="/calendars">
          <el-icon><Calendar /></el-icon>
          <span>校历管理</span>
        </el-menu-item>
        <el-menu-item index="/training-programs">
          <el-icon><Document /></el-icon>
          <span>培养方案</span>
        </el-menu-item>
        <el-menu-item index="/base-info">
          <el-icon><InfoFilled /></el-icon>
          <span>基础信息</span>
        </el-menu-item>
        <el-menu-item index="/recycle-bin">
          <el-icon><Delete /></el-icon>
          <span>回收站</span>
        </el-menu-item>
        <el-menu-item index="/audit-logs">
          <el-icon><List /></el-icon>
          <span>审计日志</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 右侧区域 -->
    <el-container>
      <!-- 顶部栏 -->
      <el-header class="admin-header">
        <div class="header-right">
          <span class="username">{{ authStore.user?.username ?? "未登录" }}</span>
          <el-button text @click="router.push('/change-password')">修改密码</el-button>
          <el-button type="danger" text @click="handleLogout">退出</el-button>
        </div>
      </el-header>

      <!-- 内容区 -->
      <el-main class="admin-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
  User,
  Reading,
  Notebook,
  Timer,
  Calendar,
  Document,
  InfoFilled,
  Delete,
  List,
} from "@element-plus/icons-vue";
import { useAuthStore } from "@/stores/auth";

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

/** 当前激活菜单项 */
const activeMenu = computed(() => {
  const path = route.path;
  // 匹配二级路径
  if (path.startsWith("/users")) return "/users";
  return path;
});

/** 退出登录 */
async function handleLogout() {
  await authStore.logout();
}
</script>

<style scoped>
.admin-container {
  height: 100vh;
}

.admin-aside {
  background-color: #304156;
  overflow-y: auto;
}

.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  background-color: #263445;
}

.admin-header {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  background: #fff;
  border-bottom: 1px solid #e6e6e6;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.username {
  color: #606266;
}

.admin-main {
  background: #f0f2f5;
  min-height: calc(100vh - 60px);
}
</style>
