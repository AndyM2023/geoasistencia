<template>
  <div class="areas-container">
    <v-row class="mt-0 areas-header">
      <v-col cols="12">
        <div class="d-flex justify-space-between align-center">
          <h1 class="text-h4 text-white">Gestión de Áreas</h1>
          <div class="d-flex gap-2">
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
            class="text-white search-field-responsive"
            :class="{
              'search-field-mobile': $vuetify.display.smAndDown,
              'search-field-tablet': $vuetify.display.mdAndDown && !$vuetify.display.smAndDown
            }"
          ></v-text-field>
        </div>
      </v-card-title>

             <v-data-table
         :key="tableKey"
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
           <div class="d-flex flex-nowrap gap-1 actions-container">
             <v-btn icon="mdi-pencil" size="small" color="blue-400" @click="editArea(item)" title="Editar área"></v-btn>
             
             <!-- Botón dinámico según el estado del área -->
             <v-btn 
               v-if="item.status === 'active'"
               icon="mdi-account-off" 
               size="small" 
               :color="item.employee_count > 0 ? 'grey-400' : 'red-400'"
               @click="item.employee_count > 0 ? null : deleteArea(item)"
               :disabled="item.employee_count > 0"
               :title="item.employee_count > 0 ? 'No se puede desactivar: tiene empleados asignados' : 'Desactivar área'"
             ></v-btn>
             
             <v-btn 
               v-else
               icon="mdi-account-check" 
               size="small" 
               color="green-400" 
               @click="activateArea(item)"
               title="Reactivar área"
             ></v-btn>
           </div>
         </template>
        
        <template v-slot:item.latitude="{ item }">
          <span :title="item.latitude">{{ formatCoordinate(item.latitude) }}</span>
        </template>
        
        <template v-slot:item.longitude="{ item }">
          <span :title="item.longitude">{{ formatCoordinate(item.longitude) }}</span>
        </template>
        
        <template v-slot:item.description="{ item }">
          <div class="description-cell">
            <span v-for="(line, index) in formatDescription(item.description)" :key="index" class="description-line">
              {{ line }}
            </span>
          </div>
        </template>
        
        <template v-slot:item.employee_count="{ item }">
          <div class="d-flex justify-center">
            <v-chip 
              :color="item.employee_count > 0 ? 'green-500' : 'grey-500'" 
              size="small" 
              variant="tonal"
            >
              {{ item.employee_count || 0 }}
            </v-chip>
          </div>
        </template>
        
        <template v-slot:item.schedule_info="{ item }">
          <div class="d-flex justify-center">
            <v-chip 
              v-if="item.schedule"
              :color="getScheduleColor(item.schedule)" 
              size="small" 
              variant="tonal"
              :title="getScheduleTooltip(item.schedule)"
            >
              <v-icon left size="small">{{ getScheduleIcon(item.schedule) }}</v-icon>
              {{ getScheduleText(item.schedule) }}
            </v-chip>
            <v-chip 
              v-else
              color="grey-500" 
              size="small" 
              variant="tonal"
              title="Sin horario"
            >
              <v-icon left size="small">mdi-close-circle</v-icon>
              Sin horario
            </v-chip>
          </div>
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
    <v-dialog v-model="showDialog" max-width="700px" class="area-dialog">
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
                  v-model="areaForm.name"
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
                  v-model="areaForm.description"
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
                  :color="areaForm.latitude && areaForm.longitude ? 'blue-400' : 'green-400'" 
                  :variant="areaForm.latitude && areaForm.longitude ? 'flat' : 'outlined'"
                  :prepend-icon="areaForm.latitude && areaForm.longitude ? 'mdi-check-circle' : 'mdi-map-marker'" 
                  @click="showMapSelectorModal"
                  class="mb-3"
                  block
                >
                  {{ areaForm.latitude && areaForm.longitude ? '✅ Ubicación Seleccionada - Cambiar' : '📍 Seleccionar Ubicación en el Mapa' }}
                </v-btn>
              </v-col>
              
              <!-- Coordenadas y Radio -->
              <v-col cols="12" sm="6" class="pa-2">
                <v-text-field
                  v-model="areaForm.latitude"
                  label="Latitud"
                  readonly
                  required
                  :color="areaForm.latitude ? 'blue-400' : 'error'"
                  variant="outlined"
                  :prepend-icon="areaForm.latitude ? 'mdi-crosshairs-gps' : 'mdi-alert-circle'"
                  :placeholder="areaForm.latitude ? areaForm.latitude : 'Selecciona en el mapa'"
                  :error-messages="formErrors.latitude"
                  density="compact"
                  class="mb-2"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" sm="6" class="pa-2">
                <v-text-field
                  v-model="areaForm.longitude"
                  label="Longitud"
                  readonly
                  required
                  :color="areaForm.longitude ? 'blue-400' : 'error'"
                  variant="outlined"
                  :prepend-icon="areaForm.longitude ? 'mdi-crosshairs-gps' : 'mdi-alert-circle'"
                  :placeholder="areaForm.longitude ? areaForm.longitude : 'Selecciona en el mapa'"
                  :error-messages="formErrors.longitude"
                  density="compact"
                  class="mb-2"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" sm="6" class="pa-2">
                <v-text-field
                  v-model="areaForm.radius"
                  label="Radio (metros)"
                  readonly
                  required
                  :color="areaForm.radius >= 10 ? 'blue-400' : 'error'"
                  variant="outlined"
                  :prepend-icon="areaForm.radius >= 10 ? 'mdi-radius' : 'mdi-alert-circle'"
                  :placeholder="areaForm.radius ? areaForm.radius + 'm' : 'Selecciona en el mapa'"
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
                      <v-radio-group v-model="scheduleType" color="blue-400" class="mb-2">
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
                          v-if="scheduleType === 'custom'"
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
                  <div v-if="scheduleType === 'custom'" class="custom-schedule mt-3">
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
                              v-model="schedule[`${day.key}_active`]"
                              :color="schedule[`${day.key}_active`] ? 'blue-400' : 'grey-400'"
                              hide-details
                              class="mr-3"
                              @change="validateScheduleDay(day.key)"
                            ></v-checkbox>
                            <span class="text-white font-weight-medium">{{ day.label }}</span>
                          </div>
                          
                          <v-chip 
                            v-if="schedule[`${day.key}_active`]" 
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
                        <div v-if="schedule[`${day.key}_active`]" class="mt-2">
                          <v-row class="ma-0 pa-0">
                            <v-col cols="6" class="pa-1">
                              <v-text-field
                                v-model="schedule[`${day.key}_start`]"
                                label="Hora de Entrada"
                                type="time"
                                required
                                color="blue-400"
                                variant="outlined"
                                density="compact"
                                :rules="[
                                  v => !!v || 'Hora de entrada requerida',
                                  v => schedule[`${day.key}_end`] ? v < schedule[`${day.key}_end`] : true || 'La hora de entrada debe ser anterior a la de salida'
                                ]"
                                :error-messages="getScheduleFieldError(`${day.key}_start`)"
                                @blur="validateScheduleField(`${day.key}_start`)"
                              ></v-text-field>
                            </v-col>
                            <v-col cols="6" class="pa-1">
                              <v-text-field
                                v-model="schedule[`${day.key}_end`]"
                                label="Hora de Salida"
                                type="time"
                                required
                                color="blue-400"
                                variant="outlined"
                                density="compact"
                                :rules="[
                                  v => !!v || 'Hora de salida requerida',
                                  v => schedule[`${day.key}_start`] ? schedule[`${day.key}_start`] < v : true || 'La hora de salida debe ser posterior a la de entrada'
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
                        v-model.number="schedule.grace_period_minutes"
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
                        :hint="`Permite hasta ${schedule.grace_period_minutes} minutos de tardanza antes de marcar como llegada tarde`"
                        persistent-hint
                        :error-messages="formErrors.grace_period"
                        @blur="validateField('grace_period')"
                      ></v-text-field>
                    </v-card>
                  </div>
                  
                  <!-- Resumen del horario seleccionado -->
                  <div v-if="scheduleType !== 'none'" class="schedule-summary mt-3">
                    <v-alert 
                      :type="scheduleType === 'default' ? 'success' : 'info'" 
                      variant="tonal"
                    >
                      <template v-slot:prepend>
                        <v-icon>{{ scheduleType === 'default' ? 'mdi-check-circle' : 'mdi-clock' }}</v-icon>
                      </template>
                      <strong>{{ scheduleType === 'default' ? 'Horario por defecto' : 'Horario personalizado' }}</strong>
                      <br>{{ getScheduleSummary() }}
                    </v-alert>
                  </div>
                  
                  <!-- Información adicional del horario -->
                  <div v-if="scheduleType === 'custom'" class="schedule-details mt-2">
                    <v-card class="bg-dark-surface border border-blue-500/20 pa-2">
                      <h6 class="text-subtitle-2 text-white mb-2">
                        <v-icon color="blue-400" class="mr-2" size="small">mdi-information</v-icon>
                        Detalles del Horario
                      </h6>
                      <div class="text-caption text-grey-300">
                        <div v-for="day in scheduleDays" :key="day.key" class="mb-1">
                          <span v-if="schedule[`${day.key}_active`]" class="text-green-400">
                            ✅ {{ day.label }}: {{ schedule[`${day.key}_start`] }} - {{ schedule[`${day.key}_end`] }}
                          </span>
                          <span v-else class="text-grey-400">
                            ❌ {{ day.label }}: No laborable
                          </span>
                        </div>
                        <div class="mt-2 pt-2 border-top border-grey-600">
                          <strong>Tolerancia:</strong> {{ schedule.grace_period_minutes }} minutos
                        </div>
                      </div>
                    </v-card>
                  </div>
                </div>
              </v-col>
              
            </v-row>
          </v-form>
        </div>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey-400" variant="text" @click="cancelDialog">Cancelar</v-btn>
          <v-btn color="blue-400" @click="saveArea" :loading="saving" class="neon-border">Guardar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog del Selector de Mapa -->
    <v-dialog v-model="showMapSelector" max-width="1200px" persistent>
      <v-card class="bg-dark-surface border border-blue-500/20">
        <v-card-title class="text-white">
          <span class="text-h5">🗺️ Seleccionar Ubicación en el Mapa</span>
        </v-card-title>
        
        <v-card-text class="pa-4">
          <v-row>
            <!-- Primera columna: Solo el mapa -->
            <v-col cols="12" md="8" class="pa-0">
              <div class="map-container">
                <!-- Contenedor del mapa -->
                <div id="map-selector" class="map-wrapper-full"></div>
              </div>
            </v-col>
            
            <!-- Segunda columna: Controles y búsqueda -->
            <v-col cols="12" md="4" class="pa-0 pl-md-4">
              <div class="map-controls">
                                                  <!-- Campo de búsqueda -->
                 <div class="mb-0">
                   <div class="d-flex gap-2">
                     <v-text-field
                       id="map-search"
                       v-model="searchPlace"
                       label="Buscar lugar (ej: Universidad Estatal de Milagro)"
                       variant="outlined"
                       color="blue-400"
                       clearable
                       @keyup.enter="onSearchInput"
                       hide-details
                       density="compact"
                       class="flex-grow-1"
                     ></v-text-field>
                     
                     <!-- Botón de búsqueda compacto -->
                     <v-btn 
                       color="blue-400" 
                       variant="tonal" 
                       @click="onSearchInput"
                       icon="mdi-magnify"
                       size="large"
                       class="search-btn"
                     ></v-btn>
                   </div>
                 </div>
                 
                                  <!-- Control del radio -->
                 <div class="mb-2">
                   <div class="d-flex align-center gap-3 mb-2">
                     <label class="radius-label text-white mb-0">Radio del Área (metros)</label>
                     
                     <!-- Valor del radio al lado del label -->
                     <v-chip color="info" variant="tonal" size="small" class="radius-chip text-center">
                       {{ mapRadius }}m
                     </v-chip>
                   </div>
                   
                   <div class="d-flex gap-4">
                      <!-- Columna izquierda: Barra deslizadora y chip -->
                      <div class="d-flex flex-column gap-3">
                        <!-- Barra deslizadora arriba -->
                        <v-slider
                          v-model="mapRadius"
                          :min="10"
                          :max="500"
                          :step="10"
                          color="info"
                          thumb-color="info"
                          track-color="info-lighten-3"
                          thumb-label="always"
                          prepend-icon="mdi-radius"
                          class="radius-slider-compact custom-slider"
                          hide-details
                        ></v-slider>
                        
                        <!-- Chip de ubicación seleccionada abajo -->
                        <v-chip v-if="selectedLocation" color="blue-400" variant="tonal" size="small" class="location-chip">
                          <v-icon left>mdi-map-marker</v-icon>
                          Ubicación seleccionada
                        </v-chip>
                      </div>
                      
                      <!-- Columna derecha: Botón y mensaje -->
                      <div v-if="selectedLocation" class="d-flex flex-column align-center justify-center text-center">
                        <v-btn
                          size="x-small"
                          color="green-400"
                          variant="outlined"
                          icon="mdi-crosshairs-gps"
                          @click="useCurrentLocation"
                          :loading="isLocating"
                          :disabled="isLocating"
                          class="use-current-location-btn"
                          title="Usar ubicación actual"
                        ></v-btn>
                        
                        <!-- Mensaje informativo en líneas separadas -->
                        <div class="mt-2 text-center">
                          <p class="text-caption text-grey-400 text-center mb-1">
                            Cambia la ubicación
                          </p>
                          <p class="text-caption text-grey-400 text-center mb-1">
                            seleccionada por tu
                          </p>
                          <p class="text-caption text-grey-400 text-center mb-0">
                            ubicación GPS actual
                          </p>
                        </div>
                      </div>
                    </div>
                 </div>
                 
                                   <!-- Chips de estado -->
                  <div class="mb-2">
                    <div class="d-flex flex-column gap-2">
                      <v-chip v-if="isLocating" color="orange-400" variant="tonal" size="small">
                        <v-icon left>mdi-crosshairs-gps</v-icon>
                        Obteniendo ubicación...
                      </v-chip>
                      <v-chip v-if="userLocation" color="green-400" variant="tonal" size="small">
                        <v-icon left>mdi-crosshairs-gps</v-icon>
                        Ubicación actual
                      </v-chip>
                    </div>
                  </div>
                  

                
                <!-- Instrucciones -->
                <div class="mb-4">
                  <v-alert type="info" variant="tonal" density="compact">
                    <template v-slot:prepend>
                      <v-icon>mdi-information</v-icon>
                    </template>
                    <strong>Instrucciones:</strong> 
                    <br>• Escribe el nombre del lugar y presiona ENTER
                    <br>• Haz clic en el mapa para marcar la ubicación
                    <br>• Ajusta el radio con el control deslizante
                    <br>• Las coordenadas se llenarán automáticamente
                  </v-alert>
                </div>
                
                <!-- Mensaje sobre mapa -->
                <div v-if="!googleMapsAvailable" class="mb-4">
                  <v-alert type="warning" variant="tonal" density="compact">
                    <template v-slot:prepend>
                      <v-icon>mdi-alert</v-icon>
                    </template>
                    <strong>⚠️ Mapa no está disponible</strong>
                    <br>Verifica tu conexión a internet para cargar OpenStreetMap
                  </v-alert>
                </div>
                
                <!-- Botones de acción -->
                <div class="mt-4 action-buttons">
                  <v-row class="flex-grow-1">
                    <v-col cols="6">
                      <v-btn 
                        color="grey-400" 
                        variant="tonal" 
                        @click="cancelMapSelection"
                      >
                        Cancelar
                      </v-btn>
                    </v-col>
                    <v-col cols="6">
                      <v-btn 
                        color="blue-400" 
                        @click="confirmMapSelection" 
                        :disabled="!selectedLocation"
                        class="neon-border"
                      >
                        Confirmar Ubicación
                      </v-btn>
                    </v-col>
                  </v-row>
                </div>
              </div>
            </v-col>
          </v-row>
                 </v-card-text>
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



  </div>
</template>

<script>
 import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import areaService from '../services/areaService'
import useOptimizedMap from '../composables/useOptimizedMap'
import { useNotifications } from '../composables/useNotifications'

export default {
  name: 'Areas',
  setup() {
    const { showSuccess, showError, showWarning, showInfo, showLocationStatus } = useNotifications()
    
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
      // Usar el sistema global de notificaciones en lugar del mensaje local
      switch (type) {
        case 'success':
          showSuccess(text)
          break
        case 'error':
          showError(text)
          break
        case 'warning':
          showWarning(text)
          break
        case 'info':
        default:
          showInfo(text)
          break
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
     const mapRadius = ref(10)
     const userLocation = ref(null)
     const isLocating = ref(false)
     const searchPlace = ref('')
     const googleMapsAvailable = ref(true) // Siempre true con el servicio optimizado
    
    const areas = ref([])
    
    // ✅ Key dinámica para forzar re-render de la tabla
    const tableKey = ref(Date.now())
    
    // Polling automático interno para mantener la lista actualizada
    const pollingInterval = ref(null)
    const POLLING_INTERVAL_MS = 30000 // 30 segundos
    
         // Estado para mensajes
     const mensaje = ref({
       show: false,
       text: '',
       type: 'success'
     })
     
     // Estado para errores del formulario
     const formErrors = ref({
       name: '',
       description: '',
       latitude: '',
       longitude: '',
       radius: '',
       grace_period: ''
     })
     
     // Estado para el hint de descripción
     const showDescriptionHint = ref(false)
     const descriptionHint = ref('Solo se permiten letras y números')
     
     // Estado para el hint del nombre
     const showNameHint = ref(false)
     const nameHint = ref('Se permiten letras, números, espacios, guiones (-) y guiones bajos (_)')
    
    const areaForm = ref({
      name: '',
      description: '',
      latitude: '',
      longitude: '',
      radius: 200,
      status: 'active'  // CRÍTICO: Incluir status por defecto
    })
    
    // Variables para el sistema de horarios
    const scheduleType = ref('default') // 'default', 'custom', 'none'
    const schedule = ref({
      // ✅ NO inicializar con datos estáticos - usar valores mínimos
      monday_active: false,
      monday_start: null,
      monday_end: null,
      
      tuesday_active: false,
      tuesday_start: null,
      tuesday_end: null,
      
      wednesday_active: false,
      wednesday_start: null,
      wednesday_end: null,
      
      thursday_active: false,
      thursday_start: null,
      thursday_end: null,
      
      friday_active: false,
      friday_start: null,
      friday_end: null,
      
      saturday_active: false,
      saturday_start: null,
      saturday_end: null,
      
      sunday_active: false,
      sunday_start: null,
      sunday_end: null,
      
      // Tolerancia para llegadas tarde
      grace_period_minutes: 0
    })
    
    // Días de la semana para el formulario
    const scheduleDays = [
      { key: 'monday', label: 'Lunes' },
      { key: 'tuesday', label: 'Martes' },
      { key: 'wednesday', label: 'Miércoles' },
      { key: 'thursday', label: 'Jueves' },
      { key: 'friday', label: 'Viernes' },
      { key: 'saturday', label: 'Sábado' },
      { key: 'sunday', label: 'Domingo' }
    ]
    
    const headers = [
      { title: 'Nombre', key: 'name', sortable: true },
      { title: 'Descripción', key: 'description', sortable: true },
      { title: 'Empleados', key: 'employee_count', sortable: true },
      { title: 'Horarios', key: 'schedule_info', sortable: false, width: '150px' },
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
         
         console.log('📥 Datos crudos del backend:', areasData)
         console.log('📋 Array de áreas del backend:', areasArray)
         
         // Verificar si las áreas tienen schedule
         areasArray.forEach((area, index) => {
           console.log(`🔍 Área ${index + 1} (${area.name}):`, {
             id: area.id,
             name: area.name,
             hasSchedule: !!area.schedule,
             schedule: area.schedule,
             scheduleKeys: area.schedule ? Object.keys(area.schedule) : 'No schedule'
           })
         })
         
         // ✅ FILTRAR SOLO ÁREAS ACTIVAS para la lista principal
         const activeAreas = areasArray.filter(area => area.status === 'active')
         
         const areasWithCounts = activeAreas.map(area => ({
           ...area,
           employee_count: area.employee_count || 0,
           schedule: area.schedule || null  // ✅ Preservar el campo schedule
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
     
     // Función de polling automático interno
     const startPolling = () => {
       if (pollingInterval.value) {
         clearInterval(pollingInterval.value)
       }
       
       pollingInterval.value = setInterval(async () => {
         if (!loading.value) {
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
          
          // Cargar horarios del área
          loadScheduleFromArea(fullArea)
          
          // Sincronizar radio del mapa
          mapRadius.value = fullArea.radius || 100
          
          // Guardar las coordenadas para usar en el mapa
          editingArea.value.savedCoordinates = {
            lat: parseFloat(fullArea.latitude),
            lng: parseFloat(fullArea.longitude)
          }
          
          console.log('📋 Formulario cargado con:', areaForm.value)
          console.log('🕐 Horarios cargados:', schedule.value)
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
       // Verificar si el área tiene empleados antes de permitir desactivarla
       if (area.employee_count > 0) {
         showMessage(`No se puede desactivar el área "${area.name}" porque tiene ${area.employee_count} empleado(s) asignado(s). Primero debes reasignar o desactivar los empleados.`, 'warning')
         return
       }
       
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
    
    // Funciones para el sistema de horarios
    const getScheduleSummary = () => {
      if (scheduleType.value === 'default') {
        return 'Horario estándar: Lunes a Viernes de 8:00 AM a 5:00 PM con 15 minutos de tolerancia'
      } else if (scheduleType.value === 'custom') {
        const activeDays = scheduleDays.filter(day => schedule.value[`${day.key}_active`])
        if (activeDays.length === 0) return 'No hay días laborables configurados'
        
        const dayNames = activeDays.map(day => day.label).join(', ')
        const tolerance = schedule.value.grace_period_minutes
        return `${dayNames} - Tolerancia: ${tolerance} minutos`
      }
      return ''
    }
    
    const createDefaultSchedule = () => {
      // ✅ Crear horario por defecto válido y consistente con el backend
      schedule.value = {
        monday_active: true,
        monday_start: '08:00',
        monday_end: '17:00',
        
        tuesday_active: true,
        tuesday_start: '08:00',
        tuesday_end: '17:00',
        
        wednesday_active: true,
        wednesday_start: '08:00',
        wednesday_end: '17:00',
        
        thursday_active: true,
        thursday_start: '08:00',
        thursday_end: '17:00',
        
        friday_active: true,
        friday_start: '08:00',
        friday_end: '17:00',
        
        saturday_active: false,
        saturday_start: null,
        saturday_end: null,
        
        sunday_active: false,
        sunday_start: null,
        sunday_end: null,
        
        grace_period_minutes: 15
      }
      console.log('✅ createDefaultSchedule: Horario por defecto válido creado')
    }
    
    const loadScheduleFromArea = (area) => {
      console.log('🔍 loadScheduleFromArea llamado con área:', area)
      console.log('🔍 area.schedule:', area.schedule)
      console.log('🔍 area.schedule.schedule_type:', area.schedule?.schedule_type)
      console.log('🔍 area.schedule.monday_active:', area.schedule?.monday_active)
      console.log('🔍 area.schedule.tuesday_active:', area.schedule?.tuesday_active)
      console.log('🔍 area.schedule.wednesday_active:', area.schedule?.wednesday_active)
      console.log('🔍 area.schedule.thursday_active:', area.schedule?.thursday_active)
      console.log('🔍 area.schedule.friday_active:', area.schedule?.friday_active)
      console.log('🔍 area.schedule.saturday_active:', area.schedule?.saturday_active)
      console.log('🔍 area.schedule.sunday_active:', area.schedule?.sunday_active)
      
      if (area.schedule && area.schedule.schedule_type && area.schedule.schedule_type !== 'none') {
        // Si el área ya tiene horario, cargarlo según el tipo del backend
        console.log('✅ Área tiene horario, cargando como', area.schedule.schedule_type)
        
        if (area.schedule.schedule_type === 'default') {
          scheduleType.value = 'default'
          console.log('✅ Horario por defecto detectado en backend')
          
          // 🔍 DEBUG: Verificar valores específicos del lunes
          console.log('🔍 DEBUG - Valores del lunes desde backend (default):')
          console.log('   - monday_start (raw):', area.schedule.monday_start)
          console.log('   - monday_start (type):', typeof area.schedule.monday_start)
          
          // ✅ Cargar EXACTAMENTE los horarios del backend (NO datos estáticos)
          schedule.value = {
            monday_active: area.schedule.monday_active ?? false,
            monday_start: area.schedule.monday_start ?? '08:00',
            monday_end: area.schedule.monday_end ?? '17:00',
            tuesday_active: area.schedule.tuesday_active ?? false,
            tuesday_start: area.schedule.tuesday_start ?? '08:00',
            tuesday_end: area.schedule.tuesday_end ?? '17:00',
            wednesday_active: area.schedule.wednesday_active ?? false,
            wednesday_start: area.schedule.wednesday_start ?? '08:00',
            wednesday_end: area.schedule.wednesday_end ?? '17:00',
            thursday_active: area.schedule.thursday_active ?? false,
            thursday_start: area.schedule.thursday_start ?? '08:00',
            thursday_end: area.schedule.thursday_end ?? '17:00',
            friday_active: area.schedule.friday_active ?? false,
            friday_start: area.schedule.friday_start ?? '08:00',
            friday_end: area.schedule.friday_end ?? '17:00',
            saturday_active: area.schedule.saturday_active ?? false,
            saturday_start: area.schedule.saturday_start ?? null,
            saturday_end: area.schedule.saturday_end ?? null,
            sunday_active: area.schedule.sunday_active ?? false,
            sunday_start: area.schedule.sunday_start ?? null,
            sunday_end: area.schedule.sunday_end ?? null,
            grace_period_minutes: area.schedule.grace_period_minutes ?? 15
          }
        } else if (area.schedule.schedule_type === 'custom') {
          scheduleType.value = 'custom'
          console.log('✅ Horario personalizado detectado en backend')
          
          // Cargar los horarios personalizados EXACTAMENTE como están en el backend
          schedule.value = {
            monday_active: area.schedule.monday_active ?? false,
            monday_start: area.schedule.monday_start ?? '08:00',
            monday_end: area.schedule.monday_end ?? '17:00',
            tuesday_active: area.schedule.tuesday_active ?? false,
            tuesday_start: area.schedule.tuesday_start ?? '08:00',
            tuesday_end: area.schedule.tuesday_end ?? '17:00',
            wednesday_active: area.schedule.wednesday_active ?? false,
            wednesday_start: area.schedule.wednesday_start ?? '08:00',
            wednesday_end: area.schedule.wednesday_end ?? '17:00',
            thursday_active: area.schedule.thursday_active ?? false,
            thursday_start: area.schedule.thursday_start ?? '08:00',
            thursday_end: area.schedule.thursday_end ?? '17:00',
            friday_active: area.schedule.friday_active ?? false,
            friday_start: area.schedule.friday_start ?? '08:00',
            friday_end: area.schedule.friday_end ?? '17:00',
            saturday_active: area.schedule.saturday_active ?? false,
            saturday_start: area.schedule.saturday_start ?? null,
            saturday_end: area.schedule.saturday_end ?? null,
            sunday_active: area.schedule.sunday_active ?? false,
            sunday_start: area.schedule.sunday_start ?? null,
            sunday_end: area.schedule.sunday_end ?? null,
            grace_period_minutes: area.schedule.grace_period_minutes ?? 15
          }
          
          console.log('✅ Horarios personalizados cargados:', schedule.value)
        }
        
        // 🔍 DEBUG: Verificar valores específicos del lunes
        console.log('🔍 DEBUG - Valores del lunes desde backend:')
        console.log('   - monday_start (raw):', area.schedule.monday_start)
        console.log('   - monday_start (type):', typeof area.schedule.monday_start)
        console.log('   - monday_start (final):', schedule.value.monday_start)
        
        console.log('🔍 schedule.value después de cargar:', schedule.value)
        console.log('🔍 scheduleType.value después de cargar:', scheduleType.value)
      } else {
        // Si no tiene horario o schedule_type, usar el por defecto
        console.log('❌ Área no tiene horario o schedule_type, usando por defecto')
        createDefaultSchedule()
        scheduleType.value = 'default'
        console.log('🔍 schedule.value después de crear por defecto:', schedule.value)
        console.log('🔍 scheduleType.value después de crear por defecto:', scheduleType.value)
      }
    }
    
    
    
    // Funciones auxiliares para mostrar información de horarios en la tabla
    const getScheduleColor = (schedule) => {
      if (!schedule) return 'grey-500'
      
      const activeDays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        .filter(day => schedule[`${day}_active`])
      
      if (activeDays.length === 5 && !schedule.saturday_active && !schedule.sunday_active) {
        return 'green-500' // Horario estándar
      } else if (activeDays.length > 0) {
        return 'blue-500' // Horario personalizado
      } else {
        return 'orange-500' // Sin días activos
      }
    }
    
    const getScheduleIcon = (schedule) => {
      if (!schedule) return 'mdi-close-circle'
      
      const activeDays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        .filter(day => schedule[`${day}_active`])
      
      if (activeDays.length === 5 && !schedule.saturday_active && !schedule.sunday_active) {
        return 'mdi-check-circle' // Horario estándar
      } else if (activeDays.length > 0) {
        return 'mdi-cog' // Horario personalizado
      } else {
        return 'mdi-alert-circle' // Sin días activos
      }
    }
    
    const getScheduleText = (schedule) => {
      console.log('🔍 getScheduleText llamado con:', schedule)
      
      if (!schedule) {
        console.log('❌ No hay horario, retornando "Sin horario"')
        return 'Sin horario'
      }
      
      // PRIORIDAD 1: Usar schedule_type del backend si está disponible
      if (schedule.schedule_type) {
        console.log('🎯 Usando schedule_type del backend:', schedule.schedule_type)
        if (schedule.schedule_type === 'default') {
          console.log('✅ Horario estándar detectado por schedule_type')
          return 'Estándar'
        } else if (schedule.schedule_type === 'custom') {
          console.log('🔧 Horario personalizado detectado por schedule_type')
          return 'Personalizado'
        } else if (schedule.schedule_type === 'none') {
          console.log('❌ Sin horario por schedule_type')
          return 'Sin Horario'
        }
      }
      
      // PRIORIDAD 2: Fallback - adivinar basándose en días activos
      console.log('🔄 No hay schedule_type, usando fallback de días activos')
      const activeDays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        .filter(day => schedule[`${day}_active`])
      
      console.log('📅 Días activos encontrados:', activeDays)
      
      if (activeDays.length === 5 && !schedule.saturday_active && !schedule.sunday_active) {
        console.log('✅ Horario estándar detectado por fallback')
        return 'Estándar'
        } else if (activeDays.length > 0) {
        console.log('🔧 Horario personalizado detectado por fallback:', activeDays.length, 'días')
        return 'Personalizado'
      } else {
        console.log('⚠️ Horario vacío detectado por fallback')
        return 'Sin Horario'
      }
    }
    
    const getScheduleTooltip = (schedule) => {
      if (!schedule) return 'Sin horario'
      
      const activeDays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        .filter(day => schedule[`${day}_active`])
      
      if (activeDays.length === 0) {
        return 'No hay días laborables configurados'
      }
      
      const dayNames = {
        monday: 'Lun',
        tuesday: 'Mar',
        wednesday: 'Mié',
        thursday: 'Jue',
        friday: 'Vie',
        saturday: 'Sáb',
        sunday: 'Dom'
      }
      
      const activeDayNames = activeDays.map(day => dayNames[day]).join(', ')
      const tolerance = schedule.grace_period_minutes || 0
      
      return `${activeDayNames} - Tolerancia: ${tolerance} min`
    }

    // Función para formatear la descripción en múltiples líneas
    const formatDescription = (description) => {
      if (!description) return ['']
      
      // Limitar a máximo 30 caracteres
      const maxTotalLength = 30
      const maxLineLength = 15
      
      // Truncar si excede los 30 caracteres
      let truncatedDescription = description
      if (description.length > maxTotalLength) {
        truncatedDescription = description.substring(0, maxTotalLength) + '...'
      }
      
      const words = truncatedDescription.split(' ')
      const lines = []
      let currentLine = ''
      
      for (const word of words) {
        // Si la palabra es más larga que el límite de línea, dividirla
        if (word.length > maxLineLength) {
          if (currentLine) {
            lines.push(currentLine.trim())
            currentLine = ''
          }
          
          // Dividir la palabra larga en partes de maxLineLength
          for (let i = 0; i < word.length; i += maxLineLength) {
            lines.push(word.substring(i, i + maxLineLength))
          }
        } else {
          // Si agregar esta palabra excede el límite de línea, crear nueva línea
          if ((currentLine + ' ' + word).length > maxLineLength) {
            if (currentLine) {
              lines.push(currentLine.trim())
              currentLine = word
            } else {
              currentLine = word
            }
          } else {
            currentLine = currentLine ? currentLine + ' ' + word : word
          }
        }
      }
      
      // Agregar la última línea si hay contenido
      if (currentLine) {
        lines.push(currentLine.trim())
      }
      
      return lines.length > 0 ? lines : ['']
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
     
     // Funciones de validación del formulario
     const validateField = (fieldName) => {
       const value = areaForm.value[fieldName]
       let error = ''
       
       switch (fieldName) {
                   case 'name':
            if (!value) {
              error = 'Nombre es requerido'
            } else if (value.length < 3) {
              error = 'El nombre debe tener al menos 3 caracteres'
            } else if (value.length > 100) {
              error = 'El nombre no puede exceder 100 caracteres'
            } else if (!/^[a-zA-Z0-9\s_-]+$/.test(value)) {
              error = 'Se permiten letras, números, espacios, guiones (-) y guiones bajos (_)'
            }
            break
           
                   case 'description':
            if (!value) {
              error = 'Descripción es requerida'
            } else if (value.length < 3) {
              error = 'La descripción debe tener al menos 3 caracteres'
            } else if (value.length > 500) {
              error = 'La descripción no puede exceder 500 caracteres'
            } else if (!/^[a-zA-Z0-9\s]+$/.test(value)) {
              error = 'Solo se permiten letras y números'
            }
            break
           
         case 'latitude':
           if (!value) {
             error = 'Selecciona ubicación en el mapa'
           }
           break
           
         case 'longitude':
           if (!value) {
             error = 'Selecciona ubicación en el mapa'
           }
           break
           
         case 'radius':
           if (!value || value < 10) {
             error = 'Radio mínimo: 10 metros'
           }
           break
           
         case 'grace_period':
           if (scheduleType.value !== 'none') {
             const gracePeriod = schedule.value.grace_period_minutes
             if (!gracePeriod && gracePeriod !== 0) {
               error = 'Tolerancia requerida'
             } else if (gracePeriod < 0) {
               error = 'Mínimo 0 minutos'
             } else if (gracePeriod > 120) {
               error = 'Máximo 120 minutos'
             }
           }
           break
       }
       
       formErrors.value[fieldName] = error
       return !error
     }
     
     const validateScheduleField = (fieldName) => {
       const [day, type] = fieldName.split('_')
       const startTime = schedule.value[`${day}_start`]
       const endTime = schedule.value[`${day}_end`]
       
       if (schedule.value[`${day}_active`]) {
         if (type === 'start' && startTime && endTime && startTime >= endTime) {
           return false
         }
         if (type === 'end' && startTime && endTime && startTime >= endTime) {
           return false
         }
       }
       
       return true
     }
     
     const getScheduleFieldError = (fieldName) => {
       const [day, type] = fieldName.split('_')
       const startTime = schedule.value[`${day}_start`]
       const endTime = schedule.value[`${day}_end`]
       
       if (schedule.value[`${day}_active`]) {
         if (startTime && endTime && startTime >= endTime) {
           return 'La hora de entrada debe ser anterior a la de salida'
         }
       }
       
       return ''
     }
     
     const validateAllFields = () => {
       const fields = ['name', 'description', 'latitude', 'longitude', 'radius']
       let isValid = true
       
       // Validar campos básicos
       fields.forEach(field => {
         if (!validateField(field)) {
           isValid = false
         }
       })
       
       // Validar horarios si es necesario
       if (scheduleType.value !== 'none') {
         if (!validateField('grace_period')) {
           isValid = false
         }
         
         // Validar que al menos un día esté activo
         const activeDays = scheduleDays.filter(day => schedule.value[`${day.key}_active`])
         if (activeDays.length === 0) {
           isValid = false
         }
         
         // Validar horarios de días activos
         activeDays.forEach(day => {
           const startTime = schedule.value[`${day.key}_start`]
           const endTime = schedule.value[`${day.key}_end`]
           
           if (!startTime || !endTime) {
             isValid = false
           } else if (startTime >= endTime) {
             isValid = false
           }
         })
       }
       
       return isValid
     }
     
           const validateScheduleDay = (dayKey) => {
        // Validar que si se activa un día, tenga horarios válidos
        if (schedule.value[`${dayKey}_active`]) {
          const startTime = schedule.value[`${dayKey}_start`]
          const endTime = schedule.value[`${dayKey}_end`]
          
          if (!startTime || !endTime) {
            showMessage(`⚠️ El día ${scheduleDays.find(d => d.key === dayKey)?.label} está activo pero no tiene horarios configurados`, 'warning')
          }
        }
      }
      
      // Función para sanitizar el nombre del área (solo caracteres permitidos)
      const sanitizeName = (event) => {
        const input = event.target
        const value = input.value
        
        // Mostrar el hint cuando el usuario empiece a escribir
        if (!showNameHint.value && value.length > 0) {
          showNameHint.value = true
        }
        
        // Remover caracteres no permitidos (letras, números, espacios, guiones y guiones bajos)
        const sanitized = value.replace(/[^a-zA-Z0-9\s_-]/g, '')
        
        // Si el valor cambió, actualizar el campo
        if (sanitized !== value) {
          areaForm.value.name = sanitized
          // Mover el cursor al final del texto
          nextTick(() => {
            input.setSelectionRange(sanitized.length, sanitized.length)
          })
        }
      }
      
      // Función para sanitizar la descripción (solo letras y números)
      const sanitizeDescription = (event) => {
        const input = event.target
        const value = input.value
        
        // Mostrar el hint cuando el usuario empiece a escribir
        if (!showDescriptionHint.value && value.length > 0) {
          showDescriptionHint.value = true
        }
        
        // Remover caracteres no permitidos (solo letras, números y espacios)
        const sanitized = value.replace(/[^a-zA-Z0-9\s]/g, '')
        
        // Si el valor cambió, actualizar el campo
        if (sanitized !== value) {
          areaForm.value.description = sanitized
          // Mover el cursor al final del texto
          nextTick(() => {
            input.setSelectionRange(sanitized.length, sanitized.length)
          })
        }
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
       mapRadius.value = 10
       clearMap()
       
                // Resetear horarios
         createDefaultSchedule()
       
                // Limpiar errores del formulario
         Object.keys(formErrors.value).forEach(key => {
           formErrors.value[key] = ''
         })
         
         // Ocultar hints
         showDescriptionHint.value = false
         showNameHint.value = false
       
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
    
    // Observar cambios en el tipo de horario
    watch(scheduleType, (newType, oldType) => {
      console.log(`🔄 Cambio de tipo de horario: ${oldType} → ${newType}`)
      
      if (newType === 'default') {
        // ✅ Crear horario por defecto válido
        createDefaultSchedule()
        console.log('✅ Horario por defecto aplicado')
      } else if (newType === 'custom') {
        // ✅ Mantener horarios actuales pero asegurar que sean válidos
        if (oldType === 'default') {
          // Si venía de default, mantener los valores pero permitir edición
          console.log('✅ Cambiando de default a custom - horarios mantenidos')
        } else if (oldType === 'none') {
          // Si venía de none, crear horario por defecto como base
          createDefaultSchedule()
          console.log('✅ Cambiando de none a custom - horario por defecto como base')
        }
      } else if (newType === 'none') {
        // ✅ Limpiar horarios para "sin horario"
        schedule.value = {
          monday_active: false,
          monday_start: '08:00',
          monday_end: '17:00',
          tuesday_active: false,
          tuesday_start: '08:00',
          tuesday_end: '17:00',
          wednesday_active: false,
          wednesday_start: '08:00',
          wednesday_end: '17:00',
          thursday_active: false,
          thursday_start: '08:00',
          thursday_end: '17:00',
          friday_active: false,
          friday_start: '08:00',
          friday_end: '17:00',
          saturday_active: false,
          saturday_start: '08:00',
          saturday_end: '17:00',
          sunday_active: false,
          sunday_start: '08:00',
          sunday_end: '17:00',
          grace_period_minutes: 0
        }
        console.log('✅ Horarios limpiados para "sin horario"')
      }
    })
    
                 const showMapSelectorModal = async () => {
      console.log('🗺️ Abriendo modal del mapa optimizado...')
      console.log('🔔 Estado inicial de isLocating:', isLocating.value)
      
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
          
          // Mostrar notificación de búsqueda ANTES de obtener la ubicación
          console.log('📍 Mostrando notificación de búsqueda de ubicación...')
          const notificationId = showLocationStatus('getting')
          console.log('🔔 ID de notificación de búsqueda:', notificationId)
          
          // Pequeña pausa para asegurar que la notificación se muestre
          await new Promise(resolve => setTimeout(resolve, 500))
          
          // Intentar obtener ubicación actual con radio
          try {
            isLocating.value = true
            
            await getCurrentLocation({
              radius: mapRadius.value,
              title: 'Tu ubicación actual'
            })
            
            // Esperar a que el mapa se actualice y el punto sea visible
            console.log('📍 Esperando a que el punto aparezca en el mapa...')
            await new Promise(resolve => setTimeout(resolve, 1500))
            
            // Verificar que realmente se haya establecido la ubicación en el mapa
            if (selectedLocation.value) {
              console.log('📍 Ubicación establecida en el mapa:', selectedLocation.value)
              
              // Mostrar notificación de éxito solo después de que el punto esté visible
              console.log('📍 Mostrando notificación de éxito de ubicación...')
              const successId = showLocationStatus('success')
              console.log('🔔 ID de notificación de éxito:', successId)
              
              // Pausa para que se vea la notificación de éxito
              await new Promise(resolve => setTimeout(resolve, 4000))
            } else {
              console.log('⚠️ No se pudo establecer la ubicación en el mapa')
            }
            
          } catch (error) {
            console.log('📍 Usando ubicación por defecto (Ciudad de México)')
            // La ubicación por defecto ya está configurada en el servicio
            // Asegurar que se muestre el radio en la ubicación por defecto
            if (selectedLocation.value) {
              setRadius(selectedLocation.value.lat, selectedLocation.value.lng, mapRadius.value)
            }
            // Mostrar notificación de error
            console.log('📍 Mostrando notificación de error de ubicación...')
            const errorId = showLocationStatus('error')
            console.log('🔔 ID de notificación de error:', errorId)
          } finally {
            isLocating.value = false
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
        
        // Validar automáticamente los campos después de establecer los valores
        validateField('latitude')
        validateField('longitude')
        validateField('radius')
        
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
        areaForm.value.radius = 10
        mapRadius.value = 10
        
        // Validar automáticamente los campos después de limpiarlos
        validateField('latitude')
        validateField('longitude')
        validateField('radius')
      }
      
      console.log('❌ Selección de mapa cancelada')
    }
    
         // Función para usar la ubicación actual del usuario
     const useCurrentLocation = async () => {
       try {
         console.log('📍 Cambiando a ubicación actual del usuario...')
         
         // Mostrar notificación de búsqueda ANTES de obtener la ubicación
         console.log('📍 Mostrando notificación de búsqueda de ubicación...')
         showLocationStatus('getting')
         
         // Pequeña pausa para asegurar que la notificación se muestre
         await new Promise(resolve => setTimeout(resolve, 100))
         
         isLocating.value = true
         
         // Obtener ubicación actual del usuario
         await getCurrentLocation({
           radius: mapRadius.value,
           title: 'Tu ubicación actual'
         })
         
         // Si se obtuvo la ubicación exitosamente, actualizar el formulario
         if (selectedLocation.value) {
           areaForm.value.latitude = selectedLocation.value.lat
           areaForm.value.longitude = selectedLocation.value.lng
           areaForm.value.radius = mapRadius.value
           
           // Validar automáticamente los campos después de establecer los valores
           validateField('latitude')
           validateField('longitude')
           validateField('radius')
           
           // Actualizar también el radio del mapa si es necesario
           if (mapRadius.value !== selectedLocation.value.radius) {
             mapRadius.value = selectedLocation.value.radius || mapRadius.value
           }
           
           console.log('✅ Ubicación actual aplicada:', selectedLocation.value)
           console.log('📋 Formulario actualizado con ubicación actual')
           console.log('📏 Radio actualizado:', mapRadius.value)
           
           // Si estamos editando, actualizar también las coordenadas de referencia
           if (editingArea.value) {
             editingArea.value.savedCoordinates = {
               lat: selectedLocation.value.lat,
               lng: selectedLocation.value.lng
             }
             console.log('🔄 Coordenadas de referencia actualizadas con ubicación actual')
           }
           
           // Esperar a que el mapa se actualice y el punto sea visible
           console.log('📍 Esperando a que el punto aparezca en el mapa...')
           await new Promise(resolve => setTimeout(resolve, 1500))
           
           // Verificar que realmente se haya establecido la ubicación en el mapa
           if (selectedLocation.value) {
             console.log('📍 Ubicación establecida en el mapa:', selectedLocation.value)
             
             // Mostrar mensaje de éxito usando el sistema global
             console.log('📍 Mostrando notificación de éxito de ubicación...')
             showLocationStatus('success')
             
             // Pausa para que se vea la notificación de éxito
             await new Promise(resolve => setTimeout(resolve, 4000))
           } else {
             console.log('⚠️ No se pudo establecer la ubicación en el mapa')
           }
         }
         
       } catch (error) {
         console.error('❌ Error obteniendo ubicación actual:', error)
         console.log('📍 Mostrando notificación de error de ubicación...')
         showLocationStatus('error')
       } finally {
         isLocating.value = false
       }
     }
    
    // ✅ Función para validar horarios antes de guardar
    const validateSchedule = () => {
      console.log('🔍 Validando horarios...')
      console.log('🔍 scheduleType.value:', scheduleType.value)
      console.log('🔍 schedule.value:', schedule.value)
      
      if (scheduleType.value === 'none') {
        console.log('✅ Tipo "none" - no requiere validación de horarios')
        return true
      }
      
      if (scheduleType.value === 'default') {
        // Para horario por defecto, verificar que los días activos tengan horarios válidos
        const days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
        for (const day of days) {
          if (schedule.value[`${day}_active`]) {
            const start = schedule.value[`${day}_start`]
            const end = schedule.value[`${day}_end`]
            
            if (!start || !end) {
              console.error(`❌ Día ${day} activo pero sin horarios completos`)
              showMessage(`⚠️ El día ${day} está activo pero le faltan horarios de inicio o fin`, 'warning')
              return false
            }
            
            if (start >= end) {
              console.error(`❌ Día ${day}: hora inicio >= hora fin`)
              showMessage(`⚠️ El día ${day} tiene hora de inicio mayor o igual a la hora de fin`, 'warning')
              return false
            }
          }
        }
        console.log('✅ Horario por defecto válido')
        return true
      }
      
      if (scheduleType.value === 'custom') {
        // Para horario personalizado, verificar que al menos un día esté activo
        const hasActiveDay = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
          .some(day => schedule.value[`${day}_active`])
        
        if (!hasActiveDay) {
          console.error('❌ Horario personalizado sin días activos')
          showMessage('⚠️ Debes activar al menos un día para el horario personalizado', 'warning')
          return false
        }
        
        // Verificar que los días activos tengan horarios válidos
        const days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for (const day of days) {
          if (schedule.value[`${day}_active`]) {
            const start = schedule.value[`${day}_start`]
            const end = schedule.value[`${day}_end`]
            
            if (!start || !end) {
              console.error(`❌ Día ${day} activo pero sin horarios completos`)
              showMessage(`⚠️ El día ${day} está activo pero le faltan horarios de inicio o fin`, 'warning')
              return false
            }
            
            if (start >= end) {
              console.error(`❌ Día ${day}: hora inicio >= hora fin`)
              showMessage(`⚠️ El día ${day} tiene hora de inicio mayor o igual a la hora de fin`, 'warning')
              return false
            }
          }
        }
        
        console.log('✅ Horario personalizado válido')
        return true
      }
      
      console.error('❌ Tipo de horario no reconocido:', scheduleType.value)
      return false
    }
    
    // ✅ Función para forzar actualización de la interfaz
    const forceUIUpdate = () => {
      console.log('🔄 Forzando actualización de la interfaz...')
      
      // ✅ Forzar re-render completo del componente
      areas.value = [...areas.value]
      
      // ✅ Forzar re-render de la tabla agregando un key único
      tableKey.value = Date.now()
      
      // ✅ Forzar re-evaluación de computed properties
      nextTick(() => {
        console.log('✅ Interfaz actualizada con re-render completo')
        console.log('🔍 Verificando que la tabla se haya actualizado...')
        
        // Verificar que el área editada tenga el schedule_type correcto
        const editedArea = areas.value.find(area => area.id === editingArea.value?.id)
        if (editedArea && editedArea.schedule) {
          console.log(`✅ Área ${editedArea.name}: schedule_type = ${editedArea.schedule.schedule_type}`)
        }
      })
    }
    
    // ✅ Función para actualizar correctamente la lista local
    const updateLocalArea = (updatedAreaData) => {
      console.log('🔄 Actualizando área en lista local...')
      
      const areaIndex = areas.value.findIndex(area => area.id === updatedAreaData.id)
      if (areaIndex !== -1) {
        // ✅ Actualizar con los datos frescos del backend
        areas.value[areaIndex] = { ...updatedAreaData }
        console.log('✅ Área actualizada en la lista local')
        
        // ✅ Forzar re-render de la tabla
        tableKey.value = Date.now()
        
        // ✅ Verificar que se actualizó correctamente
        const updatedArea = areas.value[areaIndex]
        if (updatedArea.schedule) {
          console.log(`✅ Verificación: ${updatedArea.name} ahora tiene schedule_type = ${updatedArea.schedule.schedule_type}`)
        }
      } else {
        console.warn('⚠️ Área no encontrada en lista local para actualizar')
      }
    }
    
    const saveArea = async () => {
      console.log('🚀 === INICIO DE SAVEAREA ===')
      console.log('🔍 Iniciando saveArea...')
      console.log('📝 Datos del formulario:', areaForm.value)
      console.log('🔍 scheduleType.value:', scheduleType.value)
      console.log('🔍 schedule.value:', schedule.value)
      console.log('🔍 Estado actual del formulario de horarios')
      
      try {
        // Validar todos los campos antes de proceder
        if (!validateAllFields()) {
          console.error('❌ Validación del formulario falló')
          showMessage('⚠️ Por favor, completa todos los campos obligatorios correctamente', 'warning')
          return
        }
        
        console.log('✅ Validación del formulario pasó')
        
        console.log('🔍 Antes de validación de Vuetify...')
        console.log('🔍 form.value:', form.value)
        console.log('🔍 form.value.validate:', form.value?.validate)
        
        // Validación adicional del formulario de Vuetify
        if (!form.value.validate()) {
          console.error('❌ Validación del formulario de Vuetify falló')
          return
        }
        
        console.log('✅ Validación de Vuetify pasó')
        
        // ✅ Validar horarios antes de continuar
        if (!validateSchedule()) {
          console.error('❌ Validación de horarios falló')
          return
        }
        
        console.log('✅ Validación de horarios pasó')
        
        console.log('🔍 Antes de validación de ubicación...')
        console.log('🔍 areaForm.value.latitude:', areaForm.value.latitude)
        console.log('🔍 areaForm.value.longitude:', areaForm.value.longitude)
        
        // VALIDACIÓN CRÍTICA: Verificar que se haya seleccionado una ubicación
        if (!areaForm.value.latitude || !areaForm.value.longitude) {
          console.error('❌ No se ha seleccionado ubicación en el mapa')
          alert('⚠️ Debes seleccionar una ubicación en el mapa antes de guardar el área.')
          return
        }
        
        console.log('✅ Validación de ubicación pasó')
        
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
        
        // Preparar datos del área con horarios
        const areaData = { ...areaForm.value }
        
        // Agregar horarios según el tipo seleccionado
        if (scheduleType.value === 'default') {
          // ✅ Horario por defecto - usar valores del formulario validados
          areaData.schedule = {
            schedule_type: 'default',
            monday_active: schedule.value.monday_active,
            monday_start: schedule.value.monday_start,
            monday_end: schedule.value.monday_end,
            tuesday_active: schedule.value.tuesday_active,
            tuesday_start: schedule.value.tuesday_start,
            tuesday_end: schedule.value.tuesday_end,
            wednesday_active: schedule.value.wednesday_active,
            wednesday_start: schedule.value.wednesday_start,
            wednesday_end: schedule.value.wednesday_end,
            thursday_active: schedule.value.thursday_active,
            thursday_start: schedule.value.thursday_start,
            thursday_end: schedule.value.thursday_end,
            friday_active: schedule.value.friday_active,
            friday_start: schedule.value.friday_start,
            friday_end: schedule.value.friday_end,
            saturday_active: schedule.value.saturday_active,
            saturday_start: schedule.value.saturday_start,
            saturday_end: schedule.value.saturday_end,
            sunday_active: schedule.value.sunday_active,
            sunday_start: schedule.value.sunday_start,
            sunday_end: schedule.value.sunday_end,
            grace_period_minutes: schedule.value.grace_period_minutes
          }
          console.log('✅ Horario por defecto configurado desde formulario:', areaData.schedule)
        } else if (scheduleType.value === 'custom') {
          // ✅ Horario personalizado - incluir todos los campos
          areaData.schedule = {
            schedule_type: 'custom',
            monday_active: schedule.value.monday_active,
            monday_start: schedule.value.monday_start,
            monday_end: schedule.value.monday_end,
            tuesday_active: schedule.value.tuesday_active,
            tuesday_start: schedule.value.tuesday_start,
            tuesday_end: schedule.value.tuesday_end,
            wednesday_active: schedule.value.wednesday_active,
            wednesday_start: schedule.value.wednesday_start,
            wednesday_end: schedule.value.wednesday_end,
            thursday_active: schedule.value.thursday_active,
            thursday_start: schedule.value.thursday_start,
            thursday_end: schedule.value.thursday_end,
            friday_active: schedule.value.friday_active,
            friday_start: schedule.value.friday_start,
            friday_end: schedule.value.friday_end,
            saturday_active: schedule.value.saturday_active,
            saturday_start: schedule.value.saturday_start,
            saturday_end: schedule.value.saturday_end,
            sunday_active: schedule.value.sunday_active,
            sunday_start: schedule.value.sunday_start,
            sunday_end: schedule.value.sunday_end,
            grace_period_minutes: schedule.value.grace_period_minutes
          }
          console.log('✅ Horario personalizado configurado:', areaData.schedule)
        } else {
          // ✅ Sin horario
          areaData.schedule = {
            schedule_type: 'none'
          }
          console.log('✅ Sin horario configurado')
        }
        
        console.log('📤 Datos del área con horarios:', areaData)
        console.log('🔍 Campo schedule en areaData:', areaData.schedule)
        console.log('🔍 Tipo de schedule:', typeof areaData.schedule)
        console.log('🔍 scheduleType.value:', scheduleType.value)
        console.log('🔍 schedule.value:', schedule.value)
        console.log('🔍 schedule.value.monday_active:', schedule.value?.monday_active)
        console.log('🔍 schedule.value.tuesday_active:', schedule.value?.tuesday_active)
        console.log('🔍 schedule.value.wednesday_active:', schedule.value?.wednesday_active)
        console.log('🔍 schedule.value.thursday_active:', schedule.value?.thursday_active)
        console.log('🔍 schedule.value.friday_active:', schedule.value?.friday_active)
        console.log('🔍 schedule.value.saturday_active:', schedule.value?.saturday_active)
        console.log('🔍 schedule.value.sunday_active:', schedule.value?.sunday_active)
        
        // ✅ LOGS ESPECÍFICOS PARA VERIFICAR VALORES DE TIEMPO
        console.log('🔍 🔍 🔍 VERIFICACIÓN ESPECÍFICA DE TIEMPOS:')
        console.log('  - monday_start (schedule.value):', schedule.value?.monday_start)
        console.log('  - monday_start (areaData.schedule):', areaData.schedule?.monday_start)
        console.log('  - monday_end (schedule.value):', schedule.value?.monday_end)
        console.log('  - monday_end (areaData.schedule):', areaData.schedule?.monday_end)
        console.log('  - tuesday_start (schedule.value):', schedule.value?.tuesday_start)
        console.log('  - tuesday_start (areaData.schedule):', areaData.schedule?.tuesday_start)
        
        if (editingArea.value) {
          console.log('🔄 === ACTUALIZANDO ÁREA EXISTENTE ===')
          console.log('🔍 ID del área a editar:', editingArea.value.id)
          console.log('🔍 Datos del formulario actual:', areaForm.value)
          console.log('🔍 Schedule actual:', schedule.value)
          console.log('🔍 ScheduleType actual:', scheduleType.value)
          
          // Actualizar área existente
          const updatedArea = await areaService.update(editingArea.value.id, areaData)
          console.log('📥 Respuesta del backend (update):', updatedArea)
          console.log('🔍 Campo schedule en respuesta (update):', updatedArea.schedule)
          console.log('🔍 Campo has_schedule en respuesta (update):', updatedArea.has_schedule)
          console.log('🔍 Campo schedule_id en respuesta (update):', updatedArea.schedule_id)
          console.log('🔍 Campo schedule.schedule_type en respuesta (update):', updatedArea.schedule?.schedule_type)
          console.log('🔍 Campo schedule.monday_active en respuesta (update):', updatedArea.schedule?.monday_active)
          console.log('🔍 Campo schedule.tuesday_active en respuesta (update):', updatedArea.schedule?.tuesday_active)
          console.log('🔍 Campo schedule.wednesday_active en respuesta (update):', updatedArea.schedule?.wednesday_active)
          console.log('🔍 Campo schedule.thursday_active en respuesta (update):', updatedArea.schedule?.thursday_active)
          console.log('🔍 Campo schedule.friday_active en respuesta (update):', updatedArea.schedule?.friday_active)
          console.log('🔍 Campo schedule.saturday_active en respuesta (update):', updatedArea.schedule?.saturday_active)
          console.log('🔍 Campo schedule.sunday_active en respuesta (update):', updatedArea.schedule?.sunday_active)
          
          // ✅ ACTUALIZAR INMEDIATAMENTE el área en la lista local
          updateLocalArea(updatedArea)
          
          // ✅ Verificar que la actualización se aplicó correctamente
          console.log('🔍 Verificando actualización en lista local...')
          const updatedLocalArea = areas.value.find(area => area.id === updatedArea.id)
          if (updatedLocalArea && updatedLocalArea.schedule) {
            console.log(`✅ Verificación exitosa: ${updatedLocalArea.name} tiene schedule_type = ${updatedLocalArea.schedule.schedule_type}`)
          }
          
          // Cerrar modal y resetear formulario
          showDialog.value = false
          resetForm()
          
          showSuccess('✅ Área actualizada correctamente')
          console.log('✅ Área actualizada exitosamente')
        } else {
          console.log('🆕 Creando nueva área...')
          console.log('📤 Datos enviados al servicio:', areaData)
          
          // Crear nueva área
          const newArea = await areaService.create(areaData)
          console.log('📥 Respuesta del backend (create):', newArea)
          console.log('🔍 Campo schedule en respuesta (create):', newArea.schedule)
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
        
        // ✅ Recargar áreas solo si es necesario (después de un breve delay para asegurar sincronización)
        setTimeout(async () => {
          try {
            console.log('🔄 Recargando áreas para sincronización...')
            await loadAreas()
            console.log('✅ Áreas recargadas para sincronización')
          } catch (error) {
            console.error('❌ Error recargando áreas:', error)
          }
        }, 500)
        
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
       formErrors,
       showDescriptionHint,
       descriptionHint,
       showNameHint,
       nameHint,
      // Variables del mapa optimizado
       mapRadius,
       selectedLocation,
      isMapReady,
      mapLoading,
       userLocation,
       isLocating,
       searchPlace,
       googleMapsAvailable,
      // Variables del sistema de horarios
      scheduleType,
      schedule,
      scheduleDays,
      // ✅ Key dinámica para tabla
      tableKey,
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
             // Funciones del sistema de horarios
       getScheduleSummary,
       createDefaultSchedule,
       loadScheduleFromArea,
       getScheduleColor,
       getScheduleIcon,
             getScheduleText,
      getScheduleTooltip,
      formatDescription,
       // Funciones de validación
       validateField,
       validateScheduleField,
       validateAllFields,
       validateSchedule,
       getScheduleFieldError,
       validateScheduleDay,
       sanitizeName,
       sanitizeDescription,
      // Funciones del mapa optimizado
      showMapSelectorModal,
      confirmMapSelection,
      cancelMapSelection,
      useCurrentLocation,
      onSearchInput,
      clearMap,
      refreshMap,
      // Funciones de formateo
      formatCoordinate,
      showMessage,
      forceUIUpdate,
      updateLocalArea
    }
  }
}
</script>

<style scoped>
/* Contenedor principal sin scroll */
.areas-container {
  overflow: visible !important;
  height: auto !important;
  max-height: none !important;
}

/* Eliminar scroll en el modal del mapa */
.v-dialog .v-card {
  overflow: visible !important;
  max-height: none !important;
}

.v-dialog .v-card-text {
  overflow: visible !important;
  max-height: none !important;
}

/* Eliminar scroll en contenedores específicos */
.map-controls {
  overflow: visible !important;
  max-height: none !important;
}

/* Estilos globales para eliminar scroll */
:deep(.v-data-table) {
  overflow: visible !important;
}

:deep(.v-data-table__wrapper) {
  overflow: visible !important;
}

:deep(.v-card) {
  overflow: visible !important;
}

:deep(.v-card-text) {
  overflow: visible !important;
}

/* Asegurar que no haya scroll en el body cuando se abre el modal */
:deep(body) {
  overflow: visible !important;
}

.map-container {
  background: rgba(30, 41, 59, 0.8);
  border-radius: 12px;
  padding: 12px;
  border: 1px solid rgba(59, 130, 246, 0.2);
  overflow: visible !important;
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

/* Ajustar el slider compacto para el nuevo layout */
.radius-slider-compact :deep(.v-slider) {
  width: 100%;
  min-width: 180px;
}

.radius-slider-compact :deep(.v-slider__track) {
  width: 100% !important;
  min-width: 180px !important;
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

/* Estilos para el botón de ubicación actual */
.use-current-location-btn {
  width: 28px !important;
  height: 28px !important;
  min-width: 28px !important;
  padding: 0 !important;
  border-radius: 50% !important;
  transition: all 0.3s ease !important;
  margin: 0 auto !important;
  display: block !important;
}

.use-current-location-btn:hover {
  transform: scale(1.1) !important;
  box-shadow: 0 2px 8px rgba(34, 197, 94, 0.4) !important;
}

.use-current-location-btn .v-icon {
  font-size: 16px !important;
}

/* Centrar perfectamente la columna derecha */
.d-flex.flex-column.align-center.justify-center.text-center {
  align-items: center !important;
  justify-content: center !important;
  text-align: center !important;
  width: 100% !important;
}

/* Centrar el contenedor del mensaje */
.mt-2.text-center {
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  width: 100% !important;
}

/* Estilos para el mensaje informativo */
.text-caption.text-grey-400 {
  font-size: 8px !important;
  line-height: 1.0 !important;
  margin: 0 !important;
  opacity: 0.7 !important;
  white-space: nowrap !important;
  max-width: 90px !important;
  word-wrap: break-word !important;
  hyphens: auto !important;
  text-align: center !important;
}

/* Ajustar el espaciado del mensaje */
.text-caption.text-grey-400.mb-1 {
  margin-bottom: 1px !important;
}

.text-caption.text-grey-400.mb-0 {
  margin-bottom: 0 !important;
}

/* Asegurar que el slider y los elementos se alineen correctamente */
.d-flex.gap-4 {
  align-items: flex-start !important;
  gap: 24px !important;
}

/* Estilos para el chip de ubicación */
.location-chip {
  flex-shrink: 0 !important;
  white-space: nowrap !important;
  margin-top: 0 !important;
}

/* Estilos para el chip de radio */
.radius-chip {
  font-size: 11px !important;
  height: 20px !important;
  padding: 0 6px !important;
  margin: 0 !important;
  text-align: center !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
}

.radius-chip .v-chip__content {
  text-align: center !important;
  width: 100% !important;
  justify-content: center !important;
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
 
 /* Responsive para el header */
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
 
 /* Estilos para la sección de horarios */
 .schedule-section {
   background: rgba(15, 23, 42, 0.3);
   border-radius: 12px;
   padding: 20px;
   border: 1px solid rgba(59, 130, 246, 0.2);
 }
 
 .schedule-section h4 {
   color: #e2e8f0;
   font-weight: 600;
   margin-bottom: 20px;
 }
 
 .day-config {
   transition: all 0.3s ease;
 }
 
 .day-config:hover {
   transform: translateY(-2px);
   box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
 }
 
 .custom-schedule {
   animation: fadeIn 0.5s ease-in-out;
 }
 
 @keyframes fadeIn {
   from {
     opacity: 0;
     transform: translateY(10px);
   }
   to {
     opacity: 1;
     transform: translateY(0);
   }
 }
 
 .schedule-summary {
   animation: slideIn 0.4s ease-out;
 }
 
 @keyframes slideIn {
   from {
     opacity: 0;
     transform: translateX(-10px);
   }
   to {
     opacity: 1;
     transform: translateX(0);
   }
 }
 
 /* Estilos para los campos de tiempo */
 .custom-schedule .v-text-field {
   margin-bottom: 8px;
 }
 
 /* Estilos para los checkboxes de días */
 .custom-schedule .v-checkbox {
   margin-right: 12px;
 }
 
   /* Responsive para horarios */
  @media (max-width: 768px) {
    .schedule-section {
      padding: 16px;
    }
    
    .day-config .v-row {
      flex-direction: column;
    }
    
    .day-config .v-col {
      width: 100% !important;
      margin-bottom: 8px;
    }
  }
  
  /* Estilos para el scroll del formulario */
  .area-form-container {
    max-height: 70vh;
    overflow-y: auto;
    overflow-x: hidden;
    padding-right: 8px;
  }
  
  /* Scrollbar personalizado para el formulario */
  .area-form-scroll-wrapper::-webkit-scrollbar {
    width: 8px;
  }
  
  .area-form-scroll-wrapper::-webkit-scrollbar-track {
    background: rgba(15, 23, 42, 0.3);
    border-radius: 4px;
  }
  
  .area-form-scroll-wrapper::-webkit-scrollbar-thumb {
    background: rgba(59, 130, 246, 0.6);
    border-radius: 4px;
    transition: background 0.3s ease;
  }
  
  .area-form-scroll-wrapper::-webkit-scrollbar-thumb:hover {
    background: rgba(59, 130, 246, 0.8);
  }
  
  /* Scrollbar para Firefox */
  .area-form-scroll-wrapper {
    scrollbar-width: thin;
    scrollbar-color: rgba(59, 130, 246, 0.6) rgba(15, 23, 42, 0.3);
  }
  
  /* Ajustes para el modal del formulario */
  .area-dialog .v-card-text {
    padding: 0 !important;
  }
  
  /* Contenedor del formulario con scroll */
  .area-form-scroll-wrapper {
    padding: 20px;
    max-height: 70vh;
    overflow-y: auto;
    overflow-x: hidden;
  }
  
  /* Responsive para el scroll */
  @media (max-width: 768px) {
    .area-form-scroll-wrapper {
      max-height: 60vh;
      padding: 16px;
    }
  }
  
  @media (max-height: 800px) {
    .area-form-scroll-wrapper {
      max-height: 65vh;
    }
  }
  
  /* Mejoras adicionales para el scroll */
  .area-form-scroll-wrapper {
    /* Suavizar el scroll */
    scroll-behavior: smooth;
    
    /* Ocultar scrollbar en dispositivos móviles */
    -ms-overflow-style: none;  /* IE and Edge */
  }
  
  /* Ocultar scrollbar en dispositivos móviles */
  @media (max-width: 768px) {
    .area-form-scroll-wrapper::-webkit-scrollbar {
      display: none;
    }
    
    .area-form-scroll-wrapper {
      -ms-overflow-style: none;
      scrollbar-width: none;
    }
  }
  
  /* Indicador visual de scroll */
  .area-form-scroll-wrapper::after {
    content: '';
    position: absolute;
    bottom: 0;
    right: 0;
    width: 8px;
    height: 30px;
    background: linear-gradient(transparent, rgba(59, 130, 246, 0.3));
    border-radius: 4px;
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.3s ease;
  }
  
     .area-form-scroll-wrapper:hover::after {
     opacity: 1;
   }
   
   /* Estilos específicos para el input de búsqueda */
   .search-field-responsive {
     min-width: 200px !important;
     max-width: 300px !important;
     width: 150px !important;
   }
   
   .search-field-responsive .v-field__input {
     min-width: 200px !important;
     max-width: 300px !important;
     width: 500px !important;
   }
   
   /* Responsive para tablets */
   .search-field-tablet {
     min-width: 200px !important;
     width: 200px !important;
     max-width: 300px !important;
   }
   
   /* Responsive para móviles */
   .search-field-mobile {
     min-width: 200px !important;
     width: 300px !important;
     max-width: 70% !important;
   }
   
   /* Responsive para pantallas muy pequeñas */
   @media (max-width: 480px) {
     .search-field-mobile {
       min-width: 50% !important;
       width: 50% !important;
     }
   }
   



   

   

</style>
