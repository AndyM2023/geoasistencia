import api from './api'

class AreaService {
  // Obtener todas las áreas
  async getAll() {
    try {
      const response = await api.get('/areas/')
      return response.data
    } catch (error) {
      console.error('Error obteniendo áreas:', error)
      throw error
    }
  }

  // Obtener una área por ID
  async getById(id) {
    try {
      console.log('🔍 AreaService.getById() - Obteniendo área ID:', id)
      console.log('🌐 URL de la petición:', `/areas/${id}/`)
      
      const response = await api.get(`/areas/${id}/`)
      
      console.log('✅ Área obtenida exitosamente')
      console.log('📥 Datos del área:', response.data)
      console.log('📍 Coordenadas obtenidas:', {
        latitude: response.data.latitude,
        longitude: response.data.longitude,
        radius: response.data.radius
      })
      
      return response.data
    } catch (error) {
      console.error('❌ Error en AreaService.getById():', error)
      console.error('📊 Detalles del error:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        statusText: error.response?.statusText
      })
      throw error
    }
  }

  // Crear una nueva área
  async create(areaData) {
    try {
      console.log('🚀 AreaService.create() - Datos recibidos:', areaData)
      console.log('🌐 URL de la petición:', '/areas/')
      
      const response = await api.post('/areas/', areaData)
      console.log('✅ Respuesta exitosa:', response.data)
      return response.data
    } catch (error) {
      console.error('❌ Error en AreaService.create():', error)
      console.error('📊 Detalles del error:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        statusText: error.response?.statusText
      })
      throw error
    }
  }

  // Actualizar una área existente
  async update(id, areaData) {
    try {
      console.log('🔄 AreaService.update() - Iniciando actualización...')
      console.log('🆔 ID del área:', id)
      console.log('📤 Datos a enviar:', areaData)
      console.log('🌐 URL de la petición:', `/areas/${id}/`)
      
      // DEBUGGING: Verificar tipos de datos antes de enviar
      console.log('🔍 ANÁLISIS DE TIPOS DE DATOS:')
      console.log('  - name:', typeof areaData.name, '=', areaData.name)
      console.log('  - description:', typeof areaData.description, '=', areaData.description)
      console.log('  - latitude:', typeof areaData.latitude, '=', areaData.latitude)
      console.log('  - longitude:', typeof areaData.longitude, '=', areaData.longitude)
      console.log('  - radius:', typeof areaData.radius, '=', areaData.radius)
      console.log('  - status:', typeof areaData.status, '=', areaData.status)
      
      // Asegurar que los tipos de datos sean correctos
      const cleanData = {
        name: String(areaData.name || ''),
        description: String(areaData.description || ''),
        latitude: Number(areaData.latitude),
        longitude: Number(areaData.longitude),
        radius: Number(areaData.radius),
        status: String(areaData.status || 'active')  // CRÍTICO: Incluir status
      }
      
      console.log('🧹 DATOS LIMPIADOS:')
      console.log('  - name:', typeof cleanData.name, '=', cleanData.name)
      console.log('  - description:', typeof cleanData.description, '=', cleanData.description)
      console.log('  - latitude:', typeof cleanData.latitude, '=', cleanData.latitude)
      console.log('  - longitude:', typeof cleanData.longitude, '=', cleanData.longitude)
      console.log('  - radius:', typeof cleanData.radius, '=', cleanData.radius)
      console.log('  - status:', typeof cleanData.status, '=', cleanData.status)
      
      // Verificar que no hay valores NaN
      if (isNaN(cleanData.latitude) || isNaN(cleanData.longitude) || isNaN(cleanData.radius)) {
        console.error('❌ VALORES NaN DETECTADOS:', {
          latitude: isNaN(cleanData.latitude),
          longitude: isNaN(cleanData.longitude),
          radius: isNaN(cleanData.radius)
        })
        throw new Error('Valores numéricos inválidos detectados')
      }
      
      const response = await api.put(`/areas/${id}/`, cleanData)
      
      console.log('✅ Área actualizada exitosamente')
      console.log('📥 Respuesta del servidor:', response.data)
      
      return response.data
    } catch (error) {
      console.error('❌ Error en AreaService.update():', error)
      console.error('📊 Detalles del error:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        statusText: error.response?.statusText
      })
      throw error
    }
  }

  // Eliminar una área
  async delete(id) {
    try {
      const response = await api.delete(`/areas/${id}/`)
      return response.data
    } catch (error) {
      console.error('Error eliminando área:', error)
      throw error
    }
  }

  // Obtener empleados de un área
  async getEmployees(areaId) {
    try {
      const response = await api.get(`/areas/${areaId}/employees/`)
      return response.data
    } catch (error) {
      console.error('Error obteniendo empleados del área:', error)
      throw error
    }
  }
  
  // Reactivar área desactivada
  async activate(id) {
    try {
      const response = await api.post(`/areas/${id}/activate/`)
      return response.data
    } catch (error) {
      console.error('Error reactivando área:', error)
      throw error
    }
  }
}

export default new AreaService()
