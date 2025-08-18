<template>
  <AppBar />
  <v-container fluid class="forgot-password-container pa-0">
    <v-row no-gutters class="h-100">
      <!-- Panel izquierdo con gradiente azul oscuro -->
      <v-col cols="12" md="4" class="left-panel d-flex align-center justify-center">
        <div class="text-center">
          <h1 class="logo-text text-h3 font-weight-bold text-white">
            GEOASISTENCIA
            <br>
            ADMIN
          </h1>
          <div class="logo-glow"></div>
        </div>
      </v-col>

      <!-- Panel derecho con formulario -->
      <v-col cols="12" md="8" class="right-panel d-flex align-center justify-center">
        <v-card class="forgot-password-card" elevation="0">
          <v-card-text class="pa-8">
            <div class="text-center mb-6">
              <v-icon size="64" color="primary" class="mb-4">mdi-lock-reset</v-icon>
              <h2 class="text-h4 font-weight-bold text-white mb-2">Recuperar Contraseña</h2>
              <p class="text-body-1 text-grey-lighten-1">
                Ingresa tu email de administrador y te enviaremos instrucciones para recuperar tu contraseña.
              </p>
            </div>

            <v-form @submit.prevent="handleSubmit" class="forgot-password-form">
              <v-text-field
                v-model="form.email"
                label="EMAIL"
                type="email"
                placeholder="Ingresa tu email de administrador"
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
                  @click="goToLogin"
                  :disabled="loading"
                >
                  ← Volver al Login
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
import { authService } from '../services/authService'

export default {
  name: 'ForgotPassword',
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

    const rules = {
      required: v => !!v || 'Este campo es requerido',
      email: v => /.+@.+\..+/.test(v) || 'Email inválido'
    }

    const handleSubmit = async () => {
      loading.value = true
      error.value = ''
      success.value = ''

      try {
        const result = await authService.requestPasswordReset(form.email)
        
        if (result.success) {
          success.value = result.message
          form.email = ''
        } else {
          error.value = result.error
        }
      } catch (err) {
        error.value = 'Ocurrió un error. Por favor intenta de nuevo.'
        console.error('Error en forgot password:', err)
      } finally {
        loading.value = false
      }
    }

    const goToLogin = () => {
      router.push('/login')
    }

    return {
      form,
      loading,
      error,
      success,
      rules,
      handleSubmit,
      goToLogin
    }
  },

  // Hooks de lifecycle para controlar el scroll
  onMounted() {
    document.body.classList.add('forgot-password-page')
  },

  onUnmounted() {
    document.body.classList.remove('forgot-password-page')
  }
}
</script>

<style scoped>
.forgot-password-container {
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
  background: radial-gradient(circle at 30% 70%, rgba(0, 212, 255, 0.1) 0%, transparent 50%);
  pointer-events: none;
}

.logo-text {
  position: relative;
  z-index: 2;
  text-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
  letter-spacing: 2px;
}

.logo-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(0, 212, 255, 0.2) 0%, transparent 70%);
  border-radius: 50%;
  animation: pulse 3s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.3; transform: translate(-50%, -50%) scale(1); }
  50% { opacity: 0.6; transform: translate(-50%, -50%) scale(1.1); }
}

.right-panel {
  background: #16213e;
  position: relative;
}

.right-panel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 80% 20%, rgba(139, 92, 246, 0.05) 0%, transparent 50%);
  pointer-events: none;
}

.forgot-password-card {
  background: rgba(30, 41, 59, 0.8) !important;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 16px;
  max-width: 450px;
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

/* Eliminar bordes y márgenes globales */
:deep(.v-container) {
  margin: 0 !important;
  padding: 0 !important;
  border: none !important;
}

:deep(.v-row) {
  margin: 0 !important;
  border: none !important;
}

:deep(.v-col) {
  padding: 0 !important;
  border: none !important;
}

/* Responsive */
@media (max-width: 960px) {
  .left-panel {
    min-height: 200px;
  }
  
  .logo-text {
    font-size: 1.5rem !important;
  }
  
  .forgot-password-card {
    margin: 1rem;
  }
}

/* Asegurar que el AppBar sea visible */
:deep(.v-app-bar) {
  z-index: 1000 !important;
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
}

/* Ajustar el contenedor principal para el AppBar */
.forgot-password-container {
  position: relative;
  z-index: 1;
}
</style>
