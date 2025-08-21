import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useNotifications } from '../composables/useNotifications'

const routes = [
  {
    path: '/',
    name: 'Recognition',
    component: () => import('../views/Recognition.vue')
  },
  {
    path: '/recognition',
    redirect: '/'
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
    path: '/employee/login',
    name: 'EmployeeLogin',
    component: () => import('../views/EmployeeLogin.vue')
  },
  {
    path: '/employee/forgot-password',
    name: 'EmployeeForgotPassword',
    component: () => import('../views/EmployeeForgotPassword.vue')
  },
  {
    path: '/employee/reset-password',
    name: 'EmployeeResetPassword',
    component: () => import('../views/EmployeeResetPassword.vue')
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
  },
  {
    path: '/employee/reports',
    name: 'EmployeeReports',
    component: () => import('../views/EmployeeReports.vue'),
    meta: { requiresAuth: true, requiresAdmin: false }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Guardia de navegación para verificar autenticación
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  const { showError } = useNotifications()
  
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
      console.log(`   - Token presente: ${!!authStore.token}`)
      console.log(`   - Store inicializado: ${authStore.isInitialized}`)
      
      // Verificar si el usuario está autenticado
      if (!authStore.isAuthenticated) {
        console.log('❌ Router - Usuario no autenticado, redirigiendo a login')
        
        // Redirigir según el tipo de ruta
        if (to.path.startsWith('/employee/')) {
          // Para rutas de empleados, ir al login de empleados
          console.log('🔄 Router - Redirigiendo empleado a login de empleados')
          next('/employee/login')
        } else {
          // Para otras rutas protegidas, ir al login de admin
          console.log('🔄 Router - Redirigiendo a login de admin')
          next('/admin/login')
        }
        return
      } else {
        console.log('✅ Router - Usuario autenticado, permitiendo acceso')
        console.log(`   - Rol del usuario: ${authStore.user?.role || 'No especificado'}`)
        
        // 🔒 BLOQUEAR ACCESO ADMINISTRATIVO A EMPLEADOS
        if (to.path.startsWith('/app/') && authStore.user?.role === 'employee') {
          console.log('🚫 Router - Empleado intentando acceder a ruta administrativa, bloqueando')
          showError('No tienes permisos para acceder al panel administrativo', {
            title: 'Acceso Denegado',
            icon: 'mdi-shield-lock'
          })
          next('/employee/reports') // Redirigir a sus reportes
          return
        }
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
