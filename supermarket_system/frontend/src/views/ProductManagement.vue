<template>
  <el-card shadow="never">
    <template #header>
      <div class="header">
        <span>商品管理</span>
        <el-button type="primary">新增商品</el-button>
      </div>
    </template>
    <el-form inline>
      <el-form-item label="关键词"><el-input placeholder="SKU / 条码 / 商品名" /></el-form-item>
      <el-form-item><el-button>查询</el-button><el-button>导入 Excel</el-button><el-button>导出 Excel</el-button></el-form-item>
    </el-form>
    <el-table :data="[]" border>
      <el-table-column prop="sku" label="SKU" />
      <el-table-column prop="barcode" label="条码" />
      <el-table-column prop="name" label="商品名" />
      <el-table-column prop="price" label="价格" />
      <el-table-column prop="status" label="状态" />
      <el-table-column label="操作" width="180" />
    </el-table>
  </el-card>
</template>

<script setup lang="ts"></script>

<style scoped>
.header { display: flex; justify-content: space-between; align-items: center; }
</style>
