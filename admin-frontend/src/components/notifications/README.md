# 🔔 Sistema de Notificaciones Toast

## 📁 Estructura del Proyecto

```
admin-frontend/src/
├── components/
│   └── notifications/
│       ├── ToastNotification.vue    # Componente principal de notificaciones
│       ├── index.js                 # Exportaciones del sistema
│       └── README.md                # Esta documentación
├── composables/
│   └── useNotifications.js          # Composable para usar notificaciones
├── stores/
│   └── notifications.js             # Store Pinia para estado global
└── App.vue                          # Componente global con ToastNotification
```

## 🚀 Uso Básico

### **1. En cualquier componente Vue:**

```javascript
import { useNotifications } from '../composables/useNotifications'

export default {
  setup() {
    const { showSuccess, showError, showInfo, showWarning } = useNotifications()
    
    // Mostrar notificación de éxito
    showSuccess('Operación completada exitosamente')
    
    // Mostrar notificación de error
    showError('Ocurrió un error')
    
    // Mostrar notificación de información
    showInfo('Procesando datos...')
    
    // Mostrar notificación de advertencia
    showWarning('Atención requerida')
  }
}
```

### **2. Con opciones personalizadas:**

```javascript
showSuccess('Usuario creado', {
  title: 'Éxito',
  details: 'El usuario se ha creado correctamente',
  icon: 'mdi-account-plus',
  duration: 10000,
  closable: true
})
```

## 🎯 Tipos de Notificaciones

### **✅ Success (Éxito)**
- **Color:** Verde sólido
- **Duración por defecto:** 8 segundos
- **Icono por defecto:** `mdi-check-circle`

### **❌ Error (Error)**
- **Color:** Rojo sólido
- **Duración por defecto:** 10 segundos
- **Icono por defecto:** `mdi-alert-circle`

### **ℹ️ Info (Información)**
- **Color:** Azul sólido
- **Duración por defecto:** 6 segundos
- **Icono por defecto:** `mdi-information`

### **⚠️ Warning (Advertencia)**
- **Color:** Naranja sólido
- **Duración por defecto:** 7 segundos
- **Icono por defecto:** `mdi-alert`

## 🔧 Opciones Disponibles

```javascript
{
  title: 'Título opcional',           // Título de la notificación
  details: 'Detalles adicionales',    // Información adicional
  icon: 'mdi-custom-icon',           // Icono personalizado
  duration: 5000,                    // Duración en milisegundos
  closable: true,                    // Si se puede cerrar manualmente
  autoHide: true,                    // Si se oculta automáticamente
  maxWidth: 400,                     // Ancho máximo de la notificación
  loading: false                     // Si muestra spinner de carga
}
```

## 🎨 Métodos Especializados

### **📍 Errores de Ubicación:**
```javascript
const { showLocationError } = useNotifications()

// Maneja automáticamente diferentes tipos de errores de ubicación
showLocationError({
  error_type: 'location_out_of_range',
  message: 'Estás fuera del área permitida',
  distance_meters: 150,
  area_radius: 100,
  area_name: 'Oficina Principal'
})
```

### **👥 Éxito de Asistencia:**
```javascript
const { showAttendanceSuccess } = useNotifications()

// Maneja automáticamente diferentes tipos de asistencia
showAttendanceSuccess(
  { action_type: 'entrada', employee_name: 'Juan Pérez' },
  { distance_meters: 25 }
)
```

### **📹 Estado de Cámara:**
```javascript
const { showCameraStatus } = useNotifications()

// Maneja automáticamente diferentes estados de la cámara
showCameraStatus('starting')  // Iniciando
showCameraStatus('active')    // Activa
showCameraStatus('error')     // Error
```

## 🎭 Animaciones

- **Entrada:** Deslizamiento hacia abajo con fade-in
- **Salida:** Deslizamiento hacia arriba con fade-out
- **Duración:** 0.4 segundos con curva de bezier suave
- **Responsive:** Se adapta a diferentes tamaños de pantalla

## 📱 Responsive Design

- **Desktop:** Centrado horizontal con ancho máximo de 400px
- **Mobile:** Ocupa todo el ancho disponible con márgenes de 20px
- **Adaptación automática** al tamaño de pantalla

## 🧹 Gestión de Estado

### **Métodos de Limpieza:**
```javascript
const { clearAll, clearByType, removeNotification } = useNotifications()

// Remover notificación específica
removeNotification(notificationId)

// Limpiar todas las notificaciones
clearAll()

// Limpiar por tipo
clearByType('error')
```

### **Estadísticas:**
```javascript
const { getStats, hasActiveNotifications } = useNotifications()

// Verificar si hay notificaciones activas
if (hasActiveNotifications()) {
  console.log('Hay notificaciones activas')
}

// Obtener estadísticas
const stats = getStats()
console.log(`Total: ${stats.total}, Errores: ${stats.byType.error}`)
```

## 🔄 Lifecycle

1. **Componente montado:** Se registra en el store global
2. **Notificación mostrada:** Se agrega al array de notificaciones
3. **Timer iniciado:** Si autoHide está habilitado
4. **Auto-ocultado:** Después de la duración especificada
5. **Cleanup:** Se remueve del array y se limpia la memoria

## 🚨 Casos de Uso Comunes

### **Formularios:**
```javascript
// Validación exitosa
showSuccess('Datos guardados correctamente')

// Error de validación
showError('Por favor completa todos los campos requeridos')
```

### **Operaciones CRUD:**
```javascript
// Crear
showSuccess('Registro creado exitosamente')

// Actualizar
showSuccess('Registro actualizado correctamente')

// Eliminar
showSuccess('Registro eliminado')

// Error
showError('No se pudo completar la operación')
```

### **Estados de Carga:**
```javascript
// Inicio de operación
const loadingId = showLoading('Procesando...')

// Operación completada
removeNotification(loadingId)
showSuccess('Operación completada')
```

## 🎯 Beneficios del Sistema

- ✅ **Reutilizable:** Mismo sistema en toda la aplicación
- ✅ **Consistente:** Apariencia uniforme en todas las notificaciones
- ✅ **Escalable:** Fácil agregar nuevos tipos y funcionalidades
- ✅ **Mantenible:** Lógica centralizada y bien organizada
- ✅ **Performance:** Optimizado para múltiples notificaciones
- ✅ **Accesible:** Cumple estándares de accesibilidad web
- ✅ **Responsive:** Se adapta a todos los dispositivos

## 🔧 Personalización

### **Colores:**
Los colores se pueden personalizar en `ToastNotification.vue`:

```css
.error-notification {
  background: #dc2626 !important;
  border-color: #b91c1c !important;
}
```

### **Duración por defecto:**
Se puede modificar en `notifications.js`:

```javascript
const DEFAULT_DURATIONS = {
  [NOTIFICATION_TYPES.SUCCESS]: 8000,  // 8 segundos
  [NOTIFICATION_TYPES.ERROR]: 10000,   // 10 segundos
  // ...
}
```

### **Iconos por defecto:**
Se pueden cambiar en `notifications.js`:

```javascript
const DEFAULT_ICONS = {
  [NOTIFICATION_TYPES.SUCCESS]: 'mdi-check-circle',
  [NOTIFICATION_TYPES.ERROR]: 'mdi-alert-circle',
  // ...
}
```

## 🐛 Troubleshooting

### **Problema:** Las notificaciones no aparecen
**Solución:** Verificar que `ToastNotification` esté importado en `App.vue`

### **Problema:** Las notificaciones no se auto-ocultan
**Solución:** Verificar que `autoHide: true` esté configurado

### **Problema:** Colores no se aplican correctamente
**Solución:** Verificar que los estilos CSS tengan `!important`

### **Problema:** Múltiples notificaciones se superponen
**Solución:** El sistema maneja automáticamente el stacking, pero se puede ajustar el `z-index`

## 📚 Referencias

- **Vue 3 Composition API:** https://vuejs.org/guide/extras/composition-api-faq.html
- **Pinia Store:** https://pinia.vuejs.org/
- **Vuetify Alerts:** https://vuetifyjs.com/en/components/alerts/
- **Material Design Icons:** https://materialdesignicons.com/
