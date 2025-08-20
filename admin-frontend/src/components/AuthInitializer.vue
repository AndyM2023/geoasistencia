<template>
  <div v-if="!authStore.isInitialized" class="auth-initializer">
    <div class="initialization-overlay">
      <v-card class="initialization-card" elevation="24">
        <v-card-text class="text-center pa-8">
          <v-progress-circular 
            indeterminate 
            color="blue-400" 
            size="80" 
            width="8"
            class="mb-6"
          ></v-progress-circular>
          
          <h2 class="text-h4 text-white mb-4">
            Inicializando aplicación
          </h2>
          
          <p class="text-body-1 text-grey-300 mb-6">
            Restaurando sesión de usuario...
          </p>
          
          <div class="initialization-steps">
            <div class="step" :class="{ active: currentStep >= 1 }">
              <v-icon 
                :color="currentStep >= 1 ? 'green-400' : 'grey-500'"
                size="24"
                class="mr-3"
              >
                {{ currentStep >= 1 ? 'mdi-check-circle' : 'mdi-circle-outline' }}
              </v-icon>
              <span class="text-grey-300">Verificando sesión guardada</span>
            </div>
            
            <div class="step" :class="{ active: currentStep >= 2 }">
              <v-icon 
                :color="currentStep >= 2 ? 'green-400' : 'grey-500'"
                size="24"
                class="mr-3"
              >
                {{ currentStep >= 2 ? 'mdi-check-circle' : 'mdi-circle-outline' }}
              </v-icon>
              <span class="text-grey-300">Validando credenciales</span>
            </div>
            
            <div class="step" :class="{ active: currentStep >= 3 }">
              <v-icon 
                :color="currentStep >= 3 ? 'green-400' : 'grey-500'"
                size="24"
                class="mr-3"
              >
                {{ currentStep >= 3 ? 'mdi-check-circle' : 'mdi-circle-outline' }}
              </v-icon>
              <span class="text-grey-300">Cargando datos del usuario</span>
            </div>
          </div>
          
          <div v-if="error" class="error-message mt-6">
            <v-alert 
              type="error" 
              variant="tonal"
              class="text-left"
            >
              <template v-slot:prepend>
                <v-icon>mdi-alert-circle</v-icon>
              </template>
              <div>
                <strong>Error de inicialización:</strong>
                <p class="mt-2 mb-0">{{ error }}</p>
              </div>
            </v-alert>
            
            <v-btn 
              color="blue-400" 
              variant="outlined" 
              class="mt-4"
              @click="retryInitialization"
            >
              Reintentar
            </v-btn>
          </div>
        </v-card-text>
      </v-card>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import { useAuthStore } from '../stores/auth'

export default {
  name: 'AuthInitializer',
  setup() {
    const authStore = useAuthStore()
    const currentStep = ref(0)
    const error = ref(null)
    
    const initializeAuth = async () => {
      try {
        error.value = null
        currentStep.value = 0
        
        console.log('🚀 AuthInitializer - Iniciando proceso de inicialización...')
        
        // Verificar si ya estamos en proceso de logout
        if (localStorage.getItem('isLoggingOut')) {
          console.log('🔄 AuthInitializer - Logout en progreso, esperando...')
          await new Promise(resolve => setTimeout(resolve, 1000))
        }
        
        // Paso 1: Verificar sesión guardada
        currentStep.value = 1
        console.log('✅ Paso 1: Verificando sesión guardada')
        await new Promise(resolve => setTimeout(resolve, 500)) // Simular delay
        
        // Paso 2: Validar credenciales
        currentStep.value = 2
        console.log('✅ Paso 2: Validando credenciales')
        await new Promise(resolve => setTimeout(resolve, 500)) // Simular delay
        
        // Paso 3: Cargar datos del usuario
        currentStep.value = 3
        console.log('✅ Paso 3: Cargando datos del usuario')
        
        // Ejecutar inicialización real
        const result = await authStore.initAuth()
        
        if (result) {
          console.log('✅ AuthInitializer - Inicialización completada exitosamente')
        } else {
          console.log('ℹ️ AuthInitializer - No hay sesión activa')
        }
        
      } catch (err) {
        console.error('❌ AuthInitializer - Error durante inicialización:', err)
        
        // Solo mostrar error si no es un logout intencional
        if (!localStorage.getItem('isLoggingOut')) {
          error.value = err.message || 'Error desconocido durante la inicialización'
        } else {
          console.log('ℹ️ AuthInitializer - Error durante logout intencional, no mostrando mensaje')
        }
      }
    }
    
    const retryInitialization = () => {
      console.log('🔄 AuthInitializer - Reintentando inicialización...')
      initializeAuth()
    }
    
    // Inicializar al montar el componente
    onMounted(() => {
      console.log('🚀 AuthInitializer - Componente montado')
      initializeAuth()
    })
    
    // Watch para cambios en el estado de inicialización
    watch(() => authStore.isInitialized, (newVal) => {
      console.log(`🔄 AuthInitializer - Estado de inicialización cambió: ${newVal}`)
    })
    
    return {
      authStore,
      currentStep,
      error,
      retryInitialization
    }
  }
}
</script>

<style scoped>
.auth-initializer {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 9999;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
}

.initialization-overlay {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  padding: 20px;
}

.initialization-card {
  background: rgba(30, 41, 59, 0.95) !important;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(59, 130, 246, 0.2);
  max-width: 500px;
  width: 100%;
}

.initialization-steps {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 24px;
}

.step {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-radius: 8px;
  background: rgba(51, 65, 85, 0.5);
  transition: all 0.3s ease;
}

.step.active {
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.error-message {
  border-top: 1px solid rgba(239, 68, 68, 0.2);
  padding-top: 24px;
}
</style>
