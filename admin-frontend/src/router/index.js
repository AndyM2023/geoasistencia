import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
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
    path: '/register',
    name: 'Register',
    component: Register,
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
        name: 'AppHome',
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
  },
  // Ruta catch-all para redirigir cualquier ruta del backend al dashboard
  {
    path: '/:pathMatch(.*)*',
    redirect: '/app/dashboard'
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// Navigation guard
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Inicializar autenticación solo una vez
  if (!authStore.isInitialized && !authStore.isLoading) {
    await authStore.initAuth()
  }
  
  // Esperar a que termine la inicialización
  if (authStore.isLoading) {
    // Crear promise para esperar la inicialización
    const waitForInit = async () => {
      let attempts = 0
      while (authStore.isLoading && attempts < 50) { // Max 5 segundos
        await new Promise(resolve => setTimeout(resolve, 100))
        attempts++
      }
      next()
    }
    waitForInit()
    return
  }
  
  // Ruta requiere autenticación
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
    return
  }
  
  // Ruta requiere ser invitado (no autenticado)
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next('/app/dashboard')
    return
  }
  
  // Prevenir acceso a rutas públicas cuando está autenticado
  if (to.meta.requiresAuth === false && authStore.isAuthenticated && to.path === '/') {
    next('/app/dashboard')
    return
  }
  
  // Manejar rutas no encontradas o acceso directo a URLs
  if (to.matched.length === 0) {
    if (authStore.isAuthenticated) {
      next('/app/dashboard')
    } else {
      next('/login')
    }
    return
  }
  
  next()
})

export default router
