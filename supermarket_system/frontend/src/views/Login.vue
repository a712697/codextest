<template>
  <el-card class="login" shadow="never">
    <template #header>系统登录</template>
    <el-form label-position="top">
      <el-form-item label="用户名"><el-input /></el-form-item>
      <el-form-item label="密码"><el-input type="password" show-password /></el-form-item>
      <el-button type="primary" style="width: 100%">登录</el-button>
    </el-form>
  </el-card>
</template>

<script setup lang="ts"></script>

<style scoped>
.login { max-width: 420px; margin: 80px auto; }
</style>
