import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import ProductManagement from '../views/ProductManagement.vue'
import InventoryManagement from '../views/InventoryManagement.vue'
import Placeholder from '../views/Placeholder.vue'
import Login from '../views/Login.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: Login },
    { path: '/', component: Dashboard },
    { path: '/products', component: ProductManagement },
    { path: '/categories', component: Placeholder, props: { title: '商品分类' } },
    { path: '/brands', component: Placeholder, props: { title: '品牌管理' } },
    { path: '/suppliers', component: Placeholder, props: { title: '供应商管理' } },
    { path: '/inventory', component: InventoryManagement },
    { path: '/stock-warning', component: Placeholder, props: { title: '库存预警' } },
    { path: '/stock-in', component: Placeholder, props: { title: '入库管理' } },
    { path: '/stock-out', component: Placeholder, props: { title: '出库管理' } },
    { path: '/movements', component: Placeholder, props: { title: '库存流水' } },
    { path: '/users', component: Placeholder, props: { title: '用户管理' } },
    { path: '/roles', component: Placeholder, props: { title: '角色权限' } },
    { path: '/audit', component: Placeholder, props: { title: '操作日志' } },
    { path: '/settings', component: Placeholder, props: { title: '系统设置' } }
  ]
})
