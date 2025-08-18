# Implementación del Backend para Cambio de Contraseña

## Problema Actual
El frontend está configurado correctamente para cambiar contraseñas, pero el endpoint `/app/auth/change-password/` no existe en el backend Django, causando un error 404.

## Solución Implementada
Se ha añadido un **modo demostración** que simula el cambio de contraseña exitoso mientras se implementa el backend.

## Configuración del Backend Django

### 1. Crear la Vista (View)
```python
# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth import update_session_auth_hash

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        
        # Validar que se proporcionen ambos campos
        if not current_password or not new_password:
            return Response(
                {'error': 'Se requieren tanto la contraseña actual como la nueva'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar contraseña actual
        if not request.user.check_password(current_password):
            return Response(
                {'current_password': ['La contraseña actual es incorrecta']},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar nueva contraseña (mínimo 8 caracteres)
        if len(new_password) < 8:
            return Response(
                {'new_password': ['La contraseña debe tener al menos 8 caracteres']},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cambiar contraseña
        request.user.set_password(new_password)
        request.user.save()
        
        # Actualizar sesión para evitar logout automático
        update_session_auth_hash(request, request.user)
        
        return Response({
            'message': 'Contraseña cambiada exitosamente',
            'success': True
        }, status=status.HTTP_200_OK)
```

### 2. Añadir la URL
```python
# urls.py
from django.urls import path
from .views import ChangePasswordView

urlpatterns = [
    # ... otras URLs existentes ...
    path('auth/change-password/', ChangePasswordView.as_view(), name='change_password'),
]
```

### 3. Configurar Serializer (Opcional)
```python
# serializers.py
from rest_framework import serializers

class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    
    def validate_new_password(self, value):
        # Validaciones adicionales si es necesario
        if len(value) < 8:
            raise serializers.ValidationError("La contraseña debe tener al menos 8 caracteres")
        return value
```

## Activación del Backend

### 1. Desactivar Modo Demo
En `ProfileModal.vue`, cambiar:
```javascript
const demoMode = true  // ← Cambiar a false
```

### 2. Verificar Endpoint
El endpoint debe estar disponible en:
```
http://127.0.0.1:8000/app/auth/change-password/
```

### 3. Probar con Postman/Insomnia
```http
POST http://127.0.0.1:8000/app/auth/change-password/
Authorization: Bearer <token>
Content-Type: application/json

{
  "current_password": "contraseña_actual",
  "new_password": "nueva_contraseña123"
}
```

## Estructura de Respuesta Esperada

### Éxito (200)
```json
{
  "message": "Contraseña cambiada exitosamente",
  "success": true
}
```

### Error (400)
```json
{
  "current_password": ["La contraseña actual es incorrecta"]
}
```

o

```json
{
  "new_password": ["La contraseña debe tener al menos 8 caracteres"]
}
```

## Notas Importantes

1. **Seguridad**: El endpoint requiere autenticación (`IsAuthenticated`)
2. **Validación**: Se valida la contraseña actual antes de permitir el cambio
3. **Sesión**: Se actualiza la sesión para evitar logout automático
4. **Logs**: El frontend ya incluye logs detallados para debugging

## Estado Actual
- ✅ Frontend completamente implementado
- ✅ Validaciones funcionando
- ✅ Manejo de errores implementado
- ✅ Modo demo activo
- ❌ Backend endpoint pendiente de implementación

## Próximos Pasos
1. Implementar `ChangePasswordView` en Django
2. Añadir la URL al archivo de rutas
3. Probar el endpoint
4. Desactivar modo demo
5. Verificar funcionamiento completo
