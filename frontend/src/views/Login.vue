<template>
  <div class="login-page">
    <el-card class="login-card">
      <template #header>
        <h2 class="login-title">STSS 信息管理系统</h2>
      </template>
      <el-form @submit.prevent="handleLogin">
        <el-form-item label="用户名">
          <el-input v-model="username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" native-type="submit" class="login-btn" :loading="loading">
            登录
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { useAuthStore } from "@/stores/auth";

const username = ref("");
const password = ref("");
const loading = ref(false);
const authStore = useAuthStore();
const router = useRouter();

async function handleLogin() {
  loading.value = true;
  try {
    await authStore.login(username.value, password.value);
    router.push("/");
  } catch (e: unknown) {
    const msg = (e as { response?: { data?: { message?: string } } })?.response?.data?.message;
    ElMessage.error(msg ?? "登录失败，请重试");
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.login-page {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background: #f0f2f5;
}

.login-card {
  width: 400px;
}

.login-title {
  text-align: center;
  margin: 0;
}

.login-btn {
  width: 100%;
}
</style>
