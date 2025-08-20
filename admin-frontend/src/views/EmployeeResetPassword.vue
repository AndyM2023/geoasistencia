<template>
  <AppBar />
  <v-container fluid class="employee-reset-password-container pa-0">
    <v-row no-gutters class="h-100">
      <!-- Panel izquierdo con gradiente azul oscuro -->
      <v-col cols="12" md="4" class="left-panel d-flex align-center justify-center">
        <div class="text-center">
          <h1 class="logo-text text-h3 font-weight-bold text-white">
            GEOASISTENCIA
            <br>
            EMPLEADOS
          </h1>
          <div class="logo-glow"></div>
        </div>
      </v-col>

      <!-- Panel derecho con formulario -->
      <v-col cols="12" md="8" class="right-panel d-flex align-center justify-center">
        <v-card class="employee-reset-password-card" elevation="0">
          <v-card-text class="pa-8">
            <div class="text-center mb-6">
              <v-icon size="64" color="primary" class="mb-4">mdi-lock-reset</v-icon>
              <h2 class="text-h4 font-weight-bold text-white mb-2">Cambiar Contraseña</h2>
              <p class="text-body-1 text-grey-lighten-1">
                Ingresa tu nueva contraseña para completar la recuperación.
              </p>
            </div>

            <!-- Verificación del token -->
            <div v-if="!tokenValid" class="text-center mb-6">
              <v-progress-circular
                v-if="checkingToken"
                indeterminate
                color="primary"
                size="64"
              ></v-progress-circular>
              <div v-else-if="tokenError" class="text-center">
                <v-icon size="64" color="error" class="mb-4">mdi-alert-circle</v-icon>
                <h3 class="text-h5 text-white mb-2">Token Inválido</h3>
                <p class="text-body-1 text-grey-lighten-1 mb-4">
                  {{ tokenError }}
                </p>
                <v-btn
                  color="primary"
                  @click="goToForgotPassword"
                  class="mb-4"
                >
                  Solicitar Nuevo Enlace
                </v-btn>
              </div>
            </div>

            <!-- Formulario de cambio de contraseña -->
            <div v-else>
              <v-form ref="formRef" @submit.prevent="handleSubmit" class="employee-reset-password-form">
                <v-text-field
                  v-model="form.newPassword"
                  label="NUEVA CONTRASEÑA"
                  :type="showNewPassword ? 'text' : 'password'"
                  placeholder="Ingresa tu nueva contraseña"
                  variant="outlined"
                  color="primary"
                  bg-color="dark-surface"
                  class="mb-4"
                  :rules="[rules.required, rules.minLength]"
                  hide-details="auto"
                  :disabled="loading"
                >
                  <template v-slot:prepend-inner>
                    <v-icon color="primary">mdi-lock</v-icon>
                  </template>
                  <template v-slot:append-inner>
                    <v-btn
                      variant="text"
                      icon
                      @click="toggleNewPassword"
                      color="grey-lighten-1"
                      size="small"
                    >
                      <v-icon>{{ showNewPassword ? 'mdi-eye-off' : 'mdi-eye' }}</v-icon>
                    </v-btn>
                  </template>
                </v-text-field>

                <v-text-field
                  v-model="form.confirmPassword"
                  label="CONFIRMAR CONTRASEÑA"
                  :type="showConfirmPassword ? 'text' : 'password'"
                  placeholder="Confirma tu nueva contraseña"
                  variant="outlined"
                  color="primary"
                  bg-color="dark-surface"
                  class="mb-6"
                  :rules="[rules.required, rules.confirmPassword]"
                  hide-details="auto"
                  :disabled="loading"
                >
                  <template v-slot:prepend-inner>
                    <v-icon color="primary">mdi-lock-check</v-icon>
                  </template>
                  <template v-slot:append-inner>
                    <v-btn
                      variant="text"
                      icon
                      @click="toggleConfirmPassword"
                      color="grey-lighten-1"
                      size="small"
                    >
                      <v-icon>{{ showConfirmPassword ? 'mdi-eye-off' : 'mdi-eye' }}</v-icon>
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
                  class="mb-6"
                  elevation="2"
                >
                  <span v-if="loading">Cambiando...</span>
                  <span v-else>Cambiar Contraseña</span>
                </v-btn>

                <div class="text-center">
                  <v-btn
                    variant="text"
                    color="primary"
                    class="text-none"
                    @click="goToRecognition"
                    :disabled="loading"
                  >
                    ← Volver al Reconocimiento Facial
                  </v-btn>
                </div>
              </v-form>
            </div>

            <!-- Mensajes de error/éxito -->
            <v-alert
              v-if="error"
              type="error"
              variant="tonal"
              class="mb-4"
              closable
              @click:close="error = ''"
            >
              {{ error }}
            </v-alert>

            <v-alert
              v-if="success"
              type="success"
              variant="tonal"
              class="mb-4"
            >
              {{ success }}
            </v-alert>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import AppBar from '../components/AppBar.vue'
import { employeeAuthService } from '../services/employeeAuthService'

export default {
  name: 'EmployeeResetPassword',
  components: {
    AppBar
  },
  setup() {
    const router = useRouter()
    const route = useRoute()
    
    const form = reactive({
      newPassword: '',
      confirmPassword: ''
    })
    
    const loading = ref(false)
    const error = ref('')
    const success = ref('')
    const formRef = ref(null)
    
    // Estados para el token
    const tokenValid = ref(false)
    const checkingToken = ref(true)
    const tokenError = ref('')
    
    // Estados para mostrar/ocultar contraseñas
    const showNewPassword = ref(false)
    const showConfirmPassword = ref(false)
    
    // Obtener token de la URL
    const token = route.query.token
    
    const rules = {
      required: v => !!v || 'Este campo es requerido',
      minLength: v => v.length >= 8 || 'La contraseña debe tener al menos 8 caracteres',
      confirmPassword: v => v === form.newPassword || 'Las contraseñas no coinciden'
    }
    
    // Verificar token al cargar la página
    onMounted(async () => {
      if (!token) {
        tokenError.value = 'No se proporcionó un token de recuperación'
        checkingToken.value = false
        return
      }
      
      try {
        const result = await employeeAuthService.validateResetToken(token)
        if (result.valid) {
          tokenValid.value = true
          console.log('✅ Token válido para:', result.user_email)
        } else {
          tokenError.value = result.error || 'Token inválido o expirado'
        }
      } catch (err) {
        console.error('❌ Error validando token:', err)
        tokenError.value = 'Error validando el token de recuperación'
      } finally {
        checkingToken.value = false
      }
    })
    
    const handleSubmit = async () => {
      loading.value = true
      error.value = ''
      success.value = ''
      
      try {
        // Validar formulario
        const { valid } = await formRef.value.validate()
        if (!valid) return
        
        // Cambiar contraseña
        const result = await employeeAuthService.confirmPasswordReset(token, form.newPassword)
        
        if (result.success) {
          success.value = result.message
          form.newPassword = ''
          form.confirmPassword = ''
          
          // Redirigir después de 3 segundos
          setTimeout(() => {
            router.push('/')
          }, 3000)
        } else {
          error.value = result.error
        }
      } catch (err) {
        error.value = 'Ocurrió un error al cambiar la contraseña. Por favor intenta de nuevo.'
        console.error('Error en reset password:', err)
      } finally {
        loading.value = false
      }
    }
    
    const toggleNewPassword = () => {
      showNewPassword.value = !showNewPassword.value
    }
    
    const toggleConfirmPassword = () => {
      showConfirmPassword.value = !showConfirmPassword.value
    }
    
    const goToRecognition = () => {
      router.push('/')
    }
    
    const goToForgotPassword = () => {
      router.push('/employee/forgot-password')
    }
    
    return {
      form,
      loading,
      error,
      success,
      rules,
      formRef,
      tokenValid,
      checkingToken,
      tokenError,
      showNewPassword,
      showConfirmPassword,
      handleSubmit,
      toggleNewPassword,
      toggleConfirmPassword,
      goToRecognition,
      goToForgotPassword
    }
  }
}
</script>

<style scoped>
.employee-reset-password-container {
  min-height: calc(100vh - 64px);
  background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 100%);
  margin: 0 !important;
  padding: 0 !important;
  border: none !important;
  outline: none !important;
  margin-top: 64px !important;
}

.left-panel {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  position: relative;
  overflow: hidden;
}

.left-panel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg, rgba(59, 130, 246, 0.1) 0%, rgba(0, 212, 255, 0.1) 100%);
  z-index: 1;
}

.logo-text {
  position: relative;
  z-index: 2;
  text-shadow: 0 0 20px rgba(59, 130, 246, 0.5);
}

.logo-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(59, 130, 246, 0.3) 0%, transparent 70%);
  border-radius: 50%;
  z-index: 1;
  animation: pulse 3s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0.3;
  }
  50% {
    transform: translate(-50%, -50%) scale(1.2);
    opacity: 0.6;
  }
}

.right-panel {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  padding: 2rem;
}

.employee-reset-password-card {
  background: rgba(30, 41, 59, 0.8) !important;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 16px;
  max-width: 500px;
  width: 100%;
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

:deep(.v-btn--variant-text) {
  color: #3b82f6 !important;
}

:deep(.v-btn--variant-text:hover) {
  background-color: rgba(59, 130, 246, 0.1) !important;
}

/* Responsive */
@media (max-width: 960px) {
  .left-panel {
    display: none;
  }
  
  .right-panel {
    padding: 1rem;
  }
  
  .employee-reset-password-card {
    max-width: 100%;
  }
}

@media (max-width: 600px) {
  .employee-reset-password-container {
    margin-top: 56px !important;
  }
  
  .right-panel {
    padding: 0.5rem;
  }
  
  .employee-reset-password-card .v-card-text {
    padding: 1.5rem !important;
  }
  
  .logo-text {
    font-size: 1.5rem !important;
  }
}
</style>
