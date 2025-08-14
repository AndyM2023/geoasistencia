<template>
  <v-container fluid class="recognition-container pa-0">
    <!-- Imagen del lado izquierdo -->
    <img src="/src/assets/left-image.png" alt="Imagen izquierda" class="side-image left-image">
    
    <!-- Imagen del lado derecho -->
    <img src="/src/assets/right-image.png" alt="Imagen derecha" class="side-image right-image">
    
    <v-row no-gutters class="h-100">
      <!-- Contenido centrado de reconocimiento -->
      <v-col cols="12" class="d-flex align-center justify-center">
        <v-card class="recognition-card" elevation="0">
          <v-card-text class="pa-8">
            <h2 class="text-h4 font-weight-bold text-white mb-2">Reconocimiento Facial</h2>
            <p class="text-body-1 text-grey-lighten-1 mb-8">
              Identifícate para registrar tu asistencia
            </p>

            <!-- Área de la cámara -->
            <div class="camera-area mb-6">
              <div class="camera-placeholder d-flex align-center justify-center">
                <v-icon size="64" color="grey-lighten-1">mdi-camera</v-icon>
                <p class="text-body-2 text-grey-lighten-1 mt-2">Cámara no disponible</p>
              </div>
            </div>

            <!-- Formulario de reconocimiento -->
            <v-form @submit.prevent="handleRecognition" class="recognition-form">
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

              <v-btn
                type="submit"
                color="primary"
                size="large"
                block
                :loading="loading"
                :disabled="loading"
                class="mb-6 recognition-btn"
                elevation="2"
              >
                <v-icon left class="mr-2">mdi-face-recognition</v-icon>
                <span v-if="loading">Reconociendo...</span>
                <span v-else>RECONOCER ASISTENCIA</span>
              </v-btn>
            </v-form>

            <!-- Mensajes de estado -->
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

            <!-- Instrucciones -->
            <v-card
              variant="tonal"
              color="grey-darken-3"
              class="instructions-card"
            >
              <v-card-text class="pa-4">
                <h4 class="text-subtitle-1 font-weight-bold text-white mb-3">
                  Instrucciones:
                </h4>
                <div class="text-body-2 text-grey-lighten-1">
                  <p class="mb-1">• Asegúrate de estar bien iluminado</p>
                  <p class="mb-1">• Mira directamente a la cámara</p>
                  <p class="mb-0">• Mantén una distancia de 30-50 cm</p>
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
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'Recognition',
  setup() {
    const router = useRouter()
    
    const form = reactive({
      username: '',
      password: ''
    })
    
    const showPassword = ref(false)
    const loading = ref(false)
    const error = ref('')
    const success = ref('')

    const rules = {
      required: v => !!v || 'Este campo es requerido'
    }

    const togglePassword = () => {
      showPassword.value = !showPassword.value
    }

    const handleRecognition = async () => {
      loading.value = true
      error.value = ''
      success.value = ''

      try {
        // Simular proceso de reconocimiento
        await new Promise(resolve => setTimeout(resolve, 2000))
        
        if (form.username && form.password) {
          success.value = '¡Asistencia registrada exitosamente!'
          
          // Limpiar formulario
          form.username = ''
          form.password = ''
          
          setTimeout(() => {
            success.value = ''
          }, 3000)
        } else {
          error.value = 'Por favor completa todos los campos'
        }
      } catch (err) {
        error.value = 'Error en el reconocimiento. Intenta de nuevo.'
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
      handleRecognition
    }
  },

  // Hooks de lifecycle para controlar el scroll
  onMounted() {
    document.body.classList.add('recognition-page')
  },

  onUnmounted() {
    document.body.classList.remove('recognition-page')
  }
}
</script>

<style scoped>
.recognition-container {
  min-height: 100vh;
  background: #16213e;
  margin: 0 !important;
  padding: 0 !important;
  border: none !important;
  outline: none !important;
  position: relative;
}

/* Imágenes de los lados */
.side-image {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 300px;
  height: 300px;
  z-index: 1;
  object-fit: contain;
}

.left-image {
  left: 130px;
}

.right-image {
  right: 150px;
}





.recognition-card {
  background: rgba(30, 41, 59, 0.8) !important;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 16px;
  max-width: 500px;
  width: 100%;
}

.camera-area {
  background: rgba(15, 23, 42, 0.6);
  border: 2px dashed rgba(59, 130, 246, 0.3);
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
}

.camera-placeholder {
  flex-direction: column;
  min-height: 200px;
}

.recognition-btn {
  background: linear-gradient(135deg, #3b82f6 0%, #00d4ff 100%) !important;
  font-weight: bold;
  letter-spacing: 1px;
}

.instructions-card {
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
  
  .recognition-card {
    margin: 1rem;
  }
  
  .camera-area {
    min-height: 150px;
  }
}
</style>
