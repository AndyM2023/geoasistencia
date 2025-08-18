# ============================================================================
# IMPLEMENTACIÓN COMPLETA DEL BACKEND DJANGO PARA CAMBIO DE CONTRASEÑA
# ============================================================================
# 
# INSTRUCCIONES:
# 1. Copia este código en tu proyecto Django
# 2. Asegúrate de que las importaciones sean correctas
# 3. Reinicia el servidor Django
# 4. Prueba el endpoint
#
# ============================================================================

# ============================================================================
# 1. VISTA (VIEW) - Crear en tu app de Django (ej: views.py)
# ============================================================================

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
import logging

# Configurar logging para debugging
logger = logging.getLogger(__name__)

class ChangePasswordView(APIView):
    """
    Vista para cambiar la contraseña del usuario autenticado.
    Requiere autenticación y valida la contraseña actual.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            logger.info(f"🔐 Cambio de contraseña solicitado para usuario: {request.user.username}")
            
            # Obtener datos del request
            current_password = request.data.get('current_password')
            new_password = request.data.get('new_password')
            
            logger.info(f"🔍 Datos recibidos - current_password: {'***' if current_password else 'vacío'}, new_password: {'***' if new_password else 'vacío'}")
            
            # Validar que se proporcionen ambos campos
            if not current_password or not new_password:
                logger.warning("⚠️ Campos de contraseña faltantes")
                return Response(
                    {
                        'error': 'Se requieren tanto la contraseña actual como la nueva',
                        'detail': 'Ambos campos current_password y new_password son obligatorios'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validar contraseña actual
            if not request.user.check_password(current_password):
                logger.warning(f"⚠️ Contraseña actual incorrecta para usuario: {request.user.username}")
                return Response(
                    {
                        'current_password': ['La contraseña actual es incorrecta'],
                        'detail': 'La contraseña actual proporcionada no coincide con la registrada'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validar nueva contraseña (mínimo 8 caracteres)
            if len(new_password) < 8:
                logger.warning(f"⚠️ Nueva contraseña muy corta para usuario: {request.user.username}")
                return Response(
                    {
                        'new_password': ['La contraseña debe tener al menos 8 caracteres'],
                        'detail': 'La nueva contraseña no cumple con los requisitos mínimos de seguridad'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validar que la nueva contraseña sea diferente a la actual
            if current_password == new_password:
                logger.warning(f"⚠️ Nueva contraseña igual a la actual para usuario: {request.user.username}")
                return Response(
                    {
                        'new_password': ['La nueva contraseña debe ser diferente a la actual'],
                        'detail': 'No puedes usar la misma contraseña'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Cambiar contraseña
            logger.info(f"🔄 Cambiando contraseña para usuario: {request.user.username}")
            request.user.set_password(new_password)
            request.user.save()
            
            # Actualizar sesión para evitar logout automático
            update_session_auth_hash(request, request.user)
            
            logger.info(f"✅ Contraseña cambiada exitosamente para usuario: {request.user.username}")
            
            return Response({
                'message': 'Contraseña cambiada exitosamente',
                'success': True,
                'detail': 'Tu contraseña ha sido actualizada. La sesión se mantendrá activa.'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"❌ Error inesperado cambiando contraseña: {str(e)}")
            return Response(
                {
                    'error': 'Error interno del servidor',
                    'detail': 'Ocurrió un error inesperado al cambiar la contraseña'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ============================================================================
# 2. SERIALIZER (OPCIONAL) - Crear en serializers.py
# ============================================================================

from rest_framework import serializers

class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer para validar los datos de cambio de contraseña.
    """
    current_password = serializers.CharField(
        required=True,
        write_only=True,
        help_text="Contraseña actual del usuario"
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        min_length=8,
        help_text="Nueva contraseña (mínimo 8 caracteres)"
    )
    
    def validate_new_password(self, value):
        """
        Validación personalizada para la nueva contraseña.
        """
        if len(value) < 8:
            raise serializers.ValidationError("La contraseña debe tener al menos 8 caracteres")
        
        # Validar que contenga al menos una letra mayúscula, una minúscula y un número
        if not any(c.isupper() for c in value):
            raise serializers.ValidationError("La contraseña debe contener al menos una letra mayúscula")
        
        if not any(c.islower() for c in value):
            raise serializers.ValidationError("La contraseña debe contener al menos una letra minúscula")
        
        if not any(c.isdigit() for c in value):
            raise serializers.ValidationError("La contraseña debe contener al menos un número")
        
        return value
    
    def validate(self, data):
        """
        Validación que requiere ambos campos.
        """
        if not data.get('current_password'):
            raise serializers.ValidationError("La contraseña actual es requerida")
        
        if not data.get('new_password'):
            raise serializers.ValidationError("La nueva contraseña es requerida")
        
        return data

# ============================================================================
# 3. URLS - Añadir en urls.py
# ============================================================================

# En tu archivo urls.py principal o en la app correspondiente:
"""
from django.urls import path, include
from .views import ChangePasswordView

urlpatterns = [
    # ... otras URLs existentes ...
    path('auth/change-password/', ChangePasswordView.as_view(), name='change_password'),
]
"""

# ============================================================================
# 4. CONFIGURACIÓN DE LOGGING (OPCIONAL) - En settings.py
# ============================================================================

"""
# Añadir en settings.py para debugging detallado
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        'your_app_name': {  # Reemplaza con el nombre de tu app
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
    },
}
"""

# ============================================================================
# 5. PRUEBAS - Comandos para probar
# ============================================================================

"""
# Probar con curl:
curl -X POST http://127.0.0.1:8000/app/auth/change-password/ \
  -H "Authorization: Bearer TU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "contraseña_actual",
    "new_password": "NuevaContraseña123"
  }'

# Probar con Python requests:
import requests

url = "http://127.0.0.1:8000/app/auth/change-password/"
headers = {
    "Authorization": "Bearer TU_TOKEN_AQUI",
    "Content-Type": "application/json"
}
data = {
    "current_password": "contraseña_actual",
    "new_password": "NuevaContraseña123"
}

response = requests.post(url, json=data, headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
"""

# ============================================================================
# 6. VERIFICACIÓN DE IMPLEMENTACIÓN
# ============================================================================

"""
# Para verificar que el endpoint esté funcionando:

1. Reinicia el servidor Django
2. Verifica que no haya errores de sintaxis
3. Prueba el endpoint con Postman/Insomnia
4. Verifica los logs en la consola
5. Prueba desde el frontend

# URLs que deberían funcionar:
- http://127.0.0.1:8000/app/auth/change-password/ (POST)
- http://127.0.0.1:8000/app/auth/login/ (POST)
- http://127.0.0.1:8000/app/auth/me/ (GET)

# Si hay errores 404, verifica:
- Que las URLs estén correctamente configuradas
- Que el servidor Django esté corriendo en el puerto 8000
- Que el proxy de Vite esté configurado correctamente
"""

# ============================================================================
# 7. SOLUCIÓN DE PROBLEMAS COMUNES
# ============================================================================

"""
# Error 404: Endpoint no encontrado
- Verifica que la URL esté en el archivo urls.py correcto
- Asegúrate de que la app esté incluida en INSTALLED_APPS
- Verifica que el servidor Django esté corriendo

# Error 401: No autorizado
- Verifica que el token de autenticación sea válido
- Asegúrate de que el usuario esté autenticado

# Error 500: Error interno del servidor
- Revisa los logs de Django
- Verifica que no haya errores de sintaxis
- Asegúrate de que todas las importaciones sean correctas

# Error de CORS
- Verifica la configuración de CORS en Django
- Asegúrate de que el proxy de Vite esté funcionando
"""

print("✅ Archivo de implementación del backend creado correctamente")
print("📋 Sigue las instrucciones para implementar el cambio de contraseña")
print("🚀 Una vez implementado, el frontend se conectará automáticamente al backend")
