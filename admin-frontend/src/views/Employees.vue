<template>
  <div>
    <v-row class="mt-2 employee-header">
      <v-col cols="12">
        <div class="d-flex justify-space-between align-center">
          <h1 class="text-h4 text-white">Gestión de Empleados</h1>
          <v-btn color="blue-400" prepend-icon="mdi-plus" @click="showDialog = true" class="neon-border">
            Nuevo Empleado
          </v-btn>
        </div>
      </v-col>
    </v-row>

    <!-- Tabla de Empleados -->
    <v-card class="bg-dark-surface border border-blue-500/20 mt-6 employee-table-card">
      <v-card-title class="text-white filters-container">
        <div class="filter-item">
          <v-text-field
            v-model="search"
            append-icon="mdi-magnify"
            label="Buscar empleado"
            single-line
            hide-details
            variant="outlined"
            density="compact"
            color="blue-400"
            class="text-white search-field"
          ></v-text-field>
        </div>
        
        <!-- Toggle para cambiar entre vista de lista y tarjetas -->
        <div class="filter-item view-toggle">
          <v-btn-toggle
            v-model="viewMode"
            color="blue-400"
            group
            density="compact"
            class="view-toggle-buttons"
          >
            <v-btn value="list" prepend-icon="mdi-format-list-bulleted" title="Vista de Lista">
              Lista
            </v-btn>
            <v-btn value="cards" prepend-icon="mdi-view-grid" title="Vista de Tarjetas">
              Tarjetas
            </v-btn>
          </v-btn-toggle>
        </div>
      </v-card-title>

      <v-data-table
        v-if="viewMode === 'list'"
        :headers="headers"
        :items="employees"
        :search="search"
        :loading="loading"
        class="elevation-1 bg-dark-surface"
        theme="dark"
      >
        <template v-slot:item.actions="{ item }">
          <v-btn icon="mdi-pencil" size="small" color="blue-400" @click="editEmployee(item)"></v-btn>
          
          <!-- Botón dinámico según el estado del empleado -->
          <v-btn 
            v-if="item.user.is_active"
            icon="mdi-account-off" 
            size="small" 
            color="red-400" 
            @click="deleteEmployee(item)"
            title="Desactivar empleado"
          ></v-btn>
          
          <v-btn 
            v-else
            icon="mdi-account-check" 
            size="small" 
            color="green-400" 
            @click="activateEmployee(item)"
            title="Reactivar empleado"
          ></v-btn>
        </template>
      </v-data-table>
      
      <!-- Vista de Tarjetas -->
      <div v-if="viewMode === 'cards'" class="cards-container">
        <v-row>
          <v-col 
            v-for="employee in filteredEmployees" 
            :key="employee.id" 
            cols="12" 
            sm="6" 
            md="4" 
            lg="3"
          >
            <v-card class="employee-card bg-dark-surface border border-blue-500/20" elevation="2">
              <!-- Foto del empleado -->
              <div class="employee-photo-container">
                <v-avatar 
                  v-if="employee.photo_url" 
                  :image="employee.photo_url" 
                  size="80"
                  class="employee-photo"
                ></v-avatar>
                <v-avatar 
                  v-else 
                  size="80"
                  color="blue-400"
                  class="employee-photo-placeholder"
                >
                  <v-icon size="40" color="white">mdi-account</v-icon>
                </v-avatar>
              </div>
              
              <!-- Información del empleado -->
              <v-card-text class="text-center pa-4">
                <h3 class="text-h6 text-white mb-2">{{ employee.full_name }}</h3>
                <p class="text-grey-400 mb-1">{{ employee.position }}</p>
                <p class="text-grey-500 text-sm">{{ employee.area_name }}</p>
                <p class="text-blue-400 text-sm font-weight-medium">{{ employee.email_display }}</p>
              </v-card-text>
              
              <!-- Acciones -->
              <v-card-actions class="justify-center pa-4">
                <v-btn 
                  icon="mdi-pencil" 
                  size="small" 
                  color="blue-400" 
                  @click="editEmployee(employee)"
                  title="Editar"
                ></v-btn>
                
                <v-btn 
                  v-if="employee.user.is_active"
                  icon="mdi-account-off" 
                  size="small" 
                  color="red-400" 
                  @click="deleteEmployee(employee)"
                  title="Desactivar"
                ></v-btn>
                
                <v-btn 
                  v-else
                  icon="mdi-account-check" 
                  size="small" 
                  color="green-400" 
                  @click="activateEmployee(employee)"
                  title="Reactivar"
                ></v-btn>
              </v-card-actions>
            </v-card>
          </v-col>
        </v-row>
      </div>
    </v-card>

    <!-- Diálogo para crear/editar empleado -->
    <v-dialog v-model="showDialog" max-width="600px" persistent @after-enter="onDialogOpened">
      <v-card class="bg-dark-surface border border-blue-500/20">
        <v-card-title class="text-white">
          <span v-if="editingEmployee">Editar Empleado</span>
          <span v-else>Nuevo Empleado</span>
        </v-card-title>
        
        <v-card-text>
          <v-form ref="form" v-model="valid">
            <v-row>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="employeeForm.first_name"
                  label="Nombre"
                  variant="outlined"
                  color="blue-400"
                  :rules="[v => !!v || 'El nombre es requerido']"
                  required
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="employeeForm.last_name"
                  label="Apellido"
                  variant="outlined"
                  color="blue-400"
                  :rules="[v => !!v || 'El apellido es requerido']"
                  required
                ></v-text-field>
              </v-col>
              
              <v-col cols="12">
                <v-text-field
                  v-model="employeeForm.email"
                  label="Email"
                  type="email"
                  variant="outlined"
                  color="blue-400"
                  :rules="[
                    v => !!v || 'El email es requerido',
                    v => /.+@.+\..+/.test(v) || 'El email debe ser válido'
                  ]"
                  required
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="employeeForm.position"
                  label="Cargo"
                  variant="outlined"
                  color="blue-400"
                  :rules="[v => !!v || 'El cargo es requerido']"
                  required
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" sm="6">
                <v-select
                  v-model="employeeForm.area"
                  :items="areas"
                  item-title="name"
                  item-value="id"
                  label="Área"
                  variant="outlined"
                  color="blue-400"
                  :rules="[v => !!v || 'El área es requerida']"
                  required
                ></v-select>
              </v-col>
            </v-row>

            <!-- Sección de Registro Facial -->
            <v-row>
              <v-col cols="12">
                <v-divider class="mb-4"></v-divider>
                <h3 class="text-white mb-4">🎯 Registro Facial</h3>
              </v-col>
            </v-row>

            <v-row>
              <v-col cols="12">
                <v-card class="bg-dark-surface border border-blue-500/20">
                  <v-card-title class="text-sm text-blue-400">📷 Registro Facial</v-card-title>
                  <v-card-text>
                    <!-- Componente de captura de rostros - solo cuando el diálogo esté listo -->
                    <div v-if="dialogReady" class="text-center">
                      <v-btn
                        @click="showFaceRegistration = true"
                        color="blue-400"
                        size="large"
                        prepend-icon="mdi-camera"
                        :disabled="!employeeForm.first_name || !employeeForm.last_name"
                        block
                      >
                        🎯 Iniciar Registro Facial
                      </v-btn>
                      
                      <p class="text-grey-400 text-sm mt-2">
                        💡 Completa el nombre y apellido para habilitar el registro facial
                      </p>
                      <p class="text-blue-400 text-xs mt-1">
                                                 📸 Se capturarán 15 fotos para máxima velocidad
                      </p>
                      <p class="text-green-400 text-xs mt-1">
                        🎯 Umbral de confianza: 80% (más permisivo)
                      </p>
                    </div>
                    
                    <!-- Mensaje mientras carga el componente -->
                    <div v-else class="text-center py-4">
                      <v-progress-circular indeterminate color="blue-400" class="mb-2"></v-progress-circular>
                      <p class="text-grey-300">Preparando componente de cámara...</p>
                    </div>
                    
                    <!-- Estado verificando (mientras se consulta la base de datos) -->
                    <div v-if="faceRegistration.status === 'checking'" class="mt-4 text-center">
                      <v-divider class="mb-4"></v-divider>
                      <v-progress-circular 
                        indeterminate 
                        color="blue-400"
                        size="32"
                        class="mb-2"
                      ></v-progress-circular>
                      <p class="text-grey-300 text-sm">Verificando estado del registro facial...</p>
                    </div>
                    
                    <!-- Estado después de captura -->
                    <div v-else-if="faceRegistration.status === 'captured'" class="mt-4 text-center">
                      <v-divider class="mb-4"></v-divider>
                      <v-icon color="green-400" size="48" class="mb-2">mdi-camera-check</v-icon>
                      <h4 class="text-white mb-2">{{ faceRegistration.statusText }}</h4>
                      <p class="text-grey-300 mb-3">📸 {{ faceRegistration.photosCount }} fotos listas para procesar</p>
                      
                      <v-btn 
                        @click="trainFaceModel"
                        color="blue-400"
                        block
                        :loading="faceRegistration.isTraining"
                        prepend-icon="mdi-face-recognition"
                      >
                        Procesar y Guardar Rostros
                      </v-btn>
                    </div>
                    
                    <!-- Estado procesando -->
                    <div v-else-if="faceRegistration.isTraining" class="mt-4 text-center">
                      <v-divider class="mb-4"></v-divider>
                      <v-progress-circular 
                        indeterminate 
                        color="orange-400"
                        size="64"
                        class="mb-3"
                      ></v-progress-circular>
                      <h4 class="text-white mb-2">{{ faceRegistration.statusText }}</h4>
                      <p class="text-grey-300">Generando embeddings faciales...</p>
                    </div>
                    
                    <!-- Estado completado -->
                    <div v-else-if="faceRegistration.status === 'trained'" class="mt-4 text-center">
                      <v-divider class="mb-4"></v-divider>
                      <v-icon color="green-500" size="64" class="mb-3">mdi-check-circle</v-icon>
                      <h4 class="text-green-400 mb-2">Rostro Registrado Correctamente</h4>
                      <p class="text-grey-300 mb-3">{{ faceRegistration.photosCount }} fotos procesadas y guardadas</p>
                      
                      <div class="d-flex gap-2 justify-center">
                        <v-btn 
                          @click="showFaceRegistration = true"
                          color="blue-400"
                          variant="outlined"
                          size="small"
                          prepend-icon="mdi-camera-plus"
                        >
                          Actualizar Rostro
                        </v-btn>
                        
                        <v-btn 
                          @click="resetFaceRegistration"
                          color="grey-600"
                          variant="outlined"
                          size="small"
                        >
                          Cancelar
                        </v-btn>
                      </div>
                    </div>
                    
                    <!-- Ayuda si faltan datos -->
                    <div v-if="!employeeForm.first_name || !employeeForm.last_name" class="mt-4">
                      <v-alert
                        type="info"
                        variant="tonal"
                        density="compact"
                      >
                        💡 Completa el nombre y apellido para habilitar la captura facial
                      </v-alert>
                    </div>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        
        <v-card-actions class="justify-end pa-4">
          <v-btn 
            color="grey-600" 
            variant="outlined" 
            @click="showDialog = false"
            :disabled="saving"
          >
            Cancelar
          </v-btn>
          
          <v-btn 
            color="blue-400" 
            @click="saveEmployee"
            :loading="saving"
            :disabled="!valid"
          >
            {{ editingEmployee ? 'Actualizar' : 'Crear' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Diálogo de confirmación para eliminar -->
    <v-dialog v-model="showDeleteDialog" max-width="400px">
      <v-card class="bg-dark-surface border border-red-500/20">
        <v-card-title class="text-white">
          Confirmar Desactivación
        </v-card-title>
        
        <v-card-text>
          <p class="text-grey-400">
            ¿Estás seguro de que quieres desactivar al empleado 
            <strong>{{ employeeToDelete?.full_name }}</strong>?
          </p>
          <p class="text-grey-500 text-sm mt-2">
            El empleado no podrá acceder al sistema, pero sus datos se mantendrán.
          </p>
        </v-card-text>
        
        <v-card-actions class="justify-end pa-4">
          <v-btn 
            color="grey-600" 
            variant="outlined" 
            @click="showDeleteDialog = false"
          >
            Cancelar
          </v-btn>
          
          <v-btn 
            color="red-400" 
            @click="confirmDelete"
            :loading="deleting"
          >
            Desactivar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Componente de registro facial -->
    <FaceRegistration
      v-if="showFaceRegistration"
      :employee-id="editingEmployee?.id || 'new'"
      :employee-name="`${employeeForm.first_name} ${employeeForm.last_name}`"
      :target-count="15"
      @registro-completo="onRegistroCompleto"
      @registro-error="onRegistroError"
      @close="showFaceRegistration = false"
    />

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
import { ref, onMounted, computed } from 'vue'
import { employeeService } from '../services/employeeService'
import areaService from '../services/areaService'
import { faceService } from '../services/faceService'
import FaceRegistration from '../components/FaceRegistration.vue'

export default {
  name: 'Employees',
  components: {
    FaceRegistration
  },
  setup() {
    const search = ref('')
    const loading = ref(false)
    const viewMode = ref('list') // Modo de vista: 'list' o 'cards'
    const saving = ref(false)
    const deleting = ref(false)
    const showDialog = ref(false)
    const showDeleteDialog = ref(false)
    const showFaceRegistration = ref(false)
    const valid = ref(false)
    const form = ref(null)
    const dialogReady = ref(false)
    
    const editingEmployee = ref(null)
    const employeeToDelete = ref(null)
    
    const employees = ref([])
    const areas = ref([])
    
    // Estado para mensajes
    const mensaje = ref({
      show: false,
      text: '',
      type: 'success'
    })
   
    // Estados para registro facial
    const faceRegistration = ref({
      isCapturing: false,
      isTraining: false,
      status: 'pending', // pending, captured, trained, error
      statusText: 'Sin registrar',
      photosCount: 0,
      confidence: 90,
      capturedPhotos: null
    })
    
    const employeeForm = ref({
      first_name: '',
      last_name: '',
      email: '',
      position: '',
      area: null
    })
    
    const positions = [
      'Desarrollador',
      'Diseñador',
      'Gerente',
      'Analista',
      'Administrativo',
      'Operario'
    ]
    
    const headers = [
      { title: 'ID', key: 'employee_id', sortable: true },
      { title: 'Nombre Completo', key: 'full_name', sortable: true },
      { title: 'Email', key: 'email_display', sortable: true },
      { title: 'Cargo', key: 'position', sortable: true },
      { title: 'Área', key: 'area_name', sortable: true },
      { title: 'Acciones', key: 'actions', sortable: false }
    ]
    
    // Computed property para empleados filtrados por búsqueda
    const filteredEmployees = computed(() => {
      if (!search.value) return employees.value
      
      const searchTerm = search.value.toLowerCase()
      return employees.value.filter(employee => 
        employee.full_name?.toLowerCase().includes(searchTerm) ||
        employee.email_display?.toLowerCase().includes(searchTerm) ||
        employee.position?.toLowerCase().includes(searchTerm) ||
        employee.area_name?.toLowerCase().includes(searchTerm)
      )
    })
    
    const loadEmployees = async () => {
      loading.value = true
      try {
        // CARGAR DESDE API REAL
        const employeesData = await employeeService.getAll()
        // El backend devuelve {count, next, previous, results}
        // Necesitamos acceder a results que es el array de empleados
        employees.value = employeesData.results || employeesData
      } catch (error) {
        console.error('Error cargando empleados:', error)
        showMessage('Error cargando empleados', 'error')
      } finally {
        loading.value = false
      }
    }
    
    const loadAreas = async () => {
      try {
        const areasData = await areaService.getAll()
        areas.value = areasData.results || areasData
      } catch (error) {
        console.error('Error cargando áreas:', error)
        showMessage('Error cargando áreas', 'error')
      }
    }
    
    const showMessage = (text, type = 'success') => {
      mensaje.value = {
        show: true,
        text,
        type
      }
    }
    
    const onDialogOpened = async () => {
      console.log('🚪 Diálogo abierto, preparando componente de cámara...')
      // Esperar más tiempo para asegurar que todo esté renderizado en el modal
      await new Promise(resolve => setTimeout(resolve, 800))
      dialogReady.value = true
      console.log('✅ Componente de cámara listo')
      
      // Debug adicional: verificar estado del DOM
      setTimeout(() => {
        const videos = document.querySelectorAll('video')
        const videoById = document.getElementById('face-capture-video')
        console.log('🔍 Estado del DOM después de preparación:')
        console.log(`   - Videos en DOM: ${videos.length}`)
        console.log(`   - Video por ID: ${!!videoById}`)
        console.log(`   - Diálogos activos: ${document.querySelectorAll('.v-dialog--active').length}`)
      }, 100)
    }
    
    const editEmployee = (employee) => {
      editingEmployee.value = employee
      employeeForm.value = {
        first_name: employee.user.first_name,
        last_name: employee.user.last_name,
        email: employee.user.email,
        position: employee.position,
        area: employee.area
      }
      showDialog.value = true
      
      // Verificar estado facial en segundo plano (sin bloquear)
      checkFaceRegistrationStatus(employee.id)
    }
    
    const deleteEmployee = (employee) => {
      employeeToDelete.value = employee
      showDeleteDialog.value = true
    }
    
    const confirmDelete = async () => {
      if (!employeeToDelete.value) return
      
      deleting.value = true
      try {
        await employeeService.delete(employeeToDelete.value.id)
        showMessage('Empleado desactivado correctamente')
        await loadEmployees()
        showDeleteDialog.value = false
        employeeToDelete.value = null
      } catch (error) {
        console.error('Error desactivando empleado:', error)
        showMessage('Error desactivando empleado', 'error')
      } finally {
        deleting.value = false
      }
    }
    
    const activateEmployee = async (employee) => {
      try {
        await employeeService.activate(employee.id)
        showMessage('Empleado reactivado correctamente')
        await loadEmployees()
      } catch (error) {
        console.error('Error reactivando empleado:', error)
        showMessage('Error reactivando empleado', 'error')
      }
    }
    
    const saveEmployee = async () => {
      if (!form.value?.validate()) return
      
      saving.value = true
      try {
        let savedEmployee
        
        if (editingEmployee.value) {
          // Actualizar empleado existente
          savedEmployee = await employeeService.update(editingEmployee.value.id, employeeForm.value)
          showMessage('Empleado actualizado correctamente')
        } else {
          // Crear nuevo empleado
          savedEmployee = await employeeService.create(employeeForm.value)
          showMessage('Empleado creado correctamente')
          
          // Si se creó exitosamente, mostrar registro facial
          if (savedEmployee && savedEmployee.id) {
            editingEmployee.value = savedEmployee
            showFaceRegistration.value = true
            return // No cerrar el diálogo aún
          }
        }
        
        await loadEmployees() // Recargar lista
        showDialog.value = false
        dialogReady.value = false // Resetear estado del diálogo
        editingEmployee.value = null
        employeeForm.value = {
          first_name: '',
          last_name: '',
          email: '',
          position: '',
          area: null
        }
        resetFaceRegistration() // Resetear estado facial
      } catch (error) {
        console.error('Error guardando empleado:', error)
        showMessage('Error guardando empleado', 'error')
      } finally {
        saving.value = false
      }
    }
    
    const onPhotoCaptured = (photoData) => {
      console.log('📸 Foto capturada:', photoData)
      faceRegistration.value.photosCount++
      faceRegistration.value.statusText = `Foto ${faceRegistration.value.photosCount} capturada`
    }
    
    const onCaptureComplete = (photos) => {
      console.log('✅ Captura completada:', photos.length, 'fotos')
      faceRegistration.value.capturedPhotos = photos
      faceRegistration.value.status = 'captured'
      faceRegistration.value.statusText = `${photos.length} fotos capturadas`
    }
    
    const onCaptureStopped = () => {
      console.log('⏹️ Captura detenida')
      faceRegistration.value.isCapturing = false
      faceRegistration.value.statusText = 'Captura detenida'
    }
    
    const onRegistroCompleto = async (result) => {
      console.log('✅ Registro facial completado:', result)
      faceRegistration.value.status = 'trained'
      faceRegistration.value.statusText = 'Rostros procesados y guardados correctamente'
      faceRegistration.value.photosCount = result.photosCount
      showFaceRegistration.value = false
      
      // Mostrar mensaje de éxito
      showMessage('Registro facial completado exitosamente')
    }
    
    const onRegistroError = (error) => {
      console.error('❌ Error en registro facial:', error)
      faceRegistration.value.status = 'error'
      faceRegistration.value.statusText = `Error: ${error.message || 'Error en registro'}`
      showFaceRegistration.value = false
      
      // Mostrar mensaje de error
      showMessage('Error en registro facial: ' + error.message, 'error')
    }
    
    const trainFaceModel = async () => {
      if (!faceRegistration.value.capturedPhotos || faceRegistration.value.capturedPhotos.length === 0) {
        alert('Primero debes capturar fotos')
        return
      }
      
      // Verificar que el empleado esté guardado
      if (!editingEmployee.value || !editingEmployee.value.id) {
        alert('Primero debes guardar el empleado antes de procesar el rostro facial')
        return
      }
      
      faceRegistration.value.isTraining = true
      faceRegistration.value.statusText = 'Procesando rostros y generando embeddings...'
      
      try {
        console.log('🎯 Entrenando modelo facial...')
        console.log('📸 Fotos a procesar:', faceRegistration.value.capturedPhotos.length)
        console.log('👤 Empleado ID:', editingEmployee.value.id)
        
        // Enviar fotos al backend para registro facial
        const result = await faceService.registerFace(
          editingEmployee.value.id,
          faceRegistration.value.capturedPhotos
        )
        
        console.log('📡 Respuesta del backend:', result)
        
        if (result.success) {
          faceRegistration.value.status = 'trained'
          faceRegistration.value.statusText = 'Rostros procesados y guardados correctamente'
          faceRegistration.value.confidence = 95
          faceRegistration.value.photosCount = result.photos_count
          
          console.log('✅ Rostros procesados:', result.message)
        } else {
          throw new Error(result.message || 'Error desconocido en el backend')
        }
        
      } catch (error) {
        console.error('❌ Error entrenando modelo:', error)
        faceRegistration.value.status = 'error'
        faceRegistration.value.statusText = `Error: ${error.message || 'Error en entrenamiento'}`
        
        // Mostrar error más detallado
        if (error.response) {
          console.error('📡 Respuesta del servidor:', error.response.data)
          console.error('📊 Estado HTTP:', error.response.status)
        }
      } finally {
        faceRegistration.value.isTraining = false
      }
    }
    
    const resetFaceRegistration = () => {
      faceRegistration.value = {
        isCapturing: false,
        isTraining: false,
        status: 'pending',
        statusText: 'Sin registrar',
        photosCount: 0,
        confidence: 90,
        capturedPhotos: null
      }
    }

    const checkFaceRegistrationStatus = async (employeeId) => {
      try {
        console.log('🔍 Verificando estado de registro facial para empleado:', employeeId)
        
        // Mostrar estado de verificación
        faceRegistration.value = {
          isCapturing: false,
          isTraining: false,
          status: 'checking',
          statusText: 'Verificando...',
          photosCount: 0,
          confidence: 90,
          capturedPhotos: null
        }
        
        // Llamar al servicio para verificar el estado
        const response = await faceService.getFaceStatus(employeeId)
        
        if (response.has_profile && response.is_trained) {
          // El empleado ya tiene rostro registrado
          faceRegistration.value = {
            isCapturing: false,
            isTraining: false,
            status: 'trained',
            statusText: 'Rostro ya registrado',
            photosCount: response.photos_count || 0,
            confidence: 90,
            capturedPhotos: null
          }
          console.log('✅ Empleado ya tiene rostro registrado:', response)
        } else {
          // El empleado no tiene rostro registrado
          faceRegistration.value = {
            isCapturing: false,
            isTraining: false,
            status: 'pending',
            statusText: 'Sin registrar',
            photosCount: 0,
            confidence: 90,
            capturedPhotos: null
          }
          console.log('❌ Empleado no tiene rostro registrado')
        }
      } catch (error) {
        console.error('Error verificando estado facial:', error)
        // En caso de error, asumir que no tiene rostro registrado
        faceRegistration.value = {
          isCapturing: false,
          isTraining: false,
          status: 'pending',
          statusText: 'Sin registrar',
          photosCount: 0,
          confidence: 90,
          capturedPhotos: null
        }
      }
    }
    
    onMounted(() => {
      loadEmployees()
      loadAreas()
    })
    
    return {
      search,
      loading,
      saving,
      deleting,
      showDialog,
      showDeleteDialog,
      showFaceRegistration,
      valid,
      form,
      dialogReady,
      editingEmployee,
      employeeToDelete,
      employees,
      areas,
      employeeForm,
      positions,
      headers,
      mensaje,
      viewMode,
      filteredEmployees,
      loadEmployees,
      loadAreas,
      onDialogOpened,
      editEmployee,
      deleteEmployee,
      confirmDelete,
      activateEmployee,
      saveEmployee,
      // Funciones de registro facial
      faceRegistration,
      onPhotoCaptured,
      onCaptureComplete,
      onCaptureStopped,
      onRegistroCompleto,
      onRegistroError,
      trainFaceModel,
      resetFaceRegistration,
      checkFaceRegistrationStatus
    }
  }
}
</script>

<style scoped>
.custom-snackbar {
  z-index: 9999;
}

.custom-snackbar .v-snackbar__content {
  font-weight: 500;
}

.custom-snackbar .v-snackbar__actions {
  margin-left: 16px;
}
</style>
