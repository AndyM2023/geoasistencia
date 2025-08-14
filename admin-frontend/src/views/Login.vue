<template>
  <v-container fluid class="login-container pa-0">
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
        <v-card class="login-card" elevation="0">
          <v-card-text class="pa-8">
            <h2 class="text-h4 font-weight-bold text-white mb-2">Log in</h2>
            <p class="text-body-1 text-grey-lighten-1 mb-8">
              New to Geoasistencia? 
              <v-btn variant="text" color="primary" class="text-none px-1">Sign up</v-btn>
            </p>

            <v-form @submit.prevent="handleLogin" class="login-form">
              <v-text-field
                v-model="form.email"
                label="EMAIL"
                type="email"
                placeholder="Enter your email"
                variant="outlined"
                color="primary"
                bg-color="dark-surface"
                class="mb-4"
                :rules="[rules.required, rules.email]"
                hide-details="auto"
              >
                <template v-slot:prepend-inner>
                  <v-icon color="primary">mdi-email</v-icon>
                </template>
              </v-text-field>

              <v-text-field
                v-model="form.password"
                label="PASSWORD"
                :type="showPassword ? 'text' : 'password'"
                placeholder="Enter your password"
                variant="outlined"
                color="primary"
                bg-color="dark-surface"
                class="mb-4"
                :rules="[rules.required]"
                hide-details="auto"
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
                  >
                    <v-icon>{{ showPassword ? 'mdi-eye-off' : 'mdi-eye' }}</v-icon>
                  </v-btn>
                </template>
              </v-text-field>

              <div class="d-flex justify-space-between align-center mb-6">
                <v-checkbox
                  v-model="form.keepSignedIn"
                  label="Keep me signed in on this device"
                  color="primary"
                  hide-details
                  class="text-grey-lighten-1"
                ></v-checkbox>
                <v-btn
                  variant="text"
                  color="primary"
                  class="text-none"
                >
                  Forgot password?
                </v-btn>
              </div>

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
                <span v-if="loading">Logging in...</span>
                <span v-else>Login</span>
              </v-btn>
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

            <!-- Credenciales de demo -->
            <v-card
              variant="tonal"
              color="grey-darken-3"
              class="demo-credentials"
            >
              <v-card-text class="pa-4">
                <h4 class="text-subtitle-1 font-weight-bold text-white mb-3">
                  Demo Credentials:
                </h4>
                <div class="text-body-2 text-grey-lighten-1">
                  <p class="mb-1">
                    <strong>Email:</strong> admin@geoasistencia.com
                  </p>
                  <p class="mb-0">
                    <strong>Password:</strong> admin123
                  </p>
                </div>
              </v-card-text>
            </v-card>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    
    const form = reactive({
      email: '',
      password: '',
      keepSignedIn: false
    })
    
    const showPassword = ref(false)
    const loading = ref(false)
    const error = ref('')
    const success = ref('')

    const rules = {
      required: v => !!v || 'This field is required',
      email: v => /.+@.+\..+/.test(v) || 'Email must be valid'
    }

    const togglePassword = () => {
      showPassword.value = !showPassword.value
    }

    const handleLogin = async () => {
      loading.value = true
      error.value = ''
      success.value = ''

      try {
        const result = await authStore.login(form.email, form.password)
        
        if (result.success) {
          success.value = 'Login successful! Redirecting...'
          
          setTimeout(() => {
            router.push('/')
          }, 1500)
        } else {
          error.value = result.error
        }
      } catch (err) {
        error.value = 'An error occurred. Please try again.'
      } finally {
        loading.value = false
      }
    }

    return {
      form,
      showPassword,
      loading,
      error,
      success,
      rules,
      togglePassword,
      handleLogin
    }
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 100%);
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

.login-card {
  background: rgba(30, 41, 59, 0.8) !important;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 16px;
  max-width: 450px;
  width: 100%;
}

.demo-credentials {
  background: rgba(51, 65, 85, 0.6) !important;
  border: 1px solid rgba(59, 130, 246, 0.2);
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

:deep(.v-checkbox .v-selection-control__input) {
  color: #00d4ff !important;
}

:deep(.v-checkbox .v-label) {
  color: #cbd5e1 !important;
}

/* Responsive */
@media (max-width: 960px) {
  .left-panel {
    min-height: 200px;
  }
  
  .logo-text {
    font-size: 1.5rem !important;
  }
  
  .login-card {
    margin: 1rem;
  }
}
</style>
