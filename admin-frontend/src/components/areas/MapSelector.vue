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
                  <strong>Google Maps no disponible</strong>
                  <br>Por favor, verifica tu conexión a internet
                </v-alert>
              </div>
            </div>
          </v-col>
        </v-row>
      </v-card-text>
      
      <v-card-actions class="pa-4">
        <v-spacer></v-spacer>
        <v-btn color="grey-400" variant="outlined" @click="$emit('cancel')">
          Cancelar
        </v-btn>
        <v-btn 
          color="blue-400" 
          variant="flat" 
          @click="confirmLocation"
          :disabled="!selectedLocation"
          :loading="confirming"
        >
          Confirmar Ubicación
        </v-btn>
      </v-card-actions>
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

<style scoped>
.map-container {
  position: relative;
  width: 100%;
  height: 500px;
  border-radius: 12px;
  overflow: hidden;
  border: 2px solid rgba(59, 130, 246, 0.3);
}

.map-wrapper-full {
  width: 100%;
  height: 100%;
  background: #1e293b;
}

.map-controls {
  height: 100%;
  overflow-y: auto;
  padding-right: 8px;
}

.radius-label {
  font-weight: 600;
  font-size: 14px;
}

.radius-chip {
  min-width: 60px;
  justify-content: center;
}

.radius-slider-compact {
  margin: 0;
}

.location-chip {
  text-align: center;
  min-width: 140px;
}

.use-current-location-btn {
  min-width: 40px;
  height: 40px;
}

.search-btn {
  min-width: 48px;
  height: 48px;
}

/* Scrollbar personalizado para los controles */
.map-controls::-webkit-scrollbar {
  width: 6px;
}

.map-controls::-webkit-scrollbar-track {
  background: rgba(15, 23, 42, 0.3);
  border-radius: 3px;
}

.map-controls::-webkit-scrollbar-thumb {
  background: rgba(59, 130, 246, 0.6);
  border-radius: 3px;
}

.map-controls::-webkit-scrollbar-thumb:hover {
  background: rgba(59, 130, 246, 0.8);
}

/* Responsive */
@media (max-width: 768px) {
  .map-container {
    height: 300px;
  }
  
  .map-controls {
    margin-top: 16px;
    padding-right: 0;
  }
}
</style>
