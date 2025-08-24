import { ref, watch } from 'vue'

export default function useSchedule() {
  // Variables para el sistema de horarios
  const scheduleType = ref('default') // 'default', 'custom', 'none'
  const schedule = ref({
    // NO inicializar con datos estáticos - usar valores mínimos
    monday_active: false,
    monday_start: null,
    monday_end: null,
    
    tuesday_active: false,
    tuesday_start: null,
    tuesday_end: null,
    
    wednesday_active: false,
    wednesday_start: null,
    wednesday_end: null,
    
    thursday_active: false,
    thursday_start: null,
    thursday_end: null,
    
    friday_active: false,
    friday_start: null,
    friday_end: null,
    
    saturday_active: false,
    saturday_start: null,
    saturday_end: null,
    
    sunday_active: false,
    sunday_start: null,
    sunday_end: null,
    
    // Tolerancia para llegadas tarde
    grace_period_minutes: 0
  })
  
  // Días de la semana para el formulario
  const scheduleDays = [
    { key: 'monday', label: 'Lunes' },
    { key: 'tuesday', label: 'Martes' },
    { key: 'wednesday', label: 'Miércoles' },
    { key: 'thursday', label: 'Jueves' },
    { key: 'friday', label: 'Viernes' },
    { key: 'saturday', label: 'Sábado' },
    { key: 'sunday', label: 'Domingo' }
  ]
  
  // Funciones para el sistema de horarios
  const getScheduleSummary = () => {
    if (scheduleType.value === 'default') {
      return 'Horario estándar: Lunes a Viernes de 8:00 AM a 5:00 PM con 15 minutos de tolerancia'
    } else if (scheduleType.value === 'custom') {
      const activeDays = scheduleDays.filter(day => schedule.value[`${day.key}_active`])
      if (activeDays.length === 0) return 'No hay días laborables configurados'
      
      const dayNames = activeDays.map(day => day.label).join(', ')
      const tolerance = schedule.value.grace_period_minutes
      return `${dayNames} - Tolerancia: ${tolerance} minutos`
    }
    return ''
  }
  
  const createDefaultSchedule = () => {
    // Crear horario por defecto válido y consistente con el backend
    schedule.value = {
      monday_active: true,
      monday_start: '08:00',
      monday_end: '17:00',
      
      tuesday_active: true,
      tuesday_start: '08:00',
      tuesday_end: '17:00',
      
      wednesday_active: true,
      wednesday_start: '08:00',
      wednesday_end: '17:00',
      
      thursday_active: true,
      thursday_start: '08:00',
      thursday_end: '17:00',
      
      friday_active: true,
      friday_start: '08:00',
      friday_end: '17:00',
      
      saturday_active: false,
      saturday_start: null,
      saturday_end: null,
      
      sunday_active: false,
      sunday_start: null,
      sunday_end: null,
      
      grace_period_minutes: 15
    }
    console.log('✅ createDefaultSchedule: Horario por defecto válido creado')
  }
  
  const loadScheduleFromArea = (area) => {
    console.log('🔍 loadScheduleFromArea llamado con área:', area)
    console.log('🔍 area.schedule:', area.schedule)
    console.log('🔍 area.schedule.schedule_type:', area.schedule?.schedule_type)
    
    if (area.schedule && area.schedule.schedule_type && area.schedule.schedule_type !== 'none') {
      // Si el área ya tiene horario, cargarlo según el tipo del backend
      console.log('✅ Área tiene horario, cargando como', area.schedule.schedule_type)
      
      if (area.schedule.schedule_type === 'default') {
        scheduleType.value = 'default'
        console.log('✅ Horario por defecto detectado en backend')
        
        // Cargar EXACTAMENTE los horarios del backend (NO datos estáticos)
        schedule.value = {
          monday_active: area.schedule.monday_active ?? false,
          monday_start: area.schedule.monday_start ?? '08:00',
          monday_end: area.schedule.monday_end ?? '17:00',
          tuesday_active: area.schedule.tuesday_active ?? false,
          tuesday_start: area.schedule.tuesday_start ?? '08:00',
          tuesday_end: area.schedule.tuesday_end ?? '17:00',
          wednesday_active: area.schedule.wednesday_active ?? false,
          wednesday_start: area.schedule.wednesday_start ?? '08:00',
          wednesday_end: area.schedule.wednesday_end ?? '17:00',
          thursday_active: area.schedule.thursday_active ?? false,
          thursday_start: area.schedule.thursday_start ?? '08:00',
          thursday_end: area.schedule.thursday_end ?? '17:00',
          friday_active: area.schedule.friday_active ?? false,
          friday_start: area.schedule.friday_start ?? '08:00',
          friday_end: area.schedule.friday_end ?? '17:00',
          saturday_active: area.schedule.saturday_active ?? false,
          saturday_start: area.schedule.saturday_start ?? null,
          saturday_end: area.schedule.saturday_end ?? null,
          sunday_active: area.schedule.sunday_active ?? false,
          sunday_start: area.schedule.sunday_start ?? null,
          sunday_end: area.schedule.sunday_end ?? null,
          grace_period_minutes: area.schedule.grace_period_minutes ?? 15
        }
      } else if (area.schedule.schedule_type === 'custom') {
        scheduleType.value = 'custom'
        console.log('✅ Horario personalizado detectado en backend')
        
        // Cargar los horarios personalizados EXACTAMENTE como están en el backend
        schedule.value = {
          monday_active: area.schedule.monday_active ?? false,
          monday_start: area.schedule.monday_start ?? '08:00',
          monday_end: area.schedule.monday_end ?? '17:00',
          tuesday_active: area.schedule.tuesday_active ?? false,
          tuesday_start: area.schedule.tuesday_start ?? '08:00',
          tuesday_end: area.schedule.tuesday_end ?? '17:00',
          wednesday_active: area.schedule.wednesday_active ?? false,
          wednesday_start: area.schedule.wednesday_start ?? '08:00',
          wednesday_end: area.schedule.wednesday_end ?? '17:00',
          thursday_active: area.schedule.thursday_active ?? false,
          thursday_start: area.schedule.thursday_start ?? '08:00',
          thursday_end: area.schedule.thursday_end ?? '17:00',
          friday_active: area.schedule.friday_active ?? false,
          friday_start: area.schedule.friday_start ?? '08:00',
          friday_end: area.schedule.friday_end ?? '17:00',
          saturday_active: area.schedule.saturday_active ?? false,
          saturday_start: area.schedule.saturday_start ?? null,
          saturday_end: area.schedule.saturday_end ?? null,
          sunday_active: area.schedule.sunday_active ?? false,
          sunday_start: area.schedule.sunday_start ?? null,
          sunday_end: area.schedule.sunday_end ?? null,
          grace_period_minutes: area.schedule.grace_period_minutes ?? 15
        }
        
        console.log('✅ Horarios personalizados cargados:', schedule.value)
      }
      
      console.log('🔍 schedule.value después de cargar:', schedule.value)
      console.log('🔍 scheduleType.value después de cargar:', scheduleType.value)
    } else {
      // Si no tiene horario o schedule_type, usar el por defecto
      console.log('❌ Área no tiene horario o schedule_type, usando por defecto')
      createDefaultSchedule()
      scheduleType.value = 'default'
      console.log('🔍 schedule.value después de crear por defecto:', schedule.value)
      console.log('🔍 scheduleType.value después de crear por defecto:', scheduleType.value)
    }
  }
  
  // Funciones auxiliares para mostrar información de horarios en la tabla
  const getScheduleColor = (scheduleData) => {
    if (!scheduleData) return 'grey-500'
    
    const activeDays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
      .filter(day => scheduleData[`${day}_active`])
    
    if (activeDays.length === 5 && !scheduleData.saturday_active && !scheduleData.sunday_active) {
      return 'green-500' // Horario estándar
    } else if (activeDays.length > 0) {
      return 'blue-500' // Horario personalizado
    } else {
      return 'orange-500' // Sin días activos
    }
  }
  
  const getScheduleIcon = (scheduleData) => {
    if (!scheduleData) return 'mdi-close-circle'
    
    const activeDays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
      .filter(day => scheduleData[`${day}_active`])
    
    if (activeDays.length === 5 && !scheduleData.saturday_active && !scheduleData.sunday_active) {
      return 'mdi-check-circle' // Horario estándar
    } else if (activeDays.length > 0) {
      return 'mdi-cog' // Horario personalizado
    } else {
      return 'mdi-alert-circle' // Sin días activos
    }
  }
  
  const getScheduleText = (scheduleData) => {
    console.log('🔍 getScheduleText llamado con:', scheduleData)
    
    if (!scheduleData) {
      console.log('❌ No hay horario, retornando "Sin horario"')
      return 'Sin horario'
    }
    
    // PRIORIDAD 1: Usar schedule_type del backend si está disponible
    if (scheduleData.schedule_type) {
      console.log('🎯 Usando schedule_type del backend:', scheduleData.schedule_type)
      if (scheduleData.schedule_type === 'default') {
        console.log('✅ Horario estándar detectado por schedule_type')
        return 'Horario Estándar'
      } else if (scheduleData.schedule_type === 'custom') {
        console.log('🔧 Horario personalizado detectado por schedule_type')
        return 'Horario Personalizado'
      } else if (scheduleData.schedule_type === 'none') {
        console.log('❌ Sin horario por schedule_type')
        return 'Sin Horario'
      }
    }
    
    // PRIORIDAD 2: Fallback - adivinar basándose en días activos
    console.log('🔄 No hay schedule_type, usando fallback de días activos')
    const activeDays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
      .filter(day => scheduleData[`${day}_active`])
    
    console.log('📅 Días activos encontrados:', activeDays)
    
    if (activeDays.length === 5 && !scheduleData.saturday_active && !scheduleData.sunday_active) {
      console.log('✅ Horario estándar detectado por fallback')
      return 'Horario Estándar'
    } else if (activeDays.length > 0) {
      console.log('🔧 Horario personalizado detectado por fallback:', activeDays.length, 'días')
      return 'Horario Personalizado'
    } else {
      console.log('⚠️ Horario vacío detectado por fallback')
      return 'Sin Horario'
    }
  }
  
  const getScheduleTooltip = (scheduleData) => {
    if (!scheduleData) return 'Sin horario configurado'
    
    const activeDays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
      .filter(day => scheduleData[`${day}_active`])
    
    if (activeDays.length === 0) {
      return 'No hay días laborables configurados'
    }
    
    const dayNames = {
      monday: 'Lun',
      tuesday: 'Mar',
      wednesday: 'Mié',
      thursday: 'Jue',
      friday: 'Vie',
      saturday: 'Sáb',
      sunday: 'Dom'
    }
    
    const activeDayNames = activeDays.map(day => dayNames[day]).join(', ')
    const tolerance = scheduleData.grace_period_minutes || 0
    
    return `${activeDayNames} - Tolerancia: ${tolerance} min`
  }
  
  // ✅ Función para validar horarios antes de guardar
  const validateSchedule = () => {
    console.log('🔍 Validando horarios...')
    console.log('🔍 scheduleType.value:', scheduleType.value)
    console.log('🔍 schedule.value:', schedule.value)
    
    if (scheduleType.value === 'none') {
      console.log('✅ Tipo "none" - no requiere validación de horarios')
      return true
    }
    
    if (scheduleType.value === 'default') {
      // Para horario por defecto, verificar que los días activos tengan horarios válidos
      const days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
      for (const day of days) {
        if (schedule.value[`${day}_active`]) {
          const start = schedule.value[`${day}_start`]
          const end = schedule.value[`${day}_end`]
          
          if (!start || !end) {
            console.error(`❌ Día ${day} activo pero sin horarios completos`)
            return false
          }
          
          if (start >= end) {
            console.error(`❌ Día ${day}: hora inicio >= hora fin`)
            return false
          }
        }
      }
      console.log('✅ Horario por defecto válido')
      return true
    }
    
    if (scheduleType.value === 'custom') {
      // Para horario personalizado, verificar que al menos un día esté activo
      const hasActiveDay = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        .some(day => schedule.value[`${day}_active`])
      
      if (!hasActiveDay) {
        console.error('❌ Horario personalizado sin días activos')
        return false
      }
      
      // Verificar que los días activos tengan horarios válidos
      const days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
      for (const day of days) {
        if (schedule.value[`${day}_active`]) {
          const start = schedule.value[`${day}_start`]
          const end = schedule.value[`${day}_end`]
          
          if (!start || !end) {
            console.error(`❌ Día ${day} activo pero sin horarios completos`)
            return false
          }
          
          if (start >= end) {
            console.error(`❌ Día ${day}: hora inicio >= hora fin`)
            return false
          }
        }
      }
      
      console.log('✅ Horario personalizado válido')
      return true
    }
    
    console.error('❌ Tipo de horario no reconocido:', scheduleType.value)
    return false
  }
  
  // Observar cambios en el tipo de horario
  watch(scheduleType, (newType, oldType) => {
    console.log(`🔄 Cambio de tipo de horario: ${oldType} → ${newType}`)
    
    if (newType === 'default') {
      // ✅ Crear horario por defecto válido
      createDefaultSchedule()
      console.log('✅ Horario por defecto aplicado')
    } else if (newType === 'custom') {
      // ✅ Mantener horarios actuales pero asegurar que sean válidos
      if (oldType === 'default') {
        // Si venía de default, mantener los valores pero permitir edición
        console.log('✅ Cambiando de default a custom - horarios mantenidos')
      } else if (oldType === 'none') {
        // Si venía de none, crear horario por defecto como base
        createDefaultSchedule()
        console.log('✅ Cambiando de none a custom - horario por defecto como base')
      }
    } else if (newType === 'none') {
      // ✅ Limpiar horarios para "sin horario"
      schedule.value = {
        monday_active: false,
        monday_start: '08:00',
        monday_end: '17:00',
        tuesday_active: false,
        tuesday_start: '08:00',
        tuesday_end: '17:00',
        wednesday_active: false,
        wednesday_start: '08:00',
        wednesday_end: '17:00',
        thursday_active: false,
        thursday_start: '08:00',
        thursday_end: '17:00',
        friday_active: false,
        friday_start: '08:00',
        friday_end: '17:00',
        saturday_active: false,
        saturday_start: '08:00',
        saturday_end: '17:00',
        sunday_active: false,
        sunday_start: '08:00',
        sunday_end: '17:00',
        grace_period_minutes: 0
      }
      console.log('✅ Horarios limpiados para "sin horario"')
    }
  })
  
  return {
    scheduleType,
    schedule,
    scheduleDays,
    getScheduleSummary,
    createDefaultSchedule,
    loadScheduleFromArea,
    getScheduleColor,
    getScheduleIcon,
    getScheduleText,
    getScheduleTooltip,
    validateSchedule
  }
}
