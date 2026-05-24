<template>
  <div class="login-page">
    <el-card class="login-card">
      <template #header>
        <h2 class="login-title">STSS 信息管理系统</h2>
      </template>
      <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleLogin">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
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
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, type FormInstance, type FormRules } from "element-plus";
import { useAuthStore } from "@/stores/auth";

interface LoginForm {
  username: string;
  password: string;
}

const form = reactive<LoginForm>({ username: "", password: "" });
const formRef = ref<FormInstance>();
const loading = ref(false);
const authStore = useAuthStore();
const router = useRouter();

/** 表单验证规则 */
const rules: FormRules<LoginForm> = {
  username: [{ required: true, message: "请输入用户名", trigger: "blur" }],
  password: [{ required: true, message: "请输入密码", trigger: "blur" }],
};

/** 将后端错误码映射为中文提示 */
function getErrorMessage(code: number): string {
  switch (code) {
    case 1001:
      return "用户名或密码错误";
    case 1002:
      return "账户已被禁用，请联系管理员";
    case 1003:
      return "账户已被锁定，请稍后再试";
    default:
      return "登录失败，请重试";
  }
}

async function handleLogin() {
  const valid = await formRef.value?.validate().catch(() => false);
  if (!valid) return;

  loading.value = true;
  try {
    await authStore.login(form.username, form.password);
    router.push("/");
  } catch (e: unknown) {
    const err = e as { response?: { data?: { code?: number; message?: string } } };
    const code = err?.response?.data?.code ?? 0;
    ElMessage.error(getErrorMessage(code));
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
