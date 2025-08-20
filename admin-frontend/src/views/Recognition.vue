<template>
  <AppBar />
  
  <!-- Sistema de notificaciones flotantes -->
  <div class="notifications-overlay">
    <!-- Notificación de error -->
    <transition name="slide-down">
      <v-alert
        v-if="error"
        type="error"
        variant="tonal"
        class="floating-notification error-notification"
        closable
        @click:close="error = ''"
        max-width="400"
      >
        <template v-slot:prepend>
          <v-icon>mdi-alert-circle</v-icon>
        </template>
        {{ error }}
      </v-alert>
    </transition>

    <!-- Notificación de éxito -->
    <transition name="slide-down">
      <v-alert
        v-if="success"
        type="success"
        variant="tonal"
        class="floating-notification success-notification"
        max-width="400"
      >
        <template v-slot:prepend>
          <v-icon>mdi-check-circle</v-icon>
        </template>
        {{ success }}
      </v-alert>
    </transition>

    <!-- Notificación de ubicación -->
    <transition name="slide-down">
      <v-alert
        v-if="locationStatus"
        type="info"
        variant="tonal"
        class="floating-notification location-notification"
        max-width="400"
        :icon="gettingLocation ? 'mdi-loading mdi-spin' : 'mdi-map-marker'"
      >
        <div class="d-flex align-center">
          <span v-if="gettingLocation" class="mr-2">
            <v-progress-circular indeterminate size="16" color="info"></v-progress-circular>
          </span>
          {{ locationStatus }}
        </div>
      </v-alert>
    </transition>
  </div>
  
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
            <h2 class="text-h6 text-h5-md font-weight-bold text-white mb-1 text-center">Reconocimiento Facial</h2>
            
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
                    
                    <!-- Mensaje de error si existe -->
                    <div v-if="error" class="camera-error-message mt-3">
                      <v-alert
                        type="error"
                        variant="tonal"
                        density="compact"
                        class="text-center"
                        max-width="300"
                      >
                        <template v-slot:prepend>
                          <v-icon>mdi-alert-circle</v-icon>
                        </template>
                        {{ error }}
                      </v-alert>
                    </div>
                    
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
                    
                    <!-- Botón de reinicio si hay error -->
                    <v-btn
                      v-if="error"
                      @click="resetCamera"
                      color="secondary"
                      size="small"
                      variant="outlined"
                      class="mt-2"
                      :loading="loading"
                    >
                      <v-icon left size="16" class="mr-1">mdi-refresh</v-icon>
                      Reintentar
                    </v-btn>
                  </div>
                  
                  <!-- Estado activo: Overlay de la cámara -->
                  <div v-else class="camera-overlay">
                    <div class="camera-controls">
                      <v-btn
                        icon
                        color="red"
                        size="small"
                        class="close-camera-btn"
                        @click.stop="stopCamera"
                        title="Cerrar cámara"
                      >
                        <v-icon>mdi-close</v-icon>
                      </v-btn>
                      
                      <v-btn
                        icon
                        color="blue"
                        size="small"
                        class="reset-camera-btn"
                        @click.stop="resetCamera"
                        title="Reiniciar cámara"
                      >
                        <v-icon>mdi-refresh</v-icon>
                      </v-btn>
                    </div>
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
                    @input="resetInactivityTimer"
                    @focus="resetInactivityTimer"
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
                    @input="resetInactivityTimer"
                    @focus="resetInactivityTimer"
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

                  <!-- Enlace para recuperar contraseña -->
                  <div class="text-center mb-4">
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

                <!-- Los mensajes ahora se muestran como overlays flotantes -->

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
                      <p class="mb-1">• Mantén una distancia de 30-50 cm</p>
                      <p class="mb-0">• Permite el acceso a tu ubicación GPS</p>
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
    const locationStatus = ref('') // Estado de la ubicación
    const gettingLocation = ref(false) // Estado de obtención de ubicación
    
    // Variables para controlar el estado de validación de los campos
    const fieldsInSuccessMode = ref(false) // Indica si los campos están en modo éxito
    const inactivityTimer = ref(null) // Timer para volver al estado normal
    
    // Variables de la cámara
    const isCameraActive = ref(false)
    const videoElement = ref(null)
    const stream = ref(null)

    // Reglas de validación dinámicas
    const rules = {
      required: v => {
        // Si estamos en modo éxito, no mostrar validación roja
        if (fieldsInSuccessMode.value) {
          return true
        }
        return !!v || 'Este campo es requerido'
      }
    }

    // Función para alternar visibilidad de contraseña
    const togglePassword = () => {
      showPassword.value = !showPassword.value
    }

    // Función para activar modo éxito en los campos
    const activateSuccessMode = () => {
      fieldsInSuccessMode.value = true
      console.log('✅ Campos activados en modo éxito (sin validación roja)')
      
      // Limpiar timer anterior si existe
      if (inactivityTimer.value) {
        clearTimeout(inactivityTimer.value)
      }
      
      // Configurar timer de 5 segundos para volver al estado normal
      inactivityTimer.value = setTimeout(() => {
        fieldsInSuccessMode.value = false
        console.log('🔄 Campos regresaron al estado normal después de 5 segundos de inactividad')
      }, 5000)
    }

    // Función para resetear el timer de inactividad
    const resetInactivityTimer = () => {
      if (inactivityTimer.value) {
        clearTimeout(inactivityTimer.value)
      }
      
      // Solo resetear si estamos en modo éxito
      if (fieldsInSuccessMode.value) {
        inactivityTimer.value = setTimeout(() => {
          fieldsInSuccessMode.value = false
          console.log('🔄 Campos regresaron al estado normal después de 5 segundos de inactividad')
        }, 5000)
      }
    }

    // Función principal de reconocimiento
    const handleRecognition = async () => {
      loading.value = true
      error.value = ''
      success.value = ''
      locationStatus.value = ''
      gettingLocation.value = false

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

        // Obtener ubicación actual del usuario
        console.log('📍 Obteniendo ubicación del usuario...')
        gettingLocation.value = true
        locationStatus.value = '📍 Obteniendo tu ubicación GPS...'
        
        let location
        try {
          location = await getCurrentLocation()
          console.log('✅ Ubicación obtenida:', location)
          gettingLocation.value = false
          
          // Auto-ocultar notificación de ubicación después de 6 segundos
          setTimeout(() => {
            locationStatus.value = ''
          }, 6000)
          
        } catch (locationError) {
          console.error('❌ Error obteniendo ubicación:', locationError)
          gettingLocation.value = false
          locationStatus.value = ''
          error.value = locationError.message
          return
        }

        // Verificar rostro y marcar asistencia
        const result = await verifyFaceAndMarkAttendance(
          employeeData.employee_id,
          photoBase64,
          employeeData.area_id,
          location
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
            const distanceInfo = result.location_info?.distance_meters ? 
              ` (a ${result.location_info.distance_meters}m del centro del área)` : ''
            success.value = `✅ ENTRADA registrada exitosamente para ${attendanceData.employee_name}${distanceInfo}`
          } else if (attendanceData.action_type === 'salida') {
            console.log('⏰ Procesando SALIDA')
            const distanceInfo = result.location_info?.distance_meters ? 
              ` (a ${result.location_info.distance_meters}m del centro del área)` : ''
            success.value = `⏰ SALIDA registrada exitosamente para ${attendanceData.employee_name}${distanceInfo}`
          } else if (attendanceData.action_type === 'completo') {
            console.log('ℹ️ Procesando COMPLETO')
            success.value = `ℹ️ ${attendanceData.employee_name} ya tiene entrada y salida registradas para hoy`
          } else {
            console.log('❓ ACTION_TYPE no reconocido, usando mensaje genérico')
            success.value = `¡Asistencia registrada exitosamente! Rostro verificado con ${Math.round(result.confidence * 100)}% de confianza`
          }
          
          // Activar modo éxito en los campos (sin validación roja)
          activateSuccessMode()
          
          // Limpiar formulario
          form.username = ''
          form.password = ''
          
          // Detener cámara
          await stopCamera()
          
          // Auto-ocultar notificación de éxito después de 8 segundos
          setTimeout(() => {
            success.value = ''
          }, 8000)
        } else {
          // Manejar errores del backend con mensajes personalizados
          if (result.action_type === 'completo') {
            // Caso especial: ya tiene entrada y salida (no es realmente un error)
            success.value = `ℹ️ ${result.message}`
            // Activar modo éxito en los campos para este caso también
            activateSuccessMode()
            setTimeout(() => {
              success.value = ''
            }, 8000)
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
            // Activar modo éxito en los campos para este caso también
            activateSuccessMode()
            setTimeout(() => {
              success.value = ''
            }, 8000)
          } else if (backendResponse.error_type === 'location_out_of_range') {
            // Error de ubicación fuera del área
            error.value = `📍 ${backendResponse.message}`
            console.log('📍 Error de ubicación:', {
              distance: backendResponse.distance_meters,
              areaRadius: backendResponse.area_radius,
              areaName: backendResponse.area_name
            })
          } else if (backendResponse.error_type === 'location_not_available') {
            // Error de ubicación no disponible
            error.value = `📍 ${backendResponse.message}`
          } else if (backendResponse.error_type === 'wrong_area_assignment') {
            // Error de área incorrecta
            error.value = `🏢 ${backendResponse.message}`
          } else if (backendResponse.error_type === 'area_inactive') {
            // Error de área inactiva
            error.value = `🏢 ${backendResponse.message}`
          } else if (backendResponse.error_type === 'invalid_coordinates') {
            // Error de coordenadas inválidas
            error.value = `📍 ${backendResponse.message}`
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
        
        // IMPORTANTE: Hacer visible el video ANTES de acceder a la cámara
        // Esto evita el error "Starting videoinput failed"
        videoElement.value.style.display = 'block'
        
        // Pequeña pausa para asegurar que el DOM se actualice
        await new Promise(resolve => setTimeout(resolve, 100))
        
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
            console.log('📹 Video metadata cargado')
            resolve()
          }
        })
        
        // Activar la cámara
        isCameraActive.value = true
        console.log('🎯 Cámara activada exitosamente')
        
        // Limpiar errores previos si la cámara se activó correctamente
        if (error.value) {
          error.value = ''
        }
        
      } catch (err) {
        console.error('❌ Error iniciando cámara:', err)
        error.value = 'Error al acceder a la cámara: ' + err.message
        
        // Ocultar el video en caso de error
        if (videoElement.value) {
          videoElement.value.style.display = 'none'
        }
        
        // Mostrar errores específicos
        if (err.name === 'NotAllowedError') {
          error.value = 'Permiso denegado para acceder a la cámara. Verifica los permisos del navegador.'
        } else if (err.name === 'NotFoundError') {
          error.value = 'No se encontró ninguna cámara en tu dispositivo.'
        } else if (err.name === 'NotReadableError') {
          error.value = 'La cámara está siendo usada por otra aplicación.'
        } else if (err.name === 'DOMException' && err.message.includes('Starting videoinput failed')) {
          error.value = 'Error al iniciar la entrada de video. Intenta recargar la página.'
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
          // Ocultar el video después de detener la cámara
          videoElement.value.style.display = 'none'
        }
        
        isCameraActive.value = false
        console.log('✅ Cámara detenida exitosamente')
        
      } catch (err) {
        console.error('❌ Error deteniendo cámara:', err)
        // Asegurar que el estado se resetee incluso si hay error
        isCameraActive.value = false
        if (videoElement.value) {
          videoElement.value.style.display = 'none'
        }
      }
    }

    // Función para reiniciar la cámara en caso de problemas
    const resetCamera = async () => {
      try {
        console.log('🔄 Reiniciando cámara...')
        
        // Detener cámara actual
        await stopCamera()
        
        // Pequeña pausa para asegurar limpieza
        await new Promise(resolve => setTimeout(resolve, 500))
        
        // Intentar iniciar de nuevo
        await startCamera()
        
        console.log('✅ Cámara reiniciada exitosamente')
        
      } catch (err) {
        console.error('❌ Error reiniciando cámara:', err)
        error.value = 'Error al reiniciar la cámara: ' + err.message
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





    // Función para obtener ubicación actual del navegador
    const getCurrentLocation = () => {
      return new Promise((resolve, reject) => {
        // Verificar si el navegador soporta geolocalización
        if (!navigator.geolocation) {
          reject(new Error('Tu navegador no soporta geolocalización. Usa un navegador más moderno.'))
          return
        }

        // Verificar permisos de ubicación primero
        if (navigator.permissions && navigator.permissions.query) {
          navigator.permissions.query({ name: 'geolocation' }).then((permissionStatus) => {
            console.log('🔐 Estado del permiso de ubicación:', permissionStatus.state)
            
            if (permissionStatus.state === 'denied') {
              reject(new Error('Acceso a ubicación denegado. Permite el acceso a la ubicación en tu navegador para marcar asistencia.'))
              return
            }
            
            // Si el permiso está otorgado o es prompt, continuar
            requestLocation()
          }).catch(() => {
            // Si no se puede verificar permisos, continuar directamente
            requestLocation()
          })
        } else {
          // Navegadores que no soportan permissions API
          requestLocation()
        }

        function requestLocation() {
          // Opciones para obtener ubicación precisa
          const options = {
            enableHighAccuracy: true,  // Máxima precisión
            timeout: 15000,           // 15 segundos de timeout
            maximumAge: 0             // No usar ubicación en caché
          }

          console.log('📍 Solicitando ubicación GPS...')
          
          // Obtener ubicación actual
          navigator.geolocation.getCurrentPosition(
            (position) => {
              console.log('✅ Ubicación obtenida exitosamente:')
              console.log(`   - Latitud: ${position.coords.latitude}`)
              console.log(`   - Longitud: ${position.coords.longitude}`)
              console.log(`   - Precisión: ${position.coords.accuracy} metros`)
              console.log(`   - Timestamp: ${new Date(position.timestamp).toLocaleString()}`)
              
              // Mostrar estado exitoso con coordenadas
              locationStatus.value = `📍 Ubicación obtenida: ${position.coords.latitude.toFixed(6)}, ${position.coords.longitude.toFixed(6)} (Precisión: ${Math.round(position.coords.accuracy)}m)`
              
              resolve({
                latitude: position.coords.latitude,
                longitude: position.coords.longitude,
                accuracy: position.coords.accuracy,
                timestamp: position.timestamp
              })
            },
            (error) => {
              console.error('❌ Error obteniendo ubicación:', error)
              console.log('   - Error code:', error.code)
              console.log('   - Error message:', error.message)
              
              // Mensajes de error personalizados según el tipo
              let errorMessage = 'Error obteniendo ubicación'
              switch (error.code) {
                case error.PERMISSION_DENIED:
                  errorMessage = 'Acceso a ubicación denegado. Permite el acceso a la ubicación en tu navegador para marcar asistencia.'
                  break
                case error.POSITION_UNAVAILABLE:
                  errorMessage = 'Ubicación no disponible. Verifica que tu GPS esté activado.'
                  break
                case error.TIMEOUT:
                  errorMessage = 'Tiempo de espera agotado. Intenta nuevamente en un área con mejor señal GPS.'
                  break
                default:
                  errorMessage = `Error de ubicación: ${error.message}`
              }
              
              reject(new Error(errorMessage))
            },
            options
          )
        }
      })
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

    // Lifecycle: Cleanup al desmontar
    onUnmounted(() => {
      // Limpiar timer de inactividad
      if (inactivityTimer.value) {
        clearTimeout(inactivityTimer.value)
      }
      
      // Limpiar cámara
      if (stream.value) {
        stream.value.getTracks().forEach(track => track.stop())
      }
      if (videoElement.value) {
        videoElement.value.style.display = 'none'
        videoElement.value.srcObject = null
      }
      isCameraActive.value = false
    })

    // Función para ir a recuperar contraseña
    const goToForgotPassword = () => {
      router.push('/employee/forgot-password')
    }

    return {
      // Variables del formulario
      form,
      showPassword,
      loading,
      error,
      success,
      locationStatus,
      gettingLocation,
      
      // Variables de la cámara
      isCameraActive,
      videoElement,
      
      // Variables de validación
      fieldsInSuccessMode,
      
      // Reglas de validación
      rules,
      
      // Métodos
      togglePassword,
      handleRecognition,
      startCamera,
      stopCamera,
      resetCamera,
      goToForgotPassword,
      
      // Funciones de validación
      activateSuccessMode,
      resetInactivityTimer
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

/* Responsive para imágenes laterales - Solución mejorada */
@media (max-width: 1400px) {
  .side-image {
    width: 250px;
    height: 250px;
  }
  
  .left-image {
    left: 30px;
  }
  
  .right-image {
    right: 30px;
  }
  
  /* Ajustar botones en pantallas grandes */
  .activate-camera-btn,
  .recognition-btn {
    font-size: 0.9rem !important;
    padding: 10px 20px !important;
  }
}

@media (max-width: 1200px) {
  .side-image {
    width: 200px;
    height: 200px;
  }
  
  .left-image {
    left: 20px;
  }
  
  .right-image {
    right: 20px;
  }
}

@media (max-width: 1000px) {
  .side-image {
    width: 160px;
    height: 160px;
  }
  
  .left-image {
    left: 15px;
  }
  
  .right-image {
    right: 15px;
  }
}

@media (max-width: 900px) {
  .side-image {
    width: 120px;
    height: 120px;
  }
  
  .left-image {
    left: 10px;
  }
  
  .right-image {
    right: 10px;
  }
}

@media (max-width: 800px) {
  .side-image {
    width: 100px;
    height: 100px;
  }
  
  .left-image {
    left: 5px;
  }
  
  .right-image {
    right: 5px;
  }
}

.recognition-card {
  background: rgba(30, 41, 59, 0.8) !important;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 16px;
  max-width: 700px;
  width: 100%;
  margin-top: 10px;
  transition: all 0.3s ease;
}

/* Responsive para la tarjeta principal */
@media (max-width: 1200px) {
  .recognition-card {
    max-width: 600px;
    margin-top: 25px;
  }
}

@media (max-width: 1000px) {
  .recognition-card {
    max-width: 550px;
    margin-top: 20px;
  }
}

@media (max-width: 900px) {
  .recognition-card {
    max-width: 500px;
    margin-top: 15px;
  }
}

@media (max-width: 800px) {
  .recognition-card {
    max-width: 450px;
    margin-top: 10px;
  }
}

@media (max-width: 768px) {
  .recognition-card {
    max-width: 95%;
    margin-top: 15px;
    margin-left: 2.5%;
    margin-right: 2.5%;
  }
}

@media (max-width: 600px) {
  .recognition-card {
    max-width: 98%;
    margin-top: 10px;
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
  min-height: 280px;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
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
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 1rem;
}

.camera-error-message {
  width: 100%;
  max-width: 300px;
  margin-top: 10px;
}

.camera-error-message .v-alert {
  border-radius: 8px;
  font-size: 0.875rem;
}

.camera-error-message .v-alert__content {
  padding: 8px 12px;
}

.activate-camera-btn {
  background: linear-gradient(135deg, #3b82f6 0%, #00d4ff 100%) !important;
  font-weight: bold;
  letter-spacing: 1px;
  box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
  transition: all 0.3s ease;
  white-space: nowrap;
  overflow: visible;
  text-overflow: clip;
  min-width: fit-content;
  width: auto;
  max-width: none;
  height: auto;
  line-height: 1.2;
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

/* Controles de la cámara */
.camera-controls {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  gap: 8px;
  pointer-events: auto;
}

.reset-camera-btn {
  background: rgba(0, 0, 0, 0.7) !important;
  transition: all 0.3s ease;
}

.reset-camera-btn:hover {
  background: rgba(0, 0, 0, 0.9) !important;
  transform: scale(1.1);
}

.close-camera-btn:hover {
  background: rgba(0, 0, 0, 0.9) !important;
  transform: scale(1.1);
}

/* Responsive para el área de cámara */
@media (max-width: 1200px) {
  .activate-camera-btn {
    font-size: 0.875rem !important;
    padding: 8px 16px !important;
    min-width: fit-content !important;
  }
  
  .recognition-btn {
    font-size: 0.875rem !important;
    padding: 8px 16px !important;
  }
  
  .camera-area {
    min-height: 260px;
  }
}

@media (max-width: 1000px) {
  .activate-camera-btn {
    font-size: 0.8rem !important;
    padding: 6px 12px !important;
    min-width: fit-content !important;
  }
  
  .recognition-btn {
    font-size: 0.8rem !important;
    padding: 6px 12px !important;
  }
  
  .camera-area {
    min-height: 250px;
  }
}

@media (max-width: 960px) {
  .camera-area {
    padding: 1.5rem;
    max-width: 100%;
    min-height: 240px;
  }
  
  .camera-placeholder {
    min-height: 180px;
  }
  
  .activate-camera-btn {
    font-size: 0.75rem !important;
    padding: 6px 10px !important;
    min-width: fit-content !important;
  }
  
  .recognition-btn {
    font-size: 0.75rem !important;
    padding: 6px 10px !important;
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
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  min-width: 0;
  width: auto;
  max-width: 100%;
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
@media (max-width: 1200px) {
  .recognition-container {
    padding: 0 280px; /* Espacio para las imágenes de 250px + margen */
  }
}

@media (max-width: 1000px) {
  .recognition-container {
    padding: 0 200px; /* Espacio para las imágenes de 160px + margen */
  }
}

@media (max-width: 900px) {
  .recognition-container {
    padding: 0 150px; /* Espacio para las imágenes de 120px + margen */
  }
}

@media (max-width: 800px) {
  .recognition-container {
    padding: 0 120px; /* Espacio para las imágenes de 100px + margen */
  }
}

@media (max-width: 768px) {
  .recognition-container {
    padding: 0 1rem; /* En tablets y móviles las imágenes se ocultan */
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
    min-height: 220px;
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
  
  /* Botones en móviles */
  .activate-camera-btn {
    font-size: 0.7rem !important;
    padding: 4px 8px !important;
    min-width: fit-content !important;
  }
  
  .recognition-btn {
    font-size: 0.7rem !important;
    padding: 4px 8px !important;
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
    min-height: 200px;
  }
  
  /* Botones en pantallas muy pequeñas */
  .activate-camera-btn {
    font-size: 0.65rem !important;
    padding: 3px 6px !important;
    min-width: fit-content !important;
  }
  
  .recognition-btn {
    font-size: 0.65rem !important;
    padding: 3px 6px !important;
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

/* Estilos para el enlace de recuperar contraseña */
.forgot-password-link {
  font-size: 0.875rem !important;
  text-decoration: none !important;
  transition: all 0.3s ease !important;
}

.forgot-password-link:hover {
  color: #00d4ff !important;
  transform: translateY(-1px) !important;
}

/* Responsive para el enlace de recuperar contraseña */
@media (max-width: 600px) {
  .forgot-password-link {
    font-size: 0.8rem !important;
  }
}

/* Estilos para el botón de verificación de radio */
.verify-radius-btn {
  width: 28px !important;
  height: 28px !important;
  border-radius: 50% !important;
  min-width: 28px !important;
  max-width: 28px !important;
}

/* Estilos para campos en modo éxito */
.recognition-form .v-text-field.v-input--density-compact.v-text-field--variant-outlined.v-field--focused.v-field--variant-outlined.v-field--focused .v-field__outline {
  border-color: #4ade80 !important; /* Verde para indicar éxito */
}

.recognition-form .v-text-field.v-input--density-compact.v-text-field--variant-outlined.v-field--variant-outlined .v-field__outline {
  border-color: #4ade80 !important; /* Verde para indicar éxito cuando están en modo éxito */
}

/* Transición suave para el cambio de color */
.recognition-form .v-text-field .v-field__outline {
  transition: border-color 0.3s ease;
}

/* Sistema de notificaciones flotantes */
.notifications-overlay {
  position: fixed;
  top: 80px; /* Debajo del AppBar */
  left: 50%;
  transform: translateX(-50%);
  z-index: 1001;
  pointer-events: none; /* Permite que los clics pasen a través del overlay */
}

.floating-notification {
  pointer-events: auto; /* Restaura los clics en la notificación */
  margin-bottom: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: white !important;
}

.floating-notification * {
  color: white !important;
}

.floating-notification .v-alert__content,
.floating-notification .v-alert__title,
.floating-notification .v-alert__body {
  color: white !important;
}

.floating-notification .v-icon,
.floating-notification .v-btn__content .v-icon {
  color: white !important;
}

.floating-notification .v-progress-circular {
  color: white !important;
}

/* Asegurar que los botones de cerrar sean visibles */
.floating-notification .v-btn--icon {
  color: white !important;
}

.floating-notification .v-btn--icon:hover {
  background-color: rgba(255, 255, 255, 0.1) !important;
}

/* Estilos específicos para cada tipo de notificación */
.error-notification {
  background: #dc2626 !important; /* Rojo sólido más visible */
  border-color: #b91c1c !important;
}

.success-notification {
  background: #16a34a !important; /* Verde sólido más visible */
  border-color: #15803d !important;
}

.location-notification {
  background: #2563eb !important; /* Azul sólido más visible */
  border-color: #1d4ed8 !important;
}

/* Asegurar que los mensajes de error específicos sean visibles */
.error-notification .v-alert__content,
.error-notification .v-alert__body {
  font-weight: 500 !important;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3) !important;
}

/* Mejorar la legibilidad del texto en todas las notificaciones */
.floating-notification .v-alert__content {
  font-weight: 500 !important;
  line-height: 1.4 !important;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2) !important;
}

/* Animaciones de entrada y salida */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-down-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(-20px);
}

.slide-down-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-20px);
}

.slide-down-enter-to,
.slide-down-leave-from {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}

/* Responsive para notificaciones */
@media (max-width: 600px) {
  .notifications-overlay {
    top: 70px;
    left: 20px;
    right: 20px;
    transform: none;
  }
  
  .floating-notification {
    max-width: none !important;
    width: 100%;
  }
  
  .slide-down-enter-from,
  .slide-down-leave-to {
    transform: translateY(-20px);
  }
  
  .slide-down-enter-to,
  .slide-down-leave-from {
    transform: translateY(0);
  }
}
</style>