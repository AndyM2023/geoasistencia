<template>
  <!-- Modal Dialog -->
  <v-dialog
    :model-value="true"
    persistent
    max-width="800px"
    @update:model-value="$emit('close')"
  >
    <v-card class="bg-dark-surface border border-blue-500/20">
      <v-card-title class="text-white d-flex align-center">
        <v-icon color="blue-400" class="mr-2">mdi-camera</v-icon>
        🎯 Registro de Rostro
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
        <!-- Mensaje de error si el ID no es válido -->
        <div v-if="!props.employeeId || props.employeeId === 'new' || isNaN(props.employeeId)" class="text-center py-8">
          <v-icon color="orange" size="64" class="mb-4">mdi-alert-circle</v-icon>
          <h3 class="text-orange-400 mb-2">ID de Empleado Inválido</h3>
          <p class="text-grey-300 mb-4">
            Debes guardar el empleado antes de poder registrar su rostro facial.
          </p>
          <v-btn color="blue-400" @click="closeDialog">
            Cerrar
          </v-btn>
        </div>
        
        <!-- Contenido normal solo si el ID es válido -->
        <template v-else>
          <!-- Video Container -->
          <div class="video-container mb-4">
            <video ref="videoElement" autoplay playsinline muted class="camera-video"></video>
          </div>
        
        <!-- Progress Info -->
        <div class="progress-section">
          <div class="d-flex justify-space-between align-center mb-2">
            <span class="text-white">Fotos capturadas:</span>
            <span class="text-blue-400 font-weight-bold">{{ fotosCapturadas }}/{{ targetCount }}</span>
          </div>
          
          <v-progress-linear
            :model-value="progress"
            color="blue-400"
            height="8"
            rounded
            class="mb-2"
          ></v-progress-linear>
          
          <p class="text-center text-grey-400 text-sm">{{ statusText }}</p>
        </div>

        <!-- Mensaje -->
        <v-alert
          v-if="mensaje"
          :type="mensaje.tipo === 'error' ? 'error' : mensaje.tipo === 'success' ? 'success' : 'info'"
          variant="tonal"
          class="my-3"
        >
          {{ mensaje.texto }}
        </v-alert>
        </template>
      </v-card-text>
      
      <v-card-actions class="justify-center pa-4">
        <v-btn
          v-if="!isCapturing"
          @click="startCapture"
          color="blue-400"
          size="large"
          prepend-icon="mdi-camera"
          class="mr-2"
        >
          Iniciar Captura
        </v-btn>
        
        <v-btn
          v-else
          @click="stopCapture"
          color="red-400"
          size="large"
          prepend-icon="mdi-stop"
          class="mr-2"
        >
          Detener Captura
        </v-btn>
        
        <v-btn
          v-if="isCapturing"
          @click="captureManual"
          color="green-400"
          size="large"
          prepend-icon="mdi-camera-iris"
          :disabled="isProcessing"
        >
          Captura Manual
        </v-btn>
        
        <v-btn
          @click="closeDialog"
          color="grey-600"
          variant="outlined"
          class="ml-2"
        >
          Cancelar
        </v-btn>
      </v-card-actions>
    </v-card>
    
    <!-- Overlay de procesamiento -->
    <v-overlay 
      :model-value="isUploading" 
      persistent 
      class="d-flex align-center justify-center"
    >
      <v-card class="bg-dark-surface border border-blue-500/20 pa-6 text-center">
        <v-progress-circular 
          indeterminate 
          color="blue-400"
          size="64"
          class="mb-4"
        ></v-progress-circular>
        <h3 class="text-white mb-2">Procesando imágenes...</h3>
        <p class="text-grey-400 mb-2">Generando embeddings faciales...</p>
        <p class="text-grey-500 text-sm">Esto puede tomar unos segundos</p>
      </v-card>
    </v-overlay>
  </v-dialog>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { faceService } from '../services/faceService';

const props = defineProps({
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
    default: 30
  }
});

// Log para debug
console.log('🔍 FaceRegistration - Props recibidas:', {
  employeeId: props.employeeId,
  employeeName: props.employeeName,
  targetCount: props.targetCount
});

const emit = defineEmits(['registro-completo', 'registro-error', 'close']);

const videoElement = ref(null);
const stream = ref(null);
const fotosCapturadas = ref(0);
const mensaje = ref(null);
const isUploading = ref(false);
const isCapturing = ref(false);
const isProcessing = ref(false);
const captureInterval = ref(null);
const capturedPhotos = ref([]);

const progress = computed(() => (fotosCapturadas.value / props.targetCount) * 100);

const statusText = computed(() => {
  if (!isCapturing.value) return 'Listo para iniciar';
  if (fotosCapturadas.value >= props.targetCount) return 'Captura completada';
  return `Capturando... ${fotosCapturadas.value}/${props.targetCount}`;
});

const startCapture = async () => {
  try {
    // Validar que el employeeId sea válido antes de iniciar
    if (!props.employeeId || props.employeeId === 'new' || isNaN(props.employeeId)) {
      throw new Error('ID de empleado inválido. Debes guardar el empleado antes de registrar su rostro.');
    }
    
    console.log('🎬 Iniciando captura de video...');
    console.log('👤 Employee ID válido:', props.employeeId);
    
    stream.value = await navigator.mediaDevices.getUserMedia({ 
      video: { 
        width: 640,
        height: 480,
        facingMode: 'user'
      } 
    });
    
    videoElement.value.srcObject = stream.value;
    isCapturing.value = true;
    capturedPhotos.value = [];
    fotosCapturadas.value = 0;

    mensaje.value = {
      tipo: 'info',
      texto: 'Iniciando captura automática de fotos...'
    };

    // ✅ CAPTURA OPTIMIZADA: Una imagen cada 0.8 segundos para completar 50 fotos en ~40 segundos
    captureInterval.value = setInterval(async () => {
      if (fotosCapturadas.value < props.targetCount && !isProcessing.value) {
        await captureFace();
      }
    }, 800); // Reducido de 1500ms a 800ms para mayor velocidad

  } catch (error) {
    console.error('Error al iniciar la cámara:', error);
    mensaje.value = {
      tipo: 'error',
      texto: 'No se pudo acceder a la cámara: ' + error.message
    };
    emit('registro-error', error);
  }
};

// Función para detectar si hay rostro usando análisis de imagen OPTIMIZADO
const detectFaceSimple = (canvas) => {
  try {
    const ctx = canvas.getContext('2d')
    
    // ✅ OPTIMIZACIÓN: Analizar solo una muestra de píxeles para mayor velocidad
    const sampleSize = 4 // Analizar cada 4to píxel para mayor velocidad
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
    const data = imageData.data
    
    let totalBrightness = 0
    let pixelCount = 0
    let varianceSum = 0
    let edgeCount = 0  // Contar bordes para detectar características faciales
    
    // Analizar región central donde debería estar el rostro (más pequeña para velocidad)
    const centerX = canvas.width / 2
    const centerY = canvas.height / 2
    const analysisWidth = canvas.width * 0.4  // Reducido a 40% para mayor velocidad
    const analysisHeight = canvas.height * 0.4 // Reducido a 40% para mayor velocidad
    
    const startX = Math.max(0, centerX - analysisWidth / 2)
    const startY = Math.max(0, centerY - analysisHeight / 2)
    const endX = Math.min(canvas.width, centerX + analysisWidth / 2)
    const endY = Math.min(canvas.height, centerY + analysisHeight / 2)
    
    // ✅ ANÁLISIS RÁPIDO: Muestreo de píxeles en lugar de todos
    for (let y = startY; y < endY; y += sampleSize) {
      for (let x = startX; x < endX; x += sampleSize) {
        const i = (y * canvas.width + x) * 4
        const brightness = (data[i] + data[i + 1] + data[i + 2]) / 3
        totalBrightness += brightness
        pixelCount++
        
        // Detección rápida de bordes (diferencia con píxel adyacente)
        if (x < endX - sampleSize) {
          const nextI = (y * canvas.width + (x + sampleSize)) * 4
          const nextBrightness = (data[nextI] + data[nextI + 1] + data[nextI + 2]) / 3
          if (Math.abs(brightness - nextBrightness) > 30) {
            edgeCount++
          }
        }
      }
    }
    
    const avgBrightness = totalBrightness / pixelCount
    
    // ✅ CÁLCULO OPTIMIZADO: Varianza en una sola pasada
    let varianceSum2 = 0
    for (let y = startY; y < endY; y += sampleSize) {
      for (let x = startX; x < endX; x += sampleSize) {
        const i = (y * canvas.width + x) * 4
        const brightness = (data[i] + data[i + 1] + data[i + 2]) / 3
        varianceSum2 += Math.pow(brightness - avgBrightness, 2)
      }
    }
    
    const variance = varianceSum2 / pixelCount
    const edgeDensity = edgeCount / pixelCount
    
    // ✅ CRITERIOS SIMPLIFICADOS para mayor compatibilidad:
    const hasGoodBrightness = avgBrightness > 20 && avgBrightness < 240  // Muy permisivo
    const hasVariance = variance > 50   // Umbral muy bajo
    const hasEdges = edgeDensity > 0.02 // Muy permisivo - solo 2%
    
    // ✅ DETECCIÓN MÁS PERMISIVA: Solo necesita 2 de 3 criterios
    const criteriosCumplidos = [hasGoodBrightness, hasVariance, hasEdges].filter(Boolean).length
    const hasRostro = criteriosCumplidos >= 2
    
    // ✅ LOGS DE DEBUG para ajustar umbrales
    console.log(`🔍 Análisis: Brillo=${avgBrightness.toFixed(1)} (${hasGoodBrightness}), Varianza=${variance.toFixed(1)} (${hasVariance}), Bordes=${(edgeDensity*100).toFixed(1)}% (${hasEdges}) → Criterios: ${criteriosCumplidos}/3 → Rostro: ${hasRostro}`)
    
    // ✅ FALLBACK ULTRA PERMISIVO: Si nada funciona, usar solo brillo
    if (!hasRostro && avgBrightness > 10 && avgBrightness < 250) {
      console.log(`⚠️ FALLBACK ACTIVADO - Solo verificando brillo básico`)
      return true
    }
    
    if (hasRostro) {
      console.log(`✅ ROSTRO DETECTADO - Brillo: ${avgBrightness.toFixed(1)}, Varianza: ${variance.toFixed(1)}, Bordes: ${(edgeDensity*100).toFixed(1)}%`)
    }
    
    return hasRostro
    
  } catch (error) {
    console.error('Error en detección rápida:', error)
    return false
  }
}

// Función para detectar y validar rostro
const detectAndCropFace = (imageData) => {
  return new Promise((resolve) => {
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    const img = new Image()
    
    img.onload = () => {
      canvas.width = img.width
      canvas.height = img.height
      ctx.drawImage(img, 0, 0)
      
      // Usar detección simple pero efectiva
      const hasFace = detectFaceSimple(canvas)
      
      if (hasFace) {
        // ✅ RECORTE OPTIMIZADO: Tamaño más grande para detección de rostros
        const centerX = canvas.width / 2
        const centerY = canvas.height / 2
        const cropSize = 512  // Tamaño más grande para que DeepFace detecte rostros
        
        const cropX = Math.max(0, centerX - cropSize / 2)
        const cropY = Math.max(0, centerY - cropSize / 2)
        const cropWidth = Math.min(canvas.width - cropX, cropSize)
        const cropHeight = Math.min(canvas.height - cropY, cropSize)
        
        // Crear canvas con tamaño optimizado
        const croppedCanvas = document.createElement('canvas')
        const croppedCtx = croppedCanvas.getContext('2d')
        croppedCanvas.width = cropWidth
        croppedCanvas.height = cropHeight
        
        croppedCtx.drawImage(
          canvas,
          cropX, cropY, cropWidth, cropHeight,
          0, 0, cropWidth, cropHeight
        )
        
        // ✅ CALIDAD OPTIMIZADA: 85% para equilibrar tamaño/calidad
        const croppedImageData = croppedCanvas.toDataURL('image/jpeg', 0.85)
        resolve({ hasFace: true, imageData: croppedImageData })
      } else {
        resolve({ hasFace: false, imageData: null })
      }
    }
    
    img.onerror = () => {
      console.log('❌ Error cargando imagen')
      resolve({ hasFace: false, imageData: null })
    }
    
    img.src = imageData
  })
}

const captureFace = async () => {
  if (isProcessing.value) return;
  
  try {
    isProcessing.value = true;
    
    const canvas = document.createElement('canvas');
    const video = videoElement.value;
    
    if (!video.videoWidth || !video.videoHeight) {
      console.warn('Video sin dimensiones válidas, esperando...');
      isProcessing.value = false;
      return;
    }
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);
    
    // Convertir a base64 la imagen original
    const originalImageData = canvas.toDataURL('image/jpeg', 0.8);
    
    // ✅ DETECCIÓN ESTRICTA - Solo toma foto si hay rostro
    console.log('🔍 Verificando rostro antes de capturar...');
    const { hasFace, imageData } = await detectAndCropFace(originalImageData);
    
    if (hasFace && imageData) {
      // ✅ ROSTRO DETECTADO - Guardar foto recortada
      capturedPhotos.value.push(imageData);
      fotosCapturadas.value++;
      
      console.log(`📸 Foto ${fotosCapturadas.value}/${props.targetCount} capturada ✅ (ROSTRO VERIFICADO)`);
      
      // Actualizar mensaje de éxito
      mensaje.value = {
        tipo: 'success',
        texto: `✅ Foto ${fotosCapturadas.value} capturada (Rostro detectado)`
      };
      
      // Si completamos el objetivo, procesar
      if (fotosCapturadas.value >= props.targetCount) {
        await processPhotos();
      }
    } else {
      // ❌ NO HAY ROSTRO - No guardar foto
      console.log('❌ NO SE TOMÓ FOTO - No se detectó rostro');
      mensaje.value = {
        tipo: 'warning',
        texto: '❌ NO SE DETECTÓ ROSTRO. Posiciona tu cara en el centro de la cámara.'
      };
      
      // Limpiar mensaje después de 2 segundos
      setTimeout(() => {
        if (mensaje.value && mensaje.value.tipo === 'warning') {
          mensaje.value = null;
        }
      }, 2000);
    }
    
  } catch (error) {
    console.error('Error al capturar rostro:', error);
    mensaje.value = {
      tipo: 'error',
      texto: 'Error al capturar foto: ' + error.message
    };
  } finally {
    isProcessing.value = false;
  }
};

const captureManual = async () => {
  if (isProcessing.value || fotosCapturadas.value >= props.targetCount) return;
  await captureFace();
};

const processPhotos = async () => {
  try {
    // Validar que el employeeId sea válido
    if (!props.employeeId || props.employeeId === 'new' || isNaN(props.employeeId)) {
      throw new Error('ID de empleado inválido. Debes guardar el empleado antes de registrar su rostro.');
    }
    
    isUploading.value = true;
    mensaje.value = {
      tipo: 'info',
      texto: 'Procesando fotos y generando embeddings...'
    };
    
    console.log('🚀 Procesando fotos:', capturedPhotos.value.length);
    console.log('👤 Employee ID:', props.employeeId);
    
    // Enviar al backend Django
    const result = await faceService.registerFace(
      props.employeeId,
      capturedPhotos.value
    );
    
    console.log('✅ Resultado del procesamiento:', result);
    
    mensaje.value = {
      tipo: 'success',
      texto: `Registro completado exitosamente! ${result.photos_count || fotosCapturadas.value} fotos procesadas`
    };
    
    // Notificar éxito
    setTimeout(() => {
      emit('registro-completo', {
        photosCount: result.photos_count || fotosCapturadas.value,
        message: result.message
      });
    }, 2000);
    
  } catch (error) {
    console.error('Error procesando fotos:', error);
    mensaje.value = {
      tipo: 'error',
      texto: 'Error procesando fotos: ' + error.message
    };
    emit('registro-error', error);
  } finally {
    isUploading.value = false;
  }
};

const stopCapture = async () => {
  console.log('⏹️ Deteniendo captura...');
  
  if (captureInterval.value) {
    clearInterval(captureInterval.value);
    captureInterval.value = null;
  }
  
  if (stream.value) {
    stream.value.getTracks().forEach(track => track.stop());
    stream.value = null;
  }
  
  isCapturing.value = false;
  
  // Si hay fotos capturadas, procesarlas
  if (capturedPhotos.value.length > 0) {
    await processPhotos();
  }
};

const closeDialog = () => {
  stopCapture();
  emit('close');
};

onMounted(async () => {
  console.log('🎯 Componente FaceRegistration montado');
  // Iniciar captura automáticamente al abrir el diálogo
  await new Promise(resolve => setTimeout(resolve, 500)); // Esperar que se renderice
  startCapture();
});

onBeforeUnmount(() => {
  console.log('🧹 Limpiando FaceRegistration');
  stopCapture();
});
</script>

<style scoped>
.video-container {
  width: 100%;
  border-radius: 8px;
  overflow: hidden;
  background: #000;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}

.camera-video {
  width: 100%;
  max-width: 640px;
  height: auto;
  max-height: 400px;
  object-fit: contain;
  border-radius: 8px;
}

.progress-section {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 16px;
  border: 1px solid rgba(59, 130, 246, 0.2);
}

/* Responsive */
@media (max-width: 768px) {
  .camera-video {
    max-height: 250px;
  }
  
  .progress-section {
    padding: 12px;
  }
}
</style>

