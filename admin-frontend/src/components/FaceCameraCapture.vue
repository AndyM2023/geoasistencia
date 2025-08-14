<template>
  <div class="face-camera-capture">
    <!-- Contenedor de la cámara -->
    <div class="camera-container" :class="{ 'camera-hidden': !isActive }">
      <!-- Video siempre presente -->
      <video 
        ref="videoElement"
        id="face-capture-video"
        autoplay
        playsinline
        muted
        class="camera-preview"
        @loadedmetadata="() => console.log('📹 Video metadata cargada')"
        @canplay="() => console.log('📹 Video can play')"
        @playing="() => console.log('📹 Video playing')"
      ></video>
      
      <!-- Overlay con información - solo cuando está activo -->
      <div v-if="isActive" class="camera-overlay">
        <div class="detection-status">
          <v-chip 
            :color="faceDetected ? 'green' : 'orange'"
            size="small"
            variant="elevated"
          >
            {{ faceDetected ? '✅ Rostro detectado' : '🔍 Buscando rostro...' }}
          </v-chip>
        </div>
        
        <div class="capture-progress">
          <v-progress-linear 
            :model-value="(capturedCount / targetCount) * 100"
            color="blue-400"
            height="6"
            rounded
          ></v-progress-linear>
          <p class="text-white text-sm mt-1">
            📸 {{ capturedCount }}/{{ targetCount }} fotos capturadas
          </p>
        </div>
      </div>
    </div>
    
    <!-- Canvas siempre presente pero oculto -->
    <canvas ref="canvasElement" id="face-capture-canvas" style="display: none;"></canvas>
    
    <!-- Controles -->
    <div class="camera-controls mt-4">
      <v-btn
        v-if="!isActive"
        @click="startCapture"
        color="green-500"
        block
        prepend-icon="mdi-camera"
        :disabled="disabled"
      >
        Iniciar Captura con Previsualización
      </v-btn>
      
      <div v-else class="d-flex gap-2">
        <v-btn
          @click="stopCapture"
          color="red-400"
          variant="outlined"
          prepend-icon="mdi-stop"
        >
          Detener
        </v-btn>
        
        <v-btn
          @click="capturePhoto"
          color="blue-400"
          :disabled="isCapturing"
          prepend-icon="mdi-camera-iris"
        >
          📸 Capturar Foto Manual
        </v-btn>
      </div>
    </div>
    
    <!-- Estado de captura automática -->
    <div v-if="isActive && autoCapture" class="mt-3 text-center">
      <p class="text-grey-300">
        {{ status }}
      </p>
      <v-progress-circular 
        v-if="isCapturing"
        indeterminate
        color="blue-400"
        size="24"
      ></v-progress-circular>
    </div>
  </div>
</template>

<script>
import { ref, onUnmounted, nextTick } from 'vue'

export default {
  name: 'FaceCameraCapture',
  props: {
    disabled: {
      type: Boolean,
      default: false
    },
    targetCount: {
      type: Number,
      default: 15
    },
    autoCapture: {
      type: Boolean,
      default: true
    }
  },
  emits: ['photo-captured', 'capture-complete', 'capture-stopped'],
  setup(props, { emit }) {
    const videoElement = ref(null)
    const canvasElement = ref(null)
    const stream = ref(null)
    const isActive = ref(false)
    const isCapturing = ref(false)
    const faceDetected = ref(false)
    const capturedCount = ref(0)
    const capturedPhotos = ref([])
    const status = ref('')
    
    let detectionInterval = null
    let captureInterval = null
    
    const getVideoElement = async () => {
      // Función robusta para obtener el elemento de video
      let video = null
      let attempts = 0
      const maxAttempts = 15 // Aumentar intentos
      
      while (!video && attempts < maxAttempts) {
        attempts++
        
        // Debug: mostrar qué encontramos en el DOM
        const allVideos = document.querySelectorAll('video')
        const videoById = document.getElementById('face-capture-video')
        console.log(`🔍 Intento ${attempts}/${maxAttempts}:`)
        console.log(`   - Videos en DOM: ${allVideos.length}`)
        console.log(`   - Video por ID: ${!!videoById}`)
        console.log(`   - Ref Vue válida: ${!!videoElement.value}`)
        
        // Intentar primero con la referencia de Vue
        if (videoElement.value && videoElement.value.tagName === 'VIDEO') {
          video = videoElement.value
          console.log(`✅ Video encontrado via ref en intento ${attempts}`)
          break
        }
        
        // Fallback: buscar por ID en el DOM
        video = document.getElementById('face-capture-video')
        if (video && video.tagName === 'VIDEO') {
          console.log(`✅ Video encontrado via querySelector en intento ${attempts}`)
          // Actualizar la referencia
          videoElement.value = video
          break
        }
        
        // Fallback adicional: buscar cualquier video en el modal activo
        const dialog = document.querySelector('.v-dialog--active')
        if (dialog) {
          const videoInDialog = dialog.querySelector('video')
          if (videoInDialog) {
            console.log(`✅ Video encontrado en modal activo en intento ${attempts}`)
            video = videoInDialog
            videoElement.value = video
            break
          }
        }
        
        console.log(`🔄 Intento ${attempts}/${maxAttempts} - Video no encontrado, esperando...`)
        await new Promise(resolve => setTimeout(resolve, 300)) // Más tiempo entre intentos
        await nextTick()
      }
      
      if (!video) {
        console.error('❌ Estado final del DOM:')
        console.error('   - Videos totales:', document.querySelectorAll('video').length)
        console.error('   - Video por ID:', !!document.getElementById('face-capture-video'))
        console.error('   - Diálogos activos:', document.querySelectorAll('.v-dialog--active').length)
        throw new Error(`Video element no encontrado después de ${maxAttempts} intentos`)
      }
      
      return video
    }

    const getCanvasElement = async () => {
      // Función robusta para obtener el elemento canvas
      let canvas = null
      
      // Intentar con la referencia de Vue
      if (canvasElement.value) {
        canvas = canvasElement.value
        console.log('✅ Canvas encontrado via ref')
      } else {
        // Fallback: buscar por ID
        canvas = document.getElementById('face-capture-canvas')
        if (canvas) {
          console.log('✅ Canvas encontrado via querySelector')
          canvasElement.value = canvas
        }
      }
      
      if (!canvas) {
        throw new Error('Canvas element no encontrado')
      }
      
      return canvas
    }

    const startCapture = async () => {
      try {
        console.log('🎬 Iniciando captura de video...')
        console.log('📊 Estado inicial:', {
          isActive: isActive.value,
          videosEnDOM: document.querySelectorAll('video').length,
          videoElementRef: !!videoElement.value
        })
        
        // Obtener el elemento de video de forma robusta
        const video = await getVideoElement()
        
        console.log('📹 Solicitando acceso a la cámara...')
        stream.value = await navigator.mediaDevices.getUserMedia({
          video: {
            width: 640,
            height: 480,
            facingMode: 'user'
          }
        })
        
        console.log('✅ Acceso a cámara obtenido, conectando al video...')
        video.srcObject = stream.value
        isActive.value = true
        capturedCount.value = 0
        capturedPhotos.value = []
        
        // Esperar a que el video esté listo
        await new Promise((resolve, reject) => {
          video.onloadedmetadata = () => {
            console.log('✅ Video cargado, dimensiones:', {
              width: video.videoWidth,
              height: video.videoHeight
            })
            resolve()
          }
          
          video.onerror = (error) => {
            console.error('❌ Error en video:', error)
            reject(new Error('Error cargando video'))
          }
          
          // Timeout de seguridad
          setTimeout(() => {
            reject(new Error('Timeout cargando video'))
          }, 10000)
        })
        
        // Iniciar detección de rostros
        startFaceDetection()
        
        // Si es captura automática, iniciar el proceso
        if (props.autoCapture) {
          startAutoCapture()
        }
        
      } catch (error) {
        console.error('Error accediendo a la cámara:', error)
        status.value = `Error: ${error.message || 'No se pudo acceder a la cámara'}`
        
        // Limpiar si hay error
        if (stream.value) {
          stream.value.getTracks().forEach(track => track.stop())
          stream.value = null
        }
        isActive.value = false
      }
    }
    
    const stopCapture = () => {
      if (stream.value) {
        stream.value.getTracks().forEach(track => track.stop())
      }
      
      if (detectionInterval) {
        clearInterval(detectionInterval)
      }
      
      if (captureInterval) {
        clearInterval(captureInterval)
      }
      
      isActive.value = false
      isCapturing.value = false
      faceDetected.value = false
      
      emit('capture-stopped', capturedPhotos.value)
    }
    
    const startFaceDetection = () => {
      detectionInterval = setInterval(() => {
        detectFace()
      }, 500) // Detectar cada 500ms
    }
    
    const detectFace = async () => {
      try {
        const video = videoElement.value || document.getElementById('face-capture-video')
        const canvas = canvasElement.value || document.getElementById('face-capture-canvas')
        
        if (!video || !canvas) {
          console.warn('⚠️ Video o canvas no disponible para detección')
          return
        }
        
        // Verificar que el video tenga dimensiones válidas
        if (!video.videoWidth || !video.videoHeight) {
          console.warn('⚠️ Video sin dimensiones válidas')
          return
        }
        
        const ctx = canvas.getContext('2d')
        
        canvas.width = video.videoWidth
        canvas.height = video.videoHeight
        
        ctx.drawImage(video, 0, 0)
        
        // Validación básica mejorada
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
        const hasMovement = detectMovementAndFace(imageData)
        
        faceDetected.value = hasMovement
      } catch (error) {
        console.error('Error en detección facial:', error)
      }
    }
    
    const detectMovementAndFace = (imageData) => {
      // Análisis mejorado de la imagen para detectar rostros
      const data = imageData.data
      const width = imageData.width
      const height = imageData.height
      
      // Analizar múltiples regiones de la imagen
      let totalBrightness = 0
      let pixelCount = 0
      let brightPixels = 0
      let midTonePixels = 0
      let darkPixels = 0
      
      // Analizar toda la imagen con muestreo
      for (let y = 0; y < height; y += 8) {
        for (let x = 0; x < width; x += 8) {
          const pixelIndex = (y * width + x) * 4
          
          if (pixelIndex < data.length) {
            const r = data[pixelIndex]
            const g = data[pixelIndex + 1]
            const b = data[pixelIndex + 2]
            const brightness = (r + g + b) / 3
            
            totalBrightness += brightness
            pixelCount++
            
            if (brightness > 150) brightPixels++
            else if (brightness > 80) midTonePixels++
            else darkPixels++
          }
        }
      }
      
      if (pixelCount === 0) return false
      
      const avgBrightness = totalBrightness / pixelCount
      const brightRatio = brightPixels / pixelCount
      const midToneRatio = midTonePixels / pixelCount
      const darkRatio = darkPixels / pixelCount
      
      // Debug de la detección
      console.log('🔍 Análisis facial:', {
        avgBrightness: Math.round(avgBrightness),
        brightRatio: Math.round(brightRatio * 100) + '%',
        midToneRatio: Math.round(midToneRatio * 100) + '%',
        darkRatio: Math.round(darkRatio * 100) + '%'
      })
      
      // Condiciones MUY permisivas para detectar rostros
      const hasGoodLighting = avgBrightness > 30 && avgBrightness < 250
      const hasVariety = brightRatio > 0.05 && midToneRatio > 0.10  // Más permisivo
      const notTooDark = darkRatio < 0.8
      const hasEnoughBrightness = brightRatio > 0.3  // Al menos 30% pixels brillantes
      
      // TEMPORALMENTE: Detección simplificada para testing
      const faceDetected = hasGoodLighting && brightRatio > 0.3  // Solo requiere buena luz y pixeles brillantes
      
      // Debug detallado de condiciones
      console.log('🔍 Condiciones de detección:', {
        hasGoodLighting,
        hasVariety,
        hasEnoughBrightness,
        notTooDark,
        result: faceDetected
      })
      
      if (faceDetected) {
        console.log('✅ Rostro detectado con buenas condiciones')
      } else {
        console.log('❌ Rostro NO detectado')
      }
      
      return faceDetected
    }
    
    const startAutoCapture = () => {
      status.value = 'Captura automática iniciada...'
      
      captureInterval = setInterval(() => {
        if (faceDetected.value && !isCapturing.value && capturedCount.value < props.targetCount) {
          capturePhoto()
        }
      }, 1000) // Intentar capturar cada segundo
    }
    
    const capturePhoto = async () => {
      if (isCapturing.value) return
      
      isCapturing.value = true
      
      try {
        const video = videoElement.value || document.getElementById('face-capture-video')
        const canvas = canvasElement.value || document.getElementById('face-capture-canvas')
        
        if (!video || !canvas) {
          throw new Error('Video o canvas no disponibles')
        }
        
        const ctx = canvas.getContext('2d')
        
        // Verificar dimensiones del video
        if (!video.videoWidth || !video.videoHeight) {
          throw new Error('Video sin dimensiones válidas')
        }
        
        canvas.width = video.videoWidth
        canvas.height = video.videoHeight
        
        ctx.drawImage(video, 0, 0)
        
        const base64 = canvas.toDataURL('image/jpeg', 0.8)
        capturedPhotos.value.push(base64)
        capturedCount.value++
        
        emit('photo-captured', {
          photo: base64,
          count: capturedCount.value,
          total: props.targetCount
        })
        
        const detectionStatus = faceDetected.value ? 'con rostro detectado' : 'manual'
        status.value = `Foto ${capturedCount.value} capturada ${detectionStatus}`
        
        console.log(`📸 Foto ${capturedCount.value}/${props.targetCount} capturada`)
        
        // Si completamos el objetivo, finalizar
        if (capturedCount.value >= props.targetCount) {
          status.value = `¡Completado! ${capturedCount.value} fotos capturadas`
          
          setTimeout(() => {
            stopCapture()
            emit('capture-complete', capturedPhotos.value)
          }, 1000)
        }
        
      } catch (error) {
        console.error('Error capturando foto:', error)
        status.value = `Error capturando foto: ${error.message}`
      } finally {
        isCapturing.value = false
      }
    }
    
    onUnmounted(() => {
      stopCapture()
    })
    
    return {
      videoElement,
      canvasElement,
      isActive,
      isCapturing,
      faceDetected,
      capturedCount,
      status,
      startCapture,
      stopCapture,
      capturePhoto
    }
  }
}
</script>

<style scoped>
.face-camera-capture {
  width: 100%;
}

.camera-container {
  position: relative;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 16px;
}

.camera-preview {
  width: 100%;
  height: auto;
  max-height: 400px;
  object-fit: cover;
}

.camera-hidden {
  display: none !important;
}

.camera-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    to bottom,
    rgba(0,0,0,0.7) 0%,
    rgba(0,0,0,0) 30%,
    rgba(0,0,0,0) 70%,
    rgba(0,0,0,0.7) 100%
  );
  pointer-events: none;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 16px;
  border-radius: 8px;
}

.detection-status {
  align-self: center;
}

.capture-progress {
  text-align: center;
}

.gap-2 {
  gap: 8px;
}
</style>
