<template>
  <el-card shadow="never">
    <template #header>{{ title }}</template>
    <el-empty description="模块骨架已预留，按开发顺序接入 API 和权限按钮。" />
  </el-card>
</template>

<script setup lang="ts">
defineProps<{ title: string }>()
</script>
