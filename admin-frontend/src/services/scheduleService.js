import api from './api'

class ScheduleService {
  /**
   * Obtener horario de un área específica
   */
  async getSchedule(areaId) {
    try {
      const response = await api.get(`/area-schedules/?area_id=${areaId}`)
      return response.data
    } catch (error) {
      console.error('Error obteniendo horario:', error)
      throw error
    }
  }

  /**
   * Crear horario para un área
   */
  async createSchedule(scheduleData) {
    try {
      const response = await api.post('/area-schedules/', scheduleData)
      return response.data
    } catch (error) {
      console.error('Error creando horario:', error)
      throw error
    }
  }

  /**
   * Actualizar horario existente
   */
  async updateSchedule(scheduleId, scheduleData) {
    try {
      const response = await api.patch(`/area-schedules/${scheduleId}/`, scheduleData)
      return response.data
    } catch (error) {
      console.error('Error actualizando horario:', error)
      throw error
    }
  }

  /**
   * Crear horario por defecto para un área
   */
  async createDefaultSchedule(areaId) {
    try {
      const response = await api.post(`/area-schedules/${areaId}/create_default/`)
      return response.data
    } catch (error) {
      console.error('Error creando horario por defecto:', error)
      throw error
    }
  }

  /**
   * Eliminar horario de un área
   */
  async deleteSchedule(scheduleId) {
    try {
      const response = await api.delete(`/area-schedules/${scheduleId}/`)
      return response.data
    } catch (error) {
      console.error('Error eliminando horario:', error)
      throw error
    }
  }

  /**
   * Validar horario antes de enviar
   */
  validateSchedule(schedule) {
    const errors = []
    
    // Validar que al menos un día esté activo
    const activeDays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    const hasActiveDay = activeDays.some(day => schedule[`${day}_active`])
    
    if (!hasActiveDay) {
      errors.push('Al menos un día debe estar activo')
    }

    // Validar horarios de días activos
    activeDays.forEach(day => {
      if (schedule[`${day}_active`]) {
        const start = schedule[`${day}_start`]
        const end = schedule[`${day}_end`]
        
        if (!start || !end) {
          errors.push(`${day} debe tener hora de inicio y fin`)
        } else if (start >= end) {
          errors.push(`${day} la hora de inicio debe ser menor que la de fin`)
        }
      }
    })

    // Validar tolerancia
    if (schedule.grace_period_minutes < 0 || schedule.grace_period_minutes > 120) {
      errors.push('La tolerancia debe estar entre 0 y 120 minutos')
    }

    return errors
  }

  /**
   * Crear horario por defecto (8:00 AM - 5:00 PM, L-V)
   */
  createDefaultScheduleData() {
    return {
      monday_start: '08:00',
      monday_end: '17:00',
      monday_active: true,
      tuesday_start: '08:00',
      tuesday_end: '17:00',
      tuesday_active: true,
      wednesday_start: '08:00',
      wednesday_end: '17:00',
      wednesday_active: true,
      thursday_start: '08:00',
      thursday_end: '17:00',
      thursday_active: true,
      friday_start: '08:00',
      friday_end: '17:00',
      friday_active: true,
      saturday_start: null,
      saturday_end: null,
      saturday_active: false,
      sunday_start: null,
      sunday_end: null,
      sunday_active: false,
      grace_period_minutes: 15
    }
  }
}

export default new ScheduleService()
