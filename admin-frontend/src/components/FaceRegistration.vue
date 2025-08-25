<template>
  <!-- Modal Dialog -->
  <v-dialog
    :model-value="showDialog"
    persistent
    max-width="800px"
    @update:model-value="$emit('close')"
  >
    <!-- Debug info -->
    <div style="display: none;">
      Debug: showDialog={{ showDialog }}, employeeId={{ employeeId }}, employeeName={{ employeeName }}
    </div>
    
    <v-card class="bg-dark-surface border border-blue-500/20">
      <v-card-title class="text-white d-flex align-center">
        <v-icon color="blue-400" class="mr-2">mdi-camera</v-icon>
        📷 Registro de Rostro - {{ displayEmployeeName }}
        <v-spacer></v-spacer>
        <v-btn 
          icon="mdi-close" 
          size="small" 
          color="grey-400" 
          variant="text"
          @click="closeDialog"
        ></v-btn>
      </v-card-title>
      
      <v-card-text>
        <!-- Video Container -->
        <div class="video-container mb-4">
          <video 
            ref="videoElement" 
            autoplay 
            playsinline 
            muted 
            class="camera-video"
            :class="{ 'capturing': isCapturing }"
            style="width: 100%; max-width: 640px; height: auto; max-height: 400px;"
          ></video>
          
          <!-- Status Overlay -->
          <div v-if="!isCapturing" class="camera-status-overlay">
            <v-icon color="orange" size="48" class="mb-2">mdi-camera-off</v-icon>
            <p class="text-orange-400 text-center mb-2">Cámara no iniciada</p>
            <v-btn
              @click="startCapture"
              color="blue-400"
              size="large"
              prepend-icon="mdi-camera"
            >
              Iniciar Cámara
            </v-btn>
          </div>
          
          <!-- Capture Progress -->
          <div v-if="isCapturing" class="capture-status-overlay">
            <div class="capture-indicator">
              <v-progress-circular
                :model-value="(fotosCapturadas / targetCount) * 100"
                :color="faceDetected ? 'green-400' : 'orange-400'"
                size="64"
                width="6"
                class="mb-2"
              >
                {{ fotosCapturadas }}/{{ targetCount }}
              </v-progress-circular>
              <p class="text-green-400 text-center">Capturando...</p>
              <div v-if="fotosCapturadas < targetCount" class="text-center">
                <v-icon 
                  :color="faceDetected ? 'green-400' : 'orange-400'" 
                  size="24" 
                  class="mb-1"
                >
                  {{ faceDetected ? 'mdi-face' : 'mdi-face-off' }}
                </v-icon>
                <p :class="faceDetected ? 'text-green-400' : 'text-orange-400'" class="text-sm">
                  {{ faceDetected ? 'Rostro detectado ✓' : 'Buscando rostro...' }}
                </p>
                <p v-if="!faceDetected" class="text-red-400 text-xs mt-1">
                  Solo rostros humanos, no objetos
                </p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Progress Info -->
        <div class="progress-section">
          <div class="d-flex justify-space-between align-center mb-2">
            <span class="text-white">Fotos capturadas:</span>
            <span class="text-blue-400 font-weight-bold">{{ fotosCapturadas }}/{{ targetCount }}</span>
          </div>
          
          <v-progress-linear
            :model-value="(fotosCapturadas / targetCount) * 100"
            color="blue-400"
            height="8"
            rounded
            class="mb-2"
          ></v-progress-linear>
          
          <p class="text-center text-grey-400 text-sm">
            {{ isProcessing ? 'Procesando fotos...' : isCapturing ? 'Capturando fotos...' : 'Listo para iniciar' }}
          </p>
        </div>

        <!-- Debug: Estado de procesamiento -->
        <!-- <div v-if="isProcessing" class="debug-processing mb-3">
          <v-alert type="info" variant="tonal" class="text-center">
            🔍 DEBUG: isProcessing = {{ isProcessing }} | Fotos: {{ fotosCapturadas }}/{{ targetCount }}
          </v-alert>
        </div> -->

        <!-- Mensaje -->
        <v-alert
          v-if="mensaje"
          :type="mensaje.tipo === 'error' ? 'error' : mensaje.tipo === 'success' ? 'success' : 'info'"
          variant="tonal"
          class="my-3"
        >
          {{ mensaje.texto }}
        </v-alert>

        <!-- Mensaje de Procesamiento Prominente -->
        <div v-if="isProcessing" class="processing-overlay">
          <div class="processing-content">
            <v-progress-circular
              indeterminate
              color="blue-400"
              size="60"
              width="6"
              class="mb-3"
            ></v-progress-circular>
            <h4 class="text-blue-400 text-h6 mb-2">Procesando Fotos</h4>
            <p class="text-grey-300 text-center text-sm">
              Procesando {{ fotosCapturadas }} fotos...
            </p>
            <div class="processing-steps mt-3">
              <div class="step">
                <v-icon color="green-400" size="16">mdi-check</v-icon>
                <span class="text-green-400 text-sm ml-2">{{ fotosCapturadas }}/{{ targetCount }} fotos</span>
              </div>
            </div>
          </div>
        </div>
      </v-card-text>
      
      <v-card-actions class="justify-center pa-4">
        <v-btn
          v-if="!isCapturing && !isProcessing"
          @click="startCapture"
          color="blue-400"
          size="large"
          prepend-icon="mdi-camera"
          class="mr-2"
        >
          Iniciar Captura
        </v-btn>
        
        <v-btn
          v-if="isCapturing && !isProcessing"
          @click="stopCapture"
          color="red-400"
          size="large"
          prepend-icon="mdi-stop"
          class="mr-2"
        >
          Detener Captura
        </v-btn>
        
        <v-btn
          v-if="isProcessing"
          color="blue-400"
          size="large"
          prepend-icon="mdi-loading"
          loading
          disabled
          class="mr-2"
        >
          Procesando...
        </v-btn>
        
        <v-btn
          @click="closeDialog"
          color="grey-600"
          variant="outlined"
          class="ml-2"
          :disabled="isProcessing"
        >
          Cancelar
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick, watch } from 'vue';
import { faceService } from '../services/faceService';
import { capitalizeFullName } from '../utils/nameUtils';

const props = defineProps({
  showDialog: {
    type: Boolean,
    default: false
  },
  employeeId: {
    type: [String, Number],
    required: true
  },
  employeeName: {
    type: String,
    required: true
  },
  targetCount: {
    type: Number,
    default: 15
  }
});

const emit = defineEmits(['registro-completo', 'registro-error', 'close']);

// Estado del componente
const isCapturing = ref(false);
const isProcessing = ref(false);
const fotosCapturadas = ref(0);
const capturedPhotos = ref([]);
const mensaje = ref(null);
const videoElement = ref(null);
const stream = ref(null);
const captureInterval = ref(null);
const faceDetected = ref(false);

// Computed para nombre capitalizado
const displayEmployeeName = computed(() => {
  return capitalizeFullNameString(props.employeeName);
});

// Función para detectar rostro en el video
const detectFace = async () => {
  try {
    if (!videoElement.value || !stream.value) return false;
    
    // Crear canvas para procesar el frame actual
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.width = videoElement.value.videoWidth || 640;
    canvas.height = videoElement.value.videoHeight || 480;
    
    context.drawImage(videoElement.value, 0, 0);
    
    // Usar la API de detección de rostros del navegador si está disponible
    if ('FaceDetector' in window) {
      try {
        const faceDetector = new FaceDetector({
          fastMode: true,
          maxDetectedFaces: 1
        });
        
        const faces = await faceDetector.detect(canvas);
        console.log('🔍 FaceDetector API - Rostros detectados:', faces.length);
        if (faces.length > 0) {
          console.log('✅ FaceDetector API confirmó rostro real');
          return true;
        }
      } catch (faceError) {
        console.warn('⚠️ FaceDetector API falló, usando fallback:', faceError);
      }
    }
    
    // Fallback más estricto: análisis de imagen más inteligente
    const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
    const data = imageData.data;
    
    // Verificar que la imagen no esté completamente oscura o borrosa
    let totalBrightness = 0;
    let pixelCount = 0;
    let hasVariation = false;
    let lastBrightness = -1;
    let skinTonePixels = 0;
    let totalPixels = 0;
    
    // Analizar cada píxel para detectar tonos de piel
    for (let i = 0; i < data.length; i += 4) {
      const r = data[i];
      const g = data[i + 1];
      const b = data[i + 2];
      
      totalPixels++;
      
      // Calcular brillo del píxel
      const brightness = (r + g + b) / 3;
      totalBrightness += brightness;
      pixelCount++;
      
      // Detectar tonos de piel (más flexible)
      // Los tonos de piel pueden variar mucho, ser más inclusivos
      if (
        // Criterio 1: R > G > B (típico de piel)
        (r > g && g > b) ||
        // Criterio 2: R y G altos, B bajo (piel clara)
        (r > 80 && g > 60 && b < 100) ||
        // Criterio 3: R muy alto, G y B moderados (piel más oscura)
        (r > 120 && g > 50 && b < 80) ||
        // Criterio 4: Rango general de tonos de piel
        (r > 70 && g > 50 && b < 110)
      ) {
        skinTonePixels++;
      }
      
      // Verificar variación entre píxeles consecutivos
      if (lastBrightness !== -1) {
        const variation = Math.abs(brightness - lastBrightness);
        if (variation > 30) {
          hasVariation = true;
        }
      }
      lastBrightness = brightness;
    }
    
    const averageBrightness = totalBrightness / pixelCount;
    const skinTonePercentage = (skinTonePixels / totalPixels) * 100;
    
    // Criterios más equilibrados para considerar que hay un rostro:
    // 1. Brillo promedio en rango razonable
    // 2. Variación suficiente entre píxeles (no borroso)
    // 3. Porcentaje razonable de tonos de piel
    // 4. Distribución de colores típica de rostro humano
    const hasGoodBrightness = averageBrightness > 50 && averageBrightness < 220; // Rango más amplio
    const hasGoodContrast = hasVariation;
    const hasSkinTones = skinTonePercentage > 5; // Reducido de 15% a 5%
    
    console.log('🔍 Análisis de imagen (EQUILIBRADO):', {
      averageBrightness: Math.round(averageBrightness),
      hasVariation,
      hasGoodBrightness,
      hasGoodContrast,
      skinTonePixels,
      skinTonePercentage: Math.round(skinTonePercentage * 100) / 100,
      hasSkinTones
    });
    
    // Solo retornar true si se cumplen los criterios principales
    const isFace = hasGoodBrightness && hasGoodContrast && hasSkinTones;
    
    if (isFace) {
      console.log('✅ Criterios equilibrados cumplidos - Probablemente es un rostro');
    } else {
      console.log('❌ Criterios equilibrados NO cumplidos - No es un rostro');
    }
    
    return isFace;
    
  } catch (error) {
    console.error('❌ Error en detección de rostro:', error);
    return false;
  }
};

// Función para iniciar captura
const startCapture = async () => {
  try {
    console.log('🎬 Iniciando captura...');
    
    // Verificar que el video esté disponible
    if (!videoElement.value) {
      console.error('❌ Video no disponible');
      mensaje.value = { tipo: 'error', texto: 'Video no disponible' };
      return;
    }
    
    // Solicitar acceso a la cámara
    stream.value = await navigator.mediaDevices.getUserMedia({
      video: { width: 640, height: 480, facingMode: 'user' }
    });
    
    // Asignar stream al video
    videoElement.value.srcObject = stream.value;
    
    // Esperar a que el video esté listo
    await new Promise((resolve) => {
      videoElement.value.onloadedmetadata = resolve;
    });
    
    isCapturing.value = true;
    fotosCapturadas.value = 0;
    capturedPhotos.value = [];
    mensaje.value = { tipo: 'success', texto: 'Cámara iniciada. Capturando fotos...' };
    
    // Iniciar captura automática
    startAutomaticCapture();
    
  } catch (error) {
    console.error('❌ Error iniciando cámara:', error);
    mensaje.value = { tipo: 'error', texto: `Error: ${error.message}` };
  }
};

// Función para captura automática
const startAutomaticCapture = () => {
  captureInterval.value = setInterval(async () => {
    if (fotosCapturadas.value < props.targetCount) {
      await captureFace();
    } else {
      stopCapture();
      // Procesar fotos
      await processPhotos();
    }
  }, 1000);
};

// Función para capturar una foto
const captureFace = async () => {
  try {
    if (!videoElement.value || !stream.value) return;
    
    // Verificar si hay un rostro antes de capturar
    const faceDetectedResult = await detectFace();
    faceDetected.value = faceDetectedResult;
    
    if (!faceDetectedResult) {
      console.log('⚠️ No se detectó rostro, saltando captura...');
      return;
    }
    
    console.log('✅ Rostro detectado, procediendo con captura...');
    
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.width = videoElement.value.videoWidth || 640;
    canvas.height = videoElement.value.videoHeight || 480;
    
    context.drawImage(videoElement.value, 0, 0);
    const photoData = canvas.toDataURL('image/jpeg', 0.9);
    
    capturedPhotos.value.push(photoData);
    fotosCapturadas.value++;
    
    console.log(`📸 Foto ${fotosCapturadas.value}/${props.targetCount} capturada (rostro detectado)`);
    
  } catch (error) {
    console.error('❌ Error capturando foto:', error);
  }
};

// Función para procesar fotos
const processPhotos = async () => {
  try {
    console.log('🔄 Iniciando procesamiento de fotos...');
    isProcessing.value = true;
    console.log('✅ isProcessing.value =', isProcessing.value);
    mensaje.value = { tipo: 'info', texto: 'Procesando fotos...' };
    
    const result = await faceService.registerFace(
      props.employeeId,
      capturedPhotos.value
    );
    
    mensaje.value = { tipo: 'success', texto: 'Registro completado exitosamente!' };
    
    emit('registro-completo', {
      photos_count: fotosCapturadas.value,
      photos: capturedPhotos.value
    });
    
  } catch (error) {
    console.error('❌ Error procesando fotos:', error);
    mensaje.value = { tipo: 'error', texto: `Error: ${error.message}` };
    emit('registro-error', error);
  } finally {
    console.log('🔄 Finalizando procesamiento...');
    isProcessing.value = false;
    console.log('✅ isProcessing.value =', isProcessing.value);
  }
};

// Función para detener captura
const stopCapture = () => {
  if (captureInterval.value) {
    clearInterval(captureInterval.value);
    captureInterval.value = null;
  }
  
  if (stream.value) {
    stream.value.getTracks().forEach(track => track.stop());
    stream.value = null;
  }
  
  isCapturing.value = false;
  mensaje.value = { tipo: 'info', texto: 'Captura detenida' };
};

// Función para cerrar diálogo
const closeDialog = () => {
  stopCapture();
  emit('close');
};

// Lifecycle hooks
onMounted(async () => {
  console.log('🎯 FaceRegistration montado');
  console.log('🔍 Props:', props);
  console.log('🔍 showDialog:', props.showDialog);
  console.log('🔍 employeeId:', props.employeeId);
  console.log('🔍 employeeName:', props.employeeName);
  
  // ✅ Inicializar inmediatamente si el modal ya está abierto
  if (props.showDialog) {
    console.log('✅ Modal ya está abierto, inicializando...');
    await initializeVideo();
  } else {
    console.log('⏳ Modal no está abierto, esperando...');
  }
});

// ✅ Función separada para inicializar video
const initializeVideo = async () => {
  try {
    console.log('🎬 Inicializando video...');
    
    // Esperar a que el DOM se actualice completamente
    await nextTick();
    await new Promise(resolve => setTimeout(resolve, 300));
    
    // ✅ VERIFICAR SI EL VIDEO ESTÁ DISPONIBLE
    if (videoElement.value) {
      console.log('✅ Video disponible, listo para usar');
      console.log('🔍 Video element:', videoElement.value);
      console.log('🔍 Video en DOM:', document.querySelector('video'));
    } else {
      console.log('⚠️ Video no disponible, esperando...');
      
      // Esperar más tiempo para que el DOM se estabilice
      await new Promise(resolve => setTimeout(resolve, 500));
      
      if (videoElement.value) {
        console.log('✅ Video disponible después de espera');
      } else {
        console.log('❌ Video no disponible, mostrando mensaje de error');
        console.log('🔍 Debug DOM:', {
          'videoElement.value': videoElement.value,
          'document.querySelector video': document.querySelector('video'),
          'document.querySelectorAll video': document.querySelectorAll('video'),
          'video container': document.querySelector('.video-container')
        });
        mensaje.value = {
          tipo: 'error',
          texto: 'Error: No se pudo inicializar el video. Cierre y abra nuevamente el modal.'
        };
      }
    }
  } catch (error) {
    console.error('❌ Error inicializando video:', error);
    mensaje.value = {
      tipo: 'error',
      texto: `Error inicializando video: ${error.message}`
    };
  }
};

// ✅ NUEVA ESTRATEGIA: Inicializar solo cuando el modal esté visible
watch(() => props.showDialog, async (newValue, oldValue) => {
  console.log('🔍 FaceRegistration - showDialog cambió:', { newValue, oldValue });
  
  if (newValue) {
    console.log('🎯 Modal abierto, inicializando video...');
    console.log('🔍 Props en watcher:', props);
    console.log('🔍 employeeId:', props.employeeId);
    console.log('🔍 employeeName:', props.employeeName);
    await initializeVideo();
  } else {
    console.log('🔒 Modal cerrado, limpiando estado...');
    // Limpiar estado cuando se cierra el modal
    if (stream.value) {
      stream.value.getTracks().forEach(track => track.stop());
      stream.value = null;
    }
    isCapturing.value = false;
    fotosCapturadas.value = 0;
    capturedPhotos.value = [];
    mensaje.value = null;
  }
}, { immediate: false });

onBeforeUnmount(() => {
  stopCapture();
});
</script>

<style scoped>
.video-container {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  background: #000;
}

.camera-video {
  border-radius: 8px;
  transition: all 0.3s ease-in-out;
  filter: brightness(1.2) contrast(1.1) saturate(1.05);
}

.camera-video.capturing {
  filter: brightness(1.5) contrast(1.4) saturate(1.2) hue-rotate(0deg);
  box-shadow: 0 0 30px rgba(59, 130, 246, 0.5);
  transform: scale(1.01);
  transition: all 0.3s ease-in-out;
}

.camera-status-overlay,
.capture-status-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 8px;
}

.capture-indicator {
  text-align: center;
  color: white;
}

.progress-section {
  margin-top: 20px;
}

.processing-overlay {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: auto;
  height: auto;
  background: rgba(0, 0, 0, 0.95);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  border-radius: 16px;
}

.processing-content {
  text-align: center;
  color: white;
  background: rgba(30, 41, 59, 0.98);
  padding: 25px;
  border-radius: 16px;
  border: 2px solid rgba(59, 130, 246, 0.5);
  box-shadow: 0 0 30px rgba(59, 130, 246, 0.4);
  max-width: 350px;
  backdrop-filter: blur(10px);
}

.processing-steps {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 15px;
}

.step {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 6px;
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.step .v-icon {
  margin-right: 8px;
}
</style>

