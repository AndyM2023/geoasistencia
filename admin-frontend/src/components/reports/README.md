# Componentes de Reportes

Esta carpeta contiene los componentes modulares que conforman la página de reportes de asistencia.

## Estructura de Componentes

### 1. ReportFilters.vue
**Responsabilidad**: Maneja todos los filtros del reporte
- Selectores de empleado, área y estado
- Selectores de fecha (desde/hasta)
- Botones de acción (Generar Reporte, Exportar Excel, Limpiar Filtros)
- Validación de filtros
- Lógica de establecimiento automático de área al seleccionar empleado

**Props**:
- `filters`: Objeto con los filtros actuales
- `employees`: Array de empleados disponibles
- `areas`: Array de áreas disponibles
- `generating`: Boolean para estado de carga
- `hasReportData`: Boolean para habilitar exportación

**Emits**:
- `generate-report`: Solicita generar el reporte
- `export-report`: Solicita exportar el reporte
- `update:filters`: Actualiza los filtros

### 2. ReportStats.vue
**Responsabilidad**: Muestra las estadísticas del reporte
- Tarjeta de Total de Días
- Tarjeta de Tasa de Asistencia
- Tarjeta de Atrasos
- Tarjeta de Ausencias

**Props**:
- `stats`: Objeto con las estadísticas calculadas

### 3. ReportTable.vue
**Responsabilidad**: Muestra la tabla de datos del reporte
- Tabla de datos con v-data-table
- Formateo de fechas y horas
- Chips de estado con colores
- Indicadores de búsqueda activa
- Contadores de resultados

**Props**:
- `reportData`: Array con todos los datos del reporte
- `filteredReportData`: Array con los datos filtrados por búsqueda
- `search`: String de búsqueda actual
- `loading`: Boolean para estado de carga
- `tableKey`: Número para forzar re-renderizado
- `headers`: Array con las cabeceras de la tabla

### 4. ReportChart.vue
**Responsabilidad**: Muestra el gráfico de distribución de estados
- Gráfico circular de estados de asistencia
- Integración con AttendancePieChart

**Props**:
- `reportData`: Array con los datos del reporte
- `chartData`: Array con los datos procesados para el gráfico

### 5. ReportMessages.vue
**Responsabilidad**: Muestra mensajes de estado
- Mensaje cuando no hay datos
- Mensaje cuando no hay resultados de búsqueda
- Botón para limpiar búsqueda

**Props**:
- `reportData`: Array con los datos del reporte
- `filteredReportData`: Array con los datos filtrados
- `search`: String de búsqueda actual
- `loading`: Boolean para estado de carga

**Emits**:
- `clear-search`: Solicita limpiar la búsqueda

## Composable useReports

### Ubicación
`../../composables/useReports.js`

### Responsabilidad
Contiene toda la lógica de negocio de los reportes:
- Estado reactivo (filtros, datos, estadísticas, etc.)
- Computed properties (datos filtrados, datos del gráfico)
- Funciones de negocio (generar reporte, exportar, cargar datos)
- Funciones de utilidad (formateo de fechas, colores de estado)
- Watchers y lógica de inicialización

### Funciones Principales
- `generateReport()`: Genera el reporte con los filtros aplicados
- `exportReport()`: Exporta el reporte a Excel
- `clearSearch()`: Limpia la búsqueda
- `initialize()`: Inicializa el composable cargando datos básicos

### Estado Reactivo
- `search`: Término de búsqueda
- `loading`: Estado de carga
- `generating`: Estado de generación de reporte
- `filters`: Filtros aplicados
- `employees`: Lista de empleados
- `areas`: Lista de áreas
- `reportData`: Datos del reporte
- `stats`: Estadísticas calculadas

### Computed Properties
- `filteredReportData`: Datos filtrados por búsqueda
- `chartData`: Datos procesados para el gráfico

## Estilos Compartidos

Los estilos están centralizados en `../../style/reports.css` y se importan en cada componente que los necesita.

## Beneficios de la Modularización

1. **Mantenibilidad**: Cada componente tiene una responsabilidad específica
2. **Reutilización**: Los componentes pueden ser reutilizados en otras partes de la aplicación
3. **Testabilidad**: Es más fácil escribir tests unitarios para componentes pequeños
4. **Legibilidad**: El código es más fácil de entender y navegar
5. **Escalabilidad**: Facilita agregar nuevas funcionalidades
6. **Separación de Responsabilidades**: Lógica de negocio separada de la presentación

## Uso en Reports.vue

El componente principal `Reports.vue` ahora:
- Importa todos los componentes modulares
- Usa el composable `useReports` para toda la lógica de negocio
- Solo se encarga de la presentación y coordinación de componentes
- Es extremadamente limpio y legible (de ~1100 líneas a ~100 líneas)

## Comunicación entre Componentes

- **Props down**: Los datos fluyen del componente padre a los hijos
- **Events up**: Las acciones de los usuarios se comunican hacia arriba
- **v-model**: Para sincronización bidireccional de filtros
- **Computed properties**: Para datos derivados y filtrados
- **Composable**: Centraliza toda la lógica de negocio y estado

## Arquitectura Final

```
Reports.vue (Componente de Presentación)
├── useReports.js (Lógica de Negocio)
├── ReportFilters.vue (Filtros)
├── ReportStats.vue (Estadísticas)
├── ReportTable.vue (Tabla de Datos)
├── ReportChart.vue (Gráfico)
└── ReportMessages.vue (Mensajes de Estado)
```

Esta arquitectura proporciona:
- **Máxima separación de responsabilidades**
- **Código altamente mantenible**
- **Lógica reutilizable**
- **Componentes testables**
- **Fácil escalabilidad**
