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
    console.log('🚫 Acceso denegado: Ruta requiere autenticación')
    next('/login')
    return
  }
  
  // Ruta requiere ser invitado (no autenticado)
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    console.log('🚫 Usuario autenticado intentando acceder a ruta de invitado')
    next('/app/dashboard')
    return
  }
  
  // Prevenir acceso a rutas públicas cuando está autenticado
  if (to.meta.requiresAuth === false && authStore.isAuthenticated && to.path === '/') {
    console.log('🚫 Usuario autenticado redirigido al dashboard')
    next('/app/dashboard')
    return
  }
  
  next()
})

export default router
