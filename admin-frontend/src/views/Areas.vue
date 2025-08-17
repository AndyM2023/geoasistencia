<template>
  <div>
    <v-row class="mt-2 areas-header">
      <v-col cols="12">
        <div class="d-flex justify-space-between align-center">
          <h1 class="text-h4 text-white">Gestión de Áreas</h1>
          <div class="d-flex gap-2">
            <!-- ✅ BOTÓN DE CONTROL DE POLLING -->
            <v-btn 
              :color="pollingEnabled ? 'green-400' : 'orange-400'" 
              :icon="pollingEnabled ? 'mdi-pause' : 'mdi-play'"
              @click="togglePolling" 
              :title="pollingEnabled ? 'Pausar actualización automática' : 'Reanudar actualización automática'"
              variant="tonal"
              size="small"
            ></v-btn>
            
            <v-btn color="blue-400" prepend-icon="mdi-plus" @click="openNewAreaDialog" class="neon-border">
              Nueva Área
            </v-btn>
          </div>
        </div>
      </v-col>
    </v-row>

    <!-- Tabla de Áreas -->
    <v-card class="bg-dark-surface border border-blue-500/20">
      <v-card-title class="text-white">
        <div class="d-flex align-center gap-3">
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
          
          <!-- ✅ INDICADOR DE POLLING -->
          <div class="d-flex align-center gap-2">
            <v-chip 
              :color="pollingEnabled ? 'green-500' : 'orange-500'" 
              variant="tonal" 
              size="small"
              class="polling-indicator"
            >
              <v-icon left size="small">
                {{ pollingEnabled ? 'mdi-sync' : 'mdi-sync-off' }}
              </v-icon>
              {{ pollingEnabled ? 'Auto-actualizando' : 'Pausado' }}
            </v-chip>
            
            <span class="text-caption text-grey-300">
              ({{ POLLING_INTERVAL_MS / 1000 }}s)
            </span>
          </div>
        </div>
      </v-card-title>

             <v-data-table
         :headers="headers"
         :items="areas"
         :search="search"
         :loading="loading"
         :sort-by="[{ key: 'name', order: 'asc' }]"
         class="elevation-1 bg-dark-surface"
         theme="dark"
         :no-data-text="loading ? 'Cargando áreas...' : 'No hay áreas registradas'"
         :no-results-text="'No se encontraron áreas que coincidan con la búsqueda'"
       >
        <template v-slot:item.radius="{ item }">
          {{ item.radius }}m
        </template>
        
        <template v-slot:item.actions="{ item }">
          <v-btn icon="mdi-pencil" size="small" color="blue-400" @click="editArea(item)" title="Editar área"></v-btn>
          
          <!-- Botón dinámico según el estado del área -->
          <v-btn 
            v-if="item.status === 'active'"
            icon="mdi-account-off" 
            size="small" 
            color="red-400" 
            @click="deleteArea(item)"
            title="Desactivar área"
          ></v-btn>
          
          <v-btn 
            v-else
            icon="mdi-account-check" 
            size="small" 
            color="green-400" 
            @click="activateArea(item)"
            title="Reactivar área"
          ></v-btn>
        </template>
        
        <template v-slot:item.latitude="{ item }">
          <span :title="item.latitude">{{ formatCoordinate(item.latitude) }}</span>
        </template>
        
        <template v-slot:item.longitude="{ item }">
          <span :title="item.longitude">{{ formatCoordinate(item.longitude) }}</span>
        </template>
        
        <template v-slot:item.description="{ item }">
          {{ item.description }}
        </template>
        
        <template v-slot:item.employee_count="{ item }">
          <v-chip 
            :color="item.employee_count > 0 ? 'green-500' : 'grey-500'" 
            size="small" 
            variant="tonal"
          >
            {{ item.employee_count || 0 }}
          </v-chip>
        </template>
        
        <template v-slot:item.status="{ item }">
          <v-chip 
            :color="item.status === 'active' ? 'green-500' : 'red-500'" 
            size="small" 
            variant="tonal"
          >
            {{ item.status === 'active' ? 'Activa' : 'Inactiva' }}
          </v-chip>
        </template>
        

      </v-data-table>
    </v-card>

    <!-- Dialog para Crear/Editar Área -->
    <v-dialog v-model="showDialog" max-width="700px">
      <v-card class="bg-dark-surface border border-blue-500/20">
        <v-card-title class="text-white">
          <span class="text-h5">{{ editingArea ? 'Editar' : 'Nueva' }} Área</span>
          <v-spacer></v-spacer>
          <v-chip v-if="editingArea" color="blue-400" variant="tonal" size="small">
            Editando
          </v-chip>
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
                  :color="areaForm.latitude && areaForm.longitude ? 'blue-400' : 'green-400'" 
                  :variant="areaForm.latitude && areaForm.longitude ? 'flat' : 'outlined'"
                  :prepend-icon="areaForm.latitude && areaForm.longitude ? 'mdi-check-circle' : 'mdi-map-marker'" 
                  @click="showMapSelectorModal"
                  class="mb-4"
                  block
                >
                  {{ areaForm.latitude && areaForm.longitude ? '✅ Ubicación Seleccionada - Cambiar' : '📍 Seleccionar Ubicación en el Mapa' }}
                </v-btn>
              </v-col>
              
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="areaForm.latitude"
                  label="Latitud"
                  readonly
                  required
                  :rules="[v => !!v || 'Selecciona ubicación en el mapa']"
                  :color="areaForm.latitude ? 'blue-400' : 'error'"
                  variant="outlined"
                  :prepend-icon="areaForm.latitude ? 'mdi-crosshairs-gps' : 'mdi-alert-circle'"
                  :placeholder="areaForm.latitude ? areaForm.latitude : 'Selecciona en el mapa'"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="areaForm.longitude"
                  label="Longitud"
                  readonly
                  required
                  :rules="[v => !!v || 'Selecciona ubicación en el mapa']"
                  :color="areaForm.longitude ? 'blue-400' : 'error'"
                  variant="outlined"
                  :prepend-icon="areaForm.longitude ? 'mdi-crosshairs-gps' : 'mdi-alert-circle'"
                  :placeholder="areaForm.longitude ? areaForm.longitude : 'Selecciona en el mapa'"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="areaForm.radius"
                  label="Radio (metros)"
                  readonly
                  required
                  :rules="[v => (!!v && v >= 10) || 'Radio mínimo: 10 metros']"
                  :color="areaForm.radius >= 10 ? 'blue-400' : 'error'"
                  variant="outlined"
                  :prepend-icon="areaForm.radius >= 10 ? 'mdi-radius' : 'mdi-alert-circle'"
                  :placeholder="areaForm.radius ? areaForm.radius + 'm' : 'Selecciona en el mapa'"
                ></v-text-field>
              </v-col>
              

            </v-row>
          </v-form>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey-400" variant="text" @click="cancelDialog">Cancelar</v-btn>
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
        
        <v-card-text class="pa-0">
          <div class="map-container">
            <!-- Campo de búsqueda y controles del mapa -->
            <div class="map-search mb-2">
               <v-row class="mb-0">
                 <v-col cols="12" sm="8" class="pb-0">
                   <v-text-field
                     id="map-search"
                     v-model="searchPlace"
                     label="Buscar lugar (ej: Universidad Estatal de Milagro)"
                     prepend-icon="mdi-magnify"
                     variant="outlined"
                     color="blue-400"
                     clearable
                     @input="onSearchInput"
                     hide-details
                     density="compact"
                   ></v-text-field>
                 </v-col>
                 <v-col cols="12" sm="4" class="pb-0">
                   <div class="radius-control">
                     <label class="radius-label">Radio del Área (metros)</label>
                     <v-slider
                       v-model="mapRadius"
                       :min="10"
                       :max="500"
                       :step="10"
                       color="orange-500"
                       thumb-color="orange-500"
                       track-color="orange-300"
                       thumb-label="always"
                       prepend-icon="mdi-radius"
                       class="radius-slider"
                       hide-details
                     ></v-slider>
                   </div>
                 </v-col>
               </v-row>
              
              <!-- Información del radio y estado - SUPER PEGADO -->
              <div class="d-flex align-center gap-4 mt-0 pt-0">
                <v-chip color="orange-500" variant="tonal" size="small">
                  Radio: {{ mapRadius }}m
                </v-chip>
                <v-chip v-if="isLocating" color="orange-400" variant="tonal" size="small">
                  <v-icon left>mdi-crosshairs-gps</v-icon>
                  Obteniendo ubicación...
                </v-chip>
                <v-chip v-else-if="userLocation" color="green-400" variant="tonal" size="small">
                  <v-icon left>mdi-crosshairs-gps</v-icon>
                  Ubicación actual
                </v-chip>
                <v-chip v-if="selectedLocation" color="blue-400" variant="tonal" size="small">
                  Ubicación seleccionada
                </v-chip>
              </div>
            </div>
            
            <!-- Contenedor del mapa -->
            <div id="map-selector" class="map-wrapper"></div>
            
                         <!-- Instrucciones -->
             <div class="map-instructions mt-2">
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

    <!-- Snackbar para mensajes -->
    <v-snackbar
      v-model="mensaje.show"
      :color="mensaje.type"
      :timeout="4000"
      class="custom-snackbar"
    >
      {{ mensaje.text }}
      
      <template v-slot:actions>
        <v-btn
          color="white"
          variant="text"
          @click="mensaje.show = false"
        >
          Cerrar
        </v-btn>
      </template>
    </v-snackbar>

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
      clearMap,
      refreshMap
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
    
    const showMessage = (text, type = 'success') => {
      mensaje.value = {
        show: true,
        text,
        type
      }
    }
    
    const showDialog = ref(false)
    const showDeleteDialog = ref(false)

    const showMapSelector = ref(false)
    const valid = ref(false)
    const form = ref(null)
    
    const editingArea = ref(null)
    const areaToDelete = ref(null)

    
         // Variables para el selector de mapa
     const mapRadius = ref(200)
     const userLocation = ref(null)
     const isLocating = ref(false)
     const searchPlace = ref('')
     const googleMapsAvailable = ref(true) // Siempre true con el servicio optimizado
    
    const areas = ref([])
    
    // ✅ POLLING AUTOMÁTICO para mantener la lista actualizada
    const pollingInterval = ref(null)
    const pollingEnabled = ref(true)
    const POLLING_INTERVAL_MS = 30000 // 30 segundos
    
    // Estado para mensajes
    const mensaje = ref({
      show: false,
      text: '',
      type: 'success'
    })
    
    const areaForm = ref({
      name: '',
      description: '',
      latitude: '',
      longitude: '',
      radius: 200,
      status: 'active'  // CRÍTICO: Incluir status por defecto
    })
    
    const headers = [
      { title: 'Nombre', key: 'name', sortable: true },
      { title: 'Descripción', key: 'description', sortable: true },
      { title: 'Empleados', key: 'employee_count', sortable: true },
      { title: 'Latitud', key: 'latitude', sortable: true, width: '120px' },
      { title: 'Longitud', key: 'longitude', sortable: true, width: '120px' },
      { title: 'Radio', key: 'radius', sortable: true },
      { title: 'Acciones', key: 'actions', sortable: false }
    ]
    
             const loadAreas = async () => {
       loading.value = true
       try {
         const areasData = await areaService.getAll()
         // El backend devuelve {count, next, previous, results}
         // Necesitamos acceder a results que es el array de áreas
         const areasArray = areasData.results || areasData
         
         // ✅ FILTRAR SOLO ÁREAS ACTIVAS para la lista principal
         const activeAreas = areasArray.filter(area => area.status === 'active')
         
         const areasWithCounts = activeAreas.map(area => ({
           ...area,
           employee_count: area.employee_count || 0
         }))
         
         // Ordenar alfabéticamente por nombre
         areas.value = sortAreasAlphabetically(areasWithCounts)
         
         console.log('✅ Áreas activas cargadas y ordenadas alfabéticamente:', areas.value.length, 'áreas')
         console.log('📋 Orden actual:', areas.value.map(area => area.name))
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
     
     // ✅ FUNCIONES DE POLLING AUTOMÁTICO
     const startPolling = () => {
       if (pollingInterval.value) {
         clearInterval(pollingInterval.value)
       }
       
       pollingInterval.value = setInterval(async () => {
         if (pollingEnabled.value && !loading.value) {
           console.log('🔄 Polling automático: Recargando áreas...')
           await loadAreas()
         }
       }, POLLING_INTERVAL_MS)
       
       console.log('✅ Polling automático iniciado cada', POLLING_INTERVAL_MS / 1000, 'segundos')
     }
     
     const stopPolling = () => {
       if (pollingInterval.value) {
         clearInterval(pollingInterval.value)
         pollingInterval.value = null
         console.log('⏹️ Polling automático detenido')
       }
     }
     
     const togglePolling = () => {
       if (pollingEnabled.value) {
         stopPolling()
         pollingEnabled.value = false
         console.log('⏸️ Polling automático pausado')
       } else {
         pollingEnabled.value = true
         startPolling()
         console.log('▶️ Polling automático reanudado')
       }
     }
     
     const editArea = async (area) => {
        try {
          console.log('✏️ Iniciando edición de área:', area.name)
          
          // Cargar datos completos del área desde la API
          const fullArea = await areaService.getById(area.id)
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
          
          // Sincronizar radio del mapa
          mapRadius.value = fullArea.radius || 100
          
          // Guardar las coordenadas para usar en el mapa
          editingArea.value.savedCoordinates = {
            lat: parseFloat(fullArea.latitude),
            lng: parseFloat(fullArea.longitude)
          }
          
          console.log('📋 Formulario cargado con:', areaForm.value)
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
      areaToDelete.value = area
      showDeleteDialog.value = true
    }
    
    const activateArea = async (area) => {
       try {
         await areaService.activate(area.id)
         // Recargar áreas para actualizar el estado
         await loadAreas()
         showMessage('Área reactivada correctamente')
       } catch (error) {
         console.error('Error reactivando área:', error)
         showMessage('Error reactivando área: ' + (error.response?.data?.message || error.message), 'error')
       }
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
    
    // Función para ordenar áreas alfabéticamente
    const sortAreasAlphabetically = (areasArray) => {
      return areasArray.sort((a, b) => {
        // Ordenar por nombre de forma alfabética, insensible a mayúsculas/minúsculas
        const nameA = a.name.toLowerCase().trim()
        const nameB = b.name.toLowerCase().trim()
        
        // Usando localeCompare para un ordenamiento más robusto
        return nameA.localeCompare(nameB, 'es', { 
          sensitivity: 'base',
          numeric: true,
          ignorePunctuation: true
        })
      })
    }

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

    // Funciones de gestión del formulario
    const resetForm = () => {
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
      mapRadius.value = 200
      clearMap()
      
      // Resetear validación del formulario
      if (form.value) {
        form.value.resetValidation()
      }
      
      console.log('📝 Formulario reseteado')
    }

    const openNewAreaDialog = () => {
      console.log('🆕 Abriendo diálogo para nueva área')
      resetForm()
      showDialog.value = true
    }

    const cancelDialog = () => {
      console.log('❌ Cancelando diálogo')
      showDialog.value = false
      // Solo resetear si estábamos creando (no editando)
      if (!editingArea.value) {
        resetForm()
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
        // Actualizar coordenadas en el formulario
        areaForm.value.latitude = selectedLocation.value.lat
        areaForm.value.longitude = selectedLocation.value.lng
        areaForm.value.radius = mapRadius.value
        
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
        areaForm.value.radius = 200
        mapRadius.value = 200
      }
      
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

      // VALIDACIÓN CRÍTICA: Verificar que se haya seleccionado una ubicación
      if (!areaForm.value.latitude || !areaForm.value.longitude) {
        console.error('❌ No se ha seleccionado ubicación en el mapa')
        alert('⚠️ Debes seleccionar una ubicación en el mapa antes de guardar el área.')
        return
      }

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
      try {
        if (editingArea.value) {
          console.log('✏️ Actualizando área existente...')
          console.log('📤 Datos enviados para actualización:', areaForm.value)
          
          // Actualizar área existente
          const updatedArea = await areaService.update(editingArea.value.id, areaForm.value)
          const index = areas.value.findIndex(area => area.id === editingArea.value.id)
          if (index !== -1) {
            areas.value[index] = { ...updatedArea }
            
            // Reordenar lista si se cambió el nombre (para mantener orden alfabético)
            areas.value = sortAreasAlphabetically([...areas.value])
            console.log('📋 Lista reordenada después de actualización:', areas.value.map(area => area.name))
          }
          
          // CRÍTICO: Actualizar las coordenadas guardadas con los nuevos valores
          if (editingArea.value.savedCoordinates && areaForm.value.latitude && areaForm.value.longitude) {
            editingArea.value.savedCoordinates = {
              lat: parseFloat(areaForm.value.latitude),
              lng: parseFloat(areaForm.value.longitude)
            }
            console.log('🔄 Coordenadas guardadas actualizadas:', editingArea.value.savedCoordinates)
          }
          
          console.log('✅ Área actualizada:', updatedArea)
        } else {
          console.log('🆕 Creando nueva área...')
          console.log('📤 Datos enviados al servicio:', areaForm.value)
          
          // Crear nueva área
          const newArea = await areaService.create(areaForm.value)
          console.log('✅ Respuesta del servicio:', newArea)
          
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
        
        // Recargar áreas para asegurar datos actualizados
        await loadAreas()
        
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
    
         onMounted(() => {
       loadAreas()
       // ✅ INICIAR POLLING AUTOMÁTICO
       startPolling()
       // El mapService se inicializa automáticamente
       console.log('🚀 Componente Areas cargado - Mapa optimizado listo')
     })
     
     // ✅ LIMPIAR POLLING AL DESMONTAR EL COMPONENTE
     onUnmounted(() => {
       stopPolling()
       console.log('🧹 Componente Areas desmontado - Polling detenido')
     })
     
     return {
      search,
      loading,
      saving,
      deleting,
      showDialog,
      showDeleteDialog,

      showMapSelector,
      valid,
      form,
      editingArea,
      areaToDelete,

      areas,
      areaForm,
      headers,
      mensaje,
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

      confirmDelete,
      saveArea,
      openNewAreaDialog,
      cancelDialog,
      resetForm,
      sortAreasAlphabetically,
      reorderAreasList,
      // Funciones del mapa optimizado
      showMapSelectorModal,
      confirmMapSelection,
      cancelMapSelection,
      onSearchInput,
      clearMap,
      refreshMap,
      // Funciones de formateo
      formatCoordinate,
      showMessage,
      pollingEnabled, // Exponer la variable de polling para el botón
      togglePolling // Exponer la función de toggle para el botón
    }
  }
}
</script>

<style scoped>
.map-container {
  background: rgba(30, 41, 59, 0.8);
  border-radius: 12px;
  padding: 12px;
  border: 1px solid rgba(59, 130, 246, 0.2);
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
 
 /* ✅ ESTILOS PARA EL INDICADOR DE POLLING */
 .polling-indicator {
   animation: pulse 2s infinite;
   font-weight: 500 !important;
 }
 
 .polling-indicator:deep(.v-icon) {
   animation: spin 2s linear infinite;
 }
 
 @keyframes pulse {
   0%, 100% { opacity: 1; }
   50% { opacity: 0.7; }
 }
 
 @keyframes spin {
   from { transform: rotate(0deg); }
   to { transform: rotate(360deg); }
 }
 
 /* Responsive para el header con polling */
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
</style>
