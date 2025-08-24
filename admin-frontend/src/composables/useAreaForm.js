import { ref } from 'vue'
import areaService from '../services/areaService'
import { useNotifications } from './useNotifications'

export default function useAreaForm() {
  const { showSuccess, showError, showWarning, showInfo } = useNotifications()
  
  const showDialog = ref(false)
  const saving = ref(false)
  const editingArea = ref(null)
  const areaToDelete = ref(null)
  const showDeleteDialog = ref(false)
  const deleting = ref(false)
  
  const areaForm = ref({
    name: '',
    description: '',
    latitude: '',
    longitude: '',
    radius: 200,
    status: 'active'  // CRÍTICO: Incluir status por defecto
  })
  
  // Función para formatear coordenadas (mostrar solo primeros 10 caracteres)
  const formatCoordinate = (coordinate) => {
    if (!coordinate) return '-'
    const coordStr = coordinate.toString()
    return coordStr.length > 10 ? coordStr.substring(0, 10) + '...' : coordStr
  }
  
  const showMessage = (text, type = 'success') => {
    // Usar el sistema global de notificaciones en lugar del mensaje local
    switch (type) {
      case 'success':
        showSuccess(text)
        break
      case 'error':
        showError(text)
        break
      case 'warning':
        showWarning(text)
        break
      case 'info':
      default:
        showInfo(text)
        break
    }
  }
  
  // Funciones de gestión del formulario
  const resetForm = (mapRadius, clearMap, createDefaultSchedule, formErrors, showDescriptionHint, showNameHint, form) => {
    // Resetear datos del formulario
    areaForm.value = {
      name: '',
      description: '',
      latitude: '',
      longitude: '',
      radius: 200,
      status: 'active'  // CRÍTICO: Incluir status por defecto
    }
    
    // Resetear variables de edición
    editingArea.value = null
    
    // Resetear mapa
    if (mapRadius) mapRadius.value = 10
    if (clearMap) clearMap()
    
    // Resetear horarios
    if (createDefaultSchedule) createDefaultSchedule()
    
    // Limpiar errores del formulario
    if (formErrors) {
      Object.keys(formErrors.value).forEach(key => {
        formErrors.value[key] = ''
      })
    }
    
    // Ocultar hints
    if (showDescriptionHint) showDescriptionHint.value = false
    if (showNameHint) showNameHint.value = false
    
    // Resetear validación del formulario
    if (form && form.value) {
      form.value.resetValidation()
    }
    
    console.log('📝 Formulario reseteado')
  }
  
  const openNewAreaDialog = (resetForm, showDialog) => {
    console.log('🆕 Abriendo diálogo para nueva área')
    resetForm()
    showDialog.value = true
  }
  
  const cancelDialog = (showDialog, editingArea, resetForm) => {
    console.log('❌ Cancelando diálogo')
    showDialog.value = false
    // Solo resetear si estábamos creando (no editando)
    if (!editingArea.value) {
      resetForm()
    }
  }
  
  const confirmDelete = async (areaToDelete, areas, showDeleteDialog, loadAreas) => {
    if (!areaToDelete.value) return
    
    deleting.value = true
    try {
      // Eliminar desde API
      await areaService.delete(areaToDelete.value.id)
      
      // Actualizar el estado del área en lugar de removerla
      const index = areas.value.findIndex(area => area.id === areaToDelete.value.id)
      if (index !== -1) {
        areas.value[index].status = 'inactive'
      }
      
      showDeleteDialog.value = false
      areaToDelete.value = null
      
      showMessage('Área desactivada correctamente')
      console.log('Área eliminada exitosamente')
      
      // Recargar la lista para mostrar el cambio de estado
      await loadAreas()
    } catch (error) {
      console.error('Error eliminando área:', error)
      // Mostrar mensaje de error al usuario
      alert('Error eliminando área: ' + (error.response?.data?.message || error.message))
    } finally {
      deleting.value = false
    }
  }
  
  const saveArea = async (areaForm, scheduleType, schedule, validateSchedule, updateLocalArea, areas, sortAreasAlphabetically, loadAreas, resetForm, editingArea) => {
    console.log('🚀 === INICIO DE SAVEAREA ===')
    console.log('🔍 Iniciando saveArea...')
    console.log('📝 Datos del formulario:', areaForm.value)
    console.log('🔍 scheduleType.value:', scheduleType.value)
    console.log('🔍 schedule.value:', schedule.value)
    
    try {
      // Validación básica del formulario
      if (!areaForm.value.name || !areaForm.value.description || !areaForm.value.latitude || !areaForm.value.longitude || !areaForm.value.radius) {
        console.error('❌ Validación del formulario falló')
        showMessage('⚠️ Por favor, completa todos los campos obligatorios correctamente', 'warning')
        return
      }
      
      console.log('✅ Validación del formulario pasó')
      
      // La validación de Vuetify se debe hacer en el componente padre antes de llamar a esta función
      console.log('✅ Validación de Vuetify omitida (se debe hacer en el componente padre)')
      
      // ✅ Validar horarios antes de continuar
      if (!validateSchedule()) {
        console.error('❌ Validación de horarios falló')
        return
      }
      
      console.log('✅ Validación de horarios pasó')
      
      console.log('🔍 Antes de validación de ubicación...')
      console.log('🔍 areaForm.value.latitude:', areaForm.value.latitude)
      console.log('🔍 areaForm.value.longitude:', areaForm.value.longitude)
      
      // VALIDACIÓN CRÍTICA: Verificar que se haya seleccionado una ubicación
      if (!areaForm.value.latitude || !areaForm.value.longitude) {
        console.error('❌ No se ha seleccionado ubicación en el mapa')
        alert('⚠️ Debes seleccionar una ubicación en el mapa antes de guardar el área.')
        return
      }
      
      console.log('✅ Validación de ubicación pasó')
      
      // Validar que las coordenadas sean números válidos
      const lat = parseFloat(areaForm.value.latitude)
      const lng = parseFloat(areaForm.value.longitude)
      
      if (isNaN(lat) || isNaN(lng)) {
        console.error('❌ Coordenadas no son números válidos:', {
          latitude: areaForm.value.latitude,
          longitude: areaForm.value.longitude
        })
        alert('⚠️ Las coordenadas deben ser números válidos.')
        return
      }
      
      // Validar rangos de coordenadas
      if (lat < -90 || lat > 90) {
        console.error('❌ Latitud fuera de rango:', lat)
        alert('⚠️ La latitud debe estar entre -90 y 90 grados.')
        return
      }
      
      if (lng < -180 || lng > 180) {
        console.error('❌ Longitud fuera de rango:', lng)
        alert('⚠️ La longitud debe estar entre -180 y 180 grados.')
        return
      }

      // Verificar que el radio sea válido
      if (!areaForm.value.radius || areaForm.value.radius < 10) {
        console.error('❌ Radio inválido')
        alert('⚠️ El radio debe ser de al menos 10 metros.')
        return
      }
      
      // Validar que el radio sea un número
      const radius = parseInt(areaForm.value.radius)
      if (isNaN(radius) || radius < 10 || radius > 10000) {
        console.error('❌ Radio fuera de rango:', radius)
        alert('⚠️ El radio debe estar entre 10 y 10000 metros.')
        return
      }
      
      saving.value = true
      
      // Preparar datos del área con horarios
      const areaData = { ...areaForm.value }
      
      // Agregar horarios según el tipo seleccionado
      if (scheduleType.value === 'default') {
        // ✅ Horario por defecto - usar valores del formulario validados
        areaData.schedule = {
          schedule_type: 'default',
          monday_active: schedule.value.monday_active,
          monday_start: schedule.value.monday_start,
          monday_end: schedule.value.monday_end,
          tuesday_active: schedule.value.tuesday_active,
          tuesday_start: schedule.value.tuesday_start,
          tuesday_end: schedule.value.tuesday_end,
          wednesday_active: schedule.value.wednesday_active,
          wednesday_start: schedule.value.wednesday_start,
          wednesday_end: schedule.value.wednesday_end,
          thursday_active: schedule.value.thursday_active,
          thursday_start: schedule.value.thursday_start,
          thursday_end: schedule.value.thursday_end,
          friday_active: schedule.value.friday_active,
          friday_start: schedule.value.friday_start,
          friday_end: schedule.value.friday_end,
          saturday_active: schedule.value.saturday_active,
          saturday_start: schedule.value.saturday_start,
          saturday_end: schedule.value.saturday_end,
          sunday_active: schedule.value.sunday_active,
          sunday_start: schedule.value.sunday_start,
          sunday_end: schedule.value.sunday_end,
          grace_period_minutes: schedule.value.grace_period_minutes
        }
        console.log('✅ Horario por defecto configurado desde formulario:', areaData.schedule)
      } else if (scheduleType.value === 'custom') {
        // ✅ Horario personalizado - incluir todos los campos
        areaData.schedule = {
          schedule_type: 'custom',
          monday_active: schedule.value.monday_active,
          monday_start: schedule.value.monday_start,
          monday_end: schedule.value.monday_end,
          tuesday_active: schedule.value.tuesday_active,
          tuesday_start: schedule.value.tuesday_start,
          tuesday_end: schedule.value.tuesday_end,
          wednesday_active: schedule.value.wednesday_active,
          wednesday_start: schedule.value.wednesday_start,
          wednesday_end: schedule.value.wednesday_end,
          thursday_active: schedule.value.thursday_active,
          thursday_start: schedule.value.thursday_start,
          thursday_end: schedule.value.thursday_end,
          friday_active: schedule.value.friday_active,
          friday_start: schedule.value.friday_start,
          friday_end: schedule.value.friday_end,
          saturday_active: schedule.value.saturday_active,
          saturday_start: schedule.value.saturday_start,
          saturday_end: schedule.value.saturday_end,
          sunday_active: schedule.value.sunday_active,
          sunday_start: schedule.value.sunday_start,
          sunday_end: schedule.value.sunday_end,
          grace_period_minutes: schedule.value.grace_period_minutes
        }
        console.log('✅ Horario personalizado configurado:', areaData.schedule)
      } else {
        // ✅ Sin horario
        areaData.schedule = {
          schedule_type: 'none'
        }
        console.log('✅ Sin horario configurado')
      }
      
      console.log('📤 Datos del área con horarios:', areaData)
      
      if (editingArea.value) {
        console.log('🔄 === ACTUALIZANDO ÁREA EXISTENTE ===')
        console.log('🔍 ID del área a editar:', editingArea.value.id)
        
        // Actualizar área existente
        const updatedArea = await areaService.update(editingArea.value.id, areaData)
        console.log('📥 Respuesta del backend (update):', updatedArea)
        
        // ✅ ACTUALIZAR INMEDIATAMENTE el área en la lista local
        updateLocalArea(updatedArea)
        
        // Cerrar modal y resetear formulario
        showDialog.value = false
        resetForm()
        
        showSuccess('✅ Área actualizada correctamente')
        console.log('✅ Área actualizada exitosamente')
      } else {
        console.log('🆕 Creando nueva área...')
        console.log('📤 Datos enviados al servicio:', areaData)
        
        // Crear nueva área
        const newArea = await areaService.create(areaData)
        console.log('📥 Respuesta del backend (create):', newArea)
        
        // Agregar nueva área a la lista
        areas.value.push({ ...newArea })
        
        // Reordenar la lista alfabéticamente después de agregar
        areas.value = sortAreasAlphabetically([...areas.value])
        
        console.log('✅ Área creada y lista reordenada alfabéticamente')
        console.log('📋 Nuevo orden:', areas.value.map(area => area.name))
      }
      
      // CRÍTICO: Guardar ID del área editada antes de resetear
      const editedAreaId = editingArea.value?.id
      
      showDialog.value = false
      
      // ✅ Recargar áreas solo si es necesario (después de un breve delay para asegurar sincronización)
      setTimeout(async () => {
        try {
          console.log('🔄 Recargando áreas para sincronización...')
          await loadAreas()
          console.log('✅ Áreas recargadas para sincronización')
        } catch (error) {
          console.error('❌ Error recargando áreas:', error)
        }
      }, 500)
      
      // Si acabamos de editar un área, verificar que los datos se guardaron correctamente
      if (editedAreaId) {
        try {
          console.log('🔄 Verificando datos guardados del área editada ID:', editedAreaId)
          const freshAreaData = await areaService.getById(editedAreaId)
          console.log('📊 Datos frescos del área después de guardar:', freshAreaData)
          
          // Verificar que las coordenadas se guardaron correctamente
          if (freshAreaData.latitude && freshAreaData.longitude) {
            console.log('✅ Coordenadas verificadas en BD:', {
              latitude: freshAreaData.latitude,
              longitude: freshAreaData.longitude,
              radius: freshAreaData.radius
            })
          } else {
            console.warn('⚠️ Las coordenadas no se guardaron correctamente en la BD')
          }
        } catch (error) {
          console.error('❌ Error verificando datos guardados:', error)
        }
      }
      
      // Resetear formulario DESPUÉS de verificar
      resetForm()
      
      console.log('🎉 Proceso completado exitosamente')
    } catch (error) {
      console.error('❌ Error guardando área:', error)
      console.error('📊 Detalles del error:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        statusText: error.response?.statusText
      })
      
      // Mostrar mensaje de error al usuario
      alert('Error guardando área: ' + (error.response?.data?.message || error.message))
    } finally {
      saving.value = false
    }
  }
  
  return {
    showDialog,
    saving,
    editingArea,
    areaToDelete,
    showDeleteDialog,
    deleting,
    areaForm,
    formatCoordinate,
    showMessage,
    resetForm,
    openNewAreaDialog,
    cancelDialog,
    confirmDelete,
    saveArea
  }
}
