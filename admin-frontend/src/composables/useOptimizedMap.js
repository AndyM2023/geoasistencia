/**
 * useOptimizedMap - Composable para manejar mapas de forma optimizada
 * 
 * Ventajas:
 * - Carga rápida con Singleton
 * - Manejo automático de lifecycle
 * - Cache de instancias
 * - API simplificada
 */

import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import mapService from '../services/mapService'

export function useOptimizedMap(elementId = 'map') {
  // Estados reactivos
  const isMapReady = ref(false)
  const isLoading = ref(false)
  const error = ref(null)
  const mapInstance = ref(null)
  const selectedLocation = ref(null)
  const currentMarker = ref(null)
  const currentCircle = ref(null)

  /**
   * Inicializar mapa de forma optimizada
   */
  const initMap = async (options = {}) => {
    try {
      isLoading.value = true
      error.value = null

      console.log('🚀 useOptimizedMap: Inicializando mapa...')

      // Si se fuerza refresh, destruir el mapa existente primero
      if (options.forceRefresh) {
        console.log('🔄 useOptimizedMap: Forzando recreación del mapa...')
        mapService.destroyMap(elementId)
        mapInstance.value = null
        isMapReady.value = false
      }

      // Crear mapa usando el servicio singleton
      const map = await mapService.createMap(elementId, options)
      mapInstance.value = map

      // Configurar eventos del mapa
      setupMapEvents(map)

      isMapReady.value = true
      console.log('✅ useOptimizedMap: Mapa listo')

      return map
    } catch (err) {
      error.value = err.message
      console.error('❌ useOptimizedMap: Error inicializando mapa:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Configurar eventos del mapa
   */
  const setupMapEvents = (map) => {
    // Evento de click en el mapa
    map.on('click', (e) => {
      setLocation(e.latlng.lat, e.latlng.lng)
    })

    // Evento cuando el mapa está listo
    map.on('ready', () => {
      console.log('🗺️ Mapa completamente cargado')
    })
  }

  /**
   * Establecer ubicación con marcador y radio por defecto
   */
  const setLocation = (lat, lng, options = {}) => {
    if (!mapInstance.value) return

    // Remover marcador anterior
    if (currentMarker.value) {
      mapInstance.value.removeLayer(currentMarker.value)
    }

    // Crear nuevo marcador
    currentMarker.value = mapService.createMarker(
      mapInstance.value, 
      lat, 
      lng, 
      {
        title: 'Ubicación seleccionada',
        ...options
      }
    )

    // Actualizar ubicación seleccionada
    selectedLocation.value = { lat, lng }

    // Centrar mapa en la nueva ubicación
    mapInstance.value.setView([lat, lng], mapInstance.value.getZoom())

    // Mostrar círculo de radio por defecto (100 metros)
    const defaultRadius = options.radius || 100
    setRadius(lat, lng, defaultRadius)

    return currentMarker.value
  }

  /**
   * Establecer círculo de radio
   */
  const setRadius = (lat, lng, radius, options = {}) => {
    if (!mapInstance.value) return

    // Remover círculo anterior
    if (currentCircle.value) {
      mapInstance.value.removeLayer(currentCircle.value)
    }

    // Crear nuevo círculo con opciones mejoradas
    currentCircle.value = mapService.createCircle(
      mapInstance.value,
      lat,
      lng,
      radius,
      {
        color: '#3b82f6',
        fillColor: '#3b82f6',
        fillOpacity: 0.2,
        weight: 2,
        interactive: false,
        ...options
      }
    )

    // Actualizar tooltip con el nuevo radio
    if (currentCircle.value) {
      currentCircle.value.setTooltipContent(`Radio: ${radius}m`)
    }

    console.log(`📏 Radio actualizado: ${radius}m en (${lat.toFixed(6)}, ${lng.toFixed(6)})`)

    return currentCircle.value
  }

  /**
   * Buscar lugar por nombre
   */
  const searchLocation = async (query) => {
    try {
      isLoading.value = true
      const results = await mapService.geocodeSearch(query)
      
      if (results.length > 0) {
        const firstResult = results[0]
        await setLocation(firstResult.lat, firstResult.lng)
        
        // Mostrar popup con información
        if (currentMarker.value) {
          currentMarker.value.bindPopup(firstResult.name).openPopup()
        }
      }
      
      return results
    } catch (err) {
      error.value = `Error en búsqueda: ${err.message}`
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Obtener ubicación actual del usuario
   */
  const getCurrentLocation = async (options = {}) => {
    try {
      isLoading.value = true
      const location = await mapService.getCurrentLocation()
      
      await setLocation(location.lat, location.lng, {
        title: 'Tu ubicación actual',
        radius: options.radius || 100,
        ...options
      })
      
      return location
    } catch (err) {
      error.value = `Error obteniendo ubicación: ${err.message}`
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Ir a una ubicación específica
   */
  const goToLocation = (lat, lng, zoom = 18) => {
    if (!mapInstance.value) return
    
    mapInstance.value.setView([lat, lng], zoom)
  }

  /**
   * Limpiar marcadores y círculos
   */
  const clearMap = () => {
    if (!mapInstance.value) return

    if (currentMarker.value) {
      mapInstance.value.removeLayer(currentMarker.value)
      currentMarker.value = null
    }

    if (currentCircle.value) {
      mapInstance.value.removeLayer(currentCircle.value)
      currentCircle.value = null
    }

    selectedLocation.value = null
  }

  /**
   * Invalidar y recrear mapa
   */
  const refreshMap = async (options = {}) => {
    console.log('🔄 useOptimizedMap: Refrescando mapa...')
    
    if (mapInstance.value) {
      mapService.destroyMap(elementId)
      mapInstance.value = null
      isMapReady.value = false
    }
    
    // Limpiar marcadores y círculos
    currentMarker.value = null
    currentCircle.value = null
    selectedLocation.value = null
    
    // Esperar un tick antes de recrear
    await nextTick()
    await initMap({ ...options, forceRefresh: true })
    
    console.log('✅ useOptimizedMap: Mapa refrescado')
  }

  /**
   * Lifecycle: Cleanup al desmontar
   */
  onUnmounted(() => {
    clearMap()
    // Nota: No destruimos el mapa aquí para permitir reutilización
    // El mapService maneja el cleanup global
  })

  // Retornar API del composable
  return {
    // Estados
    isMapReady,
    isLoading,
    error,
    mapInstance,
    selectedLocation,
    currentMarker,
    currentCircle,
    
    // Métodos
    initMap,
    setLocation,
    setRadius,
    searchLocation,
    getCurrentLocation,
    goToLocation,
    clearMap,
    refreshMap,
    
    // Utilities
    isReady: () => mapService.isReady()
  }
}

export default useOptimizedMap
