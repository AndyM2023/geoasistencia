# 🚀 IMPLEMENTACIÓN RÁPIDA - CAMBIO DE CONTRASEÑA

## **⏱️ TIEMPO ESTIMADO: 5-10 minutos**

---

## **📋 PASO 1: Crear la Vista en Django**

### **1.1. Abre tu archivo `views.py`** (o créalo si no existe)

### **1.2. Añade este código:**

```python
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
        
        # Validar campos
        if not current_password or not new_password:
            return Response(
                {'error': 'Se requieren ambos campos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar contraseña actual
        if not request.user.check_password(current_password):
            return Response(
                {'current_password': ['La contraseña actual es incorrecta']},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar nueva contraseña
        if len(new_password) < 8:
            return Response(
                {'new_password': ['Mínimo 8 caracteres']},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cambiar contraseña
        request.user.set_password(new_password)
        request.user.save()
        update_session_auth_hash(request, request.user)
        
        return Response({
            'message': 'Contraseña cambiada exitosamente',
            'success': True
        }, status=status.HTTP_200_OK)
```

---

## **📋 PASO 2: Añadir la URL**

### **2.1. Abre tu archivo `urls.py`**

### **2.2. Añade esta línea:**

```python
from django.urls import path
from .views import ChangePasswordView

urlpatterns = [
    # ... tus URLs existentes ...
    path('auth/change-password/', ChangePasswordView.as_view(), name='change_password'),
]
```

---

## **📋 PASO 3: Reiniciar Django**

### **3.1. Detén el servidor Django** (Ctrl+C)

### **3.2. Reinicia el servidor:**
```bash
python manage.py runserver
```

---

## **📋 PASO 4: Probar el Endpoint**

### **4.1. Usa el script de prueba:**
```bash
cd admin-frontend
python test_password_change.py
```

### **4.2. O prueba con Postman/Insomnia:**
```
POST http://127.0.0.1:8000/app/auth/change-password/
Authorization: Bearer TU_TOKEN
Content-Type: application/json

{
  "current_password": "contraseña_actual",
  "new_password": "NuevaContraseña123"
}
```

---

## **✅ VERIFICACIÓN**

### **Si funciona correctamente:**
- ✅ Status 200
- ✅ Mensaje de éxito
- ✅ Contraseña cambiada en la base de datos

### **Si hay errores:**
- ❌ 404: URL no configurada
- ❌ 401: Token inválido
- ❌ 400: Datos incorrectos

---

## **🔧 SOLUCIÓN DE PROBLEMAS**

### **Error 404:**
- Verifica que la URL esté en `urls.py`
- Asegúrate de que Django esté corriendo

### **Error 401:**
- Verifica que el token sea válido
- Asegúrate de estar logueado

### **Error 500:**
- Revisa la consola de Django
- Verifica que no haya errores de sintaxis

---

## **🎯 RESULTADO FINAL**

Una vez implementado:
1. **El frontend se conectará automáticamente** al backend
2. **Los cambios de contraseña serán reales** (no demo)
3. **Las contraseñas se actualizarán** en la base de datos
4. **Podrás iniciar sesión** con la nueva contraseña

---

## **📞 AYUDA**

Si tienes problemas:
1. **Revisa la consola de Django** para errores
2. **Usa el script de prueba** para debugging
3. **Verifica que las URLs** estén correctas
4. **Asegúrate de que Django** esté corriendo en puerto 8000

---

## **🚀 ¡LISTO!**

Tu sistema de cambio de contraseña estará funcionando completamente con el backend real.
