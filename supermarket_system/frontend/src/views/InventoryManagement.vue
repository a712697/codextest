<template>
  <el-card shadow="never">
    <template #header>库存管理</template>
    <el-form inline>
      <el-form-item label="关键词"><el-input placeholder="SKU / 商品名" /></el-form-item>
      <el-form-item><el-button>查询</el-button></el-form-item>
    </el-form>
    <el-table :data="[]" border>
      <el-table-column prop="sku" label="SKU" />
      <el-table-column prop="name" label="商品名" />
      <el-table-column prop="quantity" label="当前库存" />
      <el-table-column prop="lockedQuantity" label="锁定库存" />
      <el-table-column prop="minStock" label="库存下限" />
      <el-table-column prop="warning" label="预警" />
    </el-table>
  </el-card>
</template>

<script setup lang="ts"></script>
