import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('../views/ForgotPassword.vue')
  },
  {
    path: '/reset-password',
    name: 'ResetPassword',
    component: () => import('../views/ResetPassword.vue')
  },
  {
    path: '/register',
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
      },
      {
        path: 'recognition',
        name: 'Recognition',
        component: () => import('../views/Recognition.vue')
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
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // Si la ruta requiere autenticación
  if (to.meta.requiresAuth) {
    // Verificar si el usuario está autenticado
    if (!authStore.isAuthenticated) {
      // Redirigir al login si no está autenticado
      next('/login')
      return
    }
  }
  
  // Si la ruta es login o register y el usuario está autenticado
  if ((to.name === 'Login' || to.name === 'Register' || to.name === 'ForgotPassword' || to.name === 'ResetPassword') && authStore.isAuthenticated) {
    // Redirigir al dashboard si ya está autenticado
    next('/app/dashboard')
    return
  }
  
  // Continuar con la navegación
  next()
})

export default router
