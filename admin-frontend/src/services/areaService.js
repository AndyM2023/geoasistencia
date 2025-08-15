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
      const response = await api.get(`/areas/${id}/`)
      return response.data
    } catch (error) {
      console.error('Error obteniendo área:', error)
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
      const response = await api.put(`/areas/${id}/`, areaData)
      return response.data
    } catch (error) {
      console.error('Error actualizando área:', error)
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
