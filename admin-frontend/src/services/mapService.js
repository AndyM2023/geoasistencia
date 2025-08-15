/**
 * MapService - Singleton para optimización de Leaflet
 * 
 * Características:
 * - Una sola instancia de carga de Leaflet
 * - Cache de mapas reutilizables
 * - Preloading de recursos
 * - Optimización de performance
 */

class MapService {
  constructor() {
    if (MapService.instance) {
      return MapService.instance
    }

    this.isLeafletLoaded = false
    this.isLeafletLoading = false
    this.leafletPromise = null
    this.mapInstances = new Map()
    this.defaultConfig = {
      zoom: 18,
      maxZoom: 19,
      attribution: '© OpenStreetMap contributors'
    }

    MapService.instance = this
    this.init()
  }

  /**
   * Inicialización del servicio
   */
  async init() {
    // Pre-cargar Leaflet al inicializar el servicio
    await this.loadLeaflet()
  }

  /**
   * Carga Leaflet una sola vez usando Singleton
   */
  async loadLeaflet() {
    // Si ya está cargado, retornar inmediatamente
    if (this.isLeafletLoaded && typeof L !== 'undefined') {
      return Promise.resolve()
    }

    // Si ya está en proceso de carga, retornar la promesa existente
    if (this.isLeafletLoading && this.leafletPromise) {
      return this.leafletPromise
    }

    // Marcar como en proceso de carga
    this.isLeafletLoading = true

    this.leafletPromise = new Promise((resolve, reject) => {
      // Verificar si ya está cargado globalmente
      if (typeof L !== 'undefined') {
        this.isLeafletLoaded = true
        this.isLeafletLoading = false
        resolve()
        return
      }

      console.log('🗺️ MapService: Cargando Leaflet...')

      // Crear y cargar el script
      const script = document.createElement('script')
      script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'
      script.async = true
      
      script.onload = () => {
        console.log('✅ MapService: Leaflet cargado exitosamente')
        this.isLeafletLoaded = true
        this.isLeafletLoading = false
        resolve()
      }
      
      script.onerror = () => {
        console.error('❌ MapService: Error cargando Leaflet')
        this.isLeafletLoading = false
        reject(new Error('No se pudo cargar Leaflet'))
      }
      
      document.head.appendChild(script)
    })

    return this.leafletPromise
  }

  /**
   * Crear un mapa optimizado con cache
   */
  async createMap(elementId, options = {}) {
    // Asegurar que Leaflet esté cargado
    await this.loadLeaflet()

    const config = { ...this.defaultConfig, ...options }
    
    // Verificar si ya existe una instancia para este elemento
    if (this.mapInstances.has(elementId)) {
      const existingMap = this.mapInstances.get(elementId)
      console.log('♻️ MapService: Reutilizando mapa existente para', elementId)
      return existingMap
    }

    const element = document.getElementById(elementId)
    if (!element) {
      throw new Error(`Elemento con ID '${elementId}' no encontrado`)
    }

    console.log('🆕 MapService: Creando nuevo mapa para', elementId)

    // Crear el mapa
    const map = L.map(element).setView(
      [config.lat || 19.432608, config.lng || -99.133209], // Default: Ciudad de México
      config.zoom
    )

    // Agregar capa de tiles con configuración optimizada
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: config.attribution,
      maxZoom: config.maxZoom,
      // Optimizaciones
      keepBuffer: 2, // Mantener tiles en memoria
      updateWhenIdle: false, // Actualizar mientras se mueve
      updateWhenZooming: false // Actualizar mientras se hace zoom
    }).addTo(map)

    // Cachear la instancia
    this.mapInstances.set(elementId, map)

    return map
  }

  /**
   * Destruir un mapa específico
   */
  destroyMap(elementId) {
    if (this.mapInstances.has(elementId)) {
      const map = this.mapInstances.get(elementId)
      console.log('🗑️ MapService: Destruyendo mapa para', elementId)
      
      try {
        map.remove()
        console.log('✅ MapService: Mapa removido correctamente')
      } catch (error) {
        console.warn('⚠️ MapService: Error removiendo mapa:', error)
      }
      
      this.mapInstances.delete(elementId)
      console.log('🗑️ MapService: Mapa eliminado del cache')
    } else {
      console.log('ℹ️ MapService: No hay mapa para destruir en', elementId)
    }
  }

  /**
   * Crear marcador optimizado
   */
  createMarker(map, lat, lng, options = {}) {
    const defaultOptions = {
      title: 'Ubicación',
      draggable: false,
      ...options
    }

    return L.marker([lat, lng], defaultOptions).addTo(map)
  }

  /**
   * Crear círculo (radio de área)
   */
  createCircle(map, lat, lng, radius, options = {}) {
    const defaultOptions = {
      color: '#3b82f6',
      fillColor: '#3b82f6',
      fillOpacity: 0.3,
      weight: 2,
      interactive: false, // No interfiere con los clics del mapa
      ...options
    }

    const circle = L.circle([lat, lng], {
      radius: radius,
      ...defaultOptions
    }).addTo(map)

    // Agregar tooltip con información del radio
    circle.bindTooltip(`Radio: ${radius}m`, {
      permanent: false,
      direction: 'center',
      className: 'radius-tooltip'
    })

    return circle
  }

  /**
   * Geocoding optimizado (búsqueda de lugares)
   */
  async geocodeSearch(query) {
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=5`
      )
      
      if (!response.ok) {
        throw new Error('Error en la búsqueda')
      }
      
      const results = await response.json()
      
      return results.map(result => ({
        name: result.display_name,
        lat: parseFloat(result.lat),
        lng: parseFloat(result.lon),
        type: result.type,
        importance: result.importance
      }))
    } catch (error) {
      console.error('❌ MapService: Error en geocoding:', error)
      throw error
    }
  }

  /**
   * Obtener ubicación del usuario con cache
   */
  async getCurrentLocation() {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('Geolocalización no disponible'))
        return
      }

      navigator.geolocation.getCurrentPosition(
        (position) => {
          resolve({
            lat: position.coords.latitude,
            lng: position.coords.longitude,
            accuracy: position.coords.accuracy
          })
        },
        (error) => {
          reject(error)
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 300000 // Cache por 5 minutos
        }
      )
    })
  }

  /**
   * Invalidar mapa (forzar recarga en próximo uso)
   */
  invalidateMap(elementId) {
    if (this.mapInstances.has(elementId)) {
      this.destroyMap(elementId)
    }
  }

  /**
   * Limpiar todas las instancias (para cleanup)
   */
  cleanup() {
    this.mapInstances.forEach((map, elementId) => {
      this.destroyMap(elementId)
    })
    this.mapInstances.clear()
  }

  /**
   * Verificar si Leaflet está disponible
   */
  isReady() {
    return this.isLeafletLoaded && typeof L !== 'undefined'
  }
}

// Exportar una instancia singleton
const mapService = new MapService()

export default mapService
