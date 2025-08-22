<template>
  <div class="face-capture-container">
    <!-- Área de la cámara -->
    <div class="camera-area" :class="{ 'active': isCameraActive }">
      <video 
        v-if="isCameraActive" 
        ref="videoElement" 
        autoplay 
        playsinline 
        muted
        class="camera-video"
      ></video>
      
      <div v-else class="camera-placeholder">
        <v-icon size="64" color="grey-400">mdi-camera</v-icon>
        <p class="camera-text">Click para activar cámara</p>
      </div>
      
      <!-- Botón para activar cámara -->
      <v-btn
        v-if="!isCameraActive"
        @click="startCamera"
        color="blue-500"
        size="large"
        block
        class="camera-button"
      >
        Activar Cámara
      </v-btn>
      
      <!-- Botón para capturar -->
      <v-btn
        v-if="isCameraActive && !isProcessing"
        @click="capturePhoto"
        color="green-500"
        size="large"
        block
        class="capture-button"
      >
        📸 Capturar Rostro
      </v-btn>
      
      <!-- Botón para detener cámara -->
      <v-btn
        v-if="isCameraActive"
        @click="stopCamera"
        color="red-500"
        size="small"
        variant="outlined"
        class="stop-button"
      >
        ⏹️ Detener
      </v-btn>
    </div>
    
    <!-- Estado de la captura -->
    <div v-if="captureStatus" class="capture-status">
      <v-alert
        :type="captureStatus.type"
        :title="captureStatus.title"
        :text="captureStatus.message"
        variant="tonal"
      ></v-alert>
    </div>
    
    <!-- Overlay de procesamiento -->
    <div v-if="isProcessing" class="processing-overlay">
      <v-progress-circular
        indeterminate
        color="blue-500"
        size="64"
      ></v-progress-circular>
      <p class="processing-text">{{ processingText }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onBeforeUnmount } from 'vue';

const props = defineProps({
  onPhotoCaptured: {
    type: Function,
    required: true
  }
});

const emit = defineEmits(['photo-captured', 'error']);

const videoElement = ref(null);
const isCameraActive = ref(false);
const isProcessing = ref(false);
const processingText = ref('');
const stream = ref(null);
const captureStatus = ref(null);

const startCamera = async () => {
  try {
    processingText.value = 'Iniciando cámara...';
    isProcessing.value = true;
    
    stream.value = await navigator.mediaDevices.getUserMedia({
      video: {
        width: 640,
        height: 480,
        facingMode: 'user'
      }
    });
    
    if (videoElement.value) {
      videoElement.value.srcObject = stream.value;
      isCameraActive.value = true;
      
      captureStatus.value = {
        type: 'success',
        title: 'Cámara activada',
        message: 'Posiciona tu rostro en el centro y haz clic en "Capturar Rostro"'
      };
    }
    
  } catch (error) {
    console.error('Error iniciando cámara:', error);
    captureStatus.value = {
      type: 'error',
      title: 'Error de cámara',
      message: 'No se pudo acceder a la cámara. Verifica los permisos.'
    };
    emit('error', error);
  } finally {
    isProcessing.value = false;
  }
};

const capturePhoto = async () => {
  if (!videoElement.value || !isCameraActive.value) return;
  
  try {
    isProcessing.value = true;
    processingText.value = 'Capturando rostro...';
    
    const canvas = document.createElement('canvas');
    const video = videoElement.value;
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);
    
    // Convertir a base64
    const base64 = canvas.toDataURL('image/jpeg', 0.8);
    
    captureStatus.value = {
      type: 'success',
      title: 'Rostro capturado',
      message: 'Procesando verificación facial...'
    };
    
    // Emitir la foto capturada
    emit('photo-captured', base64);
    
  } catch (error) {
    console.error('Error capturando foto:', error);
    captureStatus.value = {
      type: 'error',
      title: 'Error de captura',
      message: 'No se pudo capturar la foto. Intenta nuevamente.'
    };
    emit('error', error);
  } finally {
    isProcessing.value = false;
  }
};

const stopCamera = () => {
  if (stream.value) {
    stream.value.getTracks().forEach(track => track.stop());
    stream.value = null;
  }
  
  if (videoElement.value) {
    videoElement.value.srcObject = null;
  }
  
  isCameraActive.value = false;
  captureStatus.value = null;
};

onBeforeUnmount(() => {
  stopCamera();
});
</script>

<style scoped>
.face-capture-container {
  width: 100%;
  max-width: 500px;
  margin: 0 auto;
}

.camera-area {
  position: relative;
  width: 100%;
  height: 300px;
  border: 2px dashed #ccc;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  overflow: hidden;
}

.camera-area.active {
  border-color: #4caf50;
  background: #000;
}

.camera-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.camera-placeholder {
  text-align: center;
  color: #666;
}

.camera-text {
  margin-top: 16px;
  font-size: 16px;
}

.camera-button {
  margin-top: 20px;
}

.capture-button {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
}

.stop-button {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 10;
}

.capture-status {
  margin-top: 20px;
}

.processing-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 20;
}

.processing-text {
  color: white;
  margin-top: 16px;
  font-size: 16px;
}
</style>








