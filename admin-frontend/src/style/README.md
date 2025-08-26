# Estilos Centralizados - Carpeta Style

Esta carpeta contiene todos los estilos CSS centralizados de la aplicación, organizados por módulos y funcionalidades.

## 📁 Estructura de Archivos

```
📁 style/
├── 📄 areas.css          - Estilos para componentes de áreas
├── 📄 reports.css        - Estilos para componentes de reportes
└── 📄 README.md          - Este archivo de documentación
```

## 🎨 areas.css

### **Descripción**
Contiene todos los estilos CSS para los componentes relacionados con la gestión de áreas.

### **Componentes Cubiertos**
- **AreaForm.vue** - Formulario principal de áreas
- **AreaScheduleForm.vue** - Formulario de horarios de áreas
- **Areas.vue** - Vista principal de gestión de áreas

### **Estilos Incluidos**

#### **AreaForm.vue**
- Sección de horarios (`.schedule-section`)
- Configuración de días (`.day-config`)
- Animaciones (`.custom-schedule`, `.schedule-summary`)
- Scrollbar personalizado (`.area-form-scroll-wrapper`)
- Responsive para móviles

#### **AreaScheduleForm.vue**
- Formulario principal (`.area-schedule-form`)
- Sección de días (`.days-section`)
- Configuración de horarios (`.day-row`, `.time-inputs`)
- Alertas y mensajes (`.alert`, `.alert-info`, `.alert-success`)
- Grid de horarios (`.schedule-grid`, `.schedule-day`)
- Responsive para móviles

#### **Areas.vue (Vista Principal)**
- Contenedor principal (`.areas-container`)
- Controles del mapa (`.map-container`, `.map-search`)
- Slider de radio (`.radius-slider`)
- Chips informativos (`.v-chip`, `.radius-chip`)
- Botón de ubicación actual (`.use-current-location-btn`)
- Responsive para móviles y diferentes alturas

### **Características**
- ✅ **Estilos Responsive**: Adaptados para móviles y tablets
- ✅ **Animaciones**: Transiciones suaves y efectos hover
- ✅ **Scrollbar Personalizado**: Estilo único para el formulario
- ✅ **Compatibilidad**: Funciona en Chrome, Firefox y Safari
- ✅ **Organización**: Estilos agrupados por componente

## 📊 reports.css

### **Descripción**
Contiene todos los estilos CSS para los componentes relacionados con reportes de asistencia.

### **Componentes Cubiertos**
- **ReportStats.vue** - Tarjetas de estadísticas
- **ReportFilters.vue** - Filtros de reportes
- **ReportTable.vue** - Tabla de datos
- **ReportChart.vue** - Gráficos
- **ReportMessages.vue** - Mensajes de estado

### **Estilos Incluidos**
- Tarjetas de estadísticas (`.stats-card`)
- Layout responsive (`.dashboard-stats-row`)
- Ajustes para diferentes tamaños de pantalla

## 🚀 Beneficios de la Centralización

### **1. Mantenibilidad**
- Todos los estilos en un solo lugar
- Fácil localización y modificación
- No hay duplicación de código CSS

### **2. Consistencia**
- Estilos uniformes entre componentes
- Variables CSS centralizadas
- Patrones de diseño consistentes

### **3. Reutilización**
- Estilos compartidos entre componentes
- Fácil aplicación de temas
- Reducción de código duplicado

### **4. Organización**
- Estructura clara y lógica
- Separación por funcionalidad
- Fácil navegación y búsqueda

## 📱 Responsive Design

Todos los archivos CSS incluyen:
- **Media queries** para móviles (`@media (max-width: 768px)`)
- **Ajustes de altura** para pantallas pequeñas
- **Flexbox** y **Grid** para layouts adaptativos
- **Touch-friendly** para dispositivos móviles

## 🔧 Uso en Componentes

### **Importación Estándar**
```vue
<style>
@import '../../style/areas.css';
</style>
```

### **Importación desde Vistas**
```vue
<style>
@import '../style/areas.css';
</style>
```

## 📋 Convenciones de Nomenclatura

- **Clases principales**: `.component-name`
- **Estados**: `.component-name.active`, `.component-name.disabled`
- **Responsive**: `@media (max-width: 768px)`
- **Profundidad**: `:deep()` para estilos de componentes hijos

## 🎯 Próximos Pasos

1. **Agregar más módulos**: Empleados, Usuarios, etc.
2. **Variables CSS**: Definir colores y espaciados globales
3. **Temas**: Soporte para modo oscuro/claro
4. **Optimización**: Minificación y purga de CSS no utilizado

## 📚 Documentación Relacionada

- [Componentes de Áreas](../../components/areas/README.md)
- [Componentes de Reportes](../../components/reports/README.md)
- [Vista de Áreas](../../views/Areas.vue)
- [Vista de Reportes](../../views/Reports.vue)

---

**Nota**: Todos los estilos mantienen la funcionalidad y apariencia visual original, solo se han reorganizado para mejorar la mantenibilidad y consistencia del código.
