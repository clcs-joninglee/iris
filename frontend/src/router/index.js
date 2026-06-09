import { createRouter, createWebHistory } from 'vue-router'
import { isLoggedIn } from '../stores/auth'

//定義網址對應到哪個頁面 ex /login - LoginView
//requiresAuth: true 代表這個頁面需要登入才能看

const routes = [
  { path: '/', redirect: '/iris' },
  { path: '/login', component: () => import('../views/LoginView.vue') },
  { path: '/iris', component: () => import('../views/IrisView.vue'), meta: { requiresAuth: true } }, 
  { path: '/chart', component: () => import('../views/ChartView.vue'), meta: { requiresAuth: true } },
  { path: '/register', component: () => import('../views/RegisterView.vue') },
]


const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  if (to.meta.requiresAuth && !isLoggedIn()) {
    return '/login'
  }
})

export default router