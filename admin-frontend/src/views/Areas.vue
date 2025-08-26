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

<style>
@import '../styles/areas.css';
</style>
