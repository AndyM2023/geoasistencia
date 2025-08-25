<template>
  <v-dialog
    :model-value="showDialog"
    @update:model-value="$emit('update:showDialog', $event)"
    max-width="600px"
    persistent
  >
    <v-card class="bg-dark-surface border border-blue-500/20">
      <v-card-title class="text-white d-flex align-center">
        <v-icon color="blue-400" class="mr-2">
          {{ editingEmployee ? 'mdi-pencil' : 'mdi-plus' }}
        </v-icon>
        {{ editingEmployee ? 'Editar Empleado' : 'Crear Nuevo Empleado' }}
        <v-spacer></v-spacer>
        <v-btn 
          icon="mdi-close" 
          size="small" 
          color="grey-400" 
          variant="text"
          @click="$emit('close')"
        ></v-btn>
      </v-card-title>
      
      <v-card-text class="pa-6">
        <v-form ref="form" v-model="valid">
          <v-row>
            
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="employeeForm.first_name"
                label="Nombre"
                :rules="[rules.required, rules.firstName]"
                variant="outlined"
                color="blue-400"
                bg-color="dark-surface"
                @input="filterLettersOnly"
                @keypress="blockInvalidCharacters"
                required
              ></v-text-field>
            </v-col>
            
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="employeeForm.last_name"
                label="Apellido"
                :rules="[rules.required, rules.lastName]"
                variant="outlined"
                color="blue-400"
                bg-color="dark-surface"
                @input="filterLettersOnly"
                @keypress="blockInvalidCharacters"
                required
              ></v-text-field>
            </v-col>
            
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="employeeForm.email"
                label="Email"
                :rules="[rules.required, rules.email]"
                variant="outlined"
                color="blue-400"
                bg-color="dark-surface"
                @input="filterEmail"
                @keypress="blockInvalidEmailCharacters"
                required
              ></v-text-field>
            </v-col>
            
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="employeeForm.cedula"
                label="Cédula de Identidad"
                :rules="[rules.required, rules.cedula]"
                variant="outlined"
                color="blue-400"
                bg-color="dark-surface"
                maxlength="10"
                @input="filterNumbersOnly"
                @keypress="blockNonNumericCharacters"
                @paste="blockCedulaPaste"
                required
              ></v-text-field>
            </v-col>
            
            <v-col cols="12" sm="6">
              <v-select
                v-model="employeeForm.position"
                label="Posición"
                :items="positions"
                :rules="[rules.required]"
                variant="outlined"
                color="blue-400"
                bg-color="dark-surface"
                required
              ></v-select>
            </v-col>
            
            <v-col cols="12" sm="6">
              <v-select
                v-model="employeeForm.area"
                label="Área"
                :items="areas"
                item-title="name"
                item-value="id"
                :rules="[rules.required]"
                variant="outlined"
                color="blue-400"
                bg-color="dark-surface"
                required
              ></v-select>
            </v-col>
            
            <!-- Gestión de Fotos -->
            <v-col cols="12">
              <h3 class="text-white mb-4"> Foto del Empleado</h3>
            </v-col>
            
            <v-col cols="12">
              <v-card class="bg-dark-surface border border-blue-500/20">
                <v-card-title class="text-sm text-blue-400"> Gestión de Fotos</v-card-title>
                <v-card-text>
                  <!-- Vista previa de la foto - Solo visible cuando hay foto -->
                  <div v-if="getPhotoUrl(employeeForm.photo) || getPhotoUrl(editingEmployee?.photo)" class="text-center mb-4">
                    <v-avatar size="120" class="mb-3">
                      <v-img 
                        :src="getPhotoUrl(employeeForm.photo) || getPhotoUrl(editingEmployee?.photo) || '/default-avatar.png'" 
                        cover
                        @click="openPhotoModal(getPhotoUrl(employeeForm.photo) || getPhotoUrl(editingEmployee?.photo))"
                        style="cursor: pointer;"
                      ></v-img>
                    </v-avatar>
                    
                    <p class="text-grey-400 text-sm">
                      {{ editingEmployee?.photo ? 'Foto actual del empleado' : 'Foto seleccionada' }}
                    </p>
                  </div>
                  
                  <!-- Mensaje cuando no hay foto -->
                  <div v-else class="text-center mb-4">
                    <p class="text-grey-400 text-sm">
                      Sin foto asignada
                    </p>
                  </div>
                  
                  <!-- Botones de acción -->
                  <div class="d-flex flex-wrap gap-2 justify-center">
                    <v-btn
                      @click="showPhotoCapture = true"
                      color="blue-400"
                      size="large"
                      prepend-icon="mdi-camera"
                    >
                       Tomar Foto
                    </v-btn>
                    
                    <v-btn
                      @click="$refs.fileInput.click()"
                      color="green-400"
                      size="large"
                      prepend-icon="mdi-upload"
                    >
                      Subir Archivo
                    </v-btn>
                    
                    <!-- Eliminar foto -->
                    <v-btn
                      v-if="editingEmployee && shouldShowDeletePhotoButton(employeeForm, editingEmployee)"
                      @click="removePhoto(employeeForm, editingEmployee)"
                      color="red-400"
                      variant="outlined"
                      prepend-icon="mdi-delete"
                      size="large"
                      :disabled="employeeForm.photo === 'DELETE_PHOTO'"
                    >
                      {{ employeeForm.photo === 'DELETE_PHOTO' ? '🔄Deshacer eliminación' : ' Eliminar' }}
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
                       Formatos soportados: JPG, PNG, GIF
                    </p>
                    <p class="text-grey-400 text-xs">
                       Tamaño máximo: 5MB |  Resolución recomendada: 400x400px
                    </p>
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
            
            <!-- Sección de Registro Facial - Solo visible después de crear el empleado -->
            <v-row v-if="editingEmployee && editingEmployee.id">
              <v-col cols="12">
                <v-divider class="mb-4"></v-divider>
                <h3 class="text-white mb-4">Registro Facial</h3>
              </v-col>
            </v-row>
            
            <v-row v-if="editingEmployee && editingEmployee.id">
              <v-col cols="12">
                <v-card class="bg-dark-surface border border-blue-500/20">
                  <v-card-title class="text-sm text-blue-400"> Registro Facial</v-card-title>
                  <v-card-text>
                    <!-- Componente de captura de rostros -->
                    <div class="text-center">
                      <!-- Botón para empleados SIN rostro registrado -->
                      <v-btn
                        v-if="!editingEmployee.face_registration_status"
                        @click="$emit('face-registration', editingEmployee)"
                        color="blue-400"
                        size="large"
                        prepend-icon="mdi-camera"
                        block
                      >
                        Iniciar Registro Facial
                      </v-btn>
                      
                      <!-- Botón para empleados CON rostro registrado -->
                      <v-btn 
                        v-else
                        @click="$emit('face-registration', editingEmployee)"
                        color="blue-400"
                        variant="outlined"
                        size="large"
                        prepend-icon="mdi-camera-plus"
                        block
                      >
                        Actualizar Rostro
                      </v-btn>
                      
                      <p class="text-blue-400 text-xs mt-2">
                        {{ editingEmployee.face_registration_status ? 'Actualizar rostro existente' : 'Se capturarán 15 fotos para máxima velocidad' }}
                      </p>
                    </div>
                    
                    <!-- Estado del registro facial -->
                    <div v-if="editingEmployee.face_registration_status" class="mt-4 text-center">
                      <v-divider class="mb-4"></v-divider>
                      <v-icon color="green-500" size="48" class="mb-2">mdi-check-circle</v-icon>
                      <h4 class="text-green-400 mb-2">Rostro Registrado</h4>
                      <p class="text-grey-300 text-sm">Este empleado ya tiene rostro registrado en el sistema</p>
                    </div>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
            
            <!-- Mensaje informativo para nuevos empleados -->
            <v-row v-if="!editingEmployee">
              <v-col cols="12">
                <v-divider class="mb-4"></v-divider>
                <v-alert
                  type="info"
                  variant="tonal"
                  density="compact"
                  class="text-center"
                >
                  💡 <strong>Registro Facial:</strong> Una vez creado el empleado, podrás registrar su rostro desde la lista de empleados
                </v-alert>
              </v-col>
            </v-row>
          </v-row>
        </v-form>
      </v-card-text>
      
      <v-card-actions class="justify-end pa-4">
        <v-btn 
          color="grey-600" 
          variant="outlined" 
          @click="$emit('close')"
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

            <!-- Controles para foto capturada -->
            <div v-if="capturedPhoto" class="captured-photo-controls">
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
        
        <v-card-actions class="justify-center pa-4">
          <v-btn
            color="grey-600"
            variant="outlined"
            @click="closePhotoCapture"
          >
            Cerrar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- Modal de foto expandida -->
    <EmployeePhotoModal
      v-model:show-modal="showPhotoModal"
      :photo-url="selectedEmployeePhoto"
    />
  </v-dialog>
</template>

<script>
import { ref, reactive, computed, watch, onMounted, onUnmounted } from 'vue'
import EmployeePhotoModal from './EmployeePhotoModal.vue'

export default {
  name: 'EmployeeForm',
  components: {
    EmployeePhotoModal
  },
  props: {
    showDialog: {
      type: Boolean,
      default: false
    },
    editingEmployee: {
      type: Object,
      default: null
    },
    areas: {
      type: Array,
      default: () => []
    },
    employees: {
      type: Array,
      default: () => []
    },
    saving: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close', 'save', 'update:showDialog', 'face-registration'],
  setup(props, { emit }) {
    // Referencias del formulario
    const form = ref(null)
    const valid = ref(false)
    const fileInput = ref(null)
    const video = ref(null)
    
    // Estado del formulario
    const employeeForm = reactive({
      first_name: '',
      last_name: '',
      email: '',
      cedula: '',
      position: 'desarrollador',
      area: null,
      photo: null
    })
    
    // Estado de la cámara
    const showPhotoCapture = ref(false)
    const cameraActive = ref(false)
    const cameraLoading = ref(false)
    const capturedPhoto = ref(null)
    const stream = ref(null)
    
    // Estado del modal de foto
    const showPhotoModal = ref(false)
    const selectedEmployeePhoto = ref(null)
    
    // Posiciones disponibles
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
    
    // Reglas de validación simplificadas
    const rules = {
      required: (value) => {
        if (!value || value === '') return 'Este campo es requerido'
        return true
      },
      firstName: (value) => {
        if (!value || value.length < 2) return 'El nombre debe tener al menos 2 caracteres'
        if (value.length > 50) return 'El nombre no puede exceder 50 caracteres'
        if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(value)) {
          return 'El nombre solo puede contener letras y espacios'
        }
        return true
      },
      lastName: (value) => {
        if (!value || value.length < 2) return 'El apellido debe tener al menos 2 caracteres'
        if (value.length > 50) return 'El apellido no puede exceder 50 caracteres'
        if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(value)) {
          return 'El apellido solo puede contener letras y espacios'
        }
        return true
      },
      email: (value) => {
        if (!value) return 'El email es requerido'
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
        if (!emailRegex.test(value)) return 'Formato de email inválido'
        return true
      },
      cedula: (value) => {
        if (!value) return 'La cédula es requerida'
        if (value.length !== 10) return 'La cédula debe tener 10 dígitos'
        if (!/^\d+$/.test(value)) return 'La cédula solo puede contener números'
        
        // Verificar duplicados
        const existingCedulas = props.employees
          .filter(emp => emp.id !== props.editingEmployee?.id)
          .map(emp => emp.cedula_display || emp.cedula || emp.user?.cedula)
          .filter(Boolean)
        
        if (existingCedulas.includes(value)) {
          return 'Esta cédula ya está registrada'
        }
        
        return true
      }
    }
    
    // Filtros de input
    const filterLettersOnly = (event) => {
      event.target.value = event.target.value.replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]/g, '')
    }
    
    const filterEmail = (event) => {
      event.target.value = event.target.value.replace(/[^a-zA-Z0-9@._-]/g, '')
    }
    
    const filterNumbersOnly = (event) => {
      event.target.value = event.target.value.replace(/[^0-9]/g, '')
    }
    
    const blockInvalidCharacters = (event) => {
      const char = String.fromCharCode(event.keyCode || event.charCode)
      if (!/[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]/.test(char)) {
        event.preventDefault()
      }
    }
    
    const blockNonNumericCharacters = (event) => {
      const char = String.fromCharCode(event.keyCode || event.charCode)
      if (!/[0-9]/.test(char)) {
        event.preventDefault()
      }
    }
    
    const blockInvalidEmailCharacters = (event) => {
      const char = String.fromCharCode(event.keyCode || event.charCode)
      if (!/[a-zA-Z0-9@._-]/.test(char)) {
        event.preventDefault()
      }
    }
    
    const blockCedulaPaste = (event) => {
      event.preventDefault()
      const pastedText = (event.clipboardData || window.clipboardData).getData('text')
      const cleanText = pastedText.replace(/[^0-9]/g, '')
      event.target.value = cleanText
    }
    
    // Funciones de cámara
    const startCamera = async () => {
      try {
        cameraLoading.value = true
        stream.value = await navigator.mediaDevices.getUserMedia({ video: true })
        if (video.value) {
          video.value.srcObject = stream.value
          cameraActive.value = true
        }
      } catch (error) {
        console.error('Error al acceder a la cámara:', error)
      } finally {
        cameraLoading.value = false
      }
    }
    
    const stopCamera = () => {
      if (stream.value) {
        stream.value.getTracks().forEach(track => track.stop())
        stream.value = null
      }
      cameraActive.value = false
      if (video.value) {
        video.value.srcObject = null
      }
    }
    
    const capturePhoto = () => {
      if (video.value && stream.value) {
        const canvas = document.createElement('canvas')
        const context = canvas.getContext('2d')
        canvas.width = video.value.videoWidth
        canvas.height = video.value.videoHeight
        context.drawImage(video.value, 0, 0)
        
        canvas.toBlob((blob) => {
          capturedPhoto.value = URL.createObjectURL(blob)
          stopCamera()
        }, 'image/jpeg', 0.8)
      }
    }
    
    const acceptPhoto = () => {
      if (capturedPhoto.value) {
        // Convertir URL a Blob
        fetch(capturedPhoto.value)
          .then(res => res.blob())
          .then(blob => {
            employeeForm.photo = blob
            capturedPhoto.value = null
            showPhotoCapture.value = false
          })
      }
    }
    
    const retakePhoto = () => {
      capturedPhoto.value = null
      startCamera()
    }
    
    const closePhotoCapture = () => {
      showPhotoCapture.value = false
      capturedPhoto.value = null
      stopCamera()
    }
    
    // Funciones de foto
    const onFileSelected = (event) => {
      const file = event.target.files[0]
      if (file && file.type.startsWith('image/')) {
        employeeForm.photo = file
      }
      event.target.value = ''
    }
    
    const removePhoto = () => {
      if (employeeForm.photo) {
        employeeForm.photo = null
      } else if (editingEmployee?.photo) {
        employeeForm.photo = 'DELETE_PHOTO'
      }
    }
    
    const shouldShowDeletePhotoButton = (form, employee) => {
      return (form.photo && form.photo !== 'DELETE_PHOTO') || employee.photo
    }
    
    const getPhotoUrl = (photo) => {
      if (photo instanceof Blob) {
        return URL.createObjectURL(photo)
      }
      return photo
    }
    
    const openPhotoModal = (photoUrl) => {
      if (photoUrl) {
        selectedEmployeePhoto.value = photoUrl
        showPhotoModal.value = true
      }
    }
    
    // Función de guardado
    const saveEmployee = async () => {
      if (form.value?.validate()) {
        try {
          // Emitir el evento de guardado
          await emit('save', { ...employeeForm })
        } catch (error) {
          console.error('Error al guardar empleado:', error)
        }
      }
    }
    
    // Llenar formulario cuando se edita un empleado
    const fillForm = (employee) => {
      if (employee) {
        employeeForm.first_name = employee.user?.first_name || ''
        employeeForm.last_name = employee.user?.last_name || ''
        employeeForm.email = employee.user?.email || ''
        employeeForm.cedula = employee.cedula_display || employee.cedula || employee.user?.cedula || ''
        employeeForm.position = employee.position || 'desarrollador'
        employeeForm.area = employee.area?.id || employee.area || null
        employeeForm.photo = null
      }
    }
    
    // Resetear formulario
    const resetForm = () => {
      employeeForm.first_name = ''
      employeeForm.last_name = ''
      employeeForm.email = ''
      employeeForm.cedula = ''
      employeeForm.position = 'desarrollador'
      employeeForm.area = null
      employeeForm.photo = null
    }
    
    // Watcher para editingEmployee
    watch(() => props.editingEmployee, (newEmployee) => {
      if (newEmployee) {
        fillForm(newEmployee)
        // Verificar estado facial
        if (newEmployee.id) {
          // Aquí podrías hacer una llamada al API para verificar el estado
          // faceRegistration.status = newEmployee.face_registration_status ? 'trained' : 'idle'
        }
      } else {
        resetForm()
      }
    }, { immediate: true })
    
    // Watcher para areas para debuggear
    watch(() => props.areas, (newAreas) => {
      console.log('🔍 EmployeeForm - areas prop cambiada:', newAreas)
      console.log('🔍 EmployeeForm - areas length:', newAreas?.length)
      console.log('🔍 EmployeeForm - areas tipo:', typeof newAreas)
      console.log('🔍 EmployeeForm - areas es array:', Array.isArray(newAreas))
    }, { immediate: true })
    
    // Cleanup al desmontar
    onUnmounted(() => {
      stopCamera()
    })
    
    return {
      // Referencias
      form,
      valid,
      fileInput,
      video,
      
      // Estado
      employeeForm,
      showPhotoCapture,
      cameraActive,
      cameraLoading,
      capturedPhoto,
      // faceRegistration, // Eliminado
      showPhotoModal,
      selectedEmployeePhoto,
      
      // Datos
      positions,
      
      // Reglas
      rules,
      
      // Funciones
      filterLettersOnly,
      filterEmail,
      filterNumbersOnly,
      blockInvalidCharacters,
      blockNonNumericCharacters,
      blockInvalidEmailCharacters,
      blockCedulaPaste,
      startCamera,
      stopCamera,
      capturePhoto,
      acceptPhoto,
      retakePhoto,
      closePhotoCapture,
      onFileSelected,
      removePhoto,
      shouldShowDeletePhotoButton,
      getPhotoUrl,
      openPhotoModal,
      saveEmployee
    }
  }
}
</script>

<style scoped>
.camera-video {
  border-radius: 8px;
  background: #000;
}

.captured-photo-preview {
  text-align: center;
}

.camera-controls, .captured-photo-controls {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-top: 1rem;
}
</style>



