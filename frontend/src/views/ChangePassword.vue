<template>
  <div class="change-password-page">
    <el-card class="password-card">
      <template #header>
        <h3>修改密码</h3>
      </template>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px" @submit.prevent="handleSubmit">
        <el-form-item label="旧密码" prop="oldPassword">
          <el-input v-model="form.oldPassword" type="password" placeholder="请输入旧密码" show-password />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input v-model="form.newPassword" type="password" placeholder="请输入新密码（至少 8 位）" show-password />
        </el-form-item>
        <el-form-item label="确认新密码" prop="confirmPassword">
          <el-input v-model="form.confirmPassword" type="password" placeholder="请再次输入新密码" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" native-type="submit" :loading="loading">确认修改</el-button>
          <el-button @click="router.push('/')">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, type FormInstance, type FormRules } from "element-plus";
import apiClient from "@/api/client";

interface PasswordForm {
  oldPassword: string;
  newPassword: string;
  confirmPassword: string;
}

const form = reactive<PasswordForm>({ oldPassword: "", newPassword: "", confirmPassword: "" });
const formRef = ref<FormInstance>();
const loading = ref(false);
const router = useRouter();

const validateConfirm = (_rule: unknown, value: string, callback: (err?: Error) => void) => {
  if (value !== form.newPassword) {
    callback(new Error("两次输入的新密码不一致"));
  } else {
    callback();
  }
};

const rules: FormRules<PasswordForm> = {
  oldPassword: [{ required: true, message: "请输入旧密码", trigger: "blur" }],
  newPassword: [
    { required: true, message: "请输入新密码", trigger: "blur" },
    { min: 8, message: "新密码长度至少 8 位", trigger: "blur" },
  ],
  confirmPassword: [
    { required: true, message: "请确认新密码", trigger: "blur" },
    { validator: validateConfirm, trigger: "blur" },
  ],
};

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false);
  if (!valid) return;

  loading.value = true;
  try {
    await apiClient.post("/auth/change-password", {
      old_password: form.oldPassword,
      new_password: form.newPassword,
    });
    ElMessage.success("密码修改成功，请重新登录");
    const { useAuthStore } = await import("@/stores/auth");
    useAuthStore().logout();
  } catch {
    // 错误提示由 apiClient 拦截器统一处理
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.change-password-page {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 60px;
}

.password-card {
  width: 500px;
}
</style>
