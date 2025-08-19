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
                  class="employee-photo clickable-photo"
                  @click="openPhotoModal(employee)"
                  title="Haz clic para ver la foto completa"
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
                <p class="text-grey-600 text-xs mt-2">Cédula: {{ employee.cedula_display || employee.user?.cedula || 'N/A' }}</p>
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
                   label="Nombres"
                  variant="outlined"
                  color="blue-400"
                   maxlength="20"
                  :rules="[
                    v => !!v || 'El nombre es requerido',
                     v => v.length > 20 ? 'El nombre no puede exceder 20 caracteres' : true,
                     v => !/^[A-Za-zÁáÉéÍíÓóÚúÑñ\s]+$/.test(v) ? 'El nombre solo puede contener letras' : true
                  ]"
                  required
                   @input="(value) => filterLettersOnly(value, 'first_name')"
                   @keydown="blockInvalidCharacters($event, 'first_name')"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="employeeForm.last_name"
                  name="last_name"
                   label="Apellidos"
                  variant="outlined"
                  color="blue-400"
                   maxlength="30"
                  :rules="[
                    v => !!v || 'El apellido es requerido',
                     v => v.length > 30 ? 'Los apellidos no pueden exceder 30 caracteres' : true,
                     v => !/^[A-Za-zÁáÉéÍíÓóÚúÑñ\s]+$/.test(v) ? 'Los apellidos solo pueden contener letras y espacios' : true
                  ]"
                  required
                   @input="(value) => filterLettersOnly(value, 'last_name')"
                   @keydown="blockInvalidCharacters($event, 'last_name')"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12">
                <v-text-field
                  v-model="employeeForm.email"
                   label="Correo Electrónico"
                  type="email"
                  variant="outlined"
                  color="blue-400"
                   :rules="[
                     v => !!v || 'El email es requerido',
                     v => /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(v) || 'Debe ser un email válido'
                   ]"
                  required
                   @input="filterEmail"
                   @keydown="blockInvalidEmailCharacters"
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
                      v => /^\d{10}$/.test(v) || 'La cédula debe tener exactamente 10 dígitos',
                      v => validateEcuadorianCedula(v) || 'Cédula ecuatoriana inválida',
                      v => !existingCedulas.includes(v) || 'Esta cédula ya está registrada'
                    ]"
                    :required="!editingEmployee"
                    :disabled="editingEmployee"
                    :hint="editingEmployee ? 'La cédula no se puede modificar' : 'Se usará como contraseña del usuario'"
                    persistent-hint
                     @input="filterNumbersOnly"
                     @keydown="blockNonNumericCharacters"
                     @paste="blockCedulaPaste"
                  ></v-text-field>
                  
                  
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
                  :rules="[
                    v => !!v || 'El cargo es requerido'
                  ]"
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
                  :rules="[
                    v => !!v || 'El área es requerida',
                    v => v !== null || 'Debe seleccionar un área válida'
                  ]"
                  required
                  placeholder="Selecciona un área"
                ></v-select>
              </v-col>
            </v-row>

            <!-- Campo de Foto del Empleado -->
            <v-row>
              <v-col cols="12">
                <v-divider class="mb-4"></v-divider>
                <h3 class="text-white mb-4">📸 Foto del Empleado</h3>
              </v-col>
            </v-row>

            <v-row>
              <v-col cols="12">
                <v-card class="bg-dark-surface border border-blue-500/20">
                  <v-card-title class="text-sm text-blue-400">📷 Foto de Perfil</v-card-title>
                  <v-card-text>
                    <!-- Vista previa de la foto actual -->
                    <div v-if="(employeeForm.photo && employeeForm.photo !== 'DELETE_PHOTO') || (editingEmployee && editingEmployee.photo && employeeForm.photo !== 'DELETE_PHOTO')" class="text-center mb-4">
                      <v-avatar size="120" class="mb-3">
                        <v-img 
                          v-if="getPhotoUrl(employeeForm.photo) && employeeForm.photo !== 'DELETE_PHOTO'" 
                          :src="getPhotoUrl(employeeForm.photo)" 
                          cover
                          class="employee-photo-preview"
                        ></v-img>
                        <v-img 
                          v-else-if="editingEmployee && editingEmployee.photo && employeeForm.photo !== 'DELETE_PHOTO'" 
                          :src="editingEmployee.photo" 
                          cover
                          class="employee-photo-preview"
                        ></v-img>
                      </v-avatar>
                      <p class="text-grey-300 text-sm">Foto actual</p>
                    </div>

                    <!-- Opciones para agregar/editar foto -->
                    <div class="d-flex gap-3 justify-center flex-wrap">
                      <!-- Subir archivo -->
                      <v-btn
                        @click="$refs.fileInput.click()"
                        color="blue-400"
                        variant="outlined"
                        prepend-icon="mdi-upload"
                        size="large"
                      >
                        📁 Subir Archivo
                      </v-btn>

                      <!-- Tomar foto con cámara -->
                      <v-btn
                        @click="showPhotoCapture = true"
                        color="green-400"
                        variant="outlined"
                        prepend-icon="mdi-camera"
                        size="large"
                      >
                        📷 Tomar Foto
                      </v-btn>

                      <!-- Eliminar foto -->
                      <v-btn
                        v-if="(employeeForm.photo && employeeForm.photo !== 'DELETE_PHOTO') || (editingEmployee && editingEmployee.photo && employeeForm.photo !== 'DELETE_PHOTO')"
                        @click="removePhoto"
                        color="red-400"
                        variant="outlined"
                        prepend-icon="mdi-delete"
                        size="large"
                      >
                        🗑️ Eliminar
                      </v-btn>
                    </div>

                    <!-- Input de archivo oculto -->
                    <input
                      ref="fileInput"
                      type="file"
                      accept="image/*"
                      style="display: none"
                      @change="onFileSelected"
                    />

                    <!-- Información de ayuda -->
                    <div class="mt-4 text-center">
                      <p class="text-blue-400 text-xs mb-1">
                        📋 Formatos soportados: JPG, PNG, GIF
                      </p>
                      <p class="text-grey-400 text-xs">
                        📏 Tamaño máximo: 5MB | 📐 Resolución recomendada: 400x400px
                      </p>
                    </div>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>

                         <!-- Sección de Registro Facial - Solo visible después de crear el empleado -->
             <v-row v-if="editingEmployee && editingEmployee.id">
              <v-col cols="12">
                <v-divider class="mb-4"></v-divider>
                <h3 class="text-white mb-4"> Registro Facial</h3>
              </v-col>
            </v-row>

             <v-row v-if="editingEmployee && editingEmployee.id">
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
                        block
                      >
                        Iniciar Registro Facial
                      </v-btn>
                      
                       <p class="text-blue-400 text-xs mt-2">
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

    <!-- Modal para mostrar foto expandida -->
    <v-dialog v-model="showPhotoModal" max-width="600px" persistent>
      <v-card class="bg-dark-surface border border-blue-500/20">
        <v-card-title class="text-white d-flex justify-space-between align-center">
          <span>📸 Foto</span>
          <v-btn 
            icon="mdi-close" 
            variant="text" 
            color="white" 
            @click="closePhotoModal"
            size="small"
          ></v-btn>
        </v-card-title>
        
        <v-card-text class="text-center pa-6">
          <div v-if="selectedEmployeePhoto">
            <!-- Solo la foto expandida -->
            <v-img 
              :src="selectedEmployeePhoto.photo_url" 
              :alt="`Foto de ${selectedEmployeePhoto.full_name}`"
              max-height="500"
              contain
              class="expanded-photo"
              style="border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.3);"
            ></v-img>
          </div>
        </v-card-text>
        
        <v-card-actions class="justify-center pa-4">
          <v-btn 
            color="blue-400" 
            variant="outlined" 
            @click="closePhotoModal"
            prepend-icon="mdi-close"
          >
            Cerrar
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

    <!-- Componente de captura de foto -->
    <v-dialog v-model="showPhotoCapture" max-width="500px" persistent>
      <v-card class="bg-dark-surface border border-blue-500/20">
        <v-card-title class="text-white">
          📷 Capturar Foto del Empleado
        </v-card-title>
        
        <v-card-text>
          <div class="text-center">
            <!-- Vista previa de la cámara -->
            <div v-if="!capturedPhoto" class="camera-preview mb-4">
              <video
                ref="video"
                autoplay
                playsinline
                class="camera-video"
                style="width: 100%; max-width: 400px; height: 300px; background: #000; border-radius: 8px;"
              ></video>
              
              <div class="mt-3">
                <v-btn
                  @click="startCamera"
                  color="blue-400"
                  prepend-icon="mdi-camera"
                  size="large"
                  :loading="cameraLoading"
                >
                  Iniciar Cámara
                </v-btn>
              </div>
            </div>

            <!-- Vista previa de la foto capturada -->
            <div v-if="capturedPhoto" class="captured-photo-preview mb-4">
              <v-avatar size="200" class="mb-3">
                <v-img :src="capturedPhoto" cover></v-img>
              </v-avatar>
              <p class="text-grey-300">Foto capturada</p>
            </div>

            <!-- Controles de la cámara -->
            <div v-if="!capturedPhoto && cameraActive" class="camera-controls">
              <v-btn
                @click="capturePhoto"
                color="green-400"
                prepend-icon="mdi-camera"
                size="large"
                class="mx-2"
              >
                📸 Capturar
              </v-btn>
              
              <v-btn
                @click="stopCamera"
                color="red-400"
                variant="outlined"
                size="large"
                class="mx-2"
              >
                ⏹️ Detener
              </v-btn>
            </div>

            <!-- Controles después de capturar -->
            <div v-if="capturedPhoto" class="capture-controls">
              <v-btn
                @click="acceptPhoto"
                color="green-400"
                prepend-icon="mdi-check"
                size="large"
                class="mx-2"
              >
                ✅ Aceptar
              </v-btn>
              
              <v-btn
                @click="retakePhoto"
                color="orange-400"
                variant="outlined"
                size="large"
                class="mx-2"
              >
                🔄 Retomar
              </v-btn>
            </div>
          </div>
        </v-card-text>
        
        <v-card-actions class="justify-end pa-4">
          <v-btn 
            color="grey-600" 
            variant="outlined" 
            @click="closePhotoCapture"
          >
            Cancelar
          </v-btn>
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
    
    // Estado para captura de foto
    const showPhotoCapture = ref(false)
    const capturedPhoto = ref(null)
    const cameraActive = ref(false)
    const cameraLoading = ref(false)
    const video = ref(null)
    const stream = ref(null)
    
    const editingEmployee = ref(null)
    const employeeToDelete = ref(null)
    
    // Estado para modal de foto expandida
    const showPhotoModal = ref(false)
    const selectedEmployeePhoto = ref(null)
    
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
      position: 'desarrollador', // Usar valor por defecto más apropiado
      area: null,
      photo: null // Nuevo campo para la foto
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
      { title: 'Nombre Completo', key: 'full_name', sortable: true },
      { title: 'Cédula', key: 'cedula_display', sortable: true },
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
        employee.cedula_display?.toLowerCase().includes(searchTerm) ||
        employee.user?.cedula?.toLowerCase().includes(searchTerm) ||
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
         position: 'desarrollador',
         area: null,
         photo: null // Resetear foto
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
           position: employee.position || 'desarrollador', // Usar valor por defecto más apropiado
           area: employee.area?.id || employee.area, // Asegurar que se envíe solo el ID del área
           photo: null // No enviar foto existente en actualización, solo en creación
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
    
    // Funciones para el modal de foto expandida
    const openPhotoModal = (employee) => {
      console.log('📸 Abriendo modal de foto para:', employee.full_name)
      selectedEmployeePhoto.value = employee
      showPhotoModal.value = true
    }
    
    const closePhotoModal = () => {
      console.log('🚪 Cerrando modal de foto')
      showPhotoModal.value = false
      selectedEmployeePhoto.value = null
    }
    
         const saveEmployee = async () => {
       if (!form.value?.validate()) return
       
       saving.value = true
       try {
         let savedEmployee
         
         // 🔍 DEBUG: Mostrar datos que se van a enviar
         console.log('📤 Datos del formulario a enviar:', JSON.stringify(employeeForm.value, null, 2))
         console.log('👤 Empleado editando:', JSON.stringify(editingEmployee.value, null, 2))
         
         // Validación adicional del position
         if (employeeForm.value.position) {
           const validPositions = [
             'desarrollador', 'disenador', 'secretario', 'gerente', 'analista',
             'ingeniero', 'contador', 'recursos_humanos', 'marketing', 'ventas',
             'soporte', 'administrativo', 'operativo', 'otro'
           ]
           
           if (!validPositions.includes(employeeForm.value.position)) {
             console.error(`❌ Position inválido en el formulario: "${employeeForm.value.position}"`)
             showMessage(`Cargo inválido: "${employeeForm.value.position}". Debe seleccionar una opción válida.`, 'error')
             return
           }
         }
         
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
          position: 'desarrollador', // Usar valor por defecto
          area: null,
          photo: null // Resetear foto
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
        console.log('Iniciando procesamiento facial...')
        console.log('Fotos a procesar:', faceRegistration.value.capturedPhotos.length)
        console.log('Empleado ID:', editingEmployee.value.id)
        
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

                   // ✅ VALIDACIÓN: Función para validar cédula ecuatoriana
      const validateEcuadorianCedula = (cedula) => {
        if (cedula.length !== 10) return false
        
        // Verificar que todos sean dígitos
        if (!/^\d+$/.test(cedula)) return false
        
        // Verificar que no sea una cédula de ceros
        if (cedula === '0000000000') return false
        
        // Algoritmo de validación ecuatoriana
        let suma = 0
        const coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
        
        for (let i = 0; i < 9; i++) {
          let producto = parseInt(cedula[i]) * coeficientes[i]
          if (producto >= 10) {
            producto = Math.floor(producto / 10) + (producto % 10)
          }
          suma += producto
        }
        
        const digitoVerificador = parseInt(cedula[9])
        const modulo = suma % 10
        const resultado = modulo === 0 ? 0 : 10 - modulo
        
        return resultado === digitoVerificador
      }

      // ✅ FUNCIÓN: Filtrar solo letras y espacios (para nombre y apellidos)
      const filterLettersOnly = (value, fieldName) => {
        // Asegurar que value sea una cadena de texto
        if (typeof value !== 'string') {
          console.warn(`filterLettersOnly: valor no es string, tipo: ${typeof value}`, value)
          return ''
        }
        
        // Remover números y caracteres especiales, mantener solo letras, espacios y acentos
        const filtered = value.replace(/[^A-Za-zÁáÉéÍíÓóÚúÑñ\s]/g, '')
        
        // Actualizar el valor del campo con solo caracteres permitidos
        employeeForm.value[fieldName] = filtered
        
        return filtered
      }

      // ✅ FUNCIÓN: Filtrar email (permitir solo caracteres válidos para email)
      const filterEmail = (value) => {
        // Asegurar que value sea una cadena de texto
        if (typeof value !== 'string') {
          console.warn(`filterEmail: valor no es string, tipo: ${typeof value}`, value)
          return ''
        }
        
        // Permitir letras, números, puntos, guiones bajos, guiones medios, arrobas y puntos
        const filtered = value.replace(/[^a-zA-Z0-9._%+-@]/g, '')
        
        // Actualizar el valor del campo
        employeeForm.value.email = filtered
        
        return filtered
      }

      // ✅ FUNCIÓN: Filtrar solo números (para cédula)
      const filterNumbersOnly = (value) => {
        // Asegurar que value sea una cadena de texto
        if (typeof value !== 'string') {
          console.warn(`filterNumbersOnly: valor no es string, tipo: ${typeof value}`, value)
          return ''
        }
        
        // Remover todo excepto números
        const filtered = value.replace(/\D/g, '')
        
        // BLOQUEO TOTAL: Si ya tiene 10 dígitos, no permitir más entrada
        if (filtered.length > 10) {
          // Mantener solo los primeros 10 dígitos
          employeeForm.value.cedula = filtered.slice(0, 10)
          return filtered.slice(0, 10)
       }
       
       // Limitar a 10 dígitos máximo
        employeeForm.value.cedula = filtered.slice(0, 10)
        
        return filtered.slice(0, 10)
      }

      // ✅ FUNCIÓN: Bloquear caracteres no permitidos en nombre y apellidos
      const blockInvalidCharacters = (event, fieldName) => {
        const key = event.key
        const allowedKeys = [
          'Backspace', 'Delete', 'Tab', 'Enter', 'Escape', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown',
          'Home', 'End', 'PageUp', 'PageDown', 'Insert', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12'
        ]
        
        // Permitir teclas de navegación y control
        if (allowedKeys.includes(key)) {
          return true
        }
        
        // Permitir solo letras, espacios y acentos
        const allowedPattern = /^[A-Za-zÁáÉéÍíÓóÚúÑñ\s]$/
        
        if (!allowedPattern.test(key)) {
          // Prevenir la entrada del carácter
          event.preventDefault()
          return false
        }
        
        return true
      }

      // ✅ FUNCIÓN: Bloquear solo números en cédula
      const blockNonNumericCharacters = (event) => {
        const key = event.key
        const allowedKeys = [
          'Backspace', 'Delete', 'Tab', 'Enter', 'Escape', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown',
          'Home', 'End', 'PageUp', 'PageDown', 'Insert', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12'
        ]
        
        // Permitir teclas de navegación y control
        if (allowedKeys.includes(key)) {
          return true
        }
        
        // BLOQUEO TOTAL: Si ya tiene 10 dígitos, solo permitir Backspace y Delete
        if (employeeForm.value.cedula.length >= 10 && key !== 'Backspace' && key !== 'Delete') {
          // Prevenir la entrada del carácter
          event.preventDefault()
          return false
        }
        
        // Permitir solo números
        const allowedPattern = /^[0-9]$/
        
        if (!allowedPattern.test(key)) {
          // Prevenir la entrada del carácter
          event.preventDefault()
          return false
        }
        
        return true
      }

      // ✅ FUNCIÓN: Bloquear caracteres no válidos en email
      const blockInvalidEmailCharacters = (event) => {
        const key = event.key
        const allowedKeys = [
          'Backspace', 'Delete', 'Tab', 'Enter', 'Escape', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown',
          'Home', 'End', 'PageUp', 'PageDown', 'Insert', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12'
        ]
        
        // Permitir teclas de navegación y control
        if (allowedKeys.includes(key)) {
          return true
        }
        
        // Permitir letras, números, puntos, guiones, arrobas y símbolos válidos para email
        const allowedPattern = /^[a-zA-Z0-9._%+-@]$/
        
        if (!allowedPattern.test(key)) {
          // Prevenir la entrada del carácter
          event.preventDefault()
          return false
        }
        
        return true
      }

      // ✅ FUNCIÓN: Bloquear pegado de texto que exceda 10 dígitos en cédula
      const blockCedulaPaste = (event) => {
        // Obtener el texto del portapapeles
        const clipboardData = event.clipboardData || window.clipboardData
        const pastedText = clipboardData.getData('text')
        
        // Si el texto pegado contiene caracteres no numéricos, bloquear
        if (!/^\d+$/.test(pastedText)) {
          event.preventDefault()
          return false
        }
        
        // Si al pegar excedería los 10 dígitos, bloquear
        const currentLength = employeeForm.value.cedula.length
        if (currentLength + pastedText.length > 10) {
          event.preventDefault()
          return false
        }
        
        return true
     }

    // ✅ FUNCIÓN: Manejar la selección de archivo para la foto
    const onFileSelected = (event) => {
      const file = event.target.files[0]
      if (file) {
        // Validar tipo de archivo
        if (!file.type.startsWith('image/')) {
          showMessage('Solo se permiten archivos de imagen', 'error')
          return
        }
        
        // Validar tamaño (5MB)
        if (file.size > 5 * 1024 * 1024) {
          showMessage('El archivo es demasiado grande. Máximo 5MB', 'error')
          return
        }
        
        // Guardar el archivo directamente
        employeeForm.value.photo = file
        console.log('📸 Archivo seleccionado:', file.name, file.size, file.type)
      }
    }

    // ✅ FUNCIÓN: Eliminar la foto actual
    const removePhoto = () => {
      // Si estamos editando un empleado con foto existente, marcar para eliminación
      if (editingEmployee.value && editingEmployee.value.photo) {
        // Marcar que se debe eliminar la foto existente
        employeeForm.value.photo = 'DELETE_PHOTO'
        console.log('🗑️ Foto existente marcada para eliminación')
      } else {
        // Si es una foto nueva, simplemente limpiar
        employeeForm.value.photo = null
        console.log('🗑️ Foto nueva eliminada')
      }
    }
    
    // ✅ FUNCIÓN: Convertir base64 a archivo
    const base64ToFile = (base64String, filename = 'photo.jpg') => {
      // Remover el prefijo data:image/...;base64, si existe
      const base64Data = base64String.includes(',') ? base64String.split(',')[1] : base64String
      
      // Convertir base64 a blob
      const byteCharacters = atob(base64Data)
      const byteNumbers = new Array(byteCharacters.length)
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i)
      }
      const byteArray = new Uint8Array(byteNumbers)
      
      // Crear archivo
      const blob = new Blob([byteArray], { type: 'image/jpeg' })
      const file = new File([blob], filename, { type: 'image/jpeg' })
      
      return file
    }
    
    // ✅ FUNCIÓN: Obtener URL de la foto para vista previa
    const getPhotoUrl = (photo) => {
      if (!photo) return null
      
      if (photo instanceof File) {
        // Si es un archivo, crear URL temporal
        return URL.createObjectURL(photo)
      } else if (typeof photo === 'string' && photo.startsWith('data:')) {
        // Si es base64, usar directamente
        return photo
      } else if (typeof photo === 'string') {
        // Si es una URL, usar directamente
        return photo
      }
      
      return null
    }
    
    // ✅ FUNCIÓN: Iniciar la cámara
    const startCamera = async () => {
      try {
        cameraLoading.value = true
        stream.value = await navigator.mediaDevices.getUserMedia({ 
          video: { 
            width: { ideal: 640 }, 
            height: { ideal: 480 },
            facingMode: 'user' // Cámara frontal
          } 
        })
        
        if (video.value) {
          video.value.srcObject = stream.value
          cameraActive.value = true
          console.log('📹 Cámara iniciada')
        }
      } catch (error) {
        console.error('❌ Error al iniciar cámara:', error)
        mensaje.value = {
          show: true,
          text: 'Error al acceder a la cámara. Verifica los permisos.',
          type: 'error'
        }
      } finally {
        cameraLoading.value = false
      }
    }
    
    // ✅ FUNCIÓN: Detener la cámara
    const stopCamera = () => {
      if (stream.value) {
        stream.value.getTracks().forEach(track => track.stop())
        stream.value = null
      }
      cameraActive.value = false
      console.log('⏹️ Cámara detenida')
    }
    
    // ✅ FUNCIÓN: Capturar foto
    const capturePhoto = () => {
      if (video.value && cameraActive.value) {
        const canvas = document.createElement('canvas')
        const context = canvas.getContext('2d')
        
        canvas.width = video.value.videoWidth
        canvas.height = video.value.videoHeight
        
        context.drawImage(video.value, 0, 0)
        
        capturedPhoto.value = canvas.toDataURL('image/jpeg', 0.8)
        console.log('📸 Foto capturada')
        
        // Detener cámara después de capturar
        stopCamera()
      }
    }
    
    // ✅ FUNCIÓN: Aceptar foto capturada
    const acceptPhoto = () => {
      if (capturedPhoto.value) {
        // Convertir base64 a archivo
        const photoFile = base64ToFile(capturedPhoto.value, `photo_${Date.now()}.jpg`)
        employeeForm.value.photo = photoFile
        console.log('✅ Foto aceptada y convertida a archivo:', photoFile.name, photoFile.size)
      }
      closePhotoCapture()
    }
    
    // ✅ FUNCIÓN: Retomar foto
    const retakePhoto = () => {
      capturedPhoto.value = null
      console.log('🔄 Retomando foto')
    }
    
    // ✅ FUNCIÓN: Cerrar captura de foto
    const closePhotoCapture = () => {
      showPhotoCapture.value = false
      capturedPhoto.value = null
      stopCamera()
      console.log('🚪 Captura de foto cerrada')
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
        // Limpiar intervalos si existen
        if (window.employeeRefreshInterval) {
          clearInterval(window.employeeRefreshInterval)
        }
        
        // Detener cámara si está activa
        if (stream.value) {
          stopCamera()
        }
      })
    })
    
    return {
      // Referencias
      form,
      video,
      
      // Estado reactivo
      search,
      loading,
      saving,
      deleting,
      showDialog,
      showDeleteDialog,
      showFaceRegistration,
      valid,
      dialogReady,
      editingEmployee,
      showPhotoCapture,
      capturedPhoto,
      cameraActive,
      cameraLoading,
      
      // Estado para modal de foto expandida
      showPhotoModal,
      selectedEmployeePhoto,
      
      // Datos
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
       validateEcuadorianCedula,
       filterLettersOnly,
       filterEmail,
       filterNumbersOnly,
       blockInvalidCharacters,
       blockNonNumericCharacters,
       blockInvalidEmailCharacters,
       blockCedulaPaste,
      // Funciones para la foto
      onFileSelected,
      removePhoto,
      startCamera,
      stopCamera,
      capturePhoto,
      acceptPhoto,
      retakePhoto,
      closePhotoCapture,
      base64ToFile,
      getPhotoUrl,
      
      // Funciones para el modal de foto expandida
      openPhotoModal,
      closePhotoModal
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

/* Estilos para la foto del empleado */
.employee-photo-container {
  text-align: center;
  padding: 20px 0;
}

.employee-photo {
  border: 3px solid #3b82f6;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.employee-photo-placeholder {
  border: 3px solid #60a5fa;
  box-shadow: 0 4px 12px rgba(96, 165, 250, 0.3);
}

.employee-photo-preview {
  border: 3px solid #10b981;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

/* Estilos para la captura de foto */
.camera-preview {
  margin-bottom: 20px;
}

.camera-video {
  border: 2px solid #3b82f6;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
}

.camera-controls {
  margin-top: 20px;
}

.capture-controls {
  margin-top: 20px;
}

.captured-photo-preview {
  margin-bottom: 20px;
}

/* Estilos para las tarjetas de empleados */
.employee-card {
  transition: all 0.3s ease;
  cursor: pointer;
}

.employee-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(59, 130, 246, 0.3);
}

.cards-container {
  margin-top: 20px;
}

/* Estilos para fotos clickeables */
.clickable-photo {
  cursor: pointer;
  transition: all 0.3s ease;
}

.clickable-photo:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
}

/* Estilos para el modal de foto expandida */
.expanded-photo {
  border: 3px solid #3b82f6;
  box-shadow: 0 12px 40px rgba(59, 130, 246, 0.3);
}
</style>
