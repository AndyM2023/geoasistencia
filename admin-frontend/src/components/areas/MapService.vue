<template>
  <div></div>
</template>

<script>
export default {
  name: 'MapService',
  props: {
    mapId: {
      type: String,
      required: true
    },
    initialLat: {
      type: Number,
      default: -2.1894128
    },
    initialLng: {
      type: Number,
      default: -79.8890662
    },
    initialZoom: {
      type: Number,
      default: 15
    }
  },
  emits: ['mapReady', 'locationSelected', 'radiusChanged'],
  data() {
    return {
      map: null,
      marker: null,
      circle: null,
      geocoder: null,
      placesService: null,
      searchBox: null,
      isInitialized: false
    }
  },
  mounted() {
    this.initializeMap()
  },
  beforeUnmount() {
    this.cleanupMap()
  },
  methods: {
    async initializeMap() {
      try {
        // Verificar si Google Maps está disponible
        if (!window.google || !window.google.maps) {
          console.error('Google Maps no está disponible')
          this.$emit('mapReady', false)
          return
        }

        // Crear el mapa
        this.map = new google.maps.Map(document.getElementById(this.mapId), {
          center: { lat: this.initialLat, lng: this.initialLng },
          zoom: this.initialZoom,
          mapTypeId: google.maps.MapTypeId.ROADMAP,
          styles: this.getMapStyles(),
          zoomControl: true,
          mapTypeControl: false,
          scaleControl: true,
          streetViewControl: false,
          rotateControl: false,
          fullscreenControl: true
        })

        // Inicializar servicios
        this.geocoder = new google.maps.Geocoder()
        this.placesService = new google.maps.places.PlacesService(this.map)

        // Configurar eventos del mapa
        this.map.addListener('click', this.onMapClick)
        this.map.addListener('zoom_changed', this.onZoomChanged)

        // Marcar como inicializado
        this.isInitialized = true
        this.$emit('mapReady', true)

        // Crear marcador inicial
        this.createMarker({ lat: this.initialLat, lng: this.initialLng })

      } catch (error) {
        console.error('Error al inicializar el mapa:', error)
        this.$emit('mapReady', false)
      }
    },

    createMarker(position) {
      // Eliminar marcador anterior si existe
      if (this.marker) {
        this.marker.setMap(null)
      }

      // Crear nuevo marcador
      this.marker = new google.maps.Marker({
        position: position,
        map: this.map,
        draggable: true,
        title: 'Ubicación seleccionada',
        icon: {
          url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
            <svg width="32" height="32" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
              <circle cx="16" cy="16" r="12" fill="#3B82F6" stroke="#FFFFFF" stroke-width="2"/>
              <circle cx="16" cy="16" r="4" fill="#FFFFFF"/>
            </svg>
          `),
          scaledSize: new google.maps.Size(32, 32),
          anchor: new google.maps.Point(16, 32)
        }
      })

      // Evento de arrastre del marcador
      this.marker.addListener('dragend', () => {
        const position = this.marker.getPosition()
        this.updateLocation(position.lat(), position.lng())
      })

      // Centrar mapa en el marcador
      this.map.setCenter(position)
    },

    createCircle(center, radius) {
      // Eliminar círculo anterior si existe
      if (this.circle) {
        this.circle.setMap(null)
      }

      // Crear nuevo círculo
      this.circle = new google.maps.Circle({
        strokeColor: '#3B82F6',
        strokeOpacity: 0.8,
        strokeWeight: 2,
        fillColor: '#3B82F6',
        fillOpacity: 0.1,
        map: this.map,
        center: center,
        radius: radius
      })
    },

    onMapClick(event) {
      const position = event.latLng
      this.createMarker(position)
      this.updateLocation(position.lat(), position.lng())
    },

    updateLocation(lat, lng) {
      const position = { lat, lng }
      
      // Actualizar círculo si existe
      if (this.circle) {
        this.circle.setCenter(position)
      }

      // Emitir evento
      this.$emit('locationSelected', {
        lat: lat,
        lng: lng
      })
    },

    updateRadius(radius) {
      if (this.circle && this.marker) {
        this.circle.setRadius(radius)
        this.$emit('radiusChanged', radius)
      }
    },

    async searchLocation(query) {
      if (!this.geocoder) return null

      try {
        const result = await this.geocoder.geocode({ address: query })
        
        if (result.results.length > 0) {
          const location = result.results[0].geometry.location
          this.createMarker(location)
          this.map.setCenter(location)
          this.map.setZoom(16)
          
          this.$emit('locationSelected', {
            lat: location.lat(),
            lng: location.lng()
          })
          
          return location
        }
      } catch (error) {
        console.error('Error en la búsqueda:', error)
      }
      
      return null
    },

    async getCurrentLocation() {
      return new Promise((resolve, reject) => {
        if (!navigator.geolocation) {
          reject(new Error('Geolocalización no soportada'))
          return
        }

        navigator.geolocation.getCurrentPosition(
          (position) => {
            const location = {
              lat: position.coords.latitude,
              lng: position.coords.longitude
            }
            
            this.createMarker(location)
            this.map.setCenter(location)
            this.map.setZoom(16)
            
            this.$emit('locationSelected', location)
            resolve(location)
          },
          (error) => {
            reject(error)
          },
          {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 60000
          }
        )
      })
    },

    getMapStyles() {
      return [
        {
          featureType: 'all',
          elementType: 'labels.text.fill',
          stylers: [{ color: '#7c93a3' }, { lightness: -10 }]
        },
        {
          featureType: 'administrative.country',
          elementType: 'geometry',
          stylers: [{ visibility: 'simplified' }]
        },
        {
          featureType: 'landscape',
          elementType: 'geometry',
          stylers: [{ color: '#f5f5f2' }]
        },
        {
          featureType: 'poi',
          elementType: 'all',
          stylers: [{ visibility: 'off' }]
        },
        {
          featureType: 'road',
          elementType: 'all',
          stylers: [{ saturation: -100 }, { lightness: 45 }]
        },
        {
          featureType: 'road.highway',
          elementType: 'all',
          stylers: [{ visibility: 'simplified' }]
        },
        {
          featureType: 'road.arterial',
          elementType: 'geometry',
          stylers: [{ color: '#ffffff' }]
        },
        {
          featureType: 'transit',
          elementType: 'all',
          stylers: [{ visibility: 'off' }]
        },
        {
          featureType: 'water',
          elementType: 'all',
          stylers: [{ color: '#b9d3c2' }]
        }
      ]
    },

    onZoomChanged() {
      // Ajustar radio del círculo según el zoom
      if (this.circle) {
        const zoom = this.map.getZoom()
        const baseRadius = 100
        const adjustedRadius = baseRadius * Math.pow(2, 15 - zoom)
        this.circle.setRadius(adjustedRadius)
      }
    },

    cleanupMap() {
      if (this.marker) {
        this.marker.setMap(null)
        this.marker = null
      }
      
      if (this.circle) {
        this.circle.setMap(null)
        this.circle = null
      }
      
      if (this.map) {
        google.maps.event.clearInstanceListeners(this.map)
        this.map = null
      }
      
      this.isInitialized = false
    }
  }
}
</script>

<style scoped>
/* Este componente no tiene estilos visuales */
</style>
