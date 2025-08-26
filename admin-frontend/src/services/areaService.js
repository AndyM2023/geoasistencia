import api from './api'

class AreaService {
  // Obtener todas las áreas
  async getAll() {
    try {
      console.log('🔄 AreaService.getAll() - Iniciando petición a /areas/')
      
      // Intentar obtener todas las áreas con page_size alto
      try {
        const response = await api.get('/areas/', {
          params: {
            page_size: 1000, // Número muy alto para obtener todas las áreas
            page: 1
          }
        })
        
        console.log('✅ AreaService.getAll() - Respuesta exitosa con page_size:', response)
        console.log('📥 AreaService.getAll() - Datos recibidos:', response.data)
        
        // Verificar si realmente obtuvimos todas las áreas
        if (response.data.count && response.data.results && response.data.count <= response.data.results.length) {
          console.log('✅ Se obtuvieron todas las áreas con page_size')
          return response.data
        } else {
          console.log('⚠️ page_size no funcionó, usando método alternativo')
          return await this.getAllWithoutPagination()
        }
      } catch (pageSizeError) {
        console.log('⚠️ Error con page_size, usando método alternativo:', pageSizeError.message)
        return await this.getAllWithoutPagination()
      }
    } catch (error) {
      console.error('❌ AreaService.getAll() - Error obteniendo áreas:', error)
      console.error('📊 Detalles del error:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        statusText: error.response?.statusText
      })
      throw error
    }
  }

  // Obtener todas las áreas sin paginación (método alternativo)
  async getAllWithoutPagination() {
    try {
      console.log('🔄 AreaService.getAllWithoutPagination() - Obteniendo todas las áreas...')
      
      let allAreas = []
      let currentPage = 1
      let hasNextPage = true
      
      while (hasNextPage) {
        console.log(`📄 Obteniendo página ${currentPage}...`)
        
        const response = await api.get('/areas/', {
          params: {
            page: currentPage,
            page_size: 100 // Tamaño de página estándar
          }
        })
        
        const pageData = response.data
        const pageAreas = pageData.results || []
        
        console.log(`📋 Página ${currentPage}: ${pageAreas.length} áreas`)
        
        allAreas = [...allAreas, ...pageAreas]
        
        // Verificar si hay siguiente página
        hasNextPage = !!pageData.next
        currentPage++
        
        // Evitar bucle infinito
        if (currentPage > 100) {
          console.warn('⚠️ Límite de páginas alcanzado, deteniendo bucle')
          break
        }
      }
      
      console.log(`✅ Total de áreas obtenidas: ${allAreas.length}`)
      
      return {
        count: allAreas.length,
        results: allAreas,
        next: null,
        previous: null
      }
    } catch (error) {
      console.error('❌ AreaService.getAllWithoutPagination() - Error:', error)
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
      
      // DEBUGGING: Verificar valores específicos
      console.log('🔍 VALORES ESPECÍFICOS:')
      console.log('  - latitude es NaN?', isNaN(areaData.latitude))
      console.log('  - longitude es NaN?', isNaN(areaData.longitude))
      console.log('  - radius es NaN?', isNaN(areaData.radius))
      console.log('  - latitude es string vacío?', areaData.latitude === '')
      console.log('  - longitude es string vacío?', areaData.longitude === '')
      console.log('  - radius es string vacío?', areaData.radius === '')
      
      // Asegurar que los tipos de datos sean correctos
      const cleanData = {
        name: String(areaData.name || ''),
        description: String(areaData.description || ''),
        latitude: Number(areaData.latitude),
        longitude: Number(areaData.longitude),
        radius: Number(areaData.radius),
        status: String(areaData.status || 'active'),  // CRÍTICO: Incluir status
        schedule: areaData.schedule  // ✅ INCLUIR EL SCHEDULE COMPLETO
      }
      
      // Validar que no haya strings vacíos para coordenadas
      if (areaData.latitude === '' || areaData.longitude === '') {
        console.error('❌ COORDENADAS VACÍAS DETECTADAS:', {
          latitude: areaData.latitude,
          longitude: areaData.longitude
        })
        throw new Error('Las coordenadas no pueden estar vacías')
      }
      
      console.log('🧹 DATOS LIMPIADOS:')
      console.log('  - name:', typeof cleanData.name, '=', cleanData.name)
      console.log('  - description:', typeof cleanData.description, '=', cleanData.description)
      console.log('  - latitude:', typeof cleanData.latitude, '=', cleanData.latitude)
      console.log('  - longitude:', typeof cleanData.longitude, '=', cleanData.longitude)
      console.log('  - radius:', typeof cleanData.radius, '=', cleanData.radius)
      console.log('  - status:', typeof cleanData.status, '=', cleanData.status)
      console.log('  - schedule:', typeof cleanData.schedule, '=', cleanData.schedule)
      if (cleanData.schedule) {
        console.log('  - schedule.schedule_type:', cleanData.schedule.schedule_type)
        console.log('  - schedule.monday_start:', cleanData.schedule.monday_start, '(tipo:', typeof cleanData.schedule.monday_start, ')')
        console.log('  - schedule.monday_end:', cleanData.schedule.monday_end, '(tipo:', typeof cleanData.schedule.monday_end, ')')
        console.log('  - schedule.monday_active:', cleanData.schedule.monday_active, '(tipo:', typeof cleanData.schedule.monday_active, ')')
        console.log('  - schedule.tuesday_start:', cleanData.schedule.tuesday_start, '(tipo:', typeof cleanData.schedule.tuesday_start, ')')
        console.log('  - schedule.tuesday_end:', cleanData.schedule.tuesday_end, '(tipo:', typeof cleanData.schedule.tuesday_end, ')')
        console.log('  - schedule.tuesday_active:', cleanData.schedule.tuesday_active, '(tipo:', typeof cleanData.schedule.tuesday_active, ')')
      }
      
      // Verificar que no hay valores NaN
      if (isNaN(cleanData.latitude) || isNaN(cleanData.longitude) || isNaN(cleanData.radius)) {
        console.error('❌ VALORES NaN DETECTADOS:', {
          latitude: isNaN(cleanData.latitude),
          longitude: isNaN(cleanData.longitude),
          radius: isNaN(cleanData.radius)
        })
        throw new Error('Valores numéricos inválidos detectados')
      }
      
      console.log('📤 ENVIANDO PETICIÓN PUT con datos:', cleanData)
      console.log('🔍 VERIFICACIÓN FINAL ANTES DE ENVIAR:')
      console.log('  - schedule presente:', !!cleanData.schedule)
      if (cleanData.schedule) {
        console.log('  - schedule_type:', cleanData.schedule.schedule_type)
        console.log('  - monday_start:', cleanData.schedule.monday_start)
        console.log('  - monday_end:', cleanData.schedule.monday_end)
        console.log('  - monday_active:', cleanData.schedule.monday_active)
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
