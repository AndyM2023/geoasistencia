<template>
  <AppBar />
  <v-container fluid class="register-container pa-0">
    <v-row no-gutters class="h-100">
      <!-- Panel izquierdo con gradiente azul oscuro -->
      <v-col cols="12" md="4" class="left-panel d-flex align-center justify-center">
        <div class="text-center">
          <h1 class="logo-text text-h3 font-weight-bold text-white">
            GEOASISTENCIA
            <br>
            ADMIN
          </h1>
          <div class="logo-glow"></div>
        </div>
      </v-col>

      <!-- Panel derecho con formulario -->
      <v-col cols="12" md="8" class="right-panel d-flex align-center justify-center">
        <v-card class="register-card" elevation="0">
          <v-card-text class="pa-4">
            <h2 class="text-h5 font-weight-bold text-white mb-1">Registrar Administrador</h2>
            <p class="text-body-2 text-grey-lighten-1 mb-2">
              ¿Ya tienes cuenta? 
              <v-btn 
                variant="text" 
                color="primary" 
                class="text-none px-1"
                @click="goToLogin"
              >
                Iniciar Sesión
              </v-btn>
            </p>
            
            <v-form @submit.prevent="handleRegister" class="register-form" ref="formRef" v-show="!success">
              <!-- Nombre y Apellidos -->
              <v-row>
                <v-col cols="12" sm="6">
                  <v-text-field
                    v-model="formData.first_name"
                    label="NOMBRE"
                    type="text"
                    placeholder="Ingresa tu nombre"
                    variant="outlined"
                    :color="getFieldColor('first_name')"
                    bg-color="dark-surface"
                    class="mb-1"
                    :rules="[rules.required, rules.first_name]"
                    hide-details="auto"
                    @input="(value) => filterLettersOnly(value, 'first_name')"
                    :error-messages="getFieldError('first_name')"
                    @keydown="blockInvalidCharacters($event, 'first_name')"
                  >
                    <template v-slot:prepend-inner>
                      <v-icon color="primary">mdi-account</v-icon>
                    </template>
                  </v-text-field>
                </v-col>
                
                <v-col cols="12" sm="6">
                  <v-text-field
                    v-model="formData.last_name"
                    label="APELLIDOS"
                    type="text"
                    placeholder="Ingresa tus apellidos"
                    variant="outlined"
                    :color="getFieldColor('last_name')"
                    bg-color="dark-surface"
                    class="mb-1"
                    :rules="[rules.required, rules.last_name]"
                    hide-details="auto"
                    @input="(value) => filterLettersOnly(value, 'last_name')"
                    :error-messages="getFieldError('last_name')"
                    @keydown="blockInvalidCharacters($event, 'last_name')"
                  >
                    <template v-slot:prepend-inner>
                      <v-icon color="primary">mdi-account-outline</v-icon>
                    </template>
                  </v-text-field>
                </v-col>
              </v-row>

              <!-- Email y Cédula -->
              <v-row>
                <v-col cols="12" sm="6">
                  <v-text-field
                    v-model="formData.email"
                    label="CORREO ELECTRÓNICO"
                    type="email"
                    placeholder="ejemplo@correo.com"
                    variant="outlined"
                    :color="getFieldColor('email')"
                    bg-color="dark-surface"
                    class="mb-1"
                    :rules="[rules.required, rules.email]"
                    hide-details="auto"
                    @input="filterEmail"
                    @keydown="blockInvalidEmailCharacters"
                    :error-messages="getFieldError('email')"
                  >
                    <template v-slot:prepend-inner>
                      <v-icon color="primary">mdi-email</v-icon>
                    </template>
                  </v-text-field>
                </v-col>
                
                <v-col cols="12" sm="6">
                  <v-text-field
                    v-model="formData.cedula"
                    label="CÉDULA"
                    type="text"
                    placeholder="Número de cédula"
                    variant="outlined"
                    :color="getFieldColor('cedula')"
                    bg-color="dark-surface"
                    class="mb-1"
                    :rules="[rules.required, rules.cedula]"
                    hide-details="auto"
                    @input="filterNumbersOnly"
                    @keydown="blockNonNumericCharacters"
                    @paste="blockCedulaPaste"
                    :error-messages="getFieldError('cedula')"
                  >
                    <template v-slot:prepend-inner>
                      <v-icon color="primary">mdi-card-account-details</v-icon>
                    </template>
                  </v-text-field>
                </v-col>
              </v-row>

              <!-- Usuario y Cargo -->
              <v-row>
                <v-col cols="12" sm="6">
                  <v-text-field
                    v-model="formData.username"
                    label="USUARIO"
                    type="text"
                    placeholder="Nombre de usuario"
                    variant="outlined"
                    :color="getFieldColor('username')"
                    bg-color="dark-surface"
                    class="mb-1"
                    :rules="[rules.required, rules.username]"
                    hide-details="auto"
                    @input="(value) => filterAlphanumeric(value, 'username')"
                    :error-messages="getFieldError('username')"
                    @keydown="blockInvalidUsernameCharacters"
                  >
                    <template v-slot:prepend-inner>
                      <v-icon color="primary">mdi-at</v-icon>
                    </template>
                  </v-text-field>
                </v-col>
                
                <v-col cols="12" sm="6">
                  <v-select
                    v-model="formData.position"
                    label="ELEGIR CARGO"
                    :items="positionOptions"
                    item-title="text"
                    item-value="value"
                    variant="outlined"
                    :color="getFieldColor('position')"
                    bg-color="dark-surface"
                    class="mb-1"
                    :rules="[rules.required]"
                    hide-details="auto"
                    placeholder="Selecciona un cargo"
                    @update:model-value="validateField('position')"
                    :error-messages="getFieldError('position')"
                  >
                    <template v-slot:prepend-inner>
                      <v-icon color="primary">mdi-briefcase</v-icon>
                    </template>
                  </v-select>
                </v-col>
              </v-row>

              <!-- Contraseña y Confirmar Contraseña -->
              <v-row>
                <v-col cols="12" sm="6">
                  <v-text-field
                    v-model="formData.password"
                    label="CONTRASEÑA"
                    :type="showPassword ? 'text' : 'password'"
                    placeholder="Contraseña segura"
                    variant="outlined"
                    :color="getFieldColor('password')"
                    bg-color="dark-surface"
                    class="mb-1"
                    :rules="[rules.required, rules.password]"
                    hide-details="auto"
                    @input="validateField('password')"
                    :error-messages="getFieldError('password')"
                  >
                    <template v-slot:prepend-inner>
                      <v-icon color="primary">mdi-lock</v-icon>
                    </template>
                    <template v-slot:append-inner>
                      <v-btn
                        variant="text"
                        icon
                        @click="togglePassword"
                        color="grey-lighten-1"
                      >
                        <v-icon>{{ showPassword ? 'mdi-eye-off' : 'mdi-eye' }}</v-icon>
                      </v-btn>
                    </template>
                  </v-text-field>
                </v-col>
                
                <v-col cols="12" sm="6">
                  <v-text-field
                    v-model="formData.confirmPassword"
                    label="CONFIRMAR CONTRASEÑA"
                    :type="showConfirmPassword ? 'text' : 'password'"
                    placeholder="Repetir contraseña"
                    variant="outlined"
                    :color="getFieldColor('confirmPassword')"
                    bg-color="dark-surface"
                    class="mb-1"
                    :rules="[rules.required, rules.confirmPassword]"
                    hide-details="auto"
                    @input="validateField('confirmPassword')"
                    :error-messages="getFieldError('confirmPassword')"
                  >
                    <template v-slot:prepend-inner>
                      <v-icon color="primary">mdi-lock-check</v-icon>
                    </template>
                    <template v-slot:append-inner>
                      <v-btn
                        variant="text"
                        icon
                        @click="toggleConfirmPassword"
                        color="grey-lighten-1"
                      >
                        <v-icon>{{ showConfirmPassword ? 'mdi-eye-off' : 'mdi-eye' }}</v-icon>
                      </v-btn>
                    </template>
                  </v-text-field>
                </v-col>
              </v-row>

              

              <v-row justify="center">
                <v-col cols="12" sm="10">
                  <v-btn
                    type="submit"
                    color="primary"
                    size="large"
                    block
                    :loading="loading"
                    :disabled="loading"
                    class="mb-2"
                    elevation="2"
                  >
                                    <span v-if="loading">Registrando...</span>
                    <span v-else>Registrar Administrador</span>
                  </v-btn>
                </v-col>
              </v-row>
            </v-form>

            <!-- Mensaje de éxito grande cuando se oculta el formulario -->
            <div v-if="success" class="text-center py-8">
              <v-icon size="80" color="success" class="mb-4">mdi-check-circle</v-icon>
              <h3 class="text-h4 font-weight-bold text-white mb-4">
                {{ success.includes('inicio de sesión') ? '¡Registro e Inicio de Sesión Exitosos!' : '¡Registro Exitoso!' }}
              </h3>
              <p class="text-h6 text-grey-lighten-1 mb-4">{{ success }}</p>
              <v-progress-circular
                indeterminate
                color="primary"
                size="30"
                class="mb-2"
              ></v-progress-circular>
              <p class="text-body-2 text-grey-lighten-2">
                {{ success.includes('dashboard') ? 'Accediendo al dashboard...' : 'Redirigiendo...' }}
              </p>
            </div>

            <!-- Mensajes de error cuando el formulario está visible -->
            <v-alert
              v-if="error && !success"
              type="error"
              variant="tonal"
              class="mb-4"
              closable
              @click:close="error = ''"
            >
              {{ error }}
            </v-alert>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import AppBar from '../components/AppBar.vue'
import { authService } from '../services/authService'
import { useAuthStore } from '../stores/auth'

export default {
  name: 'Register',
  components: {
    AppBar
  },
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const formRef = ref(null)
    
    const formData = reactive({
      first_name: '',
      last_name: '',
      email: '',
      cedula: '',
      username: '',
      position: '',
      password: '',
      confirmPassword: ''
    })
    
    const showPassword = ref(false)
    const showConfirmPassword = ref(false)
    const loading = ref(false)
    const error = ref('')
    const success = ref('')

    // Opciones para el campo cargo
    const positionOptions = [
      { text: 'Administrador de Personal', value: 'Administrador de Personal' },
      { text: 'Asistente de RR. HH.', value: 'Asistente de RR. HH.' },
      { text: 'Técnico de RR. HH.', value: 'Técnico de RR. HH.' }
    ]

    const rules = {
      required: v => !!v || 'Este campo es requerido',
      
      // Nombre: máximo 20 caracteres, solo letras
      first_name: v => {
        if (!v) return 'Este campo es requerido'
        if (v.length > 20) return 'El nombre no puede exceder 20 caracteres'
        if (!/^[A-Za-zÁáÉéÍíÓóÚúÑñ\s]+$/.test(v)) return 'El nombre solo puede contener letras'
        return true
      },
      
      // Apellidos: máximo 30 caracteres, solo letras y espacios
      last_name: v => {
        if (!v) return 'Este campo es requerido'
        if (v.length > 30) return 'Los apellidos no pueden exceder 30 caracteres'
        if (!/^[A-Za-zÁáÉéÍíÓóÚúÑñ\s]+$/.test(v)) return 'Los apellidos solo pueden contener letras y espacios'
        return true
      },
      
      // Email: formato válido
      email: v => {
        if (!v) return 'Este campo es requerido'
        const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
        return pattern.test(v) || 'Debe ser un email válido'
      },
      
      // Cédula: exactamente 10 dígitos, validación ecuatoriana
      cedula: v => {
        if (!v) return 'Este campo es requerido'
        if (!/^\d{10}$/.test(v)) return 'La cédula debe tener exactamente 10 dígitos'
        
        // Validación ecuatoriana (algoritmo de verificación)
        if (!validateEcuadorianCedula(v)) return 'Cédula ecuatoriana inválida'
        return true
      },
      
      // Usuario: alfanumérico, 3-20 caracteres
      username: v => {
        if (!v) return 'Este campo es requerido'
        if (v.length < 3) return 'El usuario debe tener al menos 3 caracteres'
        if (v.length > 20) return 'El usuario no puede exceder 20 caracteres'
        if (!/^[a-zA-Z0-9]+$/.test(v)) return 'El usuario solo puede contener letras y números'
        return true
      },
      
      // Contraseña: mínimo 8 caracteres, mayúsculas, minúsculas, números
      password: v => {
        if (!v) return 'Este campo es requerido'
        if (v.length < 8) return 'La contraseña debe tener al menos 8 caracteres'
        if (!/(?=.*[a-z])/.test(v)) return 'La contraseña debe contener al menos una minúscula'
        if (!/(?=.*[A-Z])/.test(v)) return 'La contraseña debe contener al menos una mayúscula'
        if (!/(?=.*\d)/.test(v)) return 'La contraseña debe contener al menos un número'
        if (!/(?=.*[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?])/.test(v)) return 'La contraseña debe contener al menos un carácter especial'
        return true
      },
      
      // Confirmar contraseña: debe coincidir
      confirmPassword: v => {
        if (!v) return 'Este campo es requerido'
        if (v !== formData.password) return 'Las contraseñas no coinciden'
        return true
      }
    }

    // Función para validar cédula ecuatoriana
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

    // Estado de validación en tiempo real
    const fieldValidation = reactive({
      first_name: { valid: true, message: '' },
      last_name: { valid: true, message: '' },
      email: { valid: true, message: '' },
      cedula: { valid: true, message: '' },
      username: { valid: true, message: '' },
      position: { valid: true, message: '' },
      password: { valid: true, message: '' },
      confirmPassword: { valid: true, message: '' }
    })

    // Función para validar campo en tiempo real
    const validateField = (fieldName) => {
      if (!formData[fieldName]) {
        fieldValidation[fieldName] = { valid: true, message: '' }
        return
      }

      let isValid = true
      let message = ''

      // Aplicar regla específica del campo
      if (rules[fieldName]) {
        const result = rules[fieldName](formData[fieldName])
        if (result !== true) {
          isValid = false
          message = result
        }
      }

      fieldValidation[fieldName] = { valid: isValid, message: message }
    }

    // Función para obtener el color del campo según validación
    const getFieldColor = (fieldName) => {
      if (!formData[fieldName]) return 'primary'
      return fieldValidation[fieldName].valid ? 'success' : 'error'
    }

    // Función para obtener el mensaje de error del campo
    const getFieldError = (fieldName) => {
      if (!formData[fieldName]) return ''
      return fieldValidation[fieldName].message
    }

    // Función para filtrar solo letras y espacios (para nombre y apellidos)
    const filterLettersOnly = (value, fieldName) => {
      // Remover números y caracteres especiales, mantener solo letras, espacios y acentos
      const filtered = value.replace(/[^A-Za-zÁáÉéÍíÓóÚúÑñ\s]/g, '')
      
      // Actualizar el valor del campo con solo caracteres permitidos
      formData[fieldName] = filtered
      
      // Validar el campo después del filtrado
      validateField(fieldName)
      
      return filtered
    }

    // Función para filtrar solo letras y números (para username)
    const filterAlphanumeric = (value, fieldName) => {
      // Remover caracteres especiales, mantener solo letras y números
      const filtered = value.replace(/[^A-Za-z0-9]/g, '')
      
      // Actualizar el valor del campo con solo caracteres permitidos
      formData[fieldName] = filtered
      
      // Validar el campo después del filtrado
      validateField(fieldName)
      
      return filtered
    }

    // Función para filtrar email (permitir solo caracteres válidos para email)
    const filterEmail = (value) => {
      // Permitir letras, números, puntos, guiones bajos, guiones medios, arrobas y puntos
      const filtered = value.replace(/[^a-zA-Z0-9._%+-@]/g, '')
      
      // Actualizar el valor del campo
      formData.email = filtered
      
      // Validar el campo después del filtrado
      validateField('email')
      
      return filtered
    }

    // Función para filtrar solo números (para cédula)
    const filterNumbersOnly = (value) => {
      // Remover todo excepto números
      const filtered = value.replace(/\D/g, '')
      
      // BLOQUEO TOTAL: Si ya tiene 10 dígitos, no permitir más entrada
      if (filtered.length > 10) {
        // Mantener solo los primeros 10 dígitos
        formData.cedula = filtered.slice(0, 10)
        return filtered.slice(0, 10)
      }
      
      // Limitar a 10 dígitos máximo
      formData.cedula = filtered.slice(0, 10)
      
      // Validar el campo después del filtrado
      validateField('cedula')
      
      return filtered.slice(0, 10)
    }

    // Función para bloquear caracteres no permitidos en nombre y apellidos
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

    // Función para bloquear caracteres no permitidos en username
    const blockInvalidUsernameCharacters = (event) => {
      const key = event.key
      const allowedKeys = [
        'Backspace', 'Delete', 'Tab', 'Enter', 'Escape', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown',
        'Home', 'End', 'PageUp', 'PageDown', 'Insert', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12'
      ]
      
      // Permitir teclas de navegación y control
      if (allowedKeys.includes(key)) {
        return true
      }
      
      // Permitir solo letras y números
      const allowedPattern = /^[A-Za-z0-9]$/
      
      if (!allowedPattern.test(key)) {
        // Prevenir la entrada del carácter
        event.preventDefault()
        return false
      }
      
      return true
    }

    // Función para bloquear solo números en cédula
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
      if (formData.cedula.length >= 10 && key !== 'Backspace' && key !== 'Delete') {
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

    // Función para bloquear caracteres no válidos en email
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

    // Función para bloquear pegado de texto que exceda 10 dígitos en cédula
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
      const currentLength = formData.cedula.length
      if (currentLength + pastedText.length > 10) {
        event.preventDefault()
        return false
      }
      
      return true
    }

    const togglePassword = () => {
      showPassword.value = !showPassword.value
    }

    const toggleConfirmPassword = () => {
      showConfirmPassword.value = !showConfirmPassword.value
    }

    const goToLogin = () => {
      router.push('/admin/login')
    }

    const handleRegister = async () => {
      console.log('🚀 Iniciando proceso de registro...')
      
      // Validar que formRef existe
      if (!formRef.value) {
        console.error('❌ FormRef es null')
        error.value = 'Error en el formulario. Recarga la página.'
        return
      }

      // Validar formulario
      console.log('🔍 Validando formulario...')
      const { valid } = await formRef.value.validate()
      console.log('✅ Formulario válido:', valid)
      
      if (!valid) {
        console.log('❌ Formulario no válido, deteniendo registro')
        return
      }

      loading.value = true
      error.value = ''
      success.value = ''

      try {
        // Preparar datos para enviar al backend
        const registerData = {
          first_name: formData.first_name,
          last_name: formData.last_name,
          email: formData.email,
          cedula: formData.cedula,
          username: formData.username,
          position: formData.position,
          password: formData.password,
          role: 'admin' // Por defecto administrador
        }

        console.log('📤 Datos a enviar:', { ...registerData, password: '[OCULTA]' })
        console.log('📡 Llamando a authService.register...')

        const result = await authService.register(registerData)
        
        console.log('📊 Resultado del registro:', result)
        
        if (result.success) {
          console.log('✅ Registro exitoso!')
          success.value = '¡Administrador registrado exitosamente! Iniciando sesión...'
          
          // Limpiar formulario y resetear validaciones
          Object.keys(formData).forEach(key => {
            formData[key] = ''
          })
          
          // Resetear validaciones del formulario
          if (formRef.value) {
            formRef.value.resetValidation()
          }
          
          // Hacer login automático con las credenciales recién creadas
          console.log('🔐 Iniciando login automático...')
          try {
            const loginResult = await authStore.login(registerData.username, registerData.password)
            
            if (loginResult.success) {
              console.log('✅ Login automático exitoso!')
              success.value = '¡Registro e inicio de sesión exitosos! Redirigiendo al dashboard...'
              
              setTimeout(() => {
                router.push('/app/dashboard')
              }, 1500)
            } else {
              console.log('❌ Error en login automático, redirigiendo al login manual')
              success.value = '¡Registro exitoso! Redirigiendo al login...'
              
              setTimeout(() => {
                router.push('/admin/login')
              }, 1500)
            }
          } catch (loginError) {
            console.error('💥 Error en login automático:', loginError)
            success.value = '¡Registro exitoso! Redirigiendo al login...'
            
            setTimeout(() => {
              router.push('/admin/login')
            }, 1500)
          }
        } else {
          console.log('❌ Error en resultado:', result.error)
          error.value = result.error || 'Error durante el registro'
        }
      } catch (err) {
        console.error('💥 Excepción en registro:', err)
        console.error('💥 Detalles de la respuesta:', err.response)
        error.value = err.response?.data?.detail || 'Error de conexión. Intenta de nuevo.'
      } finally {
        loading.value = false
      }
    }

    // Lifecycle hooks para controlar el scroll
    onMounted(() => {
      document.body.classList.add('register-page')
    })

    onUnmounted(() => {
      document.body.classList.remove('register-page')
    })

    return {
      formData,
      formRef,
      showPassword,
      showConfirmPassword,
      loading,
      error,
      success,
      positionOptions,
      rules,
      fieldValidation,
      togglePassword,
      toggleConfirmPassword,
      goToLogin,
      handleRegister,
      validateField,
      getFieldColor,
      getFieldError,
      filterLettersOnly,
      filterAlphanumeric,
      filterNumbersOnly,
      filterEmail,
      blockInvalidCharacters,
      blockInvalidUsernameCharacters,
      blockNonNumericCharacters,
      blockInvalidEmailCharacters,
      blockCedulaPaste
    }
  }
}
</script>

<style scoped>
.register-container {
  height: calc(100vh - 64px);
  background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 100%);
  margin: 0 !important;
  padding: 0 !important;
  border: none !important;
  outline: none !important;
  margin-top: 64px !important;
  overflow-y: auto;
}

.left-panel {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  min-height: 100%;
}

.left-panel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 30% 70%, rgba(0, 212, 255, 0.1) 0%, transparent 50%);
  pointer-events: none;
}

.logo-text {
  position: relative;
  z-index: 2;
  text-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
  letter-spacing: 2px;
  text-align: center;
  word-wrap: break-word;
  overflow-wrap: break-word;
  hyphens: auto;
  max-width: 100%;
}

.logo-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(0, 212, 255, 0.2) 0%, transparent 70%);
  border-radius: 50%;
  animation: pulse 3s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.3; transform: translate(-50%, -50%) scale(1); }
  50% { opacity: 0.6; transform: translate(-50%, -50%) scale(1.1); }
}

.right-panel {
  background: #16213e;
  position: relative;
  height: 100%;
  overflow-y: auto;
  display: flex !important;
  align-items: flex-start !important;
  justify-content: center !important;
  padding: 16px 0;
}

.right-panel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 80% 20%, rgba(139, 92, 246, 0.05) 0%, transparent 50%);
  pointer-events: none;
}

  .register-card {
    background: rgba(30, 41, 59, 0.8) !important;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(59, 130, 246, 0.2);
    border-radius: 16px;
    max-width: 600px;
    width: 100%;
    margin: 20px 0 4px 0;
  }

/* Personalización de Vuetify para modo oscuro */
:deep(.v-field) {
  background-color: rgba(30, 41, 59, 0.8) !important;
  border-color: rgba(59, 130, 246, 0.3) !important;
}

:deep(.v-field--focused) {
  border-color: #00d4ff !important;
  box-shadow: 0 0 0 2px rgba(0, 212, 255, 0.2) !important;
}

:deep(.v-field__input) {
  color: #ffffff !important;
}

:deep(.v-field__label) {
  color: #cbd5e1 !important;
}

:deep(.v-btn--variant-text) {
  color: #3b82f6 !important;
}

:deep(.v-btn--variant-text:hover) {
  background-color: rgba(59, 130, 246, 0.1) !important;
}

:deep(.v-checkbox .v-selection-control__input) {
  color: #00d4ff !important;
}

:deep(.v-checkbox .v-label) {
  color: #cbd5e1 !important;
}

/* Personalización para v-select */
:deep(.v-select .v-field) {
  background-color: rgba(30, 41, 59, 0.8) !important;
  border-color: rgba(59, 130, 246, 0.3) !important;
}

:deep(.v-select .v-field--focused) {
  border-color: #00d4ff !important;
  box-shadow: 0 0 0 2px rgba(0, 212, 255, 0.2) !important;
}

:deep(.v-select .v-field__input) {
  color: #ffffff !important;
}

:deep(.v-select .v-select__selection) {
  color: #ffffff !important;
}

:deep(.v-select .v-field__placeholder) {
  color: #cbd5e1 !important;
  font-weight: 500 !important;
}

:deep(.v-select .v-field__label) {
  color: #cbd5e1 !important;
  font-weight: 500 !important;
}

:deep(.v-select .v-field__label--floating) {
  color: #cbd5e1 !important;
  font-weight: 500 !important;
}

/* Eliminar bordes y márgenes globales */
:deep(.v-container) {
  margin: 0 !important;
  padding: 0 !important;
  border: none !important;
}

:deep(.v-row) {
  margin: 0 !important;
  border: none !important;
}

:deep(.v-col) {
  padding: 0 !important;
  border: none !important;
}

/* Reducir espaciado entre campos y eliminar bordes verticales */
.register-form :deep(.v-row) {
  margin-bottom: 0 !important;
}

.register-form :deep(.v-col) {
  padding-left: 8px !important;
  padding-right: 8px !important;
  border: none !important;
}

.register-form :deep(.v-col:first-child) {
  padding-left: 0 !important;
}

.register-form :deep(.v-col:last-child) {
  padding-right: 0 !important;
}

/* Espaciado uniforme para todos los campos */
.register-form :deep(.v-input) {
  margin-bottom: 4px !important;
}

.register-form :deep(.v-field) {
  margin-bottom: 0 !important;
}

/* Asegurar que los campos individuales (no en filas) tengan el mismo espaciado */
.register-form > .v-text-field {
  margin-bottom: 4px !important;
}

/* Responsive */
@media (max-width: 1200px) {
  .logo-text {
    font-size: 2rem !important;
    letter-spacing: 1px !important;
  }
  
  .left-panel {
    padding: 2rem !important;
  }
}

@media (max-width: 960px) {
  .register-container {
    height: auto;
    min-height: calc(100vh - 64px);
  }
  
  .left-panel {
    min-height: 120px;
    height: auto;
    padding: 1.5rem !important;
    flex-direction: column;
    text-align: center;
  }
  
  .right-panel {
    height: auto;
    min-height: calc(100vh - 184px);
    align-items: center !important;
    padding: 8px 0;
  }
  
  .logo-text {
    font-size: 1.5rem !important;
    letter-spacing: 1px !important;
    line-height: 1.2 !important;
  }
  
  .register-card {
    margin: 30px 0 4px 0;
  }
  
  .register-card :deep(.v-card-text) {
    padding: 12px !important;
  }
}

@media (max-width: 768px) {
  .logo-text {
    font-size: 1.25rem !important;
    letter-spacing: 0.5px !important;
    line-height: 1.1 !important;
  }
  
  .left-panel {
    padding: 1rem !important;
    min-height: 100px;
  }
}

@media (max-width: 600px) {
  .logo-text {
    font-size: 1rem !important;
    letter-spacing: 0.5px !important;
    line-height: 1 !important;
  }
  
  .left-panel {
    padding: 0.75rem !important;
    min-height: 80px;
  }
  
  .register-card {
    margin: 20px 0 4px 0;
  }
}

@media (max-width: 480px) {
  .logo-text {
    font-size: 0.875rem !important;
    letter-spacing: 0.25px !important;
    line-height: 1 !important;
  }
  
  .left-panel {
    padding: 0.5rem !important;
    min-height: 60px;
  }
}



/* Asegurar que el AppBar sea visible */
:deep(.v-app-bar) {
  z-index: 1000 !important;
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
}

.register-container {
  position: relative;
  z-index: 1;
}
</style>
