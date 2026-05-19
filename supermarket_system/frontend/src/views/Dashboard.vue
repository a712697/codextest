<template>
  <el-row :gutter="12">
    <el-col :span="6" v-for="item in cards" :key="item.label">
      <el-card shadow="never">
        <div class="metric">{{ item.value }}</div>
        <div class="label">{{ item.label }}</div>
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup lang="ts">
const cards = [
  { label: 'SKU 数', value: 0 },
  { label: '库存预警', value: 0 },
  { label: '今日入库', value: 0 },
  { label: '今日出库', value: 0 }
]
</script>

<style scoped>
.metric { font-size: 28px; font-weight: 700; }
.label { color: #667085; margin-top: 6px; }
</style>
