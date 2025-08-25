import { ref } from 'vue'
import { faceService } from '../services/faceService'
import { useNotifications } from './useNotifications'

export function useEmployeeFaceRegistration() {
  const { showSuccess, showError, showWarning, showInfo } = useNotifications()
  
  // Estados para registro facial
  const showFaceRegistration = ref(false)
  const faceRegistration = ref({
    isCapturing: false,
    isTraining: false,
    status: 'pending', // pending, captured, trained, error
    statusText: 'Sin registrar',
    photosCount: 0,
    confidence: 90,
    capturedPhotos: null
  })
  
  const onPhotoCaptured = (photoData) => {
    console.log('📸 Foto capturada:', photoData)
    faceRegistration.value.photosCount++
    faceRegistration.value.statusText = `Foto ${faceRegistration.value.photosCount} capturada`
  }
  
  const onCaptureComplete = (photos) => {
    console.log('✅ Captura completada:', photos.length, 'fotos')
    faceRegistration.value.capturedPhotos = photos
    faceRegistration.value.status = 'captured'
    faceRegistration.value.statusText = `${photos.length} fotos capturadas`
  }
  
  const onCaptureStopped = () => {
    console.log('⏹️ Captura detenida')
    faceRegistration.value.isCapturing = false
    faceRegistration.value.statusText = 'Captura detenida'
  }
  
  const onRegistroCompleto = async (result) => {
    console.log('✅ Registro facial completado:', result)
    faceRegistration.value.status = 'trained'
    faceRegistration.value.statusText = 'Rostros procesados y guardados correctamente'
    faceRegistration.value.photosCount = result.photos_count || result.photosCount || 0
    showFaceRegistration.value = false
    
    // Mostrar mensaje de éxito
    showSuccess('✅ Registro facial completado exitosamente')
    
    // Resetear estado facial
    resetFaceRegistration()
  }
  
  const onRegistroError = (error) => {
    console.error('❌ Error en registro facial:', error)
    faceRegistration.value.status = 'error'
    faceRegistration.value.statusText = `Error: ${error.message || 'Error en registro'}`
    showFaceRegistration.value = false
    
    // Mostrar mensaje de error
    showError('❌ Error en registro facial: ' + error.message)
  }
  
  const trainFaceModel = async (editingEmployee) => {
    if (!faceRegistration.value.capturedPhotos || faceRegistration.value.capturedPhotos.length === 0) {
      showWarning('⚠️ Primero debes capturar fotos')
      return
    }
    
    // Verificar que el empleado esté guardado
    if (!editingEmployee || !editingEmployee.id) {
      showWarning('⚠️ Primero debes guardar el empleado antes de procesar el rostro facial')
      return
    }
    
    // ✅ SIMPLIFICADO: Solo mostrar estado de procesamiento
    // Las fotos ya se procesan automáticamente en FaceRegistration.vue
    faceRegistration.value.isTraining = true
    faceRegistration.value.statusText = 'Procesando rostros y generando embeddings...'
    
    try {
      console.log('Iniciando procesamiento facial...')
      console.log('Fotos a procesar:', faceRegistration.value.capturedPhotos.length)
      console.log('Empleado ID:', editingEmployee.id)
      
      // ✅ NO procesar fotos aquí - ya se procesan en FaceRegistration.vue
      // Solo simular el tiempo de procesamiento para mostrar el estado
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // Cambiar estado a completado
      faceRegistration.value.status = 'trained'
      faceRegistration.value.statusText = 'Rostros procesados y guardados correctamente'
      faceRegistration.value.photosCount = faceRegistration.value.capturedPhotos.length
      
      console.log('✅ Procesamiento simulado completado')
      
    } catch (error) {
      console.error('❌ Error en procesamiento:', error)
      faceRegistration.value.status = 'error'
      faceRegistration.value.statusText = `Error: ${error.message || 'Error en procesamiento'}`
    } finally {
      faceRegistration.value.isTraining = false
    }
  }
  
  const resetFaceRegistration = () => {
    faceRegistration.value = {
      isCapturing: false,
      isTraining: false,
      status: 'pending',
      statusText: 'Sin registrar',
      photosCount: 0,
      confidence: 90,
      capturedPhotos: null
    }
  }
  
  const checkFaceRegistrationStatus = async (employeeId) => {
    if (!employeeId || employeeId === 'new') {
      console.log('🔍 ID de empleado inválido para verificar estado facial')
      return
    }
    
    try {
      console.log('🔍 Verificando estado de registro facial para empleado:', employeeId)
      const response = await faceService.getFaceStatus(employeeId)
      const faceStatus = response.data
      
      console.log('🔍 Respuesta del servicio facial:', faceStatus)
      
      if (faceStatus.has_profile && faceStatus.is_trained) {
        console.log('✅ Empleado tiene rostro registrado COMPLETO:', faceStatus)
        faceRegistration.value.status = 'trained'
        faceRegistration.value.statusText = 'Rostro registrado correctamente'
        faceRegistration.value.photosCount = faceStatus.photos_count || 0
      } else if (faceStatus.has_profile) {
        console.log('⚠️ Empleado tiene fotos pero no está entrenado:', faceStatus)
        faceRegistration.value.status = 'captured'
        faceRegistration.value.statusText = 'Fotos capturadas, pendiente entrenamiento'
        faceRegistration.value.photosCount = faceStatus.photos_count || 0
      } else {
        console.log('❌ Empleado no tiene rostro registrado:', faceStatus)
        faceRegistration.value.status = 'pending'
        faceRegistration.value.statusText = 'Sin registrar'
        faceRegistration.value.photosCount = 0
      }
      
    } catch (error) {
      console.error('❌ Error al verificar estado facial:', error)
      faceRegistration.value.status = 'error'
      faceRegistration.value.statusText = 'Error al verificar estado'
    }
  }
  
  return {
    // Estado
    showFaceRegistration,
    faceRegistration,
    
    // Métodos
    onPhotoCaptured,
    onCaptureComplete,
    onCaptureStopped,
    onRegistroCompleto,
    onRegistroError,
    trainFaceModel,
    resetFaceRegistration,
    checkFaceRegistrationStatus
  }
}


