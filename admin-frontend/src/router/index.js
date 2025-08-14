import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import Login from '../views/Login.vue'
import Recognition from '../views/Recognition.vue'
import Layout from '../views/Layout.vue'
import Dashboard from '../views/Dashboard.vue'
import Employees from '../views/Employees.vue'
import Areas from '../views/Areas.vue'
import Reports from '../views/Reports.vue'
import About from '../views/About.vue'

const routes = [
  {
    path: '/',
    name: 'Recognition',
    component: Recognition,
    meta: { requiresAuth: false }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresGuest: true }
  },
  {
    path: '/app',
    name: 'App',
    component: Layout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/app/dashboard'
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: Dashboard
      },
      {
        path: 'employees',
        name: 'Employees',
        component: Employees
      },
      {
        path: 'areas',
        name: 'Areas',
        component: Areas
      },
      {
        path: 'reports',
        name: 'Reports',
        component: Reports
      }
    ]
  },
  {
    path: '/about',
    name: 'About',
    component: About,
    meta: { requiresAuth: false }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // Inicializar autenticación si no se ha hecho
  if (!authStore.isAuthenticated) {
    authStore.initAuth()
  }
  
  // Ruta requiere autenticación
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
    return
  }
  
  // Ruta requiere ser invitado (no autenticado)
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next('/')
    return
  }
  
  next()
})

export default router
