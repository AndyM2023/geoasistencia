# 🎯 Sistema de Reconocimiento Facial Avanzado - GEOASISTENCIA

## 📋 Descripción
Sistema profesional de reconocimiento facial usando DeepFace con RetinaFace (detector) y FaceNet (extractor de características). Diseñado para aplicaciones empresariales con gestión completa de base de datos de rostros.

## 🚀 Características Avanzadas
- **Detector**: RetinaFace (alta precisión)
- **Extractor**: FaceNet (embeddings robustos)
- **Umbral de similitud**: Configurable (por defecto 60%)
- **Almacenamiento**: Estructura de carpetas organizada por persona
- **Captura**: Integración con cámara web en tiempo real
- **Gestión**: CRUD completo de personas y rostros
- **Estadísticas**: Información detallada de la base de datos

## 📦 Instalación

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Verificar instalación
```bash
python -c "import deepface; print('✅ DeepFace instalado')"
```

## 🎮 Uso

### Sistema Principal
```bash
python advanced_face_system.py
```

**Opciones disponibles:**
1. **Registrar nueva persona** - Agregar rostros al sistema con ID y nombre
2. **Identificar persona** - Reconocer desde cámara en tiempo real
3. **Listar personas registradas** - Ver base de datos completa
4. **Información de persona específica** - Detalles de rostros registrados
5. **Eliminar persona** - Remover del sistema completamente
6. **Estadísticas de la base de datos** - Resumen general
7. **Limpiar base de datos** - Eliminar todo (con confirmación)

## 📁 Estructura de Archivos
```
face_recognition/
├── advanced_face_system.py    # Sistema principal profesional
├── simple_camera.py           # Capturador de fotos simple
├── requirements.txt           # Dependencias
├── faces/                     # Base de datos organizada por persona
│   ├── 123JuanPerez/         # Carpeta por persona (ID + Nombre)
│   │   ├── 1234567890.jpg    # Imagen del rostro
│   │   ├── 1234567890.npy    # Características faciales
│   │   └── ...               # Hasta 50 rostros por persona
│   └── 456MariaGarcia/       # Otra persona
└── temp_photos/              # Fotos temporales de identificación
```

## 🔧 Flujo de Trabajo Profesional

### 1. Registrar Empleado
1. Ejecutar `python advanced_face_system.py`
2. Opción 1: "Registrar nueva persona (cámara)"
3. Ingresar **ID único** (ej: "123")
4. Ingresar **nombre completo** (ej: "Juan Pérez")
5. **La cámara se abre automáticamente**
6. Presionar **ESPACIO** para capturar
7. Sistema detecta rostros y genera hasta 50 variaciones
8. **Se crea carpeta**: `123JuanPerez/` con rostros + características

### 2. Marcar Asistencia
1. Opción 2: "Identificar persona (cámara)"
2. **La cámara se abre automáticamente**
3. Presionar **ESPACIO** para capturar
4. Sistema identifica automáticamente
5. Si similitud ≥ 60%: ✅ Identificado con detalles
6. Si similitud < 60%: ❌ No identificado

## 🎯 Diferencias con Sistema Anterior

- **Estructura organizada**: Carpeta por persona en lugar de archivos sueltos
- **ID único**: Cada persona tiene un identificador numérico
- **Múltiples rostros**: Hasta 50 variaciones por persona
- **Gestión completa**: CRUD, estadísticas, limpieza
- **Interfaz profesional**: Menú organizado y claro
- **Manejo de errores**: Respuestas estructuradas en JSON

## ⚠️ Notas Importantes

- **Primera ejecución**: DeepFace descargará modelos automáticamente
- **Cámara**: Asegúrate de que la webcam esté disponible
- **Iluminación**: Buena iluminación mejora la precisión
- **Rostro frontal**: Posición frontal para mejor detección
- **ID único**: Cada persona debe tener un ID diferente
- **Umbral configurable**: 60% por defecto, ajustable según necesidades

## 🐛 Solución de Problemas

### Error: "No se pudo abrir la cámara"
- Verifica que la webcam esté conectada
- Cierra otras aplicaciones que usen la cámara
- Reinicia el sistema

### Error: "Similitud insuficiente"
- Mejora la iluminación
- Asegúrate de que el rostro esté frontal
- Considera registrar más rostros de la persona
- Ajusta el umbral de similitud si es necesario

### Error: "Persona no encontrada"
- Verifica que el ID sea correcto
- Usa la opción 3 para listar personas registradas
- Confirma que la persona esté registrada

## 🔮 Próximos Pasos
- Integración con Django backend
- API REST para reconocimiento
- Interfaz web para administración
- Base de datos de empleados
- Sistema de logs y auditoría
- Backup automático de base de datos
