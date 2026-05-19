import { defineStore } from "pinia";
import { ref, computed } from "vue";
import router from "@/router";
import axios from "axios";

/** 用户简要信息 */
interface UserInfo {
  userId: string;
  username: string;
  role: string;
}

export const useAuthStore = defineStore("auth", () => {
  const token = ref<string | null>(localStorage.getItem("token"));
  const refreshToken = ref<string | null>(localStorage.getItem("refreshToken"));
  const user = ref<UserInfo | null>(null);
  const permissions = ref<string[]>(
    JSON.parse(localStorage.getItem("permissions") ?? "[]")
  );

  /** 是否已认证 */
  const isAuthenticated = computed(() => token.value !== null);

  /** 检查是否拥有指定权限 */
  function hasPermission(code: string): boolean {
    return permissions.value.includes(code);
  }

  /** 登录 */
  async function login(username: string, password: string): Promise<void> {
    const res = await axios.post("/auth/login", { username, password });
    const data = res.data?.data ?? res.data;
    token.value = data.access_token ?? data.token;
    refreshToken.value = data.refresh_token ?? data.refreshToken;
    user.value = data.user ?? null;
    permissions.value = data.permissions ?? [];

    if (token.value) localStorage.setItem("token", token.value);
    if (refreshToken.value) localStorage.setItem("refreshToken", refreshToken.value);
    if (permissions.value.length) localStorage.setItem("permissions", JSON.stringify(permissions.value));
  }

  /** 退出登录 */
  async function logout(): Promise<void> {
    try {
      await axios.post("/auth/logout");
    } catch {
      // 即使接口失败也清除本地状态
    }
    token.value = null;
    refreshToken.value = null;
    user.value = null;
    permissions.value = [];
    localStorage.removeItem("token");
    localStorage.removeItem("refreshToken");
    localStorage.removeItem("permissions");

    router.push("/login");
  }

  /** 刷新 Access Token */
  async function refreshAccessToken(): Promise<void> {
    if (!refreshToken.value) throw new Error("无 refresh token");
    const res = await axios.post("/auth/refresh", {
      refresh_token: refreshToken.value,
    });
    const data = res.data?.data ?? res.data;
    token.value = data.access_token ?? data.token;
    if (token.value) localStorage.setItem("token", token.value);
  }

  /** 获取当前用户信息（占位） */
  async function fetchCurrentUser(): Promise<void> {
    // TODO: GET /auth/me 获取当前用户
  }

  return {
    token,
    refreshToken,
    user,
    permissions,
    isAuthenticated,
    hasPermission,
    login,
    logout,
    refreshAccessToken,
    fetchCurrentUser,
  };
});
