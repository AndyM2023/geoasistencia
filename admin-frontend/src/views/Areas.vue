<template>
  <div class="areas-container">
    <!-- Header con botones -->
    <AreasHeader @newArea="openNewAreaDialog" />

    <!-- Tabla de Áreas -->
    <AreasTable
      :areas="areas"
      :loading="loading"
      :tableKey="tableKey"
      @edit="editArea"
      @delete="deleteArea"
      @activate="activateArea"
    />

    <!-- NUEVO COMPONENTE AreaForm -->
    <AreaForm
      v-model:showDialog="showDialog"
      v-model:areaForm="areaForm"
      v-model:scheduleType="scheduleType"
      v-model:schedule="schedule"
      :editingArea="editingArea"
      :formErrors="formErrors"
      :saving="saving"
      @save="saveArea"
      @cancel="cancelDialog"
      @showMapSelector="showMapSelectorModal"
      @validateField="validateField"
      @sanitizeName="sanitizeName"
      @sanitizeDescription="sanitizeDescription"
      @createDefaultSchedule="createDefaultSchedule"
      @validateScheduleField="validateScheduleField"
      @getScheduleSummary="getScheduleSummary"
    />

    <!-- Selector de Mapa -->
    <MapSelector
      v-model:showMapSelector="showMapSelector"
      v-model:mapRadius="mapRadius"
      :selectedLocation="selectedLocation"
      :isLocating="isLocating"
      :userLocation="userLocation"
      :googleMapsAvailable="googleMapsAvailable"
      @search="onMapSearch"
      @useCurrentLocation="useCurrentLocation"
      @confirm="confirmMapLocation"
      @cancel="closeMapSelector"
    />
    
    <!-- Servicio del Mapa -->
    <MapService
      v-if="showMapSelector"
      mapId="map-selector"
      :initialLat="selectedLocation?.lat || -2.1894128"
      :initialLng="selectedLocation?.lng || -79.8890662"
      @mapReady="onMapReady"
      @locationSelected="onLocationSelected"
      @radiusChanged="onRadiusChanged"
    />

    <!-- Dialog de Confirmación para Eliminar -->
    <DeleteConfirmationDialog
      v-model:showDeleteDialog="showDeleteDialog"
      :areaToDelete="areaToDelete"
      :deleting="deleting"
      @confirm="confirmDelete"
      @cancel="showDeleteDialog = false"
    />
  </div>
</template>

<script>
import { ref, onMounted, nextTick, watch } from 'vue'
import useOptimizedMap from '../composables/useOptimizedMap'
import { useNotifications } from '../composables/useNotifications'
import useAreas from '../composables/useAreas'
import useSchedule from '../composables/useSchedule'
import useFormValidation from '../composables/useFormValidation'
import useAreaForm from '../composables/useAreaForm'
import AreaForm from '../components/areas/AreaForm.vue'
import AreasTable from '../components/areas/AreasTable.vue'
import AreasHeader from '../components/areas/AreasHeader.vue'
import MapSelector from '../components/areas/MapSelector.vue'
import MapService from '../components/areas/MapService.vue'
import DeleteConfirmationDialog from '../components/areas/DeleteConfirmationDialog.vue'

export default {
  name: 'Areas',
  components: {
    AreaForm,
    AreasTable,
    AreasHeader,
    MapSelector,
    MapService,
    DeleteConfirmationDialog
  },
  setup() {
    const { showSuccess, showError, showWarning, showInfo, showLocationStatus } = useNotifications()
    
    // Usar composables
    const {
      areas,
      loading,
      tableKey,
      loadAreas,
      editArea: editAreaFromComposable,
      deleteArea: deleteAreaFromComposable,
      activateArea: activateAreaFromComposable,
      updateLocalArea,
      sortAreasAlphabetically
    } = useAreas()
    
    const {
      scheduleType,
      schedule,
      scheduleDays,
      getScheduleSummary,
      createDefaultSchedule,
      loadScheduleFromArea,
      validateSchedule
    } = useSchedule()
    
    const {
      formErrors,
      showDescriptionHint,
      descriptionHint,
      showNameHint,
      nameHint,
      validateField: validateFieldFromComposable,
      validateScheduleField,
      validateAllFields,
      validateScheduleDay,
      getScheduleFieldError,
      sanitizeName: sanitizeNameFromComposable,
      sanitizeDescription: sanitizeDescriptionFromComposable,
      clearFormErrors,
      resetHints
    } = useFormValidation()
    
    const {
      showDialog,
      saving,
      editingArea,
      areaToDelete,
      showDeleteDialog,
      deleting,
      areaForm,
      formatCoordinate,
      showMessage,
      resetForm: resetFormFromComposable,
      openNewAreaDialog: openNewAreaDialogFromComposable,
      cancelDialog: cancelDialogFromComposable,
      confirmDelete: confirmDeleteFromComposable,
      saveArea: saveAreaFromComposable
    } = useAreaForm()
    
    // Usar el composable optimizado para mapas
    const {
      isMapReady,
      isLoading: mapLoading,
      selectedLocation,
      initMap,
      setLocation,
      setRadius,
      searchLocation,
      getCurrentLocation,
      clearMap,
      refreshMap
    } = useOptimizedMap('map-selector')
    
    // Variables para el selector de mapa
    const mapRadius = ref(10)
    const userLocation = ref(null)
    const isLocating = ref(false)
    const searchPlace = ref('')
    const googleMapsAvailable = ref(true) // Siempre true con el servicio optimizado
    
    const showMapSelector = ref(false)
    const valid = ref(false)
    const form = ref(null)
    
    // Función para reordenar la lista actual
    const reorderAreasList = () => {
      console.log('🔄 Reordenando lista de áreas alfabéticamente...')
      const currentOrder = areas.value.map(area => area.name)
      console.log('📋 Orden anterior:', currentOrder)
      
      areas.value = sortAreasAlphabetically([...areas.value])
      
      const newOrder = areas.value.map(area => area.name)
      console.log('📋 Nuevo orden:', newOrder)
      console.log('✅ Lista reordenada correctamente')
    }
    
    // Funciones de validación del formulario
    const validateField = (fieldName) => {
      return validateFieldFromComposable(fieldName, areaForm.value, scheduleType.value, schedule.value)
    }
    
    const sanitizeName = (event) => {
      sanitizeNameFromComposable(event, areaForm.value)
    }
    
    const sanitizeDescription = (event) => {
      sanitizeDescriptionFromComposable(event, areaForm.value)
    }
    
    // Funciones para el selector de mapa optimizado
    const onSearchInput = async () => {
      // Función optimizada para búsqueda de lugares
      const query = searchPlace.value?.trim()
      if (!query) return
      
      console.log('🔍 Buscando:', query)
      
      try {
        // Usar el servicio optimizado de búsqueda
        await searchLocation(query)
        console.log('✅ Búsqueda completada')
      } catch (error) {
        console.error('❌ Error en la búsqueda:', error)
        alert('Error en la búsqueda. Verifica tu conexión a internet.')
      }
    }

    // Observar cambios en el radio del mapa
    watch(mapRadius, (newRadius) => {
      if (selectedLocation.value && isMapReady.value) {
        // Actualizar el radio usando el servicio optimizado
        setRadius(
          selectedLocation.value.lat,
          selectedLocation.value.lng,
          newRadius,
          {
               color: '#3b82f6',
               fillColor: '#3b82f6',
               fillOpacity: 0.3,
               weight: 2
          }
        )
      }
    })

    // Observar cambios en la ubicación seleccionada para sincronizar el radio
    watch(selectedLocation, (newLocation) => {
      if (newLocation && isMapReady.value) {
        // Asegurar que el radio se muestre cuando se selecciona una nueva ubicación
        setRadius(
          newLocation.lat,
          newLocation.lng,
          mapRadius.value,
          {
             color: '#3b82f6',
             fillColor: '#3b82f6',
             fillOpacity: 0.3,
             weight: 2
          }
        )
      }
    })
    
    const showMapSelectorModal = async () => {
      console.log('🗺️ Abriendo modal del mapa optimizado...')
      console.log('🔔 Estado inicial de isLocating:', isLocating.value)
      
      showMapSelector.value = true
      
      // Usar nextTick para asegurar que el modal esté renderizado
      await nextTick()
      
      try {
        // CRÍTICO: Siempre refrescar el mapa para evitar problemas de cache
        console.log('🔄 Refrescando mapa para evitar problemas de estado...')
        
        // Inicializar mapa optimizado
        if (editingArea.value && editingArea.value.savedCoordinates) {
          console.log('📍 Editando área - usando coordenadas guardadas:', editingArea.value.savedCoordinates)
          
          // Refrescar mapa con coordenadas específicas
          await refreshMap({
            lat: editingArea.value.savedCoordinates.lat,
            lng: editingArea.value.savedCoordinates.lng
          })
          
          // Establecer ubicación con radio
          setLocation(
            editingArea.value.savedCoordinates.lat,
            editingArea.value.savedCoordinates.lng,
            {
              radius: areaForm.value.radius || mapRadius.value,
              title: 'Ubicación actual del área'
            }
          )
          
          // Sincronizar el slider del radio
          if (areaForm.value.radius) {
            mapRadius.value = areaForm.value.radius
          }
          
          console.log('📍 Mapa centrado en:', editingArea.value.savedCoordinates)
        } else {
          console.log('📱 Nueva área - obteniendo ubicación del usuario')
          
          // Refrescar mapa para nueva área
          await refreshMap()
          
          // Mostrar notificación de búsqueda ANTES de obtener la ubicación
          console.log('📍 Mostrando notificación de búsqueda de ubicación...')
          const notificationId = showLocationStatus('getting')
          console.log('🔔 ID de notificación de búsqueda:', notificationId)
          
          // Pequeña pausa para asegurar que la notificación se muestre
          await new Promise(resolve => setTimeout(resolve, 500))
          
          // Intentar obtener ubicación actual con radio
          try {
            isLocating.value = true
            
            await getCurrentLocation({
              radius: mapRadius.value,
              title: 'Tu ubicación actual'
            })
            
            // Esperar a que el mapa se actualice y el punto sea visible
            console.log('📍 Esperando a que el punto aparezca en el mapa...')
            await new Promise(resolve => setTimeout(resolve, 1500))
            
            // Verificar que realmente se haya establecido la ubicación en el mapa
            if (selectedLocation.value) {
              console.log('📍 Ubicación establecida en el mapa:', selectedLocation.value)
              
              // Mostrar notificación de éxito solo después de que el punto esté visible
              console.log('📍 Mostrando notificación de éxito de ubicación...')
              const successId = showLocationStatus('success')
              console.log('🔔 ID de notificación de éxito:', successId)
              
              // Pausa para que se vea la notificación de éxito
              await new Promise(resolve => setTimeout(resolve, 4000))
            } else {
              console.log('⚠️ No se pudo establecer la ubicación en el mapa')
            }
            
          } catch (error) {
            console.log('📍 Usando ubicación por defecto (Ciudad de México)')
            // La ubicación por defecto ya está configurada en el servicio
            // Asegurar que se muestre el radio en la ubicación por defecto
            if (selectedLocation.value) {
              setRadius(selectedLocation.value.lat, selectedLocation.value.lng, mapRadius.value)
            }
            // Mostrar notificación de error
            console.log('📍 Mostrando notificación de error de ubicación...')
            const errorId = showLocationStatus('error')
            console.log('🔔 ID de notificación de error:', errorId)
          } finally {
            isLocating.value = false
          }
        }
        
        console.log('✅ Mapa optimizado listo')
      } catch (error) {
        console.error('❌ Error inicializando mapa:', error)
        alert('Error cargando el mapa. Por favor, intenta de nuevo.')
      }
    }
    
    const confirmMapSelection = () => {
      if (selectedLocation.value) {
        // Actualizar coordenadas en el formulario
        areaForm.value.latitude = selectedLocation.value.lat
        areaForm.value.longitude = selectedLocation.value.lng
        areaForm.value.radius = mapRadius.value
        
        // Validar automáticamente los campos después de establecer los valores
        validateField('latitude')
        validateField('longitude')
        validateField('radius')
        
        console.log('✅ Ubicación confirmada:', selectedLocation.value)
        console.log('📋 Formulario actualizado:', {
          latitude: areaForm.value.latitude,
          longitude: areaForm.value.longitude,
          radius: areaForm.value.radius
        })
        
        // Si estamos editando, actualizar también las coordenadas de referencia
        if (editingArea.value) {
          editingArea.value.savedCoordinates = {
            lat: selectedLocation.value.lat,
            lng: selectedLocation.value.lng
          }
          console.log('🔄 Coordenadas de referencia actualizadas para edición:', editingArea.value.savedCoordinates)
        }
        
        showMapSelector.value = false
      } else {
        console.warn('⚠️ No hay ubicación seleccionada')
      }
    }
    
    const cancelMapSelection = () => {
      // Limpiar la selección actual
      clearMap()
      showMapSelector.value = false
      
      // Si estamos creando una nueva área, limpiar también las coordenadas del formulario
      if (!editingArea.value) {
        areaForm.value.latitude = ''
        areaForm.value.longitude = ''
        areaForm.value.radius = 10
        mapRadius.value = 10
        
        // Validar automáticamente los campos después de limpiarlos
        validateField('latitude')
        validateField('longitude')
        validateField('radius')
      }
      
      console.log('❌ Selección de mapa cancelada')
    }
    
    // Función para usar la ubicación actual del usuario
    const useCurrentLocation = async () => {
      try {
        console.log('📍 Cambiando a ubicación actual del usuario...')
        
        // Mostrar notificación de búsqueda ANTES de obtener la ubicación
        console.log('📍 Mostrando notificación de búsqueda de ubicación...')
        showLocationStatus('getting')
        
        // Pequeña pausa para asegurar que la notificación se muestre
        await new Promise(resolve => setTimeout(resolve, 100))
        
        isLocating.value = true
        
        // Obtener ubicación actual del usuario
        await getCurrentLocation({
          radius: mapRadius.value,
          title: 'Tu ubicación actual'
        })
        
        // Si se obtuvo la ubicación exitosamente, actualizar el formulario
        if (selectedLocation.value) {
          areaForm.value.latitude = selectedLocation.value.lat
          areaForm.value.longitude = selectedLocation.value.lng
          areaForm.value.radius = mapRadius.value
          
          // Validar automáticamente los campos después de establecer los valores
          validateField('latitude')
          validateField('longitude')
          validateField('radius')
          
          // Actualizar también el radio del mapa si es necesario
          if (mapRadius.value !== selectedLocation.value.radius) {
            mapRadius.value = selectedLocation.value.radius || mapRadius.value
          }
          
          console.log('✅ Ubicación actual aplicada:', selectedLocation.value)
          console.log('📋 Formulario actualizado con ubicación actual')
          console.log('📏 Radio actualizado:', mapRadius.value)
          
          // Si estamos editando, actualizar también las coordenadas de referencia
          if (editingArea.value) {
            editingArea.value.savedCoordinates = {
              lat: selectedLocation.value.lat,
              lng: selectedLocation.value.lng
            }
            console.log('🔄 Coordenadas de referencia actualizadas con ubicación actual')
          }
          
          // Esperar a que el mapa se actualice y el punto sea visible
          console.log('📍 Esperando a que el punto aparezca en el mapa...')
          await new Promise(resolve => setTimeout(resolve, 1500))
          
          // Verificar que realmente se haya establecido la ubicación en el mapa
          if (selectedLocation.value) {
            console.log('📍 Ubicación establecida en el mapa:', selectedLocation.value)
            
            // Mostrar mensaje de éxito usando el sistema global
            console.log('📍 Mostrando notificación de éxito de ubicación...')
            showLocationStatus('success')
            
            // Pausa para que se vea la notificación de éxito
            await new Promise(resolve => setTimeout(resolve, 4000))
          } else {
            console.log('⚠️ No se pudo establecer la ubicación en el mapa')
          }
        }
        
      } catch (error) {
        console.error('❌ Error obteniendo ubicación actual:', error)
        console.log('📍 Mostrando notificación de error de ubicación...')
        showLocationStatus('error')
      } finally {
        isLocating.value = false
      }
    }
    
    // Funciones de gestión del formulario
    const resetForm = () => {
      resetFormFromComposable(mapRadius, clearMap, createDefaultSchedule, formErrors, showDescriptionHint, showNameHint, form)
    }
    
    const openNewAreaDialog = () => {
      openNewAreaDialogFromComposable(resetForm, showDialog)
    }
    
    const cancelDialog = () => {
      cancelDialogFromComposable(showDialog, editingArea, resetForm)
    }
    
    const confirmDelete = async () => {
      await confirmDeleteFromComposable(areaToDelete, areas, showDeleteDialog, loadAreas)
    }
    
    const saveArea = async () => {
      await saveAreaFromComposable(areaForm, scheduleType, schedule, validateSchedule, updateLocalArea, areas, sortAreasAlphabetically, loadAreas, resetForm, editingArea)
    }
    
    // Funciones de edición y gestión de áreas
    const editArea = async (area) => {
      try {
        console.log('✏️ Iniciando edición de área:', area.name)
        
        // Cargar datos completos del área desde la API
        const fullArea = await editAreaFromComposable(area)
        if (!fullArea) return
        
        editingArea.value = fullArea
        
        console.log('📊 Datos completos del área desde BD:', fullArea)
        
        // Cargar datos en el formulario
        areaForm.value = { 
          name: fullArea.name,
          description: fullArea.description,
          latitude: fullArea.latitude,
          longitude: fullArea.longitude,
          radius: fullArea.radius,
          status: fullArea.status || 'active'  // CRÍTICO: Incluir status
        }
        
        // Cargar horarios del área
        loadScheduleFromArea(fullArea)
        
        // Sincronizar radio del mapa
        mapRadius.value = fullArea.radius || 100
        
        // Guardar las coordenadas para usar en el mapa
        editingArea.value.savedCoordinates = {
          lat: parseFloat(fullArea.latitude),
          lng: parseFloat(fullArea.longitude)
        }
        
        console.log('📋 Formulario cargado con:', areaForm.value)
        console.log('🕐 Horarios cargados:', schedule.value)
        console.log('📍 Coordenadas para el mapa:', editingArea.value.savedCoordinates)
        
        showDialog.value = true
        console.log('✅ Área cargada para edición:', fullArea)
        console.log('📍 Coordenadas para el mapa:', editingArea.value.savedCoordinates)
      } catch (error) {
        console.error('❌ Error cargando área para editar:', error)
        alert('Error cargando área: ' + (error.response?.data?.message || error.message))
      }
    }
    
    const deleteArea = (area) => {
      // Verificar si el área tiene empleados antes de permitir desactivarla
      if (area.employee_count > 0) {
        showMessage(`No se puede desactivar el área "${area.name}" porque tiene ${area.employee_count} empleado(s) asignado(s). Primero debes reasignar o desactivar los empleados.`, 'warning')
        return
      }
      
      areaToDelete.value = area
      showDeleteDialog.value = true
    }
    
    const activateArea = async (area) => {
      await activateAreaFromComposable(area)
    }
    
    // Funciones del mapa
    const onMapSearch = async (query) => {
      try {
        await searchLocation(query)
      } catch (error) {
        console.error('Error en búsqueda:', error)
      }
    }
    
    const onMapReady = () => {
      console.log('🗺️ Mapa listo')
    }
    
    const onLocationSelected = (location) => {
      console.log('📍 Ubicación seleccionada:', location)
    }
    
    const onRadiusChanged = (radius) => {
      console.log('📏 Radio cambiado:', radius)
    }
    
    const closeMapSelector = () => {
      showMapSelector.value = false
    }
    
    const confirmMapLocation = () => {
      confirmMapSelection()
    }
    
    onMounted(() => {
      console.log('🚀 Componente Areas cargado - Mapa optimizado listo')
    })
    
    return {
      // Variables del composable useAreas
      areas,
      loading,
      tableKey,
      
      // Variables del composable useSchedule
      scheduleType,
      schedule,
      scheduleDays,
      
      // Variables del composable useFormValidation
      formErrors,
      showDescriptionHint,
      descriptionHint,
      showNameHint,
      nameHint,
      
      // Variables del composable useAreaForm
      showDialog,
      saving,
      editingArea,
      areaToDelete,
      showDeleteDialog,
      deleting,
      areaForm,
      
      // Variables del mapa
      showMapSelector,
      mapRadius,
      selectedLocation,
      isMapReady,
      mapLoading,
      userLocation,
      isLocating,
      searchPlace,
      googleMapsAvailable,
      valid,
      form,
      
      // Funciones del composable useAreas
      loadAreas,
      updateLocalArea,
      sortAreasAlphabetically,
      
      // Funciones del composable useSchedule
      getScheduleSummary,
      createDefaultSchedule,
      loadScheduleFromArea,
      validateSchedule,
      
      // Funciones del composable useFormValidation
      validateField,
      validateScheduleField,
      validateAllFields,
      validateScheduleDay,
      getScheduleFieldError,
      sanitizeName,
      sanitizeDescription,
      clearFormErrors,
      resetHints,
      
      // Funciones del composable useAreaForm
      formatCoordinate,
      showMessage,
      resetForm,
      openNewAreaDialog,
      cancelDialog,
      confirmDelete,
      saveArea,
      
      // Funciones locales
      reorderAreasList,
      editArea,
      deleteArea,
      activateArea,
      showMapSelectorModal,
      confirmMapSelection,
      cancelMapSelection,
      useCurrentLocation,
      onSearchInput,
      onMapSearch,
      onMapReady,
      onLocationSelected,
      onRadiusChanged,
      closeMapSelector,
      confirmMapLocation
    }
  }
}
</script>

<style scoped>
/* Contenedor principal sin scroll */
.areas-container {
  overflow: visible !important;
  height: auto !important;
  max-height: none !important;
}

/* Eliminar scroll en el modal del mapa */
.v-dialog .v-card {
  overflow: visible !important;
  max-height: none !important;
}

.v-dialog .v-card-text {
  overflow: visible !important;
  max-height: none !important;
}

/* Eliminar scroll en contenedores específicos */
.map-controls {
  overflow: visible !important;
  max-height: none !important;
}

/* Estilos globales para eliminar scroll */
:deep(.v-data-table) {
  overflow: visible !important;
}

:deep(.v-data-table__wrapper) {
  overflow: visible !important;
}

:deep(.v-card) {
  overflow: visible !important;
}

:deep(.v-card-text) {
  overflow: visible !important;
}

/* Asegurar que no haya scroll en el body cuando se abre el modal */
:deep(body) {
  overflow: visible !important;
}

.map-container {
  background: rgba(30, 41, 59, 0.8);
  border-radius: 12px;
  padding: 12px;
  border: 1px solid rgba(59, 130, 246, 0.2);
  overflow: visible !important;
}

.map-search {
  background: rgba(15, 23, 42, 0.6);
  border-radius: 8px;
  padding: 6px;
  border: 1px solid rgba(59, 130, 246, 0.1);
}

.map-wrapper {
  height: 400px;
  border-radius: 8px;
  overflow: hidden;
  border: 2px solid rgba(59, 130, 246, 0.3);
  margin-top: 8px;
}

.map-instructions {
  background: rgba(15, 23, 42, 0.4);
  border-radius: 8px;
  padding: 12px;
}

/* Estilos para el deslizante más visible */
.radius-control {
  padding: 0;
}

.radius-label {
  display: block;
  color: #cbd5e1;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 4px;
  text-align: center;
}

.radius-slider {
  margin-top: 0;
  width: 100%;
}

.radius-slider :deep(.v-slider) {
  width: 100%;
  min-width: 200px;
}

.radius-slider :deep(.v-slider__track) {
  width: 100% !important;
  min-width: 200px !important;
}

/* Ajustar el slider compacto para el nuevo layout */
.radius-slider-compact :deep(.v-slider) {
  width: 100%;
  min-width: 180px;
}

.radius-slider-compact :deep(.v-slider__track) {
  width: 100% !important;
  min-width: 180px !important;
}

.radius-slider :deep(.v-slider__thumb) {
  background-color: #f97316 !important;
  border: 3px solid #ffffff !important;
  box-shadow: 0 0 10px rgba(249, 115, 22, 0.6) !important;
  transform: scale(1.2) !important;
}

.radius-slider :deep(.v-slider__track) {
  background-color: #fed7aa !important;
  height: 6px !important;
}

.radius-slider :deep(.v-slider__track-fill) {
  background-color: #f97316 !important;
  height: 6px !important;
}

.radius-slider :deep(.v-slider__thumb-label) {
  background-color: #f97316 !important;
  color: white !important;
  font-weight: bold !important;
  font-size: 14px !important;
  padding: 8px 12px !important;
  border-radius: 6px !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
}

.radius-slider :deep(.v-slider__thumb-label::before) {
  border-top-color: #f97316 !important;
}

/* Mejorar la visibilidad de los chips */
.v-chip {
  font-weight: 500 !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2) !important;
  margin: 0 !important;
  padding: 4px 8px !important;
}

/* Estilos para el botón de ubicación actual */
.use-current-location-btn {
  width: 28px !important;
  height: 28px !important;
  min-width: 28px !important;
  padding: 0 !important;
  border-radius: 50% !important;
  transition: all 0.3s ease !important;
  margin: 0 auto !important;
  display: block !important;
}

.use-current-location-btn:hover {
  transform: scale(1.1) !important;
  box-shadow: 0 2px 8px rgba(34, 197, 94, 0.4) !important;
}

.use-current-location-btn .v-icon {
  font-size: 16px !important;
}

/* Centrar perfectamente la columna derecha */
.d-flex.flex-column.align-center.justify-center.text-center {
  align-items: center !important;
  justify-content: center !important;
  text-align: center !important;
  width: 100% !important;
}

/* Centrar el contenedor del mensaje */
.mt-2.text-center {
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  width: 100% !important;
}

/* Estilos para el mensaje informativo */
.text-caption.text-grey-400 {
  font-size: 8px !important;
  line-height: 1.0 !important;
  margin: 0 !important;
  opacity: 0.7 !important;
  white-space: nowrap !important;
  max-width: 90px !important;
  word-wrap: break-word !important;
  hyphens: auto !important;
  text-align: center !important;
}

/* Ajustar el espaciado del mensaje */
.text-caption.text-grey-400.mb-1 {
  margin-bottom: 1px !important;
}

.text-caption.text-grey-400.mb-0 {
  margin-bottom: 0 !important;
}

/* Asegurar que el slider y los elementos se alineen correctamente */
.d-flex.gap-4 {
  align-items: flex-start !important;
  gap: 24px !important;
}

/* Estilos para el chip de ubicación */
.location-chip {
  flex-shrink: 0 !important;
  white-space: nowrap !important;
  margin-top: 0 !important;
}

/* Estilos para el chip de radio */
.radius-chip {
  font-size: 11px !important;
  height: 20px !important;
  padding: 0 6px !important;
  margin: 0 !important;
  text-align: center !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
}

.radius-chip .v-chip__content {
  text-align: center !important;
  width: 100% !important;
  justify-content: center !important;
}

/* Responsive para móviles */
@media (max-width: 768px) {
  .map-search .v-row {
    flex-direction: column;
  }
  
  .map-search .v-col {
    width: 100% !important;
    margin-bottom: 16px;
  }
  
  .radius-slider :deep(.v-slider__thumb) {
    transform: scale(1.5) !important;
  }
}
 
/* Responsive para el header */
@media (max-width: 768px) {
  .areas-header .d-flex {
    flex-direction: column;
    gap: 16px;
  }
  
  .v-card-title .d-flex {
    flex-direction: column;
    gap: 16px;
  }
}

/* Responsive para horarios */
@media (max-width: 768px) {
  .schedule-section {
    padding: 16px;
  }
  
  .day-config .v-row {
    flex-direction: column;
  }
  
  .day-config .v-col {
    width: 100% !important;
    margin-bottom: 8px;
  }
}

/* Responsive para el scroll */
@media (max-width: 768px) {
  .area-form-scroll-wrapper {
    max-height: 60vh;
    padding: 16px;
  }
}

@media (max-height: 800px) {
  .area-form-scroll-wrapper {
    max-height: 65vh;
  }
}
</style>
