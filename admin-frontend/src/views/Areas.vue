<template>
  <div>
    <v-row class="mt-2 areas-header">
      <v-col cols="12">
        <div class="d-flex justify-space-between align-center">
          <h1 class="text-h4 text-white">Gestión de Áreas</h1>
          <v-btn color="blue-400" prepend-icon="mdi-plus" @click="showDialog = true" class="neon-border">
            Nueva Área
          </v-btn>
        </div>
      </v-col>
    </v-row>

    <!-- Tabla de Áreas -->
    <v-card class="bg-dark-surface border border-blue-500/20">
      <v-card-title class="text-white">
        <v-text-field
          v-model="search"
          append-icon="mdi-magnify"
          label="Buscar área"
          single-line
          hide-details
          variant="outlined"
          density="compact"
          color="blue-400"
          class="text-white"
        ></v-text-field>
      </v-card-title>

             <v-data-table
         :headers="headers"
         :items="areas"
         :search="search"
         :loading="loading"
         class="elevation-1 bg-dark-surface"
         theme="dark"
         :no-data-text="loading ? 'Cargando áreas...' : 'No hay áreas registradas'"
         :no-results-text="'No se encontraron áreas que coincidan con la búsqueda'"
       >
        <template v-slot:item.actions="{ item }">
          <v-btn icon="mdi-map-marker" size="small" color="green-400" @click="showMap(item)" title="Ver ubicación"></v-btn>
          <v-btn icon="mdi-pencil" size="small" color="blue-400" @click="editArea(item)" title="Editar área"></v-btn>
          <v-btn icon="mdi-delete" size="small" color="red-400" @click="deleteArea(item)" title="Eliminar área"></v-btn>
        </template>
        
        <template v-slot:item.latitude="{ item }">
          <span :title="item.latitude">{{ formatCoordinate(item.latitude) }}</span>
        </template>
        
        <template v-slot:item.longitude="{ item }">
          <span :title="item.longitude">{{ formatCoordinate(item.longitude) }}</span>
        </template>
        
        <template v-slot:item.radius="{ item }">
          {{ item.radius }}m
        </template>
        
        <template v-slot:item.employee_count="{ item }">
          <div class="d-flex justify-center">
            <v-chip :color="item.employee_count > 0 ? 'green-500' : 'grey-500'" size="small" variant="tonal">
              {{ item.employee_count }}
            </v-chip>
          </div>
        </template>
      </v-data-table>
    </v-card>

    <!-- Dialog para Crear/Editar Área -->
    <v-dialog v-model="showDialog" max-width="700px">
      <v-card class="bg-dark-surface border border-blue-500/20">
        <v-card-title class="text-white">
          <span class="text-h5">{{ editingArea ? 'Editar' : 'Nueva' }} Área</span>
        </v-card-title>
        
        <v-card-text>
          <v-form ref="form" v-model="valid">
            <v-row>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="areaForm.name"
                  label="Nombre del Área"
                  required
                  :rules="[v => !!v || 'Nombre es requerido']"
                  color="blue-400"
                  variant="outlined"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="areaForm.description"
                  label="Descripción"
                  required
                  :rules="[v => !!v || 'Descripción es requerida']"
                  color="blue-400"
                  variant="outlined"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12">
                <v-btn 
                  color="green-400" 
                  variant="outlined" 
                  prepend-icon="mdi-map-marker" 
                  @click="showMapSelectorModal"
                  class="mb-4"
                  block
                >
                  📍 Seleccionar Ubicación en el Mapa
                </v-btn>
              </v-col>
              
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="areaForm.latitude"
                  label="Latitud"
                  type="number"
                  step="0.000001"
                  required
                  :rules="[v => !!v || 'Latitud es requerida']"
                  color="blue-400"
                  variant="outlined"
                  readonly
                  prepend-icon="mdi-crosshairs-gps"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="areaForm.longitude"
                  label="Longitud"
                  type="number"
                  step="0.000001"
                  required
                  :rules="[v => !!v || 'Longitud es requerida']"
                  color="blue-400"
                  variant="outlined"
                  readonly
                  prepend-icon="mdi-crosshairs-gps"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="areaForm.radius"
                  label="Radio (metros)"
                  type="number"
                  min="10"
                  max="10000"
                  required
                  :rules="[v => !!v || 'Radio es requerido', v => v >= 10 || 'Radio mínimo 10m', v => v <= 10000 || 'Radio máximo 10km']"
                  color="blue-400"
                  variant="outlined"
                  prepend-icon="mdi-radius"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12">
                <v-textarea
                  v-model="areaForm.notes"
                  label="Notas Adicionales"
                  rows="3"
                  variant="outlined"
                  color="blue-400"
                ></v-textarea>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey-400" variant="text" @click="showDialog = false">Cancelar</v-btn>
          <v-btn color="blue-400" @click="saveArea" :loading="saving" class="neon-border">Guardar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog del Selector de Mapa -->
    <v-dialog v-model="showMapSelector" max-width="900px" persistent>
      <v-card class="bg-dark-surface border border-blue-500/20">
        <v-card-title class="text-white">
          <span class="text-h5">🗺️ Seleccionar Ubicación en el Mapa</span>
        </v-card-title>
        
        <v-card-text>
          <div class="map-container">
            <!-- Campo de búsqueda -->
            <div class="map-search mb-4">
              <v-text-field
                id="map-search"
                v-model="searchPlace"
                label="Buscar lugar (ej: Universidad Estatal de Milagro)"
                prepend-icon="mdi-magnify"
                variant="outlined"
                color="blue-400"
                clearable
                @input="onSearchInput"
              ></v-text-field>
            </div>
            
            <!-- Controles del mapa -->
            <div class="map-controls mb-4">
              <v-row>
                <v-col cols="12" sm="6">
                  <v-slider
                    v-model="mapRadius"
                    :min="10"
                    :max="1000"
                    :step="10"
                    label="Radio del Área (metros)"
                    color="blue-400"
                    thumb-label="always"
                    prepend-icon="mdi-radius"
                  ></v-slider>
                </v-col>
                <v-col cols="12" sm="6">
                  <div class="d-flex align-center gap-4">
                    <v-chip color="blue-400" variant="tonal">
                      Radio: {{ mapRadius }}m
                    </v-chip>
                    <v-chip v-if="isLocating" color="orange-400" variant="tonal">
                      <v-icon left>mdi-crosshairs-gps</v-icon>
                      Obteniendo ubicación...
                    </v-chip>
                    <v-chip v-else-if="userLocation" color="green-400" variant="tonal">
                      <v-icon left>mdi-crosshairs-gps</v-icon>
                      Ubicación actual
                    </v-chip>
                    <v-chip v-if="selectedLocation" color="blue-400" variant="tonal">
                      Ubicación seleccionada
                    </v-chip>
                  </div>
                </v-col>
              </v-row>
            </div>
            
            <!-- Contenedor del mapa -->
            <div id="map-selector" class="map-wrapper"></div>
            
                         <!-- Instrucciones -->
             <div class="map-instructions mt-4">
               <v-alert type="info" variant="tonal" density="compact">
                 <template v-slot:prepend>
                   <v-icon>mdi-information</v-icon>
                 </template>
                 <strong>Instrucciones:</strong> 
                 <br>• Escribe el nombre del lugar y presiona ENTER (ej: "Universidad Estatal de Milagro")
                 <br>• Haz clic en el mapa para marcar la ubicación exacta del área
                 <br>• Ajusta el radio con el control deslizante
                 <br>• Las coordenadas se llenarán automáticamente
               </v-alert>
               
                               <!-- Mensaje sobre mapa -->
                <v-alert v-if="!googleMapsAvailable" type="warning" variant="tonal" density="compact" class="mt-2">
                  <template v-slot:prepend>
                    <v-icon>mdi-alert</v-icon>
                  </template>
                  <strong>⚠️ Mapa no está disponible</strong>
                  <br>Verifica tu conexión a internet para cargar OpenStreetMap
                </v-alert>
             </div>
          </div>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey-400" variant="text" @click="cancelMapSelection">Cancelar</v-btn>
          <v-btn 
            color="blue-400" 
            @click="confirmMapSelection" 
            :disabled="!selectedLocation"
            class="neon-border"
          >
            Confirmar Ubicación
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog de Confirmación para Eliminar -->
    <v-dialog v-model="showDeleteDialog" max-width="400px">
      <v-card class="bg-dark-surface border border-blue-500/20">
        <v-card-title class="text-h5 text-white">Confirmar Eliminación</v-card-title>
        <v-card-text class="text-grey-300">
          ¿Estás seguro de que quieres eliminar el área <strong>{{ areaToDelete?.name }}</strong>?
          <br><br>
          <v-alert type="warning" variant="tonal">
            Esta acción no se puede deshacer y eliminará todas las referencias a esta área.
          </v-alert>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey-400" variant="text" @click="showDeleteDialog = false">Cancelar</v-btn>
          <v-btn color="red-400" @click="confirmDelete" :loading="deleting">Eliminar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog del Mapa -->
    <v-dialog v-model="showMapDialog" max-width="800px">
      <v-card class="bg-dark-surface border border-blue-500/20">
        <v-card-title class="text-white">
          <span class="text-h5">Ubicación del Área: {{ selectedArea?.name }}</span>
        </v-card-title>
        
        <v-card-text>
          <div class="text-center pa-8">
            <v-icon size="64" color="green-400">mdi-map-marker</v-icon>
            <div class="text-h6 mt-4 text-white">Mapa de Ubicación</div>
            <div class="text-body-2 text-grey-300 mb-4">
              Coordenadas: {{ selectedArea?.latitude }}, {{ selectedArea?.longitude }}
              <br>
              Radio: {{ selectedArea?.radius }} metros
            </div>
            <v-alert type="info" variant="tonal">
              Aquí se implementará un mapa interactivo para visualizar y editar la ubicación del área.
            </v-alert>
          </div>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue-400" @click="showMapDialog = false" class="neon-border">Cerrar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
 import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import areaService from '../services/areaService'
import useOptimizedMap from '../composables/useOptimizedMap'

export default {
  name: 'Areas',
  setup() {
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
      clearMap
    } = useOptimizedMap('map-selector')
    
    const search = ref('')
    const loading = ref(false)
    const saving = ref(false)
    const deleting = ref(false)
    
    // Función para formatear coordenadas (mostrar solo primeros 10 caracteres)
    const formatCoordinate = (coordinate) => {
      if (!coordinate) return '-'
      const coordStr = coordinate.toString()
      return coordStr.length > 10 ? coordStr.substring(0, 10) + '...' : coordStr
    }
    const showDialog = ref(false)
    const showDeleteDialog = ref(false)
    const showMapDialog = ref(false)
    const showMapSelector = ref(false)
    const valid = ref(false)
    const form = ref(null)
    
    const editingArea = ref(null)
    const areaToDelete = ref(null)
    const selectedArea = ref(null)
    
         // Variables para el selector de mapa
     const mapRadius = ref(100)
     const userLocation = ref(null)
     const isLocating = ref(false)
     const searchPlace = ref('')
     const googleMapsAvailable = ref(true) // Siempre true con el servicio optimizado
    
    const areas = ref([])
    
    const areaForm = ref({
      name: '',
      description: '',
      latitude: '',
      longitude: '',
      radius: 100,
      notes: ''
    })
    
    const headers = [
      { title: 'Nombre', key: 'name', sortable: true },
      { title: 'Descripción', key: 'description', sortable: true },
      { title: 'Latitud', key: 'latitude', sortable: true, width: '120px' },
      { title: 'Longitud', key: 'longitude', sortable: true, width: '120px' },
      { title: 'Radio', key: 'radius', sortable: true },
      { title: 'Empleados', key: 'employee_count', sortable: true },
      { title: 'Acciones', key: 'actions', sortable: false }
    ]
    
             const loadAreas = async () => {
      loading.value = true
      try {
        const areasData = await areaService.getAll()
        // El backend devuelve {count, next, previous, results}
        // Necesitamos acceder a results que es el array de áreas
        const areasArray = areasData.results || areasData
        areas.value = areasArray.map(area => ({
          ...area,
          employee_count: area.employees?.length || 0
        }))
        console.log('Áreas cargadas:', areas.value)
      } catch (error) {
        console.error('Error cargando áreas:', error)
        // Mostrar mensaje de error al usuario
        areas.value = []
        if (error.response?.status === 401) {
          alert('Error de autenticación. Por favor, inicia sesión nuevamente.')
        } else if (error.response?.status === 403) {
          alert('No tienes permisos para ver las áreas.')
        } else if (error.response?.status >= 500) {
          alert('Error del servidor. Por favor, intenta más tarde.')
        } else {
          alert('Error cargando áreas: ' + (error.response?.data?.message || error.message))
        }
      } finally {
        loading.value = false
      }
    }
    
                   const editArea = async (area) => {
        try {
          // Cargar datos completos del área desde la API
          const fullArea = await areaService.getById(area.id)
          editingArea.value = fullArea
          areaForm.value = { 
            name: fullArea.name,
            description: fullArea.description,
            latitude: fullArea.latitude,
            longitude: fullArea.longitude,
            radius: fullArea.radius,
            notes: fullArea.notes || ''
          }
          
          // Guardar las coordenadas para usar en el mapa
          editingArea.value.savedCoordinates = {
            lat: parseFloat(fullArea.latitude),
            lng: parseFloat(fullArea.longitude)
          }
          
          showDialog.value = true
          console.log('Editando área:', fullArea)
          console.log('Coordenadas guardadas para el mapa:', editingArea.value.savedCoordinates)
        } catch (error) {
          console.error('Error cargando área para editar:', error)
          alert('Error cargando área: ' + (error.response?.data?.message || error.message))
        }
      }
    
    const deleteArea = (area) => {
      areaToDelete.value = area
      showDeleteDialog.value = true
    }
    
    const activateArea = async (area) => {
      try {
        await areaService.activate(area.id)
        // Recargar áreas para actualizar el estado
        await loadAreas()
        alert(`Área ${area.name} reactivada correctamente`)
      } catch (error) {
        console.error('Error reactivando área:', error)
        alert('Error reactivando área: ' + (error.response?.data?.message || error.message))
      }
    }
    
    const showMap = (area) => {
      selectedArea.value = area
      showMapDialog.value = true
    }
    
         const confirmDelete = async () => {
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
         
         console.log('Área eliminada exitosamente')
       } catch (error) {
         console.error('Error eliminando área:', error)
         // Mostrar mensaje de error al usuario
         alert('Error eliminando área: ' + (error.response?.data?.message || error.message))
       } finally {
         deleting.value = false
       }
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
      
      showMapSelector.value = true
      
      // Usar nextTick para asegurar que el modal esté renderizado
      await nextTick()
      
      try {
        // Inicializar mapa optimizado
        if (editingArea.value && editingArea.value.savedCoordinates) {
          console.log('📍 Editando área - usando coordenadas guardadas')
          await initMap({
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
        } else {
          console.log('📱 Nueva área - obteniendo ubicación del usuario')
          await initMap()
          
          // Intentar obtener ubicación actual con radio
          try {
            await getCurrentLocation({
              radius: mapRadius.value,
              title: 'Tu ubicación actual'
            })
          } catch (error) {
            console.log('📍 Usando ubicación por defecto (Ciudad de México)')
            // La ubicación por defecto ya está configurada en el servicio
            // Asegurar que se muestre el radio en la ubicación por defecto
            if (selectedLocation.value) {
              setRadius(selectedLocation.value.lat, selectedLocation.value.lng, mapRadius.value)
            }
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
        areaForm.value.latitude = selectedLocation.value.lat
        areaForm.value.longitude = selectedLocation.value.lng
        areaForm.value.radius = mapRadius.value
        showMapSelector.value = false
        
        console.log('✅ Ubicación confirmada:', selectedLocation.value)
      }
    }
    
    const cancelMapSelection = () => {
      // Limpiar la selección actual
      clearMap()
      showMapSelector.value = false
      console.log('❌ Selección de mapa cancelada')
    }
    
             const saveArea = async () => {
      console.log('🔍 Iniciando saveArea...')
      console.log('📝 Datos del formulario:', areaForm.value)
      console.log('✅ Validación del formulario:', form.value.validate())
      
      if (!form.value.validate()) {
        console.error('❌ Validación del formulario falló')
        return
      }
      
      saving.value = true
      try {
        if (editingArea.value) {
          console.log('✏️ Actualizando área existente...')
          // Actualizar área existente
          const updatedArea = await areaService.update(editingArea.value.id, areaForm.value)
          const index = areas.value.findIndex(area => area.id === editingArea.value.id)
          if (index !== -1) {
            areas.value[index] = { ...updatedArea, employee_count: updatedArea.employees?.length || 0 }
          }
          console.log('✅ Área actualizada:', updatedArea)
        } else {
          console.log('🆕 Creando nueva área...')
          console.log('📤 Datos enviados al servicio:', areaForm.value)
          
          // Crear nueva área
          const newArea = await areaService.create(areaForm.value)
          console.log('✅ Respuesta del servicio:', newArea)
          
          areas.value.push({ ...newArea, employee_count: 0 })
          console.log('✅ Área creada:', newArea)
        }
        
        showDialog.value = false
        editingArea.value = null
        areaForm.value = {
          name: '',
          description: '',
          latitude: '',
          longitude: '',
          radius: 100,
          notes: ''
        }
        
        // Recargar áreas para asegurar datos actualizados
        await loadAreas()
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
    
                  onMounted(() => {
      loadAreas()
      // El mapService se inicializa automáticamente
      console.log('🚀 Componente Areas cargado - Mapa optimizado listo')
     })
    
        return {
      search,
      loading,
      saving,
      deleting,
      showDialog,
      showDeleteDialog,
      showMapDialog,
      showMapSelector,
      valid,
      form,
      editingArea,
      areaToDelete,
      selectedArea,
      areas,
      areaForm,
      headers,
      // Variables del mapa optimizado
      mapRadius,
      selectedLocation,
      isMapReady,
      mapLoading,
      userLocation,
      isLocating,
      searchPlace,
      googleMapsAvailable,
      // Funciones principales
      editArea,
      deleteArea,
      activateArea,
      showMap,
      confirmDelete,
      saveArea,
      // Funciones del mapa optimizado
      showMapSelectorModal,
      confirmMapSelection,
      cancelMapSelection,
      onSearchInput,
      clearMap,
      // Funciones de formateo
      formatCoordinate
    }
  }
}
</script>
