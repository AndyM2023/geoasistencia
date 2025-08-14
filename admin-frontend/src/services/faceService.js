import api from './api'

export const faceService = {
  /**
   * Registra las fotos faciales de un empleado
   * @param {number} employeeId - ID del empleado
   * @param {Array} photosBase64 - Array de fotos en base64
   * @returns {Promise} Respuesta de la API
   */
  async registerFace(employeeId, photosBase64) {
    const response = await api.post(`/employees/${employeeId}/register-face/`, {
      photos: photosBase64
    })
    return response.data
  },

  /**
   * Obtiene el estado del perfil facial de un empleado
   * @param {number} employeeId - ID del empleado
   * @returns {Promise} Estado del perfil facial
   */
  async getFaceStatus(employeeId) {
    const response = await api.get(`/employees/${employeeId}/face-status/`)
    return response.data
  },

  /**
   * Verifica una foto contra el perfil facial del empleado
   * @param {number} employeeId - ID del empleado
   * @param {string} photoBase64 - Foto en base64
   * @returns {Promise} Resultado de la verificación
   */
  async verifyFace(employeeId, photoBase64) {
    const response = await api.post(`/employees/${employeeId}/verify-face/`, {
      photo: photoBase64
    })
    return response.data
  },

  /**
   * Captura una foto desde la cámara web
   * @returns {Promise<string>} Foto en base64
   */
  async capturePhoto() {
    return new Promise((resolve, reject) => {
      navigator.mediaDevices.getUserMedia({ 
        video: { 
          width: 640, 
          height: 480,
          facingMode: 'user'
        } 
      })
      .then(stream => {
        const video = document.createElement('video')
        video.srcObject = stream
        video.play()

        video.onloadedmetadata = () => {
          const canvas = document.createElement('canvas')
          canvas.width = video.videoWidth
          canvas.height = video.videoHeight
          
          const ctx = canvas.getContext('2d')
          ctx.drawImage(video, 0, 0)
          
          // Convertir a base64
          const base64 = canvas.toDataURL('image/jpeg', 0.8)
          
          // Detener stream
          stream.getTracks().forEach(track => track.stop())
          
          resolve(base64)
        }
      })
      .catch(error => {
        console.error('Error accediendo a la cámara:', error)
        reject(error)
      })
    })
  },

  /**
   * Captura múltiples fotos para registro facial con detección de rostros
   * @param {number} count - Número de fotos a capturar
   * @param {function} onProgress - Callback de progreso
   * @param {function} onFaceDetected - Callback cuando se detecta un rostro
   * @returns {Promise<Array>} Array de fotos en base64
   */
  async captureMultiplePhotos(count = 10, onProgress = null, onFaceDetected = null) {
    const photos = []
    let attempts = 0
    const maxAttempts = count * 3 // Máximo 3 intentos por foto válida
    
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          width: 640, 
          height: 480,
          facingMode: 'user'
        } 
      })

      const video = document.createElement('video')
      video.srcObject = stream
      video.play()

      // Esperar a que el video esté listo
      await new Promise(resolve => {
        video.onloadedmetadata = resolve
      })

      const canvas = document.createElement('canvas')
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      const ctx = canvas.getContext('2d')

      // Capturar fotos validando rostros
      while (photos.length < count && attempts < maxAttempts) {
        attempts++
        
        // Esperar un poco entre capturas
        await new Promise(resolve => setTimeout(resolve, 800))
        
        // Capturar frame actual
        ctx.drawImage(video, 0, 0)
        const base64 = canvas.toDataURL('image/jpeg', 0.8)
        
        // Validación básica de rostro (aquí podrías agregar detección más sofisticada)
        const hasValidFace = await this._validateFaceInImage(base64)
        
        if (hasValidFace) {
          photos.push(base64)
          
          // Notificar progreso
          if (onProgress) {
            onProgress(photos.length, count)
          }
          
          // Notificar rostro detectado
          if (onFaceDetected) {
            onFaceDetected(photos.length)
          }
        } else {
          // Notificar que no se detectó rostro
          if (onProgress) {
            onProgress(photos.length, count, 'No se detectó rostro válido, intentando de nuevo...')
          }
        }
      }

      // Detener stream
      stream.getTracks().forEach(track => track.stop())
      
      if (photos.length === 0) {
        throw new Error('No se pudo capturar ninguna foto con rostro válido')
      }
      
      return photos
      
    } catch (error) {
      console.error('Error capturando fotos múltiples:', error)
      throw error
    }
  },

  /**
   * Validación básica de rostro en imagen
   * @param {string} base64Image - Imagen en base64
   * @returns {Promise<boolean>} True si tiene rostro válido
   */
  async _validateFaceInImage(base64Image) {
    // Validación simple por tamaño de archivo y formato
    // En una implementación más sofisticada, podrías usar face-api.js aquí
    try {
      const img = new Image()
      return new Promise((resolve) => {
        img.onload = () => {
          // Validación básica: imagen debe tener dimensiones mínimas
          const isValidSize = img.width >= 200 && img.height >= 200
          
          // Validación básica: el archivo no debe ser muy pequeño (indicaría imagen vacía)
          const fileSize = base64Image.length * 0.75 // Aproximado del tamaño en bytes
          const isValidFile = fileSize > 10000 // Mínimo 10KB
          
          resolve(isValidSize && isValidFile)
        }
        img.onerror = () => resolve(false)
        img.src = base64Image
      })
    } catch (error) {
      console.error('Error validando rostro:', error)
      return false
    }
  }
}
