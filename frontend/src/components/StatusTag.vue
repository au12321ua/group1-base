<template>
  <el-tag :type="tagType" size="small">
    {{ status }}
  </el-tag>
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
  status: string;
}>();

/** 根据状态值返回 Element Plus Tag 类型 */
const tagType = computed(() => {
  switch (props.status) {
    case "ACTIVE":
      return "success";
    case "DISABLED":
      return "warning";
    case "DELETED":
      return "danger";
    default:
      return "info";
  }
});
</script>
