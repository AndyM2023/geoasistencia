# Sistema de Pausa Inteligente para Captura Facial

## Problema Resuelto
El sistema anterior continuaba capturando fotos cada segundo aunque no se detectara un rostro, lo que resultaba en fotos innecesarias de manos, objetos o espacios vacíos.

## Solución Implementada

### Flujo del Sistema de Pausa Inteligente

```
INICIO CAPTURA
    ↓
[Detectar Rostro] → ¿Rostro detectado?
    ↓                    ↓
   SÍ                   NO
    ↓                    ↓
[Capturar Foto]    [Incrementar Contador]
    ↓                    ↓
[Resetear Contador]  ¿Contador ≥ 3?
    ↓                    ↓
[Continuar]             SÍ
    ↓                    ↓
                    [PAUSAR CAPTURA]
                         ↓
                    [Mostrar Mensaje]
                         ↓
                    [Verificar Rostro Cada Segundo]
                         ↓
                    [Detectar Rostro] → ¿Rostro detectado?
                         ↓                    ↓
                        SÍ                   NO
                         ↓                    ↓
                    [REANUDAR CAPTURA]   [Continuar Pausa]
                         ↓                    ↓
                    [Capturar Inmediatamente] [Esperar 1 segundo]
                         ↓
                    [Continuar Captura Normal]
```

### Características del Sistema

#### 1. **Detección Inteligente EQUILIBRADA**
- Utiliza la API `FaceDetector` del navegador cuando está disponible
- Fallback a análisis de imagen personalizado con criterios EQUILIBRADOS:
  - **Tonos de piel**: >8% de la imagen (equilibrado)
  - **Piel en el centro**: >10% del área central
  - **Bordes definidos**: >1% de píxeles con cambios bruscos
  - **Brillo adecuado**: Entre 60-220 (rango flexible)
  - **Contenido mínimo**: >500 píxeles de piel
  - **No uniforme**: Debe tener variación en la imagen
  - **Sistema de puntuación**: Requiere 5 de 7 criterios (flexible)

#### 2. **Sistema de Pausa y Reanudación**
- **Umbral**: 3 intentos fallidos consecutivos (equilibrado)
- **Duración**: Pausa hasta que se detecte rostro nuevamente
- **Reanudación**: Automática cuando se detecta rostro
- **Verificación continua**: Mientras está pausado, sigue verificando cada segundo si hay rostro
- **Captura inmediata**: Al detectar rostro durante pausa, reanuda y captura inmediatamente

#### 3. **Estados Visuales**
- **Verde**: Rostro detectado, capturando normalmente
- **Naranja**: Buscando rostro, intentos en progreso
- **Rojo**: Captura pausada, no se detecta rostro

#### 4. **Mensajes Informativos**
- Estado actual de la captura
- Instrucciones claras para el usuario
- Progreso visual con indicadores de color

### Código Implementado

#### Variables de Estado
```javascript
const isPaused = ref(false);
const consecutiveFailedAttempts = ref(0);
const maxFailedAttempts = 3; // Equilibrado para balance entre sensibilidad y precisión
const pauseDuration = 2000;
```

#### Lógica de Pausa
```javascript
if (!faceDetectedResult) {
  consecutiveFailedAttempts.value++;
  if (consecutiveFailedAttempts.value >= maxFailedAttempts) {
    pauseCapture();
  }
  return;
}
```

#### Reanudación Automática
```javascript
if (isPaused.value) {
  resumeCapture();
}
```

### Beneficios

1. **Eficiencia**: No desperdicia recursos capturando fotos innecesarias
2. **Calidad**: Solo captura cuando hay un rostro presente
3. **UX Mejorada**: Feedback visual claro del estado
4. **Automático**: No requiere intervención manual del usuario
5. **Robusto**: Maneja casos edge y errores graciosamente

### Configuración

- **maxFailedAttempts**: 3 (configurable, equilibrado)
- **pauseDuration**: 2000ms (configurable)
- **captureInterval**: 1000ms (configurable)

### Criterios de Detección Equilibrados

Para que se considere que hay un rostro, se requiere al menos **5 de 7** criterios:

1. **Brillo promedio**: Entre 60-220 (flexible)
2. **Tonos de piel**: >8% de la imagen total (equilibrado)
3. **Piel en el centro**: >10% del área central (30% del radio)
4. **Bordes definidos**: >1% de píxeles con cambios bruscos
5. **Bordes razonables**: Entre 0.5-20% (flexible)
6. **Contenido mínimo**: >500 píxeles de piel
7. **No uniforme**: >0.3% de variación en la imagen

**Sistema de Puntuación**: Cada criterio cumplido suma 1 punto. Se requiere ≥5 puntos para detectar rostro.

El sistema es completamente automático y proporciona una experiencia de usuario fluida y eficiente.
