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
        �� Registro de Rostro - {{ employeeName }}
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
                color="green-400"
                size="64"
                width="6"
                class="mb-2"
              >
                {{ fotosCapturadas }}/{{ targetCount }}
              </v-progress-circular>
              <p class="text-green-400 text-center">Capturando...</p>
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
            {{ isCapturing ? 'Capturando fotos...' : 'Listo para iniciar' }}
          </p>
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
          @click="closeDialog"
          color="grey-600"
          variant="outlined"
          class="ml-2"
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
const fotosCapturadas = ref(0);
const capturedPhotos = ref([]);
const mensaje = ref(null);
const videoElement = ref(null);
const stream = ref(null);
const captureInterval = ref(null);

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
    
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.width = videoElement.value.videoWidth || 640;
    canvas.height = videoElement.value.videoHeight || 480;
    
    context.drawImage(videoElement.value, 0, 0);
    const photoData = canvas.toDataURL('image/jpeg', 0.9);
    
    capturedPhotos.value.push(photoData);
    fotosCapturadas.value++;
    
    console.log(`📸 Foto ${fotosCapturadas.value}/${props.targetCount} capturada`);
    
  } catch (error) {
    console.error('❌ Error capturando foto:', error);
  }
};

// Función para procesar fotos
const processPhotos = async () => {
  try {
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
  width: 100%;
  border-radius: 8px;
  overflow: hidden;
  background: #000;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
  position: relative;
}

.camera-video {
  width: 100%;
  max-width: 640px;
  height: auto;
  max-height: 400px;
  object-fit: contain;
  border-radius: 8px;
}

.camera-status-overlay,
.capture-status-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 10;
}

.capture-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.progress-section {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 16px;
  border: 1px solid rgba(59, 130, 246, 0.2);
}
</style>

