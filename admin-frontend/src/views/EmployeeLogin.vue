<template>
  <div class="employee-login-container">
    <AppBar />
    
    <v-container fluid class="pa-0">
      <v-row no-gutters class="h-100">
        <v-col cols="12" class="d-flex align-center justify-center">
          <v-card class="login-card" elevation="0">
            <v-card-text class="pa-8 pa-4 pa-md-8">
              <div class="text-center mb-6">
                <v-icon size="64" color="primary" class="mb-4">mdi-account-tie</v-icon>
                <h2 class="text-h4 font-weight-bold text-white mb-2">Acceso Empleados</h2>
                <p class="text-grey-400">Ingresa tus credenciales para ver tus reportes</p>
              </div>
              
              <v-form @submit.prevent="handleLogin" class="login-form">
                <v-text-field
                  v-model="form.username"
                  label="USUARIO"
                  type="text"
                  placeholder="Ingresa tu usuario"
                  variant="outlined"
                  color="primary"
                  bg-color="dark-surface"
                  class="mb-4"
                  :rules="[rules.required]"
                  hide-details="auto"
                  density="compact"
                  density-md="default"
                >
                  <template v-slot:prepend-inner>
                    <v-icon color="primary">mdi-account</v-icon>
                  </template>
                </v-text-field>

                <v-text-field
                  v-model="form.password"
                  label="CONTRASEÑA"
                  :type="showPassword ? 'text' : 'password'"
                  placeholder="Ingresa tu contraseña"
                  variant="outlined"
                  color="primary"
                  bg-color="dark-surface"
                  class="mb-6"
                  :rules="[rules.required]"
                  hide-details="auto"
                  density="compact"
                  density-md="default"
                >
                  <template v-slot:prepend-inner>
                    <v-icon color="primary">mdi-lock</v-icon>
                  </template>
                  <template v-slot:append-inner>
                    <v-btn
                      variant="text"
                      icon
                      @click="togglePassword"
                      color="grey-lighten-1"
                      size="small"
                      size-md="default"
                    >
                      <v-icon>{{ showPassword ? 'mdi-eye-off' : 'mdi-eye' }}</v-icon>
                    </v-btn>
                  </template>
                </v-text-field>

                <v-btn
                  type="submit"
                  color="primary"
                  size="large"
                  block
                  :loading="loading"
                  :disabled="loading"
                  class="mb-4 login-btn"
                  elevation="2"
                >
                  <v-icon left class="mr-2">mdi-login</v-icon>
                  <span v-if="loading">Iniciando sesión...</span>
                  <span v-else>INICIAR SESIÓN</span>
                </v-btn>
              </v-form>

              <!-- Enlaces adicionales -->
              <div class="text-center">
                <v-btn
                  variant="text"
                  color="primary"
                  size="small"
                  class="forgot-password-link"
                  @click="goToForgotPassword"
                >
                  <v-icon left size="16" class="mr-1">mdi-help-circle</v-icon>
                  ¿Olvidaste la contraseña?
                </v-btn>
              </div>

              <v-divider class="my-6 bg-grey-700"></v-divider>

                             <!-- Volver al reconocimiento -->
               <div class="text-center">
                 <v-btn
                   variant="outlined"
                   color="grey-lighten-1"
                   size="small"
                   @click="goToRecognition"
                   class="mr-2"
                 >
                   <v-icon left size="16" class="mr-1">mdi-arrow-left</v-icon>
                   Volver al Reconocimiento
                 </v-btn>
                 
                 <!-- Botón de cerrar sesión si ya está autenticado -->
                 <v-btn
                   v-if="authStore.isAuthenticated"
                   variant="outlined"
                   color="error"
                   size="small"
                   @click="handleLogout"
                 >
                   <v-icon left size="16" class="mr-1">mdi-logout</v-icon>
                   Cerrar Sesión
                 </v-btn>
               </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import AppBar from '../components/AppBar.vue'
import { attendanceService } from '../services/attendanceService'
import { useNotifications } from '../composables/useNotifications'
import { useAuthStore } from '../stores/auth'

export default {
  name: 'EmployeeLogin',
  components: {
    AppBar
  },
  setup() {
    const router = useRouter()
    const { showSuccess, showError } = useNotifications()
    const authStore = useAuthStore()
    
    // Variables del formulario
    const form = reactive({
      username: '',
      password: ''
    })
    
    // Variables de estado
    const showPassword = ref(false)
    const loading = ref(false)
    
    // Reglas de validación
    const rules = {
      required: v => !!v || 'Este campo es requerido'
    }

    // Función para alternar visibilidad de contraseña
    const togglePassword = () => {
      showPassword.value = !showPassword.value
    }

    // Función principal de login
    const handleLogin = async () => {
      loading.value = true

      try {
        // Validar campos
        if (!form.username || !form.password) {
          showError('Por favor completa todos los campos', {
            title: 'Campos Requeridos',
            icon: 'mdi-form-textbox'
          })
          return
        }

        // Intentar login del empleado
        const employeeData = await attendanceService.getEmployeeByCredentials(
          form.username, 
          form.password
        )

        if (employeeData) {
          console.log('✅ Login exitoso del empleado:', employeeData)
          
          // Actualizar el store de autenticación
          authStore.setEmployeeAuth(employeeData.user, employeeData.employee_id)
          console.log('✅ Store de autenticación actualizado para empleado')
          
          // Mostrar mensaje de éxito
          showSuccess('Sesión iniciada correctamente', {
            title: 'Bienvenido',
            icon: 'mdi-check-circle'
          })

          // Redirigir a los reportes del empleado
          setTimeout(() => {
            router.push('/employee/reports')
          }, 1500)
        }
        
      } catch (err) {
        console.error('Error en login del empleado:', err)
        
        // Manejar errores específicos
        if (err.response && err.response.status === 400) {
          showError('Credenciales inválidas. Verifica tu usuario y contraseña.', {
            title: 'Error de Autenticación',
            icon: 'mdi-account-lock'
          })
        } else if (err.message) {
          showError(err.message, {
            title: 'Error del Sistema',
            icon: 'mdi-alert-circle'
          })
        } else {
          showError('Error inesperado al iniciar sesión', {
            title: 'Error Desconocido',
            icon: 'mdi-help-circle'
          })
        }
      } finally {
        loading.value = false
      }
    }

    // Función para ir a recuperar contraseña
    const goToForgotPassword = () => {
      router.push('/employee/forgot-password')
    }

    // Función para volver al reconocimiento
    const goToRecognition = () => {
      router.push('/')
    }
    
    // Función para cerrar sesión
    const handleLogout = () => {
      // Limpiar autenticación
      authStore.logout()
      
      // Redirigir al reconocimiento
      router.push('/')
    }

    return {
      form,
      showPassword,
      loading,
      rules,
      togglePassword,
      handleLogin,
      goToForgotPassword,
      goToRecognition,
      handleLogout,
      authStore
    }
  }
}
</script>

<style scoped>
.employee-login-container {
  min-height: 100vh;
  background: #16213e;
  margin: 0 !important;
  padding: 0 !important;
  border: none !important;
  outline: none !important;
  position: relative;
  margin-top: 70px !important;
  overflow: hidden;
}

.login-card {
  background: rgba(30, 41, 59, 0.8) !important;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 16px;
  max-width: 500px;
  width: 100%;
  margin-top: 10px;
  transition: all 0.3s ease;
}

.login-btn {
  background: linear-gradient(135deg, #3b82f6 0%, #00d4ff 100%) !important;
  font-weight: bold;
  letter-spacing: 1px;
  box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
  transition: all 0.3s ease;
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
}

.forgot-password-link {
  font-size: 0.875rem !important;
  text-decoration: none !important;
  transition: all 0.3s ease !important;
}

.forgot-password-link:hover {
  color: #00d4ff !important;
  transform: translateY(-1px) !important;
}

/* Personalización de Vuetify para modo oscuro */
:deep(.v-field) {
  background-color: rgba(30, 41, 59, 0.8) !important;
  border-color: rgba(59, 130, 246, 0.3) !important;
}

:deep(.v-field--focused) {
  border-color: #00d4ff !important;
  box-shadow: 0 0 0 2px rgba(0, 212, 255, 0.2) !important;
}

:deep(.v-field__input) {
  color: #ffffff !important;
}

:deep(.v-field__label) {
  color: #cbd5e1 !important;
}

/* Responsive */
@media (max-width: 768px) {
  .login-card {
    max-width: 95%;
    margin: 1rem 2.5%;
  }
  
  .login-card .v-card-text {
    padding: 1.5rem !important;
  }
}

@media (max-width: 600px) {
  .login-card {
    max-width: 98%;
    margin: 0.5rem 1%;
  }
  
  .login-card .v-card-text {
    padding: 1rem !important;
  }
  
  .text-h4 {
    font-size: 1.5rem !important;
  }
}
</style>
