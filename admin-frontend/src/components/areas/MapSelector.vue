<template>
  <v-dialog v-model="localShowMapSelector" max-width="1200px" persistent>
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
                    {{ localMapRadius }}m
                  </v-chip>
                </div>
                
                <div class="d-flex gap-4">
                  <!-- Columna izquierda: Barra deslizadora y chip -->
                  <div class="d-flex flex-column gap-3">
                    <!-- Barra deslizadora arriba -->
                    <v-slider
                      v-model="localMapRadius"
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
                      size="small"
                      color="green-400"
                      variant="outlined"
                      prepend-icon="mdi-crosshairs-gps"
                      @click="useCurrentLocation"
                      :loading="isLocating"
                      :disabled="isLocating"
                      class="use-current-location-btn"
                      title="Usar ubicación actual"
                      block
                    >
                      <div class="text-content">
                        Cambia por la ubicación<br>
                        GPS actual
                      </div>
                    </v-btn>
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
              <div class="mt-0 mb-1 instructions-container">
                <v-alert type="info" variant="tonal" density="compact" class="compact-instructions">
                  <template v-slot:prepend>
                    <v-icon size="small">mdi-information</v-icon>
                  </template>
                  <div class="instructions-content">
                    <strong class="text-caption">Instrucciones:</strong> 
                    <br><span class="text-caption">• Escribe el nombre del lugar y presiona ENTER</span>
                    <br><span class="text-caption">• Haz clic en el mapa para marcar la ubicación</span>
                    <br><span class="text-caption">• Ajusta el radio con el control deslizante</span>
                    <br><span class="text-caption">• Las coordenadas se llenarán automáticamente</span>
                  </div>
                </v-alert>
              </div>
              
              <!-- Botones de acción -->
              <div class="mt-6 mb-2">
                <div class="d-flex justify-center gap-3">
                  <v-btn color="grey-400" variant="outlined" @click="$emit('cancel')" class="action-btn">
                    Cancelar
                  </v-btn>
                  <v-btn 
                    color="blue-400" 
                    variant="flat" 
                    @click="confirmLocation"
                    :disabled="!selectedLocation"
                    :loading="confirming"
                    class="action-btn"
                  >
                    Confirmar Ubicación
                  </v-btn>
                </div>
              </div>
              
              <!-- Mensaje sobre mapa -->
              <div v-if="!googleMapsAvailable" class="mb-4">
                <v-alert type="warning" variant="tonal" density="compact">
                  <template v-slot:prepend>
                    <v-icon>mdi-alert</v-icon>
                  </template>
                  <strong>Google Maps no disponible</strong>
                  <br>Por favor, verifica tu conexión a internet
                </v-alert>
              </div>
            </div>
          </v-col>
        </v-row>
      </v-card-text>
      
      <!-- Eliminamos el v-card-actions ya que movimos los botones arriba -->
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  name: 'MapSelector',
  props: {
    showMapSelector: {
      type: Boolean,
      default: false
    },
    mapRadius: {
      type: Number,
      default: 100
    },
    selectedLocation: {
      type: Object,
      default: null
    },
    isLocating: {
      type: Boolean,
      default: false
    },
    userLocation: {
      type: Object,
      default: null
    },
    googleMapsAvailable: {
      type: Boolean,
      default: true
    }
  },
  emits: ['update:showMapSelector', 'update:mapRadius', 'search', 'useCurrentLocation', 'confirm', 'cancel'],
  data() {
    return {
      searchPlace: '',
      confirming: false
    }
  },
  computed: {
    localShowMapSelector: {
      get() {
        return this.showMapSelector
      },
      set(value) {
        this.$emit('update:showMapSelector', value)
      }
    },
    localMapRadius: {
      get() {
        return this.mapRadius
      },
      set(value) {
        this.$emit('update:mapRadius', value)
      }
    }
  },
  methods: {
    onSearchInput() {
      this.$emit('search', this.searchPlace)
    },
    useCurrentLocation() {
      this.$emit('useCurrentLocation')
    },
    async confirmLocation() {
      this.confirming = true
      try {
        await this.$emit('confirm', {
          location: this.selectedLocation,
          radius: this.localMapRadius
        })
      } finally {
        this.confirming = false
      }
    }
  }
}
</script>
