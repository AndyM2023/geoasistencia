<template>
  <div class="login-container">
    <!-- Panel izquierdo azul -->
    <div class="left-panel">
      <div class="logo-container">
        <h1 class="logo">GEOASISTENCIA ADMIN</h1>
      </div>
    </div>

    <!-- Panel derecho blanco con formulario -->
    <div class="right-panel">
      <div class="login-form-container">
        <h2 class="login-title">Log in</h2>
        <p class="signup-text">
          New to Geoasistencia? 
          <a href="#" class="signup-link">Sign up</a>
        </p>

        <form @submit.prevent="handleLogin" class="login-form">
          <div class="form-group">
            <label for="email" class="form-label">EMAIL</label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              class="form-input"
              placeholder="Enter your email"
              required
            />
          </div>

          <div class="form-group">
            <label for="password" class="form-label">PASSWORD</label>
            <div class="password-input-container">
              <input
                id="password"
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                class="form-input"
                placeholder="Enter your password"
                required
              />
              <button
                type="button"
                class="password-toggle"
                @click="togglePassword"
              >
                <i class="mdi" :class="showPassword ? 'mdi-eye-off' : 'mdi-eye'"></i>
              </button>
            </div>
          </div>

          <div class="form-options">
            <label class="checkbox-container">
              <input
                v-model="form.keepSignedIn"
                type="checkbox"
                class="checkbox"
              />
              <span class="checkmark"></span>
              Keep me signed in on this device
            </label>
            <a href="#" class="forgot-password">Forgot password?</a>
          </div>

          <button type="submit" class="login-button" :disabled="loading">
            <span v-if="loading">Logging in...</span>
            <span v-else>Login</span>
          </button>
        </form>

        <!-- Mensajes de error/éxito -->
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
        <div v-if="success" class="success-message">
          {{ success }}
        </div>

        <!-- Credenciales de prueba -->
        <div class="demo-credentials">
          <p class="demo-title">Demo Credentials:</p>
          <p class="demo-text">Email: <strong>admin@geoasistencia.com</strong></p>
          <p class="demo-text">Password: <strong>admin123</strong></p>
        </div>
      </div>
    </div>
  </div>
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

    const togglePassword = () => {
      showPassword.value = !showPassword.value
    }

    const handleLogin = async () => {
      loading.value = true
      error.value = ''
      success.value = ''

      try {
        // Usar el store de autenticación
        const result = await authStore.login(form.email, form.password)
        
        if (result.success) {
          success.value = 'Login successful! Redirecting...'
          
          // Redirigir al dashboard
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
      togglePassword,
      handleLogin
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  height: 100vh;
  width: 100vw;
}

.left-panel {
  background: #1e3a8a;
  width: 33.333%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-container {
  text-align: center;
}

.logo {
  color: white;
  font-size: 2.5rem;
  font-weight: 700;
  letter-spacing: 2px;
  text-transform: uppercase;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.right-panel {
  background: white;
  width: 66.667%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-form-container {
  width: 100%;
  max-width: 400px;
  padding: 2rem;
}

.login-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 0.5rem;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.signup-text {
  color: #6b7280;
  margin-bottom: 2rem;
  font-size: 1rem;
}

.signup-link {
  color: #3b82f6;
  text-decoration: none;
  font-weight: 500;
}

.signup-link:hover {
  text-decoration: underline;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.form-input {
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.password-input-container {
  position: relative;
}

.password-toggle {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 0.25rem;
}

.password-toggle:hover {
  color: #374151;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.5rem;
}

.checkbox-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #374151;
  font-size: 0.875rem;
  cursor: pointer;
}

.checkbox {
  width: 1rem;
  height: 1rem;
  accent-color: #3b82f6;
}

.forgot-password {
  color: #3b82f6;
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
}

.forgot-password:hover {
  text-decoration: underline;
}

.login-button {
  background: #1e3a8a;
  color: white;
  padding: 0.875rem 1rem;
  border: none;
  border-radius: 0.375rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-top: 1rem;
}

.login-button:hover:not(:disabled) {
  background: #1e40af;
}

.login-button:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.error-message {
  background: #fef2f2;
  color: #dc2626;
  padding: 0.75rem 1rem;
  border-radius: 0.375rem;
  border: 1px solid #fecaca;
  margin-top: 1rem;
  font-size: 0.875rem;
}

.success-message {
  background: #f0fdf4;
  color: #16a34a;
  padding: 0.75rem 1rem;
  border-radius: 0.375rem;
  border: 1px solid #bbf7d0;
  margin-top: 1rem;
  font-size: 0.875rem;
}

.demo-credentials {
  margin-top: 2rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 0.375rem;
  border: 1px solid #e2e8f0;
}

.demo-title {
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
}

.demo-text {
  color: #6b7280;
  font-size: 0.75rem;
  margin: 0.25rem 0;
}

/* Responsive */
@media (max-width: 768px) {
  .login-container {
    flex-direction: column;
  }
  
  .left-panel {
    width: 100%;
    height: 30vh;
  }
  
  .right-panel {
    width: 100%;
    height: 70vh;
  }
  
  .logo {
    font-size: 2rem;
  }
  
  .login-title {
    font-size: 2rem;
  }
}
</style>
