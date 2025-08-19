import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/',
    name: 'Recognition',
    component: () => import('../views/Recognition.vue')
  },
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/admin/forgot-password',
    name: 'ForgotPassword',
    component: () => import('../views/ForgotPassword.vue')
  },
  {
    path: '/reset-password',
    name: 'ResetPassword',
    component: () => import('../views/ResetPassword.vue')
  },
  {
    path: '/admin/register',
    name: 'Register',
    component: () => import('../views/Register.vue')
  },
  {
    path: '/app',
    component: () => import('../views/Layout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/app/dashboard'
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue')
      },
      {
        path: 'employees',
        name: 'Employees',
        component: () => import('../views/Employees.vue')
      },
      {
        path: 'areas',
        name: 'Areas',
        component: () => import('../views/Areas.vue')
      },
      {
        path: 'reports',
        name: 'Reports',
        component: () => import('../views/Reports.vue')
      }
    ]
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('../views/About.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Guardia de navegación para verificar autenticación
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // 🔄 ESPERAR A QUE SE INICIALICE LA AUTENTICACIÓN
  if (!authStore.isInitialized) {
    console.log('🔄 Router - Esperando inicialización de autenticación...')
    try {
      await authStore.initAuth()
      console.log('✅ Router - Autenticación inicializada')
    } catch (error) {
      console.error('❌ Router - Error inicializando autenticación:', error)
    }
  }
  
  // Si la ruta requiere autenticación
  if (to.meta.requiresAuth) {
    console.log('🔒 Router - Ruta protegida, verificando autenticación...')
    console.log(`   - Usuario autenticado: ${authStore.isAuthenticated}`)
    console.log(`   - Usuario: ${authStore.user ? authStore.user.username : 'No hay usuario'}`)
    
    // Verificar si el usuario está autenticado
    if (!authStore.isAuthenticated) {
      console.log('❌ Router - Usuario no autenticado, redirigiendo a login')
      // Redirigir al login admin si no está autenticado
      next('/admin/login')
      return
    } else {
      console.log('✅ Router - Usuario autenticado, permitiendo acceso')
    }
  }
  
  // Si la ruta es login o register y el usuario está autenticado
  if ((to.name === 'AdminLogin' || to.name === 'Register' || to.name === 'ForgotPassword' || to.name === 'ResetPassword') && authStore.isAuthenticated) {
    console.log('🔄 Router - Usuario ya autenticado, redirigiendo a dashboard')
    // Redirigir al dashboard si ya está autenticado
    next('/app/dashboard')
    return
  }
  
  // Continuar con la navegación
  console.log('✅ Router - Navegación permitida')
  next()
})

export default router
