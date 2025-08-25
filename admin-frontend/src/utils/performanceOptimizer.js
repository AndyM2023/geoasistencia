
// Utilidades para optimizar el rendimiento de la aplicación

// Debounce function para evitar llamadas excesivas
export function debounce(func, wait) {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

// Throttle function para limitar la frecuencia de ejecución
export function throttle(func, limit) {
  let inThrottle
  return function() {
    const args = arguments
    const context = this
    if (!inThrottle) {
      func.apply(context, args)
      inThrottle = true
      setTimeout(() => inThrottle = false, limit)
    }
  }
}

// Memoization simple para funciones costosas
export function memoize(fn) {
  const cache = new Map()
  return function(...args) {
    const key = JSON.stringify(args)
    if (cache.has(key)) {
      return cache.get(key)
    }
    const result = fn.apply(this, args)
    cache.set(key, result)
    
    // Limpiar cache si es muy grande
    if (cache.size > 100) {
      const firstKey = cache.keys().next().value
      cache.delete(firstKey)
    }
    
    return result
  }
}

// Lazy loading para componentes pesados
export function lazyLoad(importFunc) {
  return () => importFunc().then(module => module.default || module)
}

// Optimización de listas grandes
export function virtualizeList(items, itemHeight, containerHeight) {
  const visibleCount = Math.ceil(containerHeight / itemHeight)
  const startIndex = Math.floor(window.scrollY / itemHeight)
  const endIndex = Math.min(startIndex + visibleCount, items.length)
  
  return {
    startIndex,
    endIndex,
    visibleItems: items.slice(startIndex, endIndex),
    totalHeight: items.length * itemHeight,
    offsetY: startIndex * itemHeight
  }
}

// Optimización de imágenes
export function optimizeImage(src, width, height, quality = 0.8) {
  if (!src) return src
  
  // Si es una imagen local, retornar como está
  if (src.startsWith('/') || src.startsWith('data:')) {
    return src
  }
  
  // Para imágenes externas, agregar parámetros de optimización
  const url = new URL(src)
  url.searchParams.set('w', width)
  url.searchParams.set('h', height)
  url.searchParams.set('q', quality)
  url.searchParams.set('fit', 'crop')
  
  return url.toString()
}

// Optimización de validaciones
export function createValidationCache() {
  const cache = new Map()
  const maxSize = 200
  
  return {
    get(key) {
      return cache.get(key)
    },
    set(key, value) {
      if (cache.size >= maxSize) {
        const firstKey = cache.keys().next().value
        cache.delete(firstKey)
      }
      cache.set(key, value)
    },
    clear() {
      cache.clear()
    }
  }
}

// Optimización de eventos
export function optimizeEventHandlers(handlers) {
  const optimized = {}
  
  for (const [key, handler] of Object.entries(handlers)) {
    if (typeof handler === 'function') {
      // Aplicar throttle a eventos de scroll y resize
      if (key.includes('scroll') || key.includes('resize')) {
        optimized[key] = throttle(handler, 16) // 60fps
      }
      // Aplicar debounce a eventos de input
      else if (key.includes('input') || key.includes('change')) {
        optimized[key] = debounce(handler, 300)
      }
      // Otros eventos se mantienen igual
      else {
        optimized[key] = handler
      }
    }
  }
  
  return optimized
}

// Optimización de watchers
export function createOptimizedWatcher(watchFn, options = {}) {
  const defaultOptions = {
    deep: false,
    immediate: false,
    flush: 'post'
  }
  
  return {
    ...defaultOptions,
    ...options,
    handler: watchFn
  }
}

// Limpiador de memoria
export function createMemoryCleaner() {
  const cleanupTasks = []
  
  return {
    add(task) {
      cleanupTasks.push(task)
    },
    cleanup() {
      cleanupTasks.forEach(task => {
        try {
          if (typeof task === 'function') {
            task()
          }
        } catch (error) {
          console.warn('Error during cleanup:', error)
        }
      })
      cleanupTasks.length = 0
    }
  }
}
