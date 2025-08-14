<template>
  <div>
    <v-row>
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
    <v-card class="bg-dark-surface border border-blue-500/20">
      <v-card-title class="text-white d-flex align-center gap-4">
        <v-select
          v-model="statusFilter"
          :items="statusOptions"
          label="Estado"
          variant="outlined"
          density="compact"
          color="blue-400"
          class="text-white"
          style="width: 150px;"
          @update:model-value="loadEmployees"
        ></v-select>
        
        <v-text-field
          v-model="search"
          append-icon="mdi-magnify"
          label="Buscar empleado"
          single-line
          hide-details
          variant="outlined"
          density="compact"
          color="blue-400"
          class="text-white"
          style="flex: 1;"
        ></v-text-field>
      </v-card-title>

      <v-data-table
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
        
        <template v-slot:item.user.is_active="{ item }">
          <v-chip :color="item.user.is_active ? 'green-500' : 'red-500'" size="small" variant="tonal">
            {{ item.user.is_active ? 'Activo' : 'Inactivo' }}
          </v-chip>
        </template>
      </v-data-table>
    </v-card>

    <!-- Dialog para Crear/Editar Empleado -->
    <v-dialog 
      v-model="showDialog" 
      max-width="600px"
      @after-enter="onDialogOpened"
    >
      <v-card class="bg-dark-surface border border-blue-500/20">
        <v-card-title class="text-white">
          <span class="text-h5">{{ editingEmployee ? 'Editar' : 'Nuevo' }} Empleado</span>
        </v-card-title>
        
        <v-card-text>
          <v-form ref="form" v-model="valid">
            <v-row>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="employeeForm.first_name"
                  label="Nombre"
                  required
                  :rules="[v => !!v || 'Nombre es requerido']"
                  color="blue-400"
                  variant="outlined"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="employeeForm.last_name"
                  label="Apellido"
                  required
                  :rules="[v => !!v || 'Apellido es requerido']"
                  color="blue-400"
                  variant="outlined"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12">
                <v-text-field
                  v-model="employeeForm.email"
                  label="Email"
                  type="email"
                  required
                  :rules="[v => !!v || 'Email es requerido', v => /.+@.+\..+/.test(v) || 'Email debe ser válido']"
                  color="blue-400"
                  variant="outlined"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" sm="6">
                <v-select
                  v-model="employeeForm.position"
                  label="Cargo"
                  :items="positions"
                  required
                  :rules="[v => !!v || 'Cargo es requerido']"
                  color="blue-400"
                  variant="outlined"
                ></v-select>
              </v-col>
              
              <v-col cols="12">
                <v-select
                  v-model="employeeForm.area"
                  label="Área de Trabajo"
                  :items="areas"
                  item-title="name"
                  item-value="id"
                  required
                  :rules="[v => !!v || 'Área es requerida']"
                  color="blue-400"
                  variant="outlined"
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
                    <FaceCameraCapture
                      v-if="dialogReady"
                      :disabled="!employeeForm.first_name || !employeeForm.last_name"
                      :target-count="15"
                      :auto-capture="true"
                      @photo-captured="onPhotoCaptured"
                      @capture-complete="onCaptureComplete"
                      @capture-stopped="onCaptureStopped"
                    />
                    
                    <!-- Mensaje mientras carga el componente -->
                    <div v-else class="text-center py-4">
                      <v-progress-circular indeterminate color="blue-400" class="mb-2"></v-progress-circular>
                      <p class="text-grey-300">Preparando componente de cámara...</p>
                    </div>
                    
                    <!-- Estado después de captura -->
                    <div v-if="faceRegistration.status === 'captured'" class="mt-4 text-center">
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
                      
                      <v-btn 
                        @click="resetFaceRegistration"
                        color="grey-600"
                        variant="outlined"
                        size="small"
                      >
                        Capturar Nuevamente
                      </v-btn>
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
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey-400" variant="text" @click="showDialog = false">Cancelar</v-btn>
          <v-btn color="blue-400" @click="saveEmployee" :loading="saving" class="neon-border">Guardar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog de Confirmación para Eliminar -->
    <v-dialog v-model="showDeleteDialog" max-width="400px">
      <v-card class="bg-dark-surface border border-blue-500/20">
        <v-card-title class="text-h5 text-white">Confirmar Desactivación</v-card-title>
        <v-card-text class="text-grey-300">
          ¿Estás seguro de que quieres desactivar a <strong>{{ employeeToDelete?.full_name }}</strong>?
          <br><br>
          <small class="text-yellow-400">Nota: El empleado será desactivado pero no eliminado. Podrás reactivarlo después.</small>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey-400" variant="text" @click="showDeleteDialog = false">Cancelar</v-btn>
          <v-btn color="orange-400" @click="confirmDelete" :loading="deleting">Desactivar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { employeeService } from '../services/employeeService'
import { areaService } from '../services/areaService'
import { faceService } from '../services/faceService'
import FaceCameraCapture from '../components/FaceCameraCapture.vue'

export default {
  name: 'Employees',
  components: {
    FaceCameraCapture
  },
  setup() {
    const search = ref('')
    const loading = ref(false)
    const statusFilter = ref('active')
    const saving = ref(false)
    const deleting = ref(false)
    const showDialog = ref(false)
    const showDeleteDialog = ref(false)
    const valid = ref(false)
    const form = ref(null)
    const dialogReady = ref(false)
    
    const editingEmployee = ref(null)
    const employeeToDelete = ref(null)
    
    const employees = ref([])
    const areas = ref([])
    
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
    
    const statusOptions = [
      { title: 'Activos', value: 'active' },
      { title: 'Inactivos', value: 'inactive' },
      { title: 'Todos', value: 'all' }
    ]
    
    const headers = [
      { title: 'ID', key: 'employee_id', sortable: true },
      { title: 'Nombre Completo', key: 'full_name', sortable: true },
      { title: 'Email', key: 'email_display', sortable: true },
      { title: 'Cargo', key: 'position', sortable: true },
      { title: 'Área', key: 'area_name', sortable: true },
      { title: 'Estado', key: 'user.is_active', sortable: true },
      { title: 'Acciones', key: 'actions', sortable: false }
    ]
    
    const loadEmployees = async () => {
      loading.value = true
      try {
        // CARGAR DESDE API REAL con filtro de estado
        const params = statusFilter.value !== 'active' ? `?status=${statusFilter.value}` : ''
        employees.value = await employeeService.getAllWithStatus(statusFilter.value)
      } catch (error) {
        console.error('Error cargando empleados:', error)
      } finally {
        loading.value = false
      }
    }
    
    const loadAreas = async () => {
      try {
        // CARGAR DESDE API REAL
        areas.value = await areaService.getAll()
      } catch (error) {
        console.error('Error cargando áreas:', error)
      }
    }
    
    const editEmployee = (employee) => {
      editingEmployee.value = employee
      // Mapear datos del empleado al formulario, extrayendo datos del usuario
      employeeForm.value = {
        first_name: employee.user?.first_name || '',
        last_name: employee.user?.last_name || '',
        email: employee.user?.email || '',
        position: employee.position || '',
        area: employee.area || null  // employee.area ya debería ser el ID
      }
      console.log('Editando empleado:', employee)
      console.log('Formulario mapeado:', employeeForm.value)
      showDialog.value = true
      dialogReady.value = false // Resetear estado del diálogo
    }
    
    const deleteEmployee = (employee) => {
      employeeToDelete.value = employee
      showDeleteDialog.value = true
    }
    
    const confirmDelete = async () => {
      if (!employeeToDelete.value) return
      
      deleting.value = true
      try {
        // SOFT DELETE - DESACTIVAR EMPLEADO
        await employeeService.delete(employeeToDelete.value.id)
        await loadEmployees() // Recargar lista
        showDeleteDialog.value = false
        employeeToDelete.value = null
      } catch (error) {
        console.error('Error desactivando empleado:', error)
      } finally {
        deleting.value = false
      }
    }
    
    const activateEmployee = async (employee) => {
      try {
        // REACTIVAR EMPLEADO
        await employeeService.activate(employee.id)
        await loadEmployees() // Recargar lista
      } catch (error) {
        console.error('Error reactivando empleado:', error)
      }
    }
    
    // Función para cuando el diálogo se abre completamente
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
    
    // Funciones para registro facial con el nuevo componente
    const onPhotoCaptured = (data) => {
      faceRegistration.value.photosCount = data.count
      console.log(`✅ Foto ${data.count}/${data.total} capturada`)
    }
    
    const onCaptureComplete = (photos) => {
      console.log(`✅ Captura completada: ${photos.length} fotos`)
      faceRegistration.value.status = 'captured'
      faceRegistration.value.statusText = `${photos.length} fotos con rostros válidos - Listo para procesar`
      faceRegistration.value.photosCount = photos.length
      faceRegistration.value.capturedPhotos = photos
    }
    
    const onCaptureStopped = (photos) => {
      console.log(`⏹️ Captura detenida: ${photos.length} fotos`)
      if (photos.length > 0) {
        faceRegistration.value.status = 'captured'
        faceRegistration.value.statusText = `${photos.length} fotos capturadas - Listo para procesar`
        faceRegistration.value.photosCount = photos.length
        faceRegistration.value.capturedPhotos = photos
      } else {
        resetFaceRegistration()
      }
    }
    
    const trainFaceModel = async () => {
      if (!faceRegistration.value.capturedPhotos || faceRegistration.value.capturedPhotos.length === 0) {
        alert('Primero debes capturar fotos')
        return
      }
      
      // Si estamos editando, necesitamos el ID del empleado
      if (!editingEmployee.value || !editingEmployee.value.id) {
        alert('Guarda el empleado primero antes de entrenar el modelo facial')
        return
      }
      
      faceRegistration.value.isTraining = true
      faceRegistration.value.statusText = 'Procesando rostros y generando embeddings...'
      
      try {
        console.log('🎯 Entrenando modelo facial...')
        
        // Enviar fotos al backend para registro facial
        const result = await faceService.registerFace(
          editingEmployee.value.id,
          faceRegistration.value.capturedPhotos
        )
        
        if (result.success) {
          faceRegistration.value.status = 'trained'
          faceRegistration.value.statusText = 'Rostros procesados y guardados correctamente'
          faceRegistration.value.confidence = 95
          faceRegistration.value.photosCount = result.photos_count
          
          console.log('✅ Rostros procesados:', result.message)
        } else {
          throw new Error(result.message)
        }
        
      } catch (error) {
        console.error('Error entrenando modelo:', error)
        faceRegistration.value.status = 'error'
        faceRegistration.value.statusText = `Error: ${error.message || 'Error en entrenamiento'}`
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
    
    const saveEmployee = async () => {
      if (!form.value?.validate()) {
        console.log('Formulario no válido')
        return
      }
      
      saving.value = true
      try {
        // Preparar datos para enviar
        const employeeData = {
          ...employeeForm.value,
          area: typeof employeeForm.value.area === 'object' ? employeeForm.value.area.id : employeeForm.value.area
        }
        
        console.log('Enviando datos del empleado:', employeeData)
        
        if (editingEmployee.value) {
          // ACTUALIZAR EN API REAL
          console.log('Actualizando empleado ID:', editingEmployee.value.id)
          console.log('Datos para actualizar:', employeeData)
          await employeeService.update(editingEmployee.value.id, employeeData)
        } else {
          // CREAR EN API REAL
          console.log('Creando nuevo empleado')
          await employeeService.create(employeeData)
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
      } finally {
        saving.value = false
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
      valid,
      form,
      dialogReady,
      editingEmployee,
      employeeToDelete,
      employees,
      areas,
      employeeForm,
      positions,
      statusFilter,
      statusOptions,
      headers,
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
      trainFaceModel,
      resetFaceRegistration
    }
  }
}
</script>
