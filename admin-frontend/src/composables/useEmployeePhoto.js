import { ref } from 'vue'
import { useNotifications } from './useNotifications'

export function useEmployeePhoto() {
  const { showSuccess, showError, showWarning, showInfo } = useNotifications()
  
  // Estado para captura de foto
  const showPhotoCapture = ref(false)
  const capturedPhoto = ref(null)
  const cameraActive = ref(false)
  const cameraLoading = ref(false)
  const video = ref(null)
  const stream = ref(null)
  
  // Estado para modal de foto expandida
  const showPhotoModal = ref(false)
  const selectedEmployeePhoto = ref(null)
  
  // ✅ FUNCIÓN: Manejar la selección de archivo para la foto
  const onFileSelected = (event, employeeForm) => {
    const file = event.target.files[0]
    if (file) {
      // Validar tipo de archivo
      if (!file.type.startsWith('image/')) {
        showError('❌ Solo se permiten archivos de imagen')
        return
      }
      
      // Validar tamaño (5MB)
      if (file.size > 5 * 1024 * 1024) {
        showError('❌ El archivo es demasiado grande. Máximo 5MB')
        return
      }
      
      // Guardar el archivo directamente
      employeeForm.value.photo = file
      console.log('📸 Archivo seleccionado:', file.name, file.size, file.type)
    }
  }

  // ✅ FUNCIÓN: Eliminar la foto actual
  const removePhoto = (employeeForm, editingEmployee) => {
    console.log('🔍 removePhoto - Estado actual:')
    console.log('   - editingEmployee?.photo:', editingEmployee?.photo)
    console.log('   - employeeForm.value.photo:', employeeForm.value.photo)
    
    // Si ya está marcada para eliminar, permitir deshacer
    if (employeeForm.value.photo === 'DELETE_PHOTO') {
      // Deshacer la eliminación
      if (editingEmployee && editingEmployee.photo) {
        // Restaurar la foto original del empleado
        employeeForm.value.photo = null // Volver al estado inicial
        console.log('🔄 Eliminación de foto deshecha')
        showInfo('ℹ️ Eliminación de foto cancelada')
      } else {
        // Limpiar la foto
        employeeForm.value.photo = null
        console.log('🔄 Eliminación de foto deshecha')
        showInfo('ℹ️ Eliminación de foto cancelada')
      }
    } else if (editingEmployee && editingEmployee.photo) {
      // Marcar que se debe eliminar la foto existente
      employeeForm.value.photo = 'DELETE_PHOTO'
      console.log('🗑️ Foto existente marcada para eliminación')
      showWarning('⚠️ Foto marcada para eliminar. Haz clic en "Guardar" para confirmar.')
    } else {
      // Si es una foto nueva, simplemente limpiar
      employeeForm.value.photo = null
      console.log('🗑️ Foto nueva eliminada')
      showInfo('ℹ️ Foto eliminada del formulario')
    }
    
    console.log('🔍 removePhoto - Estado después de la acción:')
    console.log('   - employeeForm.value.photo:', employeeForm.value.photo)
  }
  
  // ✅ FUNCIÓN: Convertir base64 a archivo
  const base64ToFile = (base64String, filename = 'photo.jpg') => {
    // Remover el prefijo data:image/...;base64, si existe
    const base64Data = base64String.includes(',') ? base64String.split(',')[1] : base64String
    
    // Convertir base64 a blob
    const byteCharacters = atob(base64Data)
    const byteNumbers = new Array(byteCharacters.length)
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i)
    }
    const byteArray = new Uint8Array(byteNumbers)
    
    // Crear archivo
    const blob = new Blob([byteArray], { type: 'image/jpeg' })
    const file = new File([blob], filename, { type: 'image/jpeg' })
    
    return file
  }
  
  // ✅ FUNCIÓN: Obtener URL de la foto para vista previa
  const getPhotoUrl = (photo) => {
    if (!photo) return null
    
    if (photo instanceof File) {
      // Si es un archivo, crear URL temporal
      return URL.createObjectURL(photo)
    } else if (typeof photo === 'string' && photo.startsWith('data:')) {
      // Si es base64, usar directamente
      return photo
    } else if (typeof photo === 'string') {
      // Si es una URL, usar directamente
      return photo
    }
    
    return null
  }

  // ✅ FUNCIÓN: Verificar si se debe mostrar el botón de eliminar foto
  const shouldShowDeletePhotoButton = (employeeForm, editingEmployee) => {
    // Mostrar si hay una foto nueva seleccionada
    if (employeeForm.value.photo && employeeForm.value.photo !== 'DELETE_PHOTO' && employeeForm.value.photo instanceof File) {
      return true
    }
    
    // Mostrar si hay una foto existente del empleado (no marcada para eliminar)
    if (editingEmployee && editingEmployee.photo && employeeForm.value.photo !== 'DELETE_PHOTO') {
      return true
    }
    
    // Mostrar si la foto está marcada para eliminar (para permitir deshacer)
    if (editingEmployee && editingEmployee.photo && employeeForm.value.photo === 'DELETE_PHOTO') {
      return true
    }
    
    // 🔍 DEBUG: Log del estado para debugging
    console.log('🔍 shouldShowDeletePhotoButton:')
    console.log('   - editingEmployee?.photo:', editingEmployee?.photo)
    console.log('   - employeeForm.value.photo:', employeeForm.value.photo)
    console.log('   - Resultado:', false)
    
    return false
  }
  
  // ✅ FUNCIÓN: Iniciar la cámara
  const startCamera = async () => {
    try {
      cameraLoading.value = true
      stream.value = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          width: { ideal: 640 }, 
          height: { ideal: 480 },
          facingMode: 'user' // Cámara frontal
        } 
      })
      
      if (video.value) {
        video.value.srcObject = stream.value
        cameraActive.value = true
        console.log('📹 Cámara iniciada')
      }
    } catch (error) {
      console.error('❌ Error al iniciar cámara:', error)
      showError('Error al acceder a la cámara. Verifica los permisos.')
    } finally {
      cameraLoading.value = false
    }
  }
  
  // ✅ FUNCIÓN: Detener la cámara
  const stopCamera = () => {
    if (stream.value) {
      stream.value.getTracks().forEach(track => track.stop())
      stream.value = null
    }
    cameraActive.value = false
    console.log('⏹️ Cámara detenida')
  }
  
  // ✅ FUNCIÓN: Capturar foto
  const capturePhoto = () => {
    if (video.value && cameraActive.value) {
      const canvas = document.createElement('canvas')
      const context = canvas.getContext('2d')
      
      canvas.width = video.value.videoWidth
      canvas.height = video.value.videoHeight
      
      context.drawImage(video.value, 0, 0)
      
      capturedPhoto.value = canvas.toDataURL('image/jpeg', 0.8)
      console.log('📸 Foto capturada')
      
      // Detener cámara después de capturar
      stopCamera()
    }
  }
  
  // ✅ FUNCIÓN: Aceptar foto capturada
  const acceptPhoto = (employeeForm) => {
    if (capturedPhoto.value) {
      // Convertir base64 a archivo
      const photoFile = base64ToFile(capturedPhoto.value, `photo_${Date.now()}.jpg`)
      employeeForm.value.photo = photoFile
      console.log('✅ Foto aceptada y convertida a archivo:', photoFile.name, photoFile.size)
    }
    closePhotoCapture()
  }
  
  // ✅ FUNCIÓN: Retomar foto
  const retakePhoto = () => {
    capturedPhoto.value = null
    console.log('🔄 Retomando foto')
  }
  
  // ✅ FUNCIÓN: Cerrar captura de foto
  const closePhotoCapture = () => {
    showPhotoCapture.value = false
    capturedPhoto.value = null
    stopCamera()
  }
  
  // ✅ FUNCIÓN: Mostrar modal de foto
  const openPhotoModal = (photoUrl) => {
    selectedEmployeePhoto.value = photoUrl
    showPhotoModal.value = true
  }
  
  // ✅ FUNCIÓN: Cerrar modal de foto
  const closePhotoModal = () => {
    showPhotoModal.value = false
    selectedEmployeePhoto.value = null
  }
  
  return {
    // Estado
    showPhotoCapture,
    capturedPhoto,
    cameraActive,
    cameraLoading,
    video,
    stream,
    showPhotoModal,
    selectedEmployeePhoto,
    
    // Métodos
    onFileSelected,
    removePhoto,
    base64ToFile,
    getPhotoUrl,
    shouldShowDeletePhotoButton,
    startCamera,
    stopCamera,
    capturePhoto,
    acceptPhoto,
    retakePhoto,
    closePhotoCapture,
    openPhotoModal,
    closePhotoModal
  }
}
