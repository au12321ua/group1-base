import type { Directive } from "vue";
import { useAuthStore } from "@/stores/auth";

/** v-permission 指令 —— 无权限时移除元素 */
export const vPermission: Directive<HTMLElement, string> = {
  mounted(el: HTMLElement, binding) {
    const authStore = useAuthStore();
    if (!authStore.hasPermission(binding.value)) {
      el.parentNode?.removeChild(el);
    }
  },
};
