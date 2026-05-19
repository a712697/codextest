<template>
  <el-container class="app">
    <el-aside width="220px">
      <div class="brand">超市商品管理</div>
      <el-menu router default-active="/">
        <el-menu-item index="/login">登录页</el-menu-item>
        <el-menu-item index="/">首页仪表盘</el-menu-item>
        <el-menu-item index="/products">商品管理</el-menu-item>
        <el-menu-item index="/categories">商品分类</el-menu-item>
        <el-menu-item index="/brands">品牌管理</el-menu-item>
        <el-menu-item index="/suppliers">供应商管理</el-menu-item>
        <el-menu-item index="/inventory">库存管理</el-menu-item>
        <el-menu-item index="/stock-warning">库存预警</el-menu-item>
        <el-menu-item index="/stock-in">入库管理</el-menu-item>
        <el-menu-item index="/stock-out">出库管理</el-menu-item>
        <el-menu-item index="/movements">库存流水</el-menu-item>
        <el-menu-item index="/users">用户管理</el-menu-item>
        <el-menu-item index="/roles">角色权限</el-menu-item>
        <el-menu-item index="/audit">操作日志</el-menu-item>
        <el-menu-item index="/settings">系统设置</el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header>生产级后台管理系统</el-header>
      <el-main><router-view /></el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.app { min-height: 100vh; }
.brand { height: 56px; display: flex; align-items: center; padding: 0 18px; font-weight: 700; }
.el-header { display: flex; align-items: center; border-bottom: 1px solid #e5e7eb; }
</style>
