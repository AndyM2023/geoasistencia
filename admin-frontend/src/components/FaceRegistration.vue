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
    console.log('🎬 Iniciando captura de video...');
    
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

    // Captura una imagen cada 1.5 segundos
    captureInterval.value = setInterval(async () => {
      if (fotosCapturadas.value < props.targetCount && !isProcessing.value) {
        await captureFace();
      }
    }, 1500);

  } catch (error) {
    console.error('Error al iniciar la cámara:', error);
    mensaje.value = {
      tipo: 'error',
      texto: 'No se pudo acceder a la cámara: ' + error.message
    };
    emit('registro-error', error);
  }
};

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
    
    // Convertir a base64
    const base64 = canvas.toDataURL('image/jpeg', 0.8);
    capturedPhotos.value.push(base64);
    fotosCapturadas.value++;
    
    console.log(`📸 Foto ${fotosCapturadas.value}/${props.targetCount} capturada`);
    
    // Actualizar mensaje
    mensaje.value = {
      tipo: 'info',
      texto: `Foto ${fotosCapturadas.value} capturada correctamente`
    };
    
    // Si completamos el objetivo, procesar
    if (fotosCapturadas.value >= props.targetCount) {
      await processPhotos();
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
    isUploading.value = true;
    mensaje.value = {
      tipo: 'info',
      texto: 'Procesando fotos y generando embeddings...'
    };
    
    console.log('🚀 Procesando fotos:', capturedPhotos.value.length);
    
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

