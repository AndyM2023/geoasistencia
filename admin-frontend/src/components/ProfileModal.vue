<template>
  <v-dialog v-model="show" max-width="600px" persistent>
    <v-card class="bg-dark-surface border border-blue-500/20">
      <!-- Header del modal -->
      <v-card-title class="text-white d-flex align-center justify-space-between">
        <div class="d-flex align-center">
          <v-icon color="blue-400" class="mr-3">mdi-account-circle</v-icon>
          <span class="text-h5">Perfil del Usuario</span>
        </div>
        <v-btn
          icon
          color="grey-400"
          variant="text"
          @click="closeModal"
          size="small"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <!-- Contenido del modal -->
      <v-card-text class="pa-6 profile-modal-scroll">
        <div v-if="loading" class="text-center py-8">
          <v-progress-circular
            indeterminate
            color="blue-400"
            size="64"
          ></v-progress-circular>
          <div class="text-white mt-4">Cargando perfil...</div>
        </div>

        <div v-else-if="error" class="text-center py-8">
          <v-icon color="red-400" size="64">mdi-alert-circle</v-icon>
          <div class="text-red-400 mt-4 text-h6">Error al cargar el perfil</div>
          <div class="text-grey-300 mt-2">{{ error }}</div>
          <v-btn
            color="blue-400"
            variant="tonal"
            @click="loadProfile"
            class="mt-4"
          >
            Reintentar
          </v-btn>
        </div>

        <div v-else-if="profile" class="profile-content">
          <!-- Header del perfil con avatar y información principal -->
          <div class="profile-header">
            <div class="profile-avatar-section">
              <v-avatar size="140" class="profile-avatar">
                <v-icon size="90" color="blue-400">mdi-account-circle</v-icon>
              </v-avatar>
              <div class="profile-status">
                <v-chip
                  :color="profile.is_active ? 'green-500' : 'red-500'"
                  variant="tonal"
                  size="small"
                  class="status-chip"
                >
                  <v-icon left size="small">
                    {{ profile.is_active ? 'mdi-check-circle' : 'mdi-close-circle' }}
                  </v-icon>
                  {{ profile.is_active ? 'Activo' : 'Inactivo' }}
                </v-chip>
              </div>
            </div>
            
            <div class="profile-info-main">
              <h2 class="profile-name">
                {{ profile.first_name }} {{ profile.last_name }}
              </h2>
              <div class="profile-role">
                <v-icon color="blue-400" size="small" class="mr-2">mdi-shield-account</v-icon>
                {{ profile.role === 'admin' ? 'Administrador del Sistema' : (profile.role === 'employee' ? 'Empleado' : profile.role || 'Usuario del Sistema') }}
              </div>
              <div class="profile-username">
                <v-icon color="grey-400" size="small" class="mr-2">mdi-at</v-icon>
                @{{ profile.username }}
              </div>
            </div>
          </div>

          <!-- Separador visual -->
          <v-divider class="profile-divider" color="rgba(59, 130, 246, 0.2)"></v-divider>

          <!-- Información de contacto -->
          <div class="profile-section">
            <div class="section-header">
              <h3 class="section-title">
                <v-icon color="blue-400" class="mr-2">mdi-contact-mail</v-icon>
                Información de Contacto
              </h3>
              <v-btn
                v-if="!isEditing"
                color="blue-400"
                variant="tonal"
                size="small"
                @click="startEditing"
                class="edit-btn"
              >
                <v-icon left size="small">mdi-pencil</v-icon>
                Editar
              </v-btn>
              <div v-else class="edit-actions">
                <v-btn
                  color="green-400"
                  variant="tonal"
                  size="small"
                  @click="saveChanges"
                  :loading="saving"
                  class="save-btn"
                >
                  <v-icon left size="small">mdi-check</v-icon>
                  Guardar
                </v-btn>
                <v-btn
                  color="grey-400"
                  variant="text"
                  size="small"
                  @click="cancelEditing"
                  class="cancel-btn"
                >
                  <v-icon left size="small">mdi-close</v-icon>
                  Cancelar
                </v-btn>
              </div>
            </div>
            <v-row>
              <v-col cols="12" sm="6">
                <div class="info-card">
                  <div class="info-icon">
                    <v-icon color="blue-400">mdi-email</v-icon>
                  </div>
                  <div class="info-content">
                    <div class="info-label">Correo Electrónico</div>
                    <div v-if="!isEditing" class="info-value">{{ profile.email || 'No especificado' }}</div>
                    <v-text-field
                      v-else
                      v-model="editForm.email"
                      label="Correo Electrónico"
                      variant="outlined"
                      color="blue-400"
                      :rules="[v => !!v || 'El correo es requerido', v => /.+@.+\..+/.test(v) || 'Formato de correo inválido']"
                      density="compact"
                      class="edit-field"
                    ></v-text-field>
                  </div>
                </div>
              </v-col>
              
              <v-col cols="12" sm="6">
                <div class="info-card">
                  <div class="info-icon">
                    <v-icon color="blue-400">mdi-account</v-icon>
                  </div>
                  <div class="info-content">
                    <div class="info-label">Nombre de Usuario</div>
                    <div v-if="!isEditing" class="info-value">{{ profile.username || 'No especificado' }}</div>
                    <v-text-field
                      v-else
                      v-model="editForm.username"
                      label="Nombre de Usuario"
                      variant="outlined"
                      color="blue-400"
                      :rules="[v => !!v || 'El nombre de usuario es requerido', v => v.length >= 3 || 'Mínimo 3 caracteres']"
                      density="compact"
                      class="edit-field"
                    ></v-text-field>
                  </div>
                </div>
              </v-col>
            </v-row>
          </div>

          <!-- Información personal -->
          <div class="profile-section">
            <div class="section-header">
              <h3 class="section-title">
                <v-icon color="blue-400" class="mr-2">mdi-account-details</v-icon>
                Información Personal
              </h3>
            </div>
            <v-row>
              <v-col cols="12" sm="6">
                <div class="info-card">
                  <div class="info-icon">
                    <v-icon color="blue-400">mdi-account-box</v-icon>
                  </div>
                  <div class="info-content">
                    <div class="info-label">Nombre</div>
                    <div v-if="!isEditing" class="info-value">{{ profile.first_name || 'No especificado' }}</div>
                    <v-text-field
                      v-else
                      v-model="editForm.first_name"
                      label="Nombre"
                      variant="outlined"
                      color="blue-400"
                      :rules="[v => !!v || 'El nombre es requerido']"
                      density="compact"
                      class="edit-field"
                    ></v-text-field>
                  </div>
                </div>
              </v-col>
              
              <v-col cols="12" sm="6">
                <div class="info-card">
                  <div class="info-icon">
                    <v-icon color="blue-400">mdi-account-box-outline</v-icon>
                  </div>
                  <div class="info-content">
                    <div class="info-label">Apellido</div>
                    <div v-if="!isEditing" class="info-value">{{ profile.last_name || 'No especificado' }}</div>
                    <v-text-field
                      v-else
                      v-model="editForm.last_name"
                      label="Apellido"
                      variant="outlined"
                      color="blue-400"
                      :rules="[v => !!v || 'El apellido es requerido']"
                      density="compact"
                      class="edit-field"
                    ></v-text-field>
                  </div>
                </div>
              </v-col>
            </v-row>
          </div>

                     <!-- Información del sistema -->
           <div class="profile-section">
             <h3 class="section-title">
               <v-icon color="blue-400" class="mr-2">mdi-cog</v-icon>
               Información del Sistema
             </h3>
             <v-row>
               <v-col cols="12" sm="6">
                 <div class="info-card">
                   <div class="info-icon">
                     <v-icon color="blue-400">mdi-calendar-plus</v-icon>
                   </div>
                   <div class="info-content">
                     <div class="info-label">Fecha de Registro</div>
                     <div class="info-value">{{ formatDate(profile.created_at) }}</div>
                   </div>
                 </div>
               </v-col>
               
                               <v-col cols="12" sm="6">
                  <div class="info-card">
                    <div class="info-icon">
                      <v-icon color="blue-400">mdi-calendar-edit</v-icon>
                    </div>
                    <div class="info-content">
                      <div class="info-label">Fecha de Actualización</div>
                      <div class="info-value">{{ formatDate(profile.updated_at) }}</div>
                    </div>
                  </div>
                </v-col>
             </v-row>
             
             <v-row v-if="profile.last_login" class="mt-3">
               <v-col cols="12" sm="6">
                 <div class="info-card">
                   <div class="info-icon">
                     <v-icon color="blue-400">mdi-clock-outline</v-icon>
                   </div>
                   <div class="info-content">
                     <div class="info-label">Último Acceso</div>
                     <div class="info-value">{{ formatDate(profile.last_login) }}</div>
                   </div>
                 </div>
               </v-col>
             </v-row>
           </div>

                     <!-- Recuperar Contraseña -->
           <!-- Seguridad de la Cuenta - Solo para Administradores -->
           <div v-if="profile.role === 'admin' || profile.role === 'administrator'" class="profile-section">
             <h3 class="section-title">
               <v-icon color="blue-400" class="mr-2">mdi-lock-reset</v-icon>
               Seguridad de la Cuenta
             </h3>
             <div class="security-card">
               <div class="security-info">
                 <v-icon color="blue-400" size="large" class="mr-3">mdi-shield-lock</v-icon>
                 <div class="security-content">
                   <div class="security-title">Cambiar Contraseña</div>
                   <div class="security-description">
                     Actualiza tu contraseña para mantener la seguridad de tu cuenta
                   </div>
                 </div>
               </div>
                                <v-btn
                   color="blue-400"
                   variant="tonal"
                   @click="openPasswordModal"
                   class="security-btn"
                 >
                   <v-icon left>mdi-key-change</v-icon>
                   Cambiar Contraseña
                 </v-btn>
             </div>
           </div>

           <!-- Grupos de permisos -->
           <div v-if="profile.groups && profile.groups.length > 0" class="profile-section">
             <h3 class="section-title">
               <v-icon color="blue-400" class="mr-2">mdi-shield-key</v-icon>
               Permisos y Grupos
             </h3>
             <div class="permissions-grid">
               <v-chip
                 v-for="group in profile.groups"
                 :key="group"
                 color="blue-400"
                 variant="tonal"
                 size="medium"
                 class="permission-chip"
               >
                 <v-icon left size="small">mdi-shield-check</v-icon>
                 {{ group }}
               </v-chip>
             </div>
           </div>
        </div>
      </v-card-text>

      <!-- Acciones del modal -->
      <v-card-actions class="pa-6 pt-0">
        <v-spacer></v-spacer>
        <v-btn
          color="blue-400"
          variant="tonal"
          @click="closeModal"
          class="px-6"
        >
          Cerrar
        </v-btn>
             </v-card-actions>
     </v-card>
   </v-dialog>

   <!-- Modal para cambiar contraseña -->
   <v-dialog v-model="showPasswordModal" max-width="500px" persistent>
     <v-card class="bg-dark-surface border border-blue-500/20">
       <!-- Header del modal -->
       <v-card-title class="text-white d-flex align-center justify-space-between">
         <div class="d-flex align-center">
           <v-icon color="blue-400" class="mr-3">mdi-lock-reset</v-icon>
           <span class="text-h5">Cambiar Contraseña</span>
         </div>
         <v-btn
           icon
           color="grey-400"
           variant="text"
           @click="closePasswordModal"
           size="small"
         >
           <v-icon>mdi-close</v-icon>
         </v-btn>
       </v-card-title>

       <!-- Contenido del modal -->
       <v-card-text class="pa-6 profile-modal-scroll">
         <div v-if="passwordLoading" class="text-center py-8">
           <v-progress-circular
             indeterminate
             color="blue-400"
             size="64"
           ></v-progress-circular>
           <div class="text-white mt-4">Cambiando contraseña...</div>
         </div>

         <div v-else-if="passwordError" class="text-center py-8">
           <v-icon color="red-400" size="64">mdi-alert-circle</v-icon>
           <div class="text-red-400 mt-4 text-h6">Error al cambiar contraseña</div>
           <div class="text-grey-300 mt-2">{{ passwordError }}</div>
           <v-btn
             color="blue-400"
             variant="tonal"
             @click="resetPasswordForm"
             class="mt-4"
           >
             Reintentar
           </v-btn>
         </div>

         <div v-else-if="passwordSuccess" class="text-center py-8">
           <v-icon color="green-400" size="64">mdi-check-circle</v-icon>
           <div class="text-green-400 mt-4 text-h6">¡Contraseña cambiada exitosamente!</div>
           <div class="text-grey-300 mt-2">Tu contraseña ha sido actualizada</div>
           <v-btn
             color="blue-400"
             variant="tonal"
             @click="closePasswordModal"
             class="mt-4"
           >
             Cerrar
           </v-btn>
         </div>

         <div v-else class="password-form">
           <v-form ref="passwordFormRef" v-model="passwordFormValid">
             <v-row>
               <v-col cols="12">
                 <v-text-field
                   v-model="passwordForm.currentPassword"
                   :type="showCurrentPassword ? 'text' : 'password'"
                   label="Contraseña Actual"
                   variant="outlined"
                   color="blue-400"
                   :rules="[v => !!v || 'La contraseña actual es requerida']"
                   prepend-inner-icon="mdi-lock"
                   :append-inner-icon="showCurrentPassword ? 'mdi-eye-off' : 'mdi-eye'"
                   @click:append-inner="showCurrentPassword = !showCurrentPassword"
                   class="password-field"
                 ></v-text-field>
               </v-col>
               
               <v-col cols="12">
                 <v-text-field
                   v-model="passwordForm.newPassword"
                   :type="showNewPassword ? 'text' : 'password'"
                   label="Nueva Contraseña"
                   variant="outlined"
                   color="blue-400"
                   :rules="[
                     v => !!v || 'La nueva contraseña es requerida',
                     v => v.length >= 8 || 'La contraseña debe tener al menos 8 caracteres',
                     v => /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(v) || 'Debe contener mayúsculas, minúsculas y números'
                   ]"
                   prepend-inner-icon="mdi-key-plus"
                   :append-inner-icon="showNewPassword ? 'mdi-eye-off' : 'mdi-eye'"
                   @click:append-inner="showNewPassword = !showNewPassword"
                   class="password-field"
                 ></v-text-field>
               </v-col>
               
               <v-col cols="12">
                 <v-text-field
                   v-model="passwordForm.confirmPassword"
                   :type="showConfirmPassword ? 'text' : 'password'"
                   label="Confirmar Nueva Contraseña"
                   variant="outlined"
                   color="blue-400"
                   :rules="[
                     v => !!v || 'Debe confirmar la nueva contraseña',
                     v => v === passwordForm.newPassword || 'Las contraseñas no coinciden'
                   ]"
                   prepend-inner-icon="mdi-key-check"
                   :append-inner-icon="showConfirmPassword ? 'mdi-eye-off' : 'mdi-eye'"
                   @click:append-inner="showConfirmPassword = !showConfirmPassword"
                   class="password-field"
                 ></v-text-field>
               </v-col>
             </v-row>
           </v-form>
         </div>
       </v-card-text>

       <!-- Acciones del modal -->
       <v-card-actions class="pa-6 pt-0" v-if="!passwordLoading && !passwordError && !passwordSuccess">
         <v-spacer></v-spacer>
         <v-btn
           color="grey-400"
           variant="text"
           @click="closePasswordModal"
           class="px-6"
         >
           Cancelar
         </v-btn>
         <v-btn
           color="blue-400"
           variant="tonal"
           @click="changePassword"
           :disabled="!passwordFormValid"
           :loading="passwordLoading"
           class="px-6"
         >
           <v-icon left>mdi-check</v-icon>
           Cambiar Contraseña
         </v-btn>
       </v-card-actions>
     </v-card>
   </v-dialog>
 </template>

<script>
import { ref, watch, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { authService } from '../services/authService'

export default {
  name: 'ProfileModal',
  props: {
    modelValue: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
         const authStore = useAuthStore()
     const show = ref(false)
     const loading = ref(false)
     const error = ref(null)
     const profile = ref(null)

     // Variables para el modal de contraseña
     const showPasswordModal = ref(false)
     const passwordLoading = ref(false)
     const passwordError = ref(null)
     const passwordSuccess = ref(false)
     const passwordFormValid = ref(false)
     const passwordFormRef = ref(null)
     const showCurrentPassword = ref(false)
     const showNewPassword = ref(false)
     const showConfirmPassword = ref(false)
     const passwordForm = ref({
       currentPassword: '',
       newPassword: '',
       confirmPassword: ''
     })

    // Computed para el v-model
    watch(() => props.modelValue, (newVal) => {
      show.value = newVal
      if (newVal) {
        loadProfile()
      }
    })

    watch(show, (newVal) => {
      emit('update:modelValue', newVal)
    })

      // Cargar perfil del usuario
  const loadProfile = async () => {
    if (!authStore.user) {
      error.value = 'No hay usuario autenticado'
      return
    }

    loading.value = true
    error.value = null

    try {
                    // Obtener datos actualizados del backend usando el nuevo método
       console.log('🔍 Llamando a getCurrentUserProfile...')
       const result = await authService.getCurrentUserProfile()
       console.log('🔍 Resultado de getCurrentUserProfile:', result)
       
       if (result.success && result.user) {
         profile.value = result.user
         console.log('✅ Perfil cargado desde backend:', profile.value)
         console.log('🔍 Campo created_at:', profile.value.created_at)
         console.log('🔍 Campo updated_at:', profile.value.updated_at)
         console.log('🔍 Tipo de created_at:', typeof profile.value.created_at)
         console.log('🔍 Tipo de updated_at:', typeof profile.value.updated_at)
         console.log('🔍 Todos los campos disponibles:', Object.keys(profile.value))
         
         // Verificar si los campos de fecha están vacíos o son null
         if (!profile.value.created_at) {
           console.log('⚠️ Campo created_at está vacío o es null')
         }
         if (!profile.value.updated_at) {
           console.log('⚠️ Campo updated_at está vacío o es null')
           // Solución temporal: usar created_at como updated_at si no está disponible
           profile.value.updated_at = profile.value.created_at
           console.log('🔧 Solución temporal: usando created_at como updated_at')
         }
                } else {
           // Si falla la API, usar datos del store como respaldo
           profile.value = { ...authStore.user }
           console.log('⚠️ Usando datos del store como respaldo:', profile.value)
           console.log('🔍 Campos del store:', Object.keys(profile.value))
           
           // Aplicar la misma lógica de respaldo para updated_at
           if (!profile.value.updated_at && profile.value.created_at) {
             profile.value.updated_at = profile.value.created_at
             console.log('🔧 Solución temporal en store: usando created_at como updated_at')
           }
         }
         } catch (err) {
       console.error('❌ Error cargando perfil desde backend:', err)
       // En caso de error, usar datos del store como respaldo
       profile.value = { ...authStore.user }
       console.log('⚠️ Usando datos del store como respaldo por error:', profile.value)
       
       // Aplicar la misma lógica de respaldo para updated_at
       if (!profile.value.updated_at && profile.value.created_at) {
         profile.value.updated_at = profile.value.created_at
         console.log('🔧 Solución temporal en catch: usando created_at como updated_at')
       }
     } finally {
      loading.value = false
    }
  }

    // Formatear fecha
    const formatDate = (dateString) => {
      if (!dateString) return 'No especificado'
      
      try {
        const date = new Date(dateString)
        return date.toLocaleDateString('es-ES', {
          year: 'numeric',
          month: 'long',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        })
      } catch (err) {
        return dateString
      }
    }

         // Cerrar modal
     const closeModal = () => {
       show.value = false
     }

     // Funciones para el modal de contraseña
     const closePasswordModal = () => {
       showPasswordModal.value = false
       resetPasswordForm()
     }

     const resetPasswordForm = () => {
       passwordForm.value = {
         currentPassword: '',
         newPassword: '',
         confirmPassword: ''
       }
       passwordError.value = null
       passwordSuccess.value = false
       showCurrentPassword.value = false
       showNewPassword.value = false
       showConfirmPassword.value = false
       if (passwordFormRef.value) {
         passwordFormRef.value.reset()
       }
     }

     // Asegurar que el formulario esté limpio al abrir el modal
     const openPasswordModal = () => {
       showPasswordModal.value = true
       resetPasswordForm()
     }

     const changePassword = async () => {
       if (!passwordFormValid.value) return

       passwordLoading.value = true
       passwordError.value = null
       passwordSuccess.value = false

       try {
         console.log('🔐 Iniciando cambio de contraseña...')
         
         // Validar que las contraseñas coincidan
         if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
           throw new Error('Las contraseñas no coinciden')
         }

                   // CAMBIO DE CONTRASEÑA REAL - Conectando con backend
          console.log('🔐 Iniciando cambio de contraseña real...')

                             // Llamada al backend para cambiar la contraseña usando el servicio de autenticación
          console.log('🔍 Enviando datos al backend:', {
            current_password: passwordForm.value.currentPassword ? '***' : 'vacío',
            new_password: passwordForm.value.newPassword ? '***' : 'vacío'
          })
          
          const result = await authService.changePassword({
            current_password: passwordForm.value.currentPassword,
            new_password: passwordForm.value.newPassword
          })
          
          if (result.success) {
            // Éxito
            passwordSuccess.value = true
            console.log('✅ Contraseña cambiada exitosamente:', result)
            
            // Mostrar mensaje de éxito por 3 segundos
            setTimeout(() => {
              closePasswordModal()
            }, 3000)
          } else {
            // Error del backend
            throw new Error(result.error || 'Error al cambiar la contraseña')
          }
         
       } catch (err) {
         console.error('❌ Error cambiando contraseña:', err)
         
         // Mensajes de error específicos
         let errorMessage = 'Error al cambiar la contraseña'
         
         if (err.message.includes('current_password')) {
           errorMessage = 'La contraseña actual es incorrecta'
         } else if (err.message.includes('new_password')) {
           errorMessage = 'La nueva contraseña no cumple con los requisitos de seguridad'
         } else if (err.message.includes('Las contraseñas no coinciden')) {
           errorMessage = 'Las contraseñas no coinciden'
         } else if (err.message.includes('Error al cambiar la contraseña')) {
           errorMessage = err.message
         } else if (err.message.includes('NetworkError') || err.message.includes('fetch')) {
           errorMessage = 'Error de conexión. Verifica tu conexión a internet'
         }
         
         passwordError.value = errorMessage
       } finally {
         passwordLoading.value = false
       }
     }

     // Variables para la edición del perfil
     const isEditing = ref(false)
     const editForm = ref({
       email: '',
       username: '',
       first_name: '',
       last_name: ''
     })
     const saving = ref(false)

     const startEditing = () => {
       isEditing.value = true
       editForm.value = { ...profile.value }
     }

     const cancelEditing = () => {
       isEditing.value = false
       editForm.value = { ...profile.value }
     }

     const saveChanges = async () => {
       if (!isEditing.value) return

       saving.value = true
       error.value = null

       try {
         console.log('�� Iniciando guardado de cambios...')
         const result = await authService.updateUserProfile(editForm.value)
         console.log('💾 Resultado de updateUserProfile:', result)

         if (result.success) {
           profile.value = result.user
           console.log('✅ Perfil actualizado:', profile.value)
           isEditing.value = false
           // Re-cargar el perfil para actualizar la fecha de actualización
           await loadProfile()
           // Mostrar mensaje de éxito por 3 segundos
           setTimeout(() => {
             // No cerrar el modal, ya que el usuario puede seguir editando
           }, 3000)
         } else {
           throw new Error(result.error || 'Error al actualizar el perfil')
         }
       } catch (err) {
         console.error('❌ Error guardando cambios:', err)
         error.value = err.message
       } finally {
         saving.value = false
       }
     }

     return {
       show,
       loading,
       error,
       profile,
       loadProfile,
       formatDate,
       closeModal,
       // Variables del modal de contraseña
       showPasswordModal,
       passwordLoading,
       passwordError,
       passwordSuccess,
       passwordFormValid,
       passwordFormRef,
       showCurrentPassword,
       showNewPassword,
       showConfirmPassword,
       passwordForm,
       // Funciones del modal de contraseña
       openPasswordModal,
       closePasswordModal,
       resetPasswordForm,
       changePassword,
       // Variables para la edición del perfil
       isEditing,
       editForm,
       saving,
       startEditing,
       cancelEditing,
       saveChanges
     }
  }
}
</script>

<style scoped>
/* Estilos del modal de perfil profesional */
.profile-content {
  animation: fadeIn 0.4s ease-out;
}

/* Header del perfil */
.profile-header {
  display: flex;
  align-items: flex-start;
  gap: 2rem;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(59, 130, 246, 0.05) 100%);
  border-radius: 16px;
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.profile-avatar-section {
  position: relative;
  flex-shrink: 0;
}

.profile-avatar {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(59, 130, 246, 0.05) 100%);
  border: 4px solid rgba(59, 130, 246, 0.3);
  box-shadow: 0 8px 32px rgba(59, 130, 246, 0.2);
  transition: all 0.3s ease;
}

.profile-avatar:hover {
  border-color: rgba(59, 130, 246, 0.6);
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(59, 130, 246, 0.3);
}

.profile-status {
  position: absolute;
  bottom: -8px;
  right: -8px;
}

.status-chip {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  font-weight: 600;
}

.profile-info-main {
  flex: 1;
  min-width: 0;
}

.profile-name {
  color: #ffffff;
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
  line-height: 1.2;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.profile-role {
  color: #60a5fa;
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
  display: flex;
  align-items: center;
}

.profile-username {
  color: #9ca3af;
  font-size: 1rem;
  font-weight: 500;
  display: flex;
  align-items: center;
}

/* Separador */
.profile-divider {
  margin: 2rem 0;
  opacity: 0.4;
}

/* Secciones del perfil */
.profile-section {
  margin-bottom: 2.5rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid rgba(59, 130, 246, 0.3);
}

.section-title {
  color: #ffffff;
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0; /* Remove default margin */
  display: flex;
  align-items: center;
}

.edit-btn {
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
  transition: all 0.3s ease;
}

.edit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(59, 130, 246, 0.3);
}

.edit-actions {
  display: flex;
  gap: 0.75rem;
}

.save-btn {
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
  transition: all 0.3s ease;
}

.save-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(59, 130, 246, 0.3);
}

.cancel-btn {
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
  transition: all 0.3s ease;
}

.cancel-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(59, 130, 246, 0.3);
}

/* Tarjetas de información */
.info-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.08) 0%, rgba(59, 130, 246, 0.03) 100%);
  border-radius: 12px;
  border: 1px solid rgba(59, 130, 246, 0.15);
  transition: all 0.3s ease;
  height: 100%;
}

.info-card:hover {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.12) 0%, rgba(59, 130, 246, 0.06) 100%);
  border-color: rgba(59, 130, 246, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(59, 130, 246, 0.15);
}

.info-icon {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(59, 130, 246, 0.1) 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.info-content {
  flex: 1;
  min-width: 0;
}

.info-label {
  color: #9ca3af;
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.info-value {
  color: #ffffff;
  font-size: 1rem;
  font-weight: 600;
  line-height: 1.4;
  word-break: break-word;
}

.edit-field .v-field__outline {
  border-color: rgba(59, 130, 246, 0.3) !important;
}

.edit-field .v-field--focused .v-field__outline {
  border-color: #60a5fa !important;
}

/* Grid de permisos */
.permissions-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.permission-chip {
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
  transition: all 0.3s ease;
}

   .permission-chip:hover {
     transform: translateY(-2px);
     box-shadow: 0 6px 16px rgba(59, 130, 246, 0.3);
   }

   /* Tarjeta de seguridad */
   .security-card {
     display: flex;
     align-items: center;
     justify-content: space-between;
     gap: 1.5rem;
     padding: 1.5rem;
     background: linear-gradient(135deg, rgba(59, 130, 246, 0.08) 0%, rgba(59, 130, 246, 0.03) 100%);
     border-radius: 16px;
     border: 1px solid rgba(59, 130, 246, 0.15);
     transition: all 0.3s ease;
   }

   .security-card:hover {
     background: linear-gradient(135deg, rgba(59, 130, 246, 0.12) 0%, rgba(59, 130, 246, 0.06) 100%);
     border-color: rgba(59, 130, 246, 0.3);
     transform: translateY(-2px);
     box-shadow: 0 8px 24px rgba(59, 130, 246, 0.15);
   }

   .security-info {
     display: flex;
     align-items: center;
     flex: 1;
   }

   .security-content {
     flex: 1;
   }

   .security-title {
     color: #ffffff;
     font-size: 1.125rem;
     font-weight: 600;
     margin-bottom: 0.5rem;
   }

   .security-description {
     color: #9ca3af;
     font-size: 0.875rem;
     line-height: 1.4;
   }

   .security-btn {
     flex-shrink: 0;
     font-weight: 600;
     box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
     transition: all 0.3s ease;
   }

   .security-btn:hover {
     transform: translateY(-2px);
     box-shadow: 0 6px 16px rgba(59, 130, 246, 0.3);
   }

   /* Formulario de contraseña */
   .password-form {
     animation: fadeIn 0.4s ease-out;
   }

   .password-field {
     margin-bottom: 1rem;
   }

   .password-field .v-field__outline {
     border-color: rgba(59, 130, 246, 0.3) !important;
   }

   .password-field .v-field--focused .v-field__outline {
     border-color: #60a5fa !important;
   }

/* Animación de entrada */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(30px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* Responsive */
@media (max-width: 768px) {
  .profile-header {
    flex-direction: column;
    text-align: center;
    gap: 1.5rem;
  }
  
  .profile-name {
    font-size: 1.75rem;
  }
  
  .profile-avatar {
    size: 120px;
  }
  
     .info-card {
     padding: 1rem;
   }
   
   .info-icon {
     width: 40px;
     height: 40px;
   }
   
   .security-card {
     flex-direction: column;
     text-align: center;
     gap: 1rem;
   }
   
   .security-info {
     flex-direction: column;
     text-align: center;
   }
}

@media (max-width: 600px) {
  .profile-header {
    padding: 1rem;
  }
  
  .profile-name {
    font-size: 1.5rem;
  }
  
  .profile-avatar {
    size: 100px;
  }
  
  .section-title {
    font-size: 1.125rem;
  }
  
     .info-card {
     flex-direction: column;
     text-align: center;
     gap: 0.75rem;
   }
   
   .security-card {
     padding: 1rem;
   }
   
   .security-title {
     font-size: 1rem;
   }
   
   .security-description {
     font-size: 0.8rem;
   }
}
</style>
