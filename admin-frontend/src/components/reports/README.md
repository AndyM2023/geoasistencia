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

## Estilos Compartidos

Los estilos están centralizados en `../../style/reports.css` y se importan en cada componente que los necesita.

## Beneficios de la Modularización

1. **Mantenibilidad**: Cada componente tiene una responsabilidad específica
2. **Reutilización**: Los componentes pueden ser reutilizados en otras partes de la aplicación
3. **Testabilidad**: Es más fácil escribir tests unitarios para componentes pequeños
4. **Legibilidad**: El código es más fácil de entender y navegar
5. **Escalabilidad**: Facilita agregar nuevas funcionalidades

## Uso en Reports.vue

El componente principal `Reports.vue` ahora:
- Importa todos los componentes modulares
- Mantiene la lógica de negocio y estado
- Coordina la comunicación entre componentes
- Es mucho más pequeño y legible (de ~1100 líneas a ~600 líneas)

## Comunicación entre Componentes

- **Props down**: Los datos fluyen del componente padre a los hijos
- **Events up**: Las acciones de los usuarios se comunican hacia arriba
- **v-model**: Para sincronización bidireccional de filtros
- **Computed properties**: Para datos derivados y filtrados
