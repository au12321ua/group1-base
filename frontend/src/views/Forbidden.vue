<template>
  <div class="forbidden-page">
    <h1>403 - 无访问权限</h1>
    <p>抱歉，您没有访问此页面的权限。</p>
    <el-button type="primary" @click="$router.push('/')">返回首页</el-button>
  </div>
</template>

<script setup lang="ts">
// 403 禁止访问页面
</script>

<style scoped>
.forbidden-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #606266;
}

.forbidden-page h1 {
  font-size: 48px;
  color: #e6a23c;
  margin-bottom: 16px;
}
</style>
