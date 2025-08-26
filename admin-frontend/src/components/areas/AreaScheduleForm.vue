<template>
  <div class="area-schedule-form">
    <div class="form-header">
      <h3>Configuración de Horarios</h3>
      <p class="text-muted">Configura los horarios de trabajo para esta área</p>
    </div>

    <!-- Botón para crear horario por defecto -->
    <div v-if="!schedule && !isEditing" class="default-schedule-section">
      <div class="alert alert-info">
        <i class="fas fa-info-circle"></i>
        <strong>Sin horario configurado</strong>
        <p>Esta área no tiene horarios configurados. Puedes crear un horario personalizado o usar el horario por defecto.</p>
      </div>
      
      <div class="button-group">
        <button 
          @click="createDefaultSchedule" 
          class="btn btn-primary"
          :disabled="loading"
        >
          <i class="fas fa-clock"></i>
          Crear Horario por Defecto (8:00 AM - 5:00 PM, L-V)
        </button>
        
        <button 
          @click="startEditing" 
          class="btn btn-outline-primary"
          :disabled="loading"
        >
          <i class="fas fa-edit"></i>
          Crear Horario Personalizado
        </button>
      </div>
    </div>

    <!-- Formulario de horarios -->
    <form v-if="isEditing || schedule" @submit.prevent="saveSchedule" class="schedule-form">
      <!-- Días de la semana -->
      <div class="days-section">
        <h4>Horarios por Día</h4>
        
        <div class="day-row" v-for="day in days" :key="day.key">
          <div class="day-header">
            <div class="day-toggle">
              <input 
                type="checkbox" 
                :id="`${day.key}_active`"
                v-model="formData[`${day.key}_active`]"
                class="form-check-input"
              />
              <label :for="`${day.key}_active`" class="form-check-label">
                {{ day.label }}
              </label>
            </div>
          </div>
          
          <div class="day-times" v-if="formData[`${day.key}_active`]">
            <div class="time-inputs">
              <div class="time-group">
                <label :for="`${day.key}_start`">Inicio:</label>
                <input 
                  type="time" 
                  :id="`${day.key}_start`"
                  v-model="formData[`${day.key}_start`]"
                  class="form-control"
                  required
                />
              </div>
              
              <div class="time-group">
                <label :for="`${day.key}_end`">Fin:</label>
                <input 
                  type="time" 
                  :id="`${day.key}_end`"
                  v-model="formData[`${day.key}_end`]"
                  class="form-control"
                  required
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Configuración adicional -->
      <div class="additional-settings">
        <h4>Configuración Adicional</h4>
        
        <div class="form-group">
          <label for="grace_period">Tolerancia para Llegadas Tarde (minutos):</label>
          <input 
            type="number" 
            id="grace_period"
            v-model.number="formData.grace_period_minutes"
            class="form-control"
            min="0"
            max="120"
            required
          />
          <small class="form-text text-muted">
            Minutos de tolerancia antes de considerar una llegada como tardanza
          </small>
        </div>
      </div>

      <!-- Botones de acción -->
      <div class="form-actions">
        <button 
          type="submit" 
          class="btn btn-success"
          :disabled="loading || !isValid"
        >
          <i class="fas fa-save"></i>
          {{ schedule ? 'Actualizar Horario' : 'Crear Horario' }}
        </button>
        
        <button 
          type="button" 
          @click="cancelEditing" 
          class="btn btn-secondary"
          :disabled="loading"
        >
          <i class="fas fa-times"></i>
          Cancelar
        </button>
        
        <button 
          v-if="schedule" 
          type="button" 
          @click="deleteSchedule" 
          class="btn btn-danger"
          :disabled="loading"
        >
          <i class="fas fa-trash"></i>
          Eliminar Horario
        </button>
      </div>
    </form>

    <!-- Horario actual (solo lectura) -->
    <div v-if="schedule && !isEditing" class="current-schedule">
      <div class="alert alert-success">
        <i class="fas fa-check-circle"></i>
        <strong>Horario Configurado</strong>
        <p>Esta área tiene horarios configurados. Puedes editarlos o eliminarlos.</p>
      </div>
      
      <div class="schedule-display">
        <h4>Horario Actual</h4>
        <div class="schedule-grid">
          <div 
            v-for="day in days" 
            :key="day.key"
            class="schedule-day"
            :class="{ 'active': schedule[`${day.key}_active`] }"
          >
            <div class="day-name">{{ day.label }}</div>
            <div v-if="schedule[`${day.key}_active`]" class="day-times">
              {{ schedule[`${day.key}_start`] }} - {{ schedule[`${day.key}_end`] }}
            </div>
            <div v-else class="day-inactive">No laborable</div>
          </div>
        </div>
        
        <div class="schedule-info">
          <p><strong>Tolerancia:</strong> {{ schedule.grace_period_minutes }} minutos</p>
        </div>
      </div>
      
      <div class="button-group">
        <button 
          @click="startEditing" 
          class="btn btn-primary"
        >
          <i class="fas fa-edit"></i>
          Editar Horario
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-overlay">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Cargando...</span>
      </div>
    </div>
  </div>
</template>

<script>
import scheduleService from '@/services/scheduleService'

export default {
  name: 'AreaScheduleForm',
  props: {
    areaId: {
      type: [Number, String],
      required: true
    },
    areaName: {
      type: String,
      default: 'Área'
    }
  },
  data() {
    return {
      schedule: null,
      isEditing: false,
      loading: false,
      formData: this.getDefaultFormData(),
      days: [
        { key: 'monday', label: 'Lunes' },
        { key: 'tuesday', label: 'Martes' },
        { key: 'wednesday', label: 'Miércoles' },
        { key: 'thursday', label: 'Jueves' },
        { key: 'friday', label: 'Viernes' },
        { key: 'saturday', label: 'Sábado' },
        { key: 'sunday', label: 'Domingo' }
      ]
    }
  },
  computed: {
    isValid() {
      const errors = scheduleService.validateSchedule(this.formData)
      return errors.length === 0
    }
  },
  async mounted() {
    await this.loadSchedule()
  },
  methods: {
    async loadSchedule() {
      try {
        this.loading = true
        const response = await scheduleService.getSchedule(this.areaId)
        if (response.length > 0) {
          this.schedule = response[0]
        }
      } catch (error) {
        console.error('Error cargando horario:', error)
        // Si no hay horario, no es un error
      } finally {
        this.loading = false
      }
    },

    getDefaultFormData() {
      return scheduleService.createDefaultScheduleData()
    },

    startEditing() {
      if (this.schedule) {
        // Cargar datos existentes
        this.formData = { ...this.schedule }
      } else {
        // Usar datos por defecto
        this.formData = this.getDefaultFormData()
      }
      this.isEditing = true
    },

    cancelEditing() {
      this.isEditing = false
      this.formData = this.getDefaultFormData()
    },

    async createDefaultSchedule() {
      try {
        this.loading = true
        const response = await scheduleService.createDefaultSchedule(this.areaId)
        this.schedule = response.schedule
        this.$emit('schedule-updated', this.schedule)
        this.$toast.success('Horario por defecto creado exitosamente')
      } catch (error) {
        console.error('Error creando horario por defecto:', error)
        this.$toast.error('Error al crear horario por defecto')
      } finally {
        this.loading = false
      }
    },

    async saveSchedule() {
      try {
        this.loading = true
        
        if (this.schedule) {
          // Actualizar horario existente
          const response = await scheduleService.updateSchedule(this.schedule.id, this.formData)
          this.schedule = response.schedule
          this.$toast.success('Horario actualizado exitosamente')
        } else {
          // Crear nuevo horario
          const scheduleData = { ...this.formData, area: this.areaId }
          const response = await scheduleService.createSchedule(scheduleData)
          this.schedule = response.schedule
          this.$toast.success('Horario creado exitosamente')
        }
        
        this.isEditing = false
        this.$emit('schedule-updated', this.schedule)
      } catch (error) {
        console.error('Error guardando horario:', error)
        this.$toast.error('Error al guardar horario')
      } finally {
        this.loading = false
      }
    },

    async deleteSchedule() {
      if (!confirm('¿Estás seguro de que quieres eliminar este horario?')) {
        return
      }

      try {
        this.loading = true
        await scheduleService.deleteSchedule(this.schedule.id)
        this.schedule = null
        this.isEditing = false
        this.$emit('schedule-updated', null)
        this.$toast.success('Horario eliminado exitosamente')
      } catch (error) {
        console.error('Error eliminando horario:', error)
        this.$toast.error('Error al eliminar horario')
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.area-schedule-form {
  position: relative;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.form-header {
  margin-bottom: 20px;
  text-align: center;
}

.form-header h3 {
  color: #333;
  margin-bottom: 5px;
}

.default-schedule-section {
  text-align: center;
  padding: 20px;
}

.alert {
  margin-bottom: 20px;
  padding: 15px;
  border-radius: 6px;
}

.alert-info {
  background-color: #d1ecf1;
  border-color: #bee5eb;
  color: #0c5460;
}

.alert-success {
  background-color: #d4edda;
  border-color: #c3e6cb;
  color: #155724;
}

.button-group {
  display: flex;
  gap: 10px;
  justify-content: center;
  flex-wrap: wrap;
}

.schedule-form {
  margin-top: 20px;
}

.days-section {
  margin-bottom: 30px;
}

.days-section h4 {
  color: #333;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid #e9ecef;
}

.day-row {
  display: flex;
  align-items: center;
  padding: 15px;
  margin-bottom: 10px;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.day-header {
  min-width: 150px;
}

.day-toggle {
  display: flex;
  align-items: center;
  gap: 10px;
}

.day-times {
  flex: 1;
  margin-left: 20px;
}

.time-inputs {
  display: flex;
  gap: 15px;
  align-items: center;
}

.time-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.time-group label {
  font-size: 0.9em;
  color: #666;
  font-weight: 500;
}

.time-group input {
  width: 120px;
}

.additional-settings {
  margin-bottom: 30px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 6px;
}

.additional-settings h4 {
  color: #333;
  margin-bottom: 15px;
}

.form-actions {
  display: flex;
  gap: 10px;
  justify-content: center;
  flex-wrap: wrap;
}

.current-schedule {
  margin-top: 20px;
}

.schedule-display {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 6px;
  margin-bottom: 20px;
}

.schedule-display h4 {
  color: #333;
  margin-bottom: 15px;
}

.schedule-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.schedule-day {
  padding: 15px;
  background: #fff;
  border-radius: 6px;
  border: 2px solid #e9ecef;
  text-align: center;
}

.schedule-day.active {
  border-color: #28a745;
  background: #f8fff9;
}

.day-name {
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.day-times {
  color: #28a745;
  font-weight: 500;
}

.day-inactive {
  color: #6c757d;
  font-style: italic;
}

.schedule-info {
  text-align: center;
  padding: 15px;
  background: #fff;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
}

@media (max-width: 768px) {
  .day-row {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .day-times {
    margin-left: 0;
    margin-top: 15px;
    width: 100%;
  }
  
  .time-inputs {
    flex-direction: column;
    gap: 10px;
  }
  
  .button-group {
    flex-direction: column;
  }
  
  .form-actions {
    flex-direction: column;
  }
}
</style>
