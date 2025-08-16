<template>
  <AppBar />
  <v-container fluid class="recognition-container pa-0">
    <!-- Imagen del lado izquierdo - Responsive -->
    <img src="/src/assets/left-image.png" alt="Imagen izquierda" class="side-image left-image d-none d-md-block">
    
    <!-- Imagen del lado derecho - Responsive -->
    <img src="/src/assets/right-image.png" alt="Imagen derecha" class="side-image right-image d-none d-md-block">
    
    <v-row no-gutters class="h-100">
      <!-- Contenido centrado de reconocimiento -->
      <v-col cols="12" class="d-flex align-center justify-center">
        <v-card class="recognition-card" elevation="0">
          <v-card-text class="pa-8 pa-4 pa-md-8">
            <h2 class="text-h6 text-h5-md font-weight-bold text-white mb-6 text-center">Reconocimiento Facial</h2>
            
            <v-row>
              <!-- Columna izquierda: Cámara -->
              <v-col cols="12" md="6" class="d-flex justify-center">
                <!-- Título invisible para alineación -->
                <div class="invisible-title mb-6"></div>
                
                <div class="camera-area" :class="{ 'camera-active': isCameraActive }">
                  <!-- Elemento de video siempre presente pero oculto -->
                  <video ref="videoElement" autoplay muted playsinline class="camera-feed" :style="{ display: isCameraActive ? 'block' : 'none' }"></video>
                  
                  <!-- Estado inicial: Placeholder -->
                  <div v-if="!isCameraActive" class="camera-placeholder d-flex align-center justify-center">
                    <v-icon size="64" color="grey-lighten-1">mdi-camera</v-icon>
                    <p class="text-body-2 text-grey-lighten-1 mt-2">Activa la cámara para capturar tu rostro</p>
                    
                    <!-- Botón para activar cámara -->
                    <v-btn
                      @click="startCamera"
                      color="primary"
                      size="large"
                      class="mt-4 activate-camera-btn"
                      :loading="loading"
                      :disabled="loading"
                    >
                      <v-icon left class="mr-2">mdi-camera</v-icon>
                       Activar Cámara
                    </v-btn>
                  </div>
                  
                  <!-- Estado activo: Overlay de la cámara -->
                  <div v-else class="camera-overlay">
                    <v-btn
                      icon
                      color="red"
                      size="small"
                      class="close-camera-btn"
                      @click.stop="stopCamera"
                    >
                      <v-icon>mdi-close</v-icon>
                    </v-btn>
                  </div>
                </div>
              </v-col>

              <!-- Columna derecha: Formulario -->
              <v-col cols="12" md="6">
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
                    class="mb-4"
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
                    :disabled="loading || !isCameraActive"
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
              </v-col>
            </v-row>
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
import { attendanceService } from '../services/attendanceService'

export default {
  name: 'Recognition',
  components: {
    AppBar
  },
  setup() {
    const router = useRouter()
    
    // Variables del formulario
    const form = reactive({
      username: '',
      password: ''
    })
    
    // Variables de estado
    const showPassword = ref(false)
    const loading = ref(false)
    const error = ref('')
    const success = ref('')
    
    // Variables de la cámara
    const isCameraActive = ref(false)
    const videoElement = ref(null)
    const stream = ref(null)

    // Reglas de validación
    const rules = {
      required: v => !!v || 'Este campo es requerido'
    }

    // Función para alternar visibilidad de contraseña
    const togglePassword = () => {
      showPassword.value = !showPassword.value
    }

    // Función principal de reconocimiento
    const handleRecognition = async () => {
      loading.value = true
      error.value = ''
      success.value = ''

      try {
        // Validar campos
        if (!form.username || !form.password) {
          error.value = 'Por favor completa todos los campos'
          return
        }

        // Verificar que la cámara esté activa
        if (!isCameraActive.value) {
          error.value = 'Primero debes activar la cámara para capturar tu rostro'
          return
        }

        // Capturar foto de la cámara
        const photoBase64 = await capturePhotoFromCamera()
        if (!photoBase64) {
          error.value = 'No se pudo capturar la foto. Intenta nuevamente.'
          return
        }

        // Obtener credenciales del empleado
        const employeeData = await getEmployeeCredentials(form.username, form.password)
        if (!employeeData) {
          error.value = 'Credenciales inválidas'
          return
        }

        console.log('�� Datos del empleado obtenidos:', employeeData)
        console.log('🔍 Employee ID:', employeeData.employee_id)
        console.log('🔍 Area ID:', employeeData.area_id)

        // Verificar rostro y marcar asistencia
        const result = await verifyFaceAndMarkAttendance(
          employeeData.employee_id,
          photoBase64,
          employeeData.area_id,
          getCurrentLocation()
        )

        if (result.success) {
          console.log('🔍 Resultado completo del backend:', result)
          console.log('📊 Confianza recibida:', result.confidence)
          console.log('📊 Confianza calculada:', Math.round(result.confidence * 100))
          console.log('📊 Tipo de confianza:', typeof result.confidence)
          
          // Acceder a los datos desde result.attendance
          const attendanceData = result.attendance
          console.log('🎯 Datos de asistencia:', attendanceData)
          console.log('🎯 ACTION_TYPE recibido:', attendanceData.action_type)
          console.log('🎯 ACTION_TYPE tipo:', typeof attendanceData.action_type)
          console.log('🎯 EMPLOYEE_NAME recibido:', attendanceData.employee_name)
          console.log('🔍 TODAS las claves del resultado:', Object.keys(result))
          console.log('🔍 VALOR de cada clave:')
          Object.keys(result).forEach(key => {
            console.log(`   - ${key}:`, result[key])
          })
          
          // Mostrar mensaje específico según el tipo de acción
          if (attendanceData.action_type === 'entrada') {
            console.log('✅ Procesando ENTRADA')
            success.value = `✅ ENTRADA registrada exitosamente para ${attendanceData.employee_name}`
          } else if (attendanceData.action_type === 'salida') {
            console.log('⏰ Procesando SALIDA')
            success.value = `⏰ SALIDA registrada exitosamente para ${attendanceData.employee_name}`
          } else if (attendanceData.action_type === 'completo') {
            console.log('ℹ️ Procesando COMPLETO')
            success.value = `ℹ️ ${attendanceData.employee_name} ya tiene entrada y salida registradas para hoy`
          } else {
            console.log('❓ ACTION_TYPE no reconocido, usando mensaje genérico')
            success.value = `¡Asistencia registrada exitosamente! Rostro verificado con ${Math.round(result.confidence * 100)}% de confianza`
          }
          
          // Limpiar formulario
          form.username = ''
          form.password = ''
          
          // Detener cámara
          await stopCamera()
          
          setTimeout(() => {
            success.value = ''
          }, 5000)
        } else {
          // Manejar errores del backend con mensajes personalizados
          if (result.action_type === 'completo') {
            // Caso especial: ya tiene entrada y salida (no es realmente un error)
            success.value = `ℹ️ ${result.message}`
            setTimeout(() => {
              success.value = ''
            }, 5000)
          } else {
            // Otros errores reales
            error.value = result.message || 'Error en el reconocimiento facial'
          }
        }
        
      } catch (err) {
        console.error('Error en reconocimiento:', err)
        
        // Verificar si es un error HTTP 400 con respuesta del backend
        if (err.response && err.response.status === 400 && err.response.data) {
          const backendResponse = err.response.data
          console.log('🔍 Respuesta del backend en error 400:', backendResponse)
          
          // Manejar casos especiales del backend
          if (backendResponse.action_type === 'completo') {
            // Caso especial: ya tiene entrada y salida (no es realmente un error)
            success.value = `ℹ️ ${backendResponse.message}`
            setTimeout(() => {
              success.value = ''
            }, 5000)
          } else if (backendResponse.message) {
            // Otros mensajes personalizados del backend
            error.value = backendResponse.message
          } else {
            // Error genérico si no hay mensaje personalizado
            error.value = 'Error en el reconocimiento: ' + (err.message || 'Error desconocido')
          }
        } else {
          // Otros tipos de errores
          error.value = 'Error en el reconocimiento: ' + (err.message || 'Error desconocido')
        }
      } finally {
        loading.value = false
      }
    }

    // Funciones para manejar la cámara
    const startCamera = async () => {
      try {
        console.log('🎬 Iniciando cámara...')
        
        // Limpiar estado previo
        error.value = ''
        
        // Verificar que el elemento de video exista
        if (!videoElement.value) {
          console.error('❌ Elemento de video no encontrado')
          error.value = 'Error: Elemento de video no encontrado. Intenta recargar la página.'
          return
        }
        
        console.log('📹 Elemento de video encontrado:', videoElement.value)
        
        // Obtener acceso a la cámara
        stream.value = await navigator.mediaDevices.getUserMedia({ 
          video: { 
            facingMode: 'user',
            width: { ideal: 640 },
            height: { ideal: 480 }
          } 
        })
        
        console.log('✅ Stream de cámara obtenido:', stream.value)
        
        // Asignar el stream al video
        videoElement.value.srcObject = stream.value
        
        // Esperar a que el video esté listo
        await new Promise((resolve) => {
          videoElement.value.onloadedmetadata = () => {
            console.log('�� Video metadata cargado')
            resolve()
          }
        })
        
        // Activar la cámara
        isCameraActive.value = true
        console.log('🎯 Cámara activada exitosamente')
        
      } catch (err) {
        console.error('❌ Error iniciando cámara:', err)
        error.value = 'Error al acceder a la cámara: ' + err.message
        
        // Mostrar errores específicos
        if (err.name === 'NotAllowedError') {
          error.value = 'Permiso denegado para acceder a la cámara. Verifica los permisos del navegador.'
        } else if (err.name === 'NotFoundError') {
          error.value = 'No se encontró ninguna cámara en tu dispositivo.'
        } else if (err.name === 'NotReadableError') {
          error.value = 'La cámara está siendo usada por otra aplicación.'
        }
      }
    }

    const stopCamera = async () => {
      try {
        console.log('⏹️ Deteniendo cámara...')
        
        if (stream.value) {
          stream.value.getTracks().forEach(track => {
            track.stop()
            console.log('🛑 Track detenido:', track.kind)
          })
          stream.value = null
        }
        
        if (videoElement.value) {
          videoElement.value.srcObject = null
        }
        
        isCameraActive.value = false
        console.log('✅ Cámara detenida exitosamente')
        
      } catch (err) {
        console.error('❌ Error deteniendo cámara:', err)
      }
    }

    // Función para capturar foto de la cámara
    const capturePhotoFromCamera = async () => {
      if (!videoElement.value) return null
      
      try {
        const canvas = document.createElement('canvas')
        const video = videoElement.value
        
        canvas.width = video.videoWidth
        canvas.height = video.videoHeight
        const ctx = canvas.getContext('2d')
        ctx.drawImage(video, 0, 0)
        
        // Convertir a base64
        return canvas.toDataURL('image/jpeg', 0.8)
      } catch (err) {
        console.error('Error capturando foto:', err)
        return null
      }
    }

    // Función para obtener credenciales del empleado
    const getEmployeeCredentials = async (username, password) => {
      try {
        const response = await attendanceService.getEmployeeByCredentials(username, password)
        return response  // Devolver el objeto completo, no solo response.user
      } catch (err) {
        console.error('Error obteniendo credenciales:', err)
        return null
      }
    }

    // Función para verificar rostro y marcar asistencia
    const verifyFaceAndMarkAttendance = async (employeeId, photoBase64, areaId, location) => {
      try {
        return await attendanceService.verifyFaceAndMarkAttendance(
          employeeId,
          photoBase64,
          areaId,
          location.latitude,
          location.longitude
        )
      } catch (err) {
        console.error('Error en verificación facial:', err)
        throw err
      }
    }

    // Función para obtener ubicación actual
    const getCurrentLocation = () => {
      // Por ahora retornamos ubicación simulada
      // En producción usarías navigator.geolocation
      return {
        latitude: -12.0464,  // Lima, Perú (ejemplo)
        longitude: -77.0428
      }
    }

    // Hooks de lifecycle
    onMounted(() => {
      document.body.classList.add('recognition-page')
      
      // Debug: verificar el elemento de video
      console.log('�� Componente montado, verificando elementos...')
      console.log('📹 videoElement ref:', videoElement.value)
      
      // Verificar después de un momento
      setTimeout(() => {
        console.log('⏰ Después de timeout - videoElement:', videoElement.value)
        const videoEl = document.querySelector('video')
        console.log('🔍 Video en DOM:', videoEl)
      }, 500)
    })

    onUnmounted(() => {
      document.body.classList.remove('recognition-page')
      stopCamera()
    })

    return {
      // Variables del formulario
      form,
      showPassword,
      loading,
      error,
      success,
      rules,
      
      // Variables de la cámara
      isCameraActive,
      videoElement,
      
      // Funciones del formulario
      togglePassword,
      handleRecognition,
      
      // Funciones de la cámara
      startCamera,
      stopCamera,
      
      // Funciones adicionales
      capturePhotoFromCamera,
      getEmployeeCredentials,
      verifyFaceAndMarkAttendance,
      getCurrentLocation
    }
  }
}
</script>

<style scoped>
.recognition-container {
  min-height: calc(100vh - 70px); /* Restar altura del AppBar */
  background: #16213e;
  margin: 0 !important;
  padding: 0 !important;
  border: none !important;
  outline: none !important;
  position: relative;
  margin-top: 70px !important; /* Agregar margen superior para el AppBar */
  overflow: hidden; /* Ocultar scroll por defecto */
}

/* Imágenes de los lados - Responsive */
.side-image {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 300px;
  height: 300px;
  z-index: 1;
  object-fit: contain;
  transition: all 0.3s ease;
}

.left-image {
  left: 40px;
}

.right-image {
  right: 50px;
}

/* Responsive para imágenes laterales */
@media (max-width: 1200px) {
  .side-image {
    width: 250px;
    height: 250px;
  }
  
  .left-image {
    left: 20px;
  }
  
  .right-image {
    right: 20px;
  }
}

@media (max-width: 960px) {
  .side-image {
    width: 200px;
    height: 200px;
  }
  
  .left-image {
    left: 10px;
  }
  
  .right-image {
    right: 10px;
  }
}

.recognition-card {
  background: rgba(30, 41, 59, 0.8) !important;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 16px;
  max-width: 700px;
  width: 100%;
  margin-top: 60px;
  transition: all 0.3s ease;
}

/* Responsive para la tarjeta principal */
@media (max-width: 960px) {
  .recognition-card {
    max-width: 95%;
    margin-top: 40px;
    margin-left: 2.5%;
    margin-right: 2.5%;
  }
}

@media (max-width: 600px) {
  .recognition-card {
    max-width: 98%;
    margin-top: 20px;
    margin-left: 1%;
    margin-right: 1%;
  }
}

.invisible-title {
  height: 32px; /* Altura aproximada del título h6 */
  visibility: hidden;
}

.camera-area {
  background: rgba(15, 23, 42, 0.6);
  border: 2px dashed rgba(59, 130, 246, 0.3);
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  width: 100%;
  max-width: 400px;
  transition: all 0.3s ease;
}

.camera-area:hover {
  border-color: rgba(0, 212, 255, 0.6);
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.2);
}

.camera-area.camera-active {
  border-color: #00d4ff;
  box-shadow: 0 0 25px rgba(0, 212, 255, 0.4);
  padding: 0;
}

.camera-video {
  position: relative;
  width: 100%;
  height: 100%;
  border-radius: 12px;
  overflow: hidden;
}

.camera-feed {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 12px;
}

.camera-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.camera-placeholder {
  flex-direction: column;
  min-height: 200px;
}

.activate-camera-btn {
  background: linear-gradient(135deg, #3b82f6 0%, #00d4ff 100%) !important;
  font-weight: bold;
  letter-spacing: 1px;
  box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
  transition: all 0.3s ease;
}

.activate-camera-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
}

.close-camera-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  pointer-events: auto;
  background: rgba(0, 0, 0, 0.7) !important;
}

/* Responsive para el área de cámara */
@media (max-width: 960px) {
  .camera-area {
    padding: 1.5rem;
    max-width: 100%;
  }
  
  .camera-placeholder {
    min-height: 180px;
  }
}

@media (max-width: 600px) {
  .camera-area {
    padding: 1rem;
    max-width: 100%;
  }
  
  .camera-placeholder {
    min-height: 150px;
  }
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

/* Responsive general */
@media (max-width: 960px) {
  .recognition-container {
    padding: 0 1rem;
  }
  
  .recognition-card {
    margin: 1rem 0;
  }
  
  .camera-area {
    min-height: 180px;
  }
  
  /* Ajustar padding de la tarjeta en tablets */
  .recognition-card .v-card-text {
    padding: 1.5rem !important;
  }
}

@media (max-width: 600px) {
  .recognition-container {
    padding: 0 0.5rem;
  }
  
  .recognition-card {
    margin: 0.5rem 0;
  }
  
  .camera-area {
    min-height: 150px;
  }
  
  /* Ajustar padding de la tarjeta en móviles */
  .recognition-card .v-card-text {
    padding: 1rem !important;
  }
  
  /* Ajustar tamaños de texto en móviles */
  .text-h6 {
    font-size: 1.25rem !important;
  }
  
  .text-body-2 {
    font-size: 0.875rem !important;
  }
}

/* Asegurar que el contenedor principal sea responsive */
@media (max-width: 480px) {
  .recognition-container {
    min-height: 100vh;
    padding: 0 0.25rem;
  }
  
  .recognition-card {
    margin: 0.25rem 0;
    border-radius: 12px;
  }
  
  .camera-area {
    border-radius: 8px;
  }
}

/* Clases CSS personalizadas para Vuetify responsive */
.text-h5-md {
  font-size: 1.5rem !important;
}

.text-caption-md {
  font-size: 0.75rem !important;
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
.recognition-container {
  position: relative;
  z-index: 1;
}

/* Responsive para imágenes laterales */
@media (max-width: 960px) {
  .text-h5-md {
    font-size: 1.25rem !important;
  }
  
  .text-caption-md {
    font-size: 0.7rem !important;
  }
}

@media (max-width: 600px) {
  .text-h5-md {
    font-size: 1.125rem !important;
  }
  
  .text-caption-md {
    font-size: 0.65rem !important;
  }
}
</style>