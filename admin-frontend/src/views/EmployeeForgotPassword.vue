<template>
  <AppBar />
  <v-container fluid class="employee-forgot-password-container pa-0">
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
        <v-card class="employee-forgot-password-card" elevation="0">
          <v-card-text class="pa-8">
            <div class="text-center mb-6">
              <v-icon size="64" color="primary" class="mb-4">mdi-account-lock</v-icon>
              <h2 class="text-h4 font-weight-bold text-white mb-2">Recuperar Contraseña</h2>
              <p class="text-body-1 text-grey-lighten-1">
                Ingresa tu email de empleado y te enviaremos instrucciones para recuperar tu contraseña.
              </p>
            </div>

            <v-form ref="formRef" @submit.prevent="handleSubmit" class="employee-forgot-password-form">
              <v-text-field
                v-model="form.email"
                label="EMAIL"
                type="email"
                placeholder="Ingresa tu email de empleado"
                variant="outlined"
                color="primary"
                bg-color="dark-surface"
                class="mb-6"
                :rules="[rules.required, rules.email]"
                hide-details="auto"
                :disabled="loading"
              >
                <template v-slot:prepend-inner>
                  <v-icon color="primary">mdi-email</v-icon>
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
                <span v-if="loading">Enviando...</span>
                <span v-else>Enviar Instrucciones</span>
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
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import AppBar from '../components/AppBar.vue'
import { employeeAuthService } from '../services/employeeAuthService'

export default {
  name: 'EmployeeForgotPassword',
  components: {
    AppBar
  },
  setup() {
    const router = useRouter()
    
    const form = reactive({
      email: ''
    })
    
    const loading = ref(false)
    const error = ref('')
    const success = ref('')
    const formRef = ref(null)

    const rules = {
      required: v => !!v || 'Este campo es requerido',
      email: v => /.+@.+\..+/.test(v) || 'Email inválido'
    }

    const handleSubmit = async () => {
      loading.value = true
      error.value = ''
      success.value = ''

      try {
        // Primero verificar que el email pertenezca a un empleado
        const verifyResult = await employeeAuthService.verifyEmployeeEmail(form.email)
        
        if (!verifyResult.success) {
          error.value = verifyResult.error
          return
        }
        
        if (!verifyResult.isEmployee) {
          error.value = 'Este email no está registrado como empleado en el sistema.'
          return
        }

        // Solicitar recuperación de contraseña
        const result = await employeeAuthService.requestPasswordReset(form.email)
        
        if (result.success) {
          success.value = result.message
          form.email = ''
          // Resetear el estado de validación del formulario
          if (formRef.value) {
            formRef.value.resetValidation()
          }
        } else {
          error.value = result.error
        }
      } catch (err) {
        error.value = 'Ocurrió un error. Por favor intenta de nuevo.'
        console.error('Error en employee forgot password:', err)
      } finally {
        loading.value = false
      }
    }

    const goToRecognition = () => {
      router.push('/')
    }

    return {
      form,
      loading,
      error,
      success,
      rules,
      formRef,
      handleSubmit,
      goToRecognition
    }
  },

  // Hooks de lifecycle para controlar el scroll
  onMounted() {
    document.body.classList.add('employee-forgot-password-page')
  },

  onUnmounted() {
    document.body.classList.remove('employee-forgot-password-page')
  }
}
</script>

<style scoped>
.employee-forgot-password-container {
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

.employee-forgot-password-card {
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
  
  .employee-forgot-password-card {
    max-width: 100%;
  }
}

@media (max-width: 600px) {
  .employee-forgot-password-container {
    margin-top: 56px !important;
  }
  
  .right-panel {
    padding: 0.5rem;
  }
  
  .employee-forgot-password-card .v-card-text {
    padding: 1.5rem !important;
  }
  
  .logo-text {
    font-size: 1.5rem !important;
  }
}
</style>
