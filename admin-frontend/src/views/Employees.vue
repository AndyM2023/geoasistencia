<template>
  <div>
    <v-row class="mt-2 employee-header">
      <v-col cols="12">
        <div class="d-flex justify-space-between align-center">
          <h1 class="text-h4 text-white">Gestión de Empleados</h1>
                     <v-btn color="blue-400" prepend-icon="mdi-plus" @click="openNewEmployeeDialog" class="neon-border">
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
                <p class="text-grey-400 mb-1">{{ positions.find(p => p.value === employee.position)?.title || employee.position }}</p>
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
                  name="first_name"
                  label="Nombre"
                  variant="outlined"
                  color="blue-400"
                  maxlength="50"
                  :rules="[
                    v => !!v || 'El nombre es requerido',
                    v => !/\d/.test(v) || 'El nombre no puede contener números',
                    v => v.length >= 2 || 'El nombre debe tener al menos 2 caracteres',
                    v => /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(v) || 'Solo se permiten letras y espacios'
                  ]"
                  required
                  @input="validateNameField"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="employeeForm.last_name"
                  name="last_name"
                  label="Apellido"
                  variant="outlined"
                  color="blue-400"
                  maxlength="50"
                  :rules="[
                    v => !!v || 'El apellido es requerido',
                    v => !/\d/.test(v) || 'El apellido no puede contener números',
                    v => v.length >= 2 || 'El apellido debe tener al menos 2 caracteres',
                    v => /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(v) || 'Solo se permiten letras y espacios'
                  ]"
                  required
                  @input="validateNameField"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12">
                <v-text-field
                  v-model="employeeForm.email"
                  label="Email"
                  type="email"
                  variant="outlined"
                  color="blue-400"
                  :rules="[v => !!v || 'El email es requerido', v => /.+@.+\..+/.test(v) || 'Email inválido']"
                  required
                ></v-text-field>
              </v-col>
              
                                             <v-col cols="12" sm="6">
                  <v-text-field
                    v-model="employeeForm.cedula"
                    label="Cédula de Identidad"
                    variant="outlined"
                    color="blue-400"
                    :rules="[
                      v => !!v || 'La cédula es requerida',
                      v => /^\d{7,10}$/.test(v) || 'La cédula debe tener entre 7 y 10 dígitos',
                      v => !existingCedulas.includes(v) || 'Esta cédula ya está registrada'
                    ]"
                    :required="!editingEmployee"
                    :disabled="editingEmployee"
                    :hint="editingEmployee ? 'La cédula no se puede modificar' : 'Se usará como contraseña del usuario'"
                    persistent-hint
                    @input="validateCedula"
                  ></v-text-field>
                  
                  
                </v-col>
              
              <v-col cols="12">
                <v-alert
                  type="info"
                  variant="tonal"
                  class="mb-4"
                  icon="mdi-information"
                >
                  <template v-slot:title>
                    <strong>🔐 Usuario y Contraseña Automáticos</strong>
                  </template>
                  <div class="text-body-2">
                    <p class="mb-2">
                      <strong>Usuario:</strong> Se generará automáticamente usando la primera letra del nombre + apellido completo
                    </p>
                    <p class="mb-2">
                      <strong>Contraseña:</strong> Será la cédula ingresada
                    </p>
                    <p class="text-caption text-grey-600">
                      <strong>Ejemplo:</strong> "Luis Roma" con cédula "12345678" → Usuario: <code>lroma</code>, Contraseña: <code>12345678</code>
                    </p>
                  </div>
                </v-alert>
              </v-col>
              
              <v-col cols="12" sm="6">
                <v-select
                  v-model="employeeForm.position"
                  :items="positions"
                  item-title="title"
                  item-value="value"
                  label="Cargo"
                  variant="outlined"
                  color="blue-400"
                  :rules="[v => !!v || 'El cargo es requerido']"
                  required
                  placeholder="Selecciona un cargo"
                ></v-select>
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
import { ref, onMounted, onUnmounted, computed } from 'vue'
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
     
                 // Computed property para obtener cédulas existentes (excluyendo el empleado actual)
       const existingCedulas = computed(() => {
         if (!editingEmployee.value) {
           // Si es un nuevo empleado, todas las cédulas existentes están prohibidas
           return employees.value.map(emp => emp.cedula_display || emp.cedula || emp.user.cedula).filter(cedula => cedula)
         } else {
           // Si es edición, excluir la cédula del empleado actual
           return employees.value
             .filter(emp => emp.id !== editingEmployee.value.id)
             .map(emp => emp.cedula_display || emp.cedula || emp.user.cedula)
             .filter(cedula => cedula)
         }
       })
    
    const employeeForm = ref({
      first_name: '',
      last_name: '',
      email: '',
      cedula: '',
      position: 'otro', // Usar valor por defecto
      area: null
    })
    
    const positions = [
      { title: 'Desarrollador', value: 'desarrollador' },
      { title: 'Diseñador', value: 'disenador' },
      { title: 'Secretario/a', value: 'secretario' },
      { title: 'Gerente', value: 'gerente' },
      { title: 'Analista', value: 'analista' },
      { title: 'Ingeniero', value: 'ingeniero' },
      { title: 'Contador', value: 'contador' },
      { title: 'Recursos Humanos', value: 'recursos_humanos' },
      { title: 'Marketing', value: 'marketing' },
      { title: 'Ventas', value: 'ventas' },
      { title: 'Soporte Técnico', value: 'soporte' },
      { title: 'Administrativo', value: 'administrativo' },
      { title: 'Operativo', value: 'operativo' },
      { title: 'Otro', value: 'otro' }
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
        // Buscar en el título del cargo (más legible para el usuario)
        positions.find(p => p.value === employee.position)?.title?.toLowerCase().includes(searchTerm) ||
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
         
         // 🔍 DEBUG: Verificar qué datos vienen del backend
         console.log('🔍 loadEmployees - Datos recibidos del backend:')
         if (employees.value.length > 0) {
           const firstEmployee = employees.value[0]
           console.log('   - Primer empleado position:', firstEmployee.position)
           console.log('   - Primer empleado position type:', typeof firstEmployee.position)
           console.log('   - Primer empleado completo:', JSON.stringify(firstEmployee, null, 2))
         }
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
        console.log('🔍 Áreas cargadas:', JSON.stringify(areas.value, null, 2))
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
     
     const openNewEmployeeDialog = () => {
       // Limpiar estado de edición
       editingEmployee.value = null
       
       // Resetear formulario
       employeeForm.value = {
         first_name: '',
         last_name: '',
         email: '',
         cedula: '',
         position: 'otro',
         area: null
       }
       
       // Resetear estado facial
       resetFaceRegistration()
       
       // Resetear validación del formulario
       if (form.value) {
         form.value.resetValidation()
       }
       
       // Abrir diálogo
       showDialog.value = true
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
                console.log('🔍 editEmployee - Empleado recibido:', JSON.stringify(employee, null, 2))
         console.log('🔍 editEmployee - User completo:', JSON.stringify(employee.user, null, 2))
         console.log('🔍 editEmployee - Cédula del empleado:', employee.cedula)
         console.log('🔍 editEmployee - Cédula del user:', employee.user.cedula)
         console.log('🔍 editEmployee - Cédula display:', employee.cedula_display)
         console.log('🔍 editEmployee - Tipo de cédula empleado:', typeof employee.cedula)
       
       editingEmployee.value = employee
                employeeForm.value = {
           first_name: employee.user.first_name,
           last_name: employee.user.last_name,
           email: employee.user.email,
           cedula: employee.cedula_display || employee.cedula || employee.user.cedula || '', // Usar cedula_display del backend
           position: employee.position || 'otro', // Usar valor por defecto si no hay cargo
           area: employee.area
         }
       
       console.log('🔍 editEmployee - Formulario preparado:', JSON.stringify(employeeForm.value, null, 2))
       console.log('🔍 editEmployee - Área del empleado:', employee.area)
       console.log('🔍 editEmployee - Área en formulario:', employeeForm.value.area)
       console.log('🔍 editEmployee - Position del empleado:', employee.position)
       console.log('🔍 editEmployee - Position en formulario:', employeeForm.value.position)
       console.log('🔍 editEmployee - Cédula en formulario:', employeeForm.value.cedula)
       
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
         
         // 🔍 DEBUG: Mostrar datos que se van a enviar
         console.log('📤 Datos del formulario a enviar:', JSON.stringify(employeeForm.value, null, 2))
         console.log('👤 Empleado editando:', JSON.stringify(editingEmployee.value, null, 2))
         
         if (editingEmployee.value) {
           // Actualizar empleado existente
           console.log('🔄 Actualizando empleado ID:', editingEmployee.value.id)
           console.log('📋 Datos de actualización:', JSON.stringify(employeeForm.value, null, 2))
           
           savedEmployee = await employeeService.update(editingEmployee.value.id, employeeForm.value)
           showMessage('Empleado actualizado correctamente')
         } else {
           // Crear nuevo empleado
           console.log('➕ Creando nuevo empleado')
           console.log('📋 Datos de creación:', employeeForm.value)
           
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
        
        // 🔄 ACTUALIZAR LISTA INMEDIATAMENTE después de cerrar diálogo
        try {
          await loadEmployees()
          console.log('✅ Lista de empleados actualizada después de cerrar diálogo')
        } catch (error) {
          console.error('❌ Error actualizando lista después de cerrar diálogo:', error)
        }
        editingEmployee.value = null
        employeeForm.value = {
          first_name: '',
          last_name: '',
          email: '',
          cedula: '',
          position: 'otro', // Usar valor por defecto
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
      faceRegistration.value.photosCount = result.photos_count || result.photosCount || 0
      showFaceRegistration.value = false
      
      // 🔄 ACTUALIZAR LISTA INMEDIATAMENTE después del registro facial
      try {
        await loadEmployees()
        console.log('✅ Lista de empleados actualizada después del registro facial')
      } catch (error) {
        console.error('❌ Error actualizando lista después del registro facial:', error)
      }
      
      // Mostrar mensaje de éxito
      showMessage('Registro facial completado exitosamente')
      
      // Cerrar el diálogo principal después del registro facial
      showDialog.value = false
      dialogReady.value = false
      editingEmployee.value = null
      resetFaceRegistration()
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
      
      // ✅ SIMPLIFICADO: Solo mostrar estado de procesamiento
      // Las fotos ya se procesan automáticamente en FaceRegistration.vue
      faceRegistration.value.isTraining = true
      faceRegistration.value.statusText = 'Procesando rostros y generando embeddings...'
      
      try {
        console.log('🎯 Iniciando procesamiento facial...')
        console.log('📸 Fotos a procesar:', faceRegistration.value.capturedPhotos.length)
        console.log('👤 Empleado ID:', editingEmployee.value.id)
        
        // ✅ NO procesar fotos aquí - ya se procesan en FaceRegistration.vue
        // Solo simular el tiempo de procesamiento para mostrar el estado
        await new Promise(resolve => setTimeout(resolve, 2000))
        
        // Cambiar estado a completado
        faceRegistration.value.status = 'trained'
        faceRegistration.value.statusText = 'Rostros procesados y guardados correctamente'
        faceRegistration.value.photosCount = faceRegistration.value.capturedPhotos.length
        
        console.log('✅ Procesamiento simulado completado')
        
      } catch (error) {
        console.error('❌ Error en procesamiento:', error)
        faceRegistration.value.status = 'error'
        faceRegistration.value.statusText = `Error: ${error.message || 'Error en procesamiento'}`
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

         // ✅ VALIDACIÓN: Función para validar campos de nombre y apellido
     const validateNameField = (event) => {
       const value = event.target.value;
       const fieldName = event.target.name;
       
       // Remover números y caracteres especiales no permitidos
       let cleanValue = value.replace(/[\d!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/g, '');
       
       // Remover espacios múltiples y espacios al inicio/final
       cleanValue = cleanValue.replace(/\s+/g, ' ').trim();
       
       // Si el valor original contenía caracteres no permitidos, actualizar el campo
       if (value !== cleanValue) {
         // Actualizar el campo correspondiente
         if (fieldName === 'first_name') {
           employeeForm.value.first_name = cleanValue;
         } else if (fieldName === 'last_name') {
           employeeForm.value.last_name = cleanValue;
         }
         
         // Mostrar mensaje informativo
         showMessage('Solo se permiten letras y espacios en nombres y apellidos', 'warning');
         
         // Forzar la validación del formulario
         if (form.value) {
           form.value.validate();
         }
       }
       
       // Validar que no quede solo espacios o esté vacío después de la limpieza
       if (cleanValue === '' || cleanValue.trim() === '') {
         if (fieldName === 'first_name') {
           employeeForm.value.first_name = '';
         } else if (fieldName === 'last_name') {
           employeeForm.value.last_name = '';
         }
         
         showMessage('El campo no puede estar vacío', 'error');
         return;
       }
       
       // Validar que el nombre/apellido tenga al menos 2 caracteres
       if (cleanValue.length > 0 && cleanValue.length < 2) {
         showMessage('El nombre y apellido deben tener al menos 2 caracteres', 'warning');
       }
     }
     
     // ✅ VALIDACIÓN: Función para validar cédula
     const validateCedula = (event) => {
       const value = event.target.value;
       
       // Solo permitir números
       let cleanValue = value.replace(/\D/g, '');
       
       // Si el valor original contenía caracteres no numéricos, actualizar el campo
       if (value !== cleanValue) {
         employeeForm.value.cedula = cleanValue;
         showMessage('La cédula solo puede contener números', 'warning');
       }
       
       // Limitar a 10 dígitos máximo
       if (cleanValue.length > 10) {
         employeeForm.value.cedula = cleanValue.substring(0, 10);
         showMessage('La cédula no puede tener más de 10 dígitos', 'warning');
       }
       
       // Forzar la validación del formulario
       if (form.value) {
         form.value.validate();
       }
     }
    
    onMounted(() => {
      loadEmployees()
      loadAreas()
      
      // 🚀 IMPLEMENTAR POLLING AUTOMÁTICO
      // Actualizar lista de empleados cada 30 segundos
      const pollingInterval = setInterval(async () => {
        console.log('🔄 Polling automático: actualizando lista de empleados...')
        try {
          await loadEmployees()
          console.log('✅ Lista de empleados actualizada automáticamente')
        } catch (error) {
          console.error('❌ Error en polling automático:', error)
        }
      }, 30000) // 30 segundos
      
      // Limpiar intervalo cuando el componente se desmonte
      onUnmounted(() => {
        clearInterval(pollingInterval)
        console.log('🧹 Polling automático detenido')
      })
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
       existingCedulas,
      headers,
      mensaje,
      viewMode,
      filteredEmployees,
      loadEmployees,
             loadAreas,
       onDialogOpened,
       openNewEmployeeDialog,
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
      checkFaceRegistrationStatus,
             // Funciones de validación
       validateNameField,
       validateCedula
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
