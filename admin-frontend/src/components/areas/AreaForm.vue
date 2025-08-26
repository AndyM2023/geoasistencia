<template>
  <v-dialog v-model="localShowDialog" max-width="700px" class="area-dialog">
    <v-card class="bg-dark-surface border border-blue-500/20">
      <v-card-title class="text-white">
        <span class="text-h5">{{ editingArea ? 'Editar' : 'Nueva' }} Área</span>
        <v-spacer></v-spacer>
        <v-chip v-if="editingArea" color="blue-400" variant="tonal" size="small">
          Editando
        </v-chip>
      </v-card-title>
      
      <!-- Contenedor con scroll para el formulario -->
      <div class="area-form-scroll-wrapper">
        <v-form ref="form" v-model="valid">
          <v-row class="ma-0 pa-0">
            <!-- Nombre y Descripción -->
            <v-col cols="12" sm="6" class="pa-2">
              <v-text-field
                v-model="localAreaForm.name"
                label="Nombre del Área"
                required
                :rules="[
                  v => !!v || 'Nombre es requerido',
                  v => v.length >= 3 || 'El nombre debe tener al menos 3 caracteres',
                  v => v.length <= 100 || 'El nombre no puede exceder 100 caracteres',
                  v => /^[a-zA-Z0-9\s_-]+$/.test(v) || 'Se permiten letras, números, espacios, guiones (-) y guiones bajos (_)'
                ]"
                color="blue-400"
                variant="outlined"
                :error-messages="formErrors.name"
                @blur="validateField('name')"
                @input="sanitizeName"
                :hint="nameHint"
                :persistent-hint="showNameHint"
                density="compact"
                class="mb-2"
              ></v-text-field>
            </v-col>
            
            <v-col cols="12" sm="6" class="pa-2">
              <v-text-field
                v-model="localAreaForm.description"
                label="Descripción"
                required
                :rules="[
                  v => !!v || 'Descripción es requerida',
                  v => v.length >= 3 || 'La descripción debe tener al menos 3 caracteres',
                  v => v.length <= 500 || 'La descripción no puede exceder 500 caracteres',
                  v => /^[a-zA-Z0-9\s]+$/.test(v) || 'Solo se permiten letras y números'
                ]"
                color="blue-400"
                variant="outlined"
                :error-messages="formErrors.description"
                @blur="validateField('description')"
                @input="sanitizeDescription"
                :hint="descriptionHint"
                :persistent-hint="showDescriptionHint"
                density="compact"
                class="mb-2"
              ></v-text-field>
            </v-col>
            
            <!-- Botón de ubicación -->
            <v-col cols="12" class="pa-2">
              <v-btn 
                :color="localAreaForm.latitude && localAreaForm.longitude ? 'blue-400' : 'green-400'" 
                :variant="localAreaForm.latitude && localAreaForm.longitude ? 'flat' : 'outlined'"
                :prepend-icon="localAreaForm.latitude && localAreaForm.longitude ? 'mdi-check-circle' : 'mdi-map-marker'" 
                @click="$emit('showMapSelector')"
                class="mb-3"
                block
              >
                {{ localAreaForm.latitude && localAreaForm.longitude ? '✅ Ubicación Seleccionada - Cambiar' : '📍 Seleccionar Ubicación en el Mapa' }}
              </v-btn>
            </v-col>
            
            <!-- Coordenadas y Radio -->
            <v-col cols="12" sm="6" class="pa-2">
              <v-text-field
                v-model="localAreaForm.latitude"
                label="Latitud"
                readonly
                required
                :color="localAreaForm.latitude ? 'blue-400' : 'error'"
                variant="outlined"
                :prepend-icon="localAreaForm.latitude ? 'mdi-crosshairs-gps' : 'mdi-alert-circle'"
                :placeholder="localAreaForm.latitude ? localAreaForm.latitude : 'Selecciona en el mapa'"
                :error-messages="formErrors.latitude"
                density="compact"
                class="mb-2"
              ></v-text-field>
            </v-col>
            
            <v-col cols="12" sm="6" class="pa-2">
              <v-text-field
                v-model="localAreaForm.longitude"
                label="Longitud"
                readonly
                required
                :color="localAreaForm.longitude ? 'blue-400' : 'error'"
                variant="outlined"
                :prepend-icon="localAreaForm.longitude ? 'mdi-crosshairs-gps' : 'mdi-alert-circle'"
                :placeholder="localAreaForm.longitude ? localAreaForm.longitude : 'Selecciona en el mapa'"
                :error-messages="formErrors.longitude"
                density="compact"
                class="mb-2"
              ></v-text-field>
            </v-col>
            
            <v-col cols="12" sm="6" class="pa-2">
              <v-text-field
                v-model="localAreaForm.radius"
                label="Radio (metros)"
                readonly
                required
                :color="localAreaForm.radius >= 10 ? 'blue-400' : 'error'"
                variant="outlined"
                :prepend-icon="localAreaForm.radius >= 10 ? 'mdi-radius' : 'mdi-alert-circle'"
                :placeholder="localAreaForm.radius ? localAreaForm.radius + 'm' : 'Selecciona en el mapa'"
                :error-messages="formErrors.radius"
                density="compact"
                class="mb-2"
              ></v-text-field>
            </v-col>
            
            <!-- NUEVA SECCIÓN: Configuración de Horarios -->
            <v-col cols="12" class="pa-2">
              <v-divider class="my-3"></v-divider>
              <div class="schedule-section">
                <h4 class="text-h6 text-white mb-2">
                  <v-icon color="blue-400" class="mr-2">mdi-clock</v-icon>
                  Configuración de Horarios de Trabajo
                </h4>
                
                <!-- Opciones de horario -->
                <v-row class="ma-0 pa-0">
                  <v-col cols="12" class="pa-0">
                    <v-radio-group v-model="localScheduleType" color="blue-400" class="mb-2">
                      <v-radio value="default" class="mb-1">
                        <template v-slot:label>
                          <div class="d-flex align-center">
                            <v-icon color="green-400" class="mr-2">mdi-check-circle</v-icon>
                            <span class="text-white">Horario por defecto (8:00 AM - 5:00 PM, Lunes a Viernes)</span>
                          </div>
                        </template>
                      </v-radio>
                      
                      <v-radio value="custom" class="mb-1">
                        <template v-slot:label>
                          <div class="d-flex align-center">
                            <v-icon color="blue-400" class="mr-2">mdi-cog</v-icon>
                            <span class="text-white">Horario personalizado</span>
                          </div>
                        </template>
                      </v-radio>
                      
                      <v-radio value="none" class="mb-1">
                        <template v-slot:label>
                          <div class="d-flex align-center">
                            <v-icon color="grey-400" class="mr-2">mdi-close-circle</v-icon>
                            <span class="text-white">Sin horario (no requiere control de tiempo)</span>
                          </div>
                        </template>
                      </v-radio>
                    </v-radio-group>
                    
                    <!-- Botón para aplicar horario por defecto -->
                    <div class="mt-2">
                      <v-btn
                        v-if="localScheduleType === 'custom'"
                        color="green-400"
                        variant="outlined"
                        size="small"
                        prepend-icon="mdi-refresh"
                        @click="createDefaultSchedule"
                      >
                        Aplicar Horario por Defecto
                      </v-btn>
                    </div>
                  </v-col>
                </v-row>
                
                <!-- Configuración de horario personalizado -->
                <div v-if="localScheduleType === 'custom'" class="custom-schedule mt-3">
                  <v-alert type="info" variant="tonal" class="mb-3">
                    <template v-slot:prepend>
                      <v-icon>mdi-information</v-icon>
                    </template>
                    <strong>Configura los horarios para cada día de la semana</strong>
                    <br>• Marca los días que son laborables
                    <br>• Define las horas de entrada y salida
                    <br>• Establece la tolerancia para llegadas tarde
                  </v-alert>
                  
                  <!-- Días de la semana -->
                  <div v-for="day in scheduleDays" :key="day.key" class="day-config mb-2">
                    <v-card class="bg-dark-surface border border-blue-500/20 pa-2">
                      <div class="d-flex align-center justify-space-between">
                        <div class="d-flex align-center">
                          <v-checkbox
                            v-model="localSchedule[`${day.key}_active`]"
                            :color="localSchedule[`${day.key}_active`] ? 'blue-400' : 'grey-400'"
                            hide-details
                            class="mr-3"
                            @change="validateScheduleDay(day.key)"
                          ></v-checkbox>
                          <span class="text-white font-weight-medium">{{ day.name }}</span>
                        </div>
                        
                        <v-chip 
                          v-if="localSchedule[`${day.key}_active`]" 
                          color="green-400" 
                          variant="tonal" 
                          size="small"
                        >
                          Laborable
                        </v-chip>
                        <v-chip 
                          v-else 
                          color="grey-400" 
                          variant="tonal" 
                          size="small"
                        >
                          No laborable
                        </v-chip>
                      </div>
                      
                      <!-- Campos de horario para días activos -->
                      <div v-if="localSchedule[`${day.key}_active`]" class="mt-2">
                        <v-row class="ma-0 pa-0">
                          <v-col cols="6" class="pa-1">
                            <v-text-field
                              v-model="localSchedule[`${day.key}_start`]"
                              label="Hora de Entrada"
                              type="time"
                              required
                              color="blue-400"
                              variant="outlined"
                              density="compact"
                              :rules="[
                                v => !!v || 'Hora de entrada requerida',
                                v => localSchedule[`${day.key}_end`] ? v < localSchedule[`${day.key}_end`] : true || 'La hora de entrada debe ser anterior a la de salida'
                              ]"
                              :error-messages="getScheduleFieldError(`${day.key}_start`)"
                              @blur="validateScheduleField(`${day.key}_start`)"
                            ></v-text-field>
                          </v-col>
                          <v-col cols="6" class="pa-1">
                            <v-text-field
                              v-model="localSchedule[`${day.key}_end`]"
                              label="Hora de Salida"
                              type="time"
                              required
                              color="blue-400"
                              variant="outlined"
                              density="compact"
                              :rules="[
                                v => !!v || 'Hora de salida requerida',
                                v => localSchedule[`${day.key}_start`] ? localSchedule[`${day.key}_start`] < v : true || 'La hora de salida debe ser posterior a la de entrada'
                              ]"
                              :error-messages="getScheduleFieldError(`${day.key}_end`)"
                              @blur="validateScheduleField(`${day.key}_end`)"
                            ></v-text-field>
                          </v-col>
                        </v-row>
                      </div>
                    </v-card>
                  </div>
                  
                  <!-- Configuración de tolerancia -->
                  <v-card class="bg-dark-surface border border-blue-500/20 pa-3 mt-3">
                    <h5 class="text-h6 text-white mb-2">
                      <v-icon color="orange-400" class="mr-2">mdi-timer-sand</v-icon>
                      Configuración de Tolerancia
                    </h5>
                    <v-text-field
                      v-model.number="localSchedule.grace_period_minutes"
                      label="Tolerancia para llegadas tarde (minutos)"
                      type="number"
                      min="0"
                      max="120"
                      required
                      color="orange-400"
                      variant="outlined"
                      density="compact"
                      :rules="[
                        v => !!v || 'Tolerancia requerida',
                        v => v >= 0 || 'Mínimo 0 minutos',
                        v => v <= 120 || 'Máximo 120 minutos'
                      ]"
                      :hint="`Permite hasta ${localSchedule.grace_period_minutes} minutos de tardanza antes de marcar como llegada tarde`"
                      persistent-hint
                      :error-messages="formErrors.grace_period"
                      @blur="validateField('grace_period')"
                    ></v-text-field>
                  </v-card>
                  
                  <!-- Resumen del horario seleccionado -->
                  <div v-if="localScheduleType !== 'none'" class="schedule-summary mt-3">
                    <v-alert 
                      :type="localScheduleType === 'default' ? 'success' : 'info'" 
                      variant="tonal"
                    >
                      <template v-slot:prepend>
                        <v-icon>{{ localScheduleType === 'default' ? 'mdi-check-circle' : 'mdi-clock' }}</v-icon>
                      </template>
                      <strong>{{ localScheduleType === 'default' ? 'Horario por defecto' : 'Horario personalizado' }}</strong>
                      <br>{{ getScheduleSummary() }}
                    </v-alert>
                  </div>
                  
                  <!-- Información adicional del horario -->
                  <div v-if="localScheduleType === 'custom'" class="schedule-details mt-2">
                    <v-card class="bg-dark-surface border border-blue-500/20 pa-2">
                      <h6 class="text-subtitle-2 text-white mb-2">
                        <v-icon color="blue-400" class="mr-2" size="small">mdi-information</v-icon>
                        Detalles del Horario
                      </h6>
                      <div class="text-caption text-grey-300">
                        <div v-for="day in scheduleDays" :key="day.key" class="mb-1">
                          <span v-if="localSchedule[`${day.key}_active`]" class="text-green-400">
                            ✅ {{ day.name }}: {{ localSchedule[`${day.key}_start`] }} - {{ localSchedule[`${day.key}_end`] }}
                          </span>
                          <span v-else class="text-grey-400">
                            ❌ {{ day.name }}: No laborable
                          </span>
                        </div>
                        <div class="mt-2 pt-2 border-top border-grey-600">
                          <strong>Tolerancia:</strong> {{ localSchedule.grace_period_minutes }} minutos
                        </div>
                      </div>
                    </v-card>
                  </div>
                </div>
              </div>
            </v-col>
          </v-row>
        </v-form>
      </div>
      
      <v-card-actions class="pa-4">
        <v-spacer></v-spacer>
        <v-btn color="grey-400" variant="outlined" @click="$emit('cancel')">
          Cancelar
        </v-btn>
        <v-btn 
          color="blue-400" 
          variant="flat" 
          @click="saveArea"
          :loading="saving"
          :disabled="saving"
        >
          {{ editingArea ? 'Actualizar' : 'Crear' }} Área
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  name: 'AreaForm',
  props: {
    showDialog: {
      type: Boolean,
      default: false
    },
    editingArea: {
      type: Object,
      default: null
    },
    areaForm: {
      type: Object,
      required: true
    },
    scheduleType: {
      type: String,
      required: true
    },
    schedule: {
      type: Object,
      required: true
    },
    formErrors: {
      type: Object,
      default: () => ({})
    },
    saving: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:showDialog', 'update:areaForm', 'update:scheduleType', 'update:schedule', 'save', 'cancel', 'showMapSelector'],
  data() {
    return {
      valid: false,
      showNameHint: false,
      nameHint: 'Se permiten letras, números, espacios, guiones (-) y guiones bajos (_)',
      showDescriptionHint: false,
      descriptionHint: 'Solo se permiten letras y números',
      scheduleDays: [
        { key: 'monday', name: 'Lunes' },
        { key: 'tuesday', name: 'Martes' },
        { key: 'wednesday', name: 'Miércoles' },
        { key: 'thursday', name: 'Jueves' },
        { key: 'friday', name: 'Viernes' },
        { key: 'saturday', name: 'Sábado' },
        { key: 'sunday', name: 'Domingo' }
      ]
    }
  },
  computed: {
    localShowDialog: {
      get() {
        return this.showDialog
      },
      set(value) {
        this.$emit('update:showDialog', value)
      }
    },
    localAreaForm: {
      get() {
        return this.areaForm
      },
      set(value) {
        this.$emit('update:areaForm', value)
      }
    },
    localScheduleType: {
      get() {
        return this.scheduleType
      },
      set(value) {
        this.$emit('update:scheduleType', value)
      }
    },
    localSchedule: {
      get() {
        return this.schedule
      },
      set(value) {
        this.$emit('update:schedule', value)
      }
    }
  },
  watch: {
    editingArea: {
      handler(newArea) {
        if (newArea) {
          // Cuando se edita un área, asegurar que el formulario sea válido
          this.$nextTick(() => {
            if (this.$refs.form) {
              this.valid = true
            }
          })
        }
      },
      immediate: true
    }
  },
  methods: {
    validateField(fieldName) {
      // Emit to parent to handle validation
      this.$emit('validateField', fieldName)
    },
    sanitizeName() {
      // Emit to parent to handle sanitization
      this.$emit('sanitizeName')
    },
    sanitizeDescription() {
      // Emit to parent to handle sanitization
      this.$emit('sanitizeDescription')
    },
    createDefaultSchedule() {
      // Emit to parent to handle default schedule creation
      this.$emit('createDefaultSchedule')
    },
    validateScheduleField(fieldName) {
      // Emit to parent to handle schedule validation
      this.$emit('validateScheduleField', fieldName)
    },
    validateScheduleDay(dayKey) {
      // Emit to parent to handle schedule day validation
      this.$emit('validateScheduleDay', dayKey)
    },
    getScheduleFieldError(fieldName) {
      // Return schedule field error from parent
      return this.formErrors[fieldName] || ''
    },
    getScheduleSummary() {
      // Emit to parent to get schedule summary
      this.$emit('getScheduleSummary')
      return 'Horarios configurados correctamente'
    },
    saveArea() {
      // Validar el formulario antes de emitir el evento
      if (this.$refs.form && this.$refs.form.validate) {
        const isValid = this.$refs.form.validate()
        if (isValid) {
          this.$emit('save')
        } else {
          console.log('❌ Validación del formulario falló')
        }
      } else {
        // Si no hay referencia al formulario, emitir directamente
        console.log('⚠️ No hay referencia al formulario, emitiendo evento save')
        this.$emit('save')
      }
    }
  }
}
</script>

<style>
@import '../../style/areas.css';
</style>
