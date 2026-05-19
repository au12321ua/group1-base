import axios from "axios";
import { ElMessage } from "element-plus";
import { useAuthStore } from "@/stores/auth";
import router from "@/router";

/** 统一 Axios 实例 */
const apiClient = axios.create({
  baseURL: "/",
  timeout: 15000,
  headers: { "Content-Type": "application/json" },
});

/** 请求拦截器 —— 附加 Bearer Token */
apiClient.interceptors.request.use((config) => {
  const authStore = useAuthStore();
  if (authStore.token) {
    config.headers.Authorization = `Bearer ${authStore.token}`;
  }
  return config;
});

/** 响应拦截器 —— Token 自动续期 + 统一错误提示 */
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // 401 且未重试过 → 尝试刷新 Token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const authStore = useAuthStore();
      try {
        await authStore.refreshAccessToken();
        originalRequest.headers.Authorization = `Bearer ${authStore.token}`;
        return apiClient(originalRequest);
      } catch {
        authStore.logout();
        router.push("/login");
        return Promise.reject(error);
      }
    }

    // 统一错误提示
    const message =
      error.response?.data?.message ??
      error.response?.data?.detail ??
      "请求失败";
    ElMessage.error(message);
    return Promise.reject(error);
  }
);

export default apiClient;
