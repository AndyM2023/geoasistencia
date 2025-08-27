# Implementación: Cambio Obligatorio de Contraseña - GeoAsistencia

## 🎯 Objetivo

Implementar un sistema que **fuerce a los empleados a cambiar su contraseña** inmediatamente después de recibir el correo de bienvenida con sus credenciales, antes de poder usar el sistema.

## ✅ Funcionalidades Implementadas

### 1. **Campo en el Modelo User**
- **Nuevo campo**: `force_password_change` (BooleanField)
- **Valor por defecto**: `True` (debe cambiar contraseña)
- **Propósito**: Controlar si el usuario debe cambiar su contraseña

### 2. **Middleware de Seguridad**
- **Archivo**: `core/middleware.py`
- **Clase**: `ForcePasswordChangeMiddleware`
- **Funcionalidad**: 
  - Intercepta todas las requests autenticadas
  - Verifica si `force_password_change = True`
  - Redirige al cambio de contraseña si es necesario
  - Bloquea acceso a APIs hasta cambiar contraseña

### 3. **Signal Automático**
- **Archivo**: `core/signals.py`
- **Función**: `force_password_change_for_new_users`
- **Funcionalidad**: Marca automáticamente nuevos usuarios para cambio de contraseña

### 4. **Servicio de Correo Actualizado**
- **Archivo**: `core/services/employee_welcome_service.py`
- **Funcionalidad**: 
  - Marca `force_password_change = True` al enviar correo
  - Incluye información sobre cambio obligatorio

### 5. **Template de Correo Mejorado**
- **Archivo**: `core/templates/core/emails/employee_welcome_email.html`
- **Nuevas secciones**:
  - ⚠️ **AVISO IMPORTANTE**: Cambio Obligatorio de Contraseña
  - 🔒 Explicación clara de la obligatoriedad
  - 📋 Instrucciones actualizadas

### 6. **API de Verificación**
- **Endpoint**: `GET /api/auth/check-password-change/`
- **Funcionalidad**: Verifica si el usuario debe cambiar contraseña
- **Respuesta**: JSON con estado y mensaje

## 🔄 Flujo de Funcionamiento

### **Paso 1: Creación de Empleado**
1. Se crea el empleado en el sistema
2. **Signal automático** marca `force_password_change = True`
3. Se envía correo de bienvenida con credenciales

### **Paso 2: Correo de Bienvenida**
1. **Correo incluye**:
   - Credenciales de acceso
   - ⚠️ **AVISO IMPORTANTE** sobre cambio obligatorio
   - Instrucciones claras
2. **Usuario marcado** para cambio obligatorio

### **Paso 3: Primer Login del Empleado**
1. Empleado accede con credenciales del correo
2. **Middleware detecta** `force_password_change = True`
3. **Redirige automáticamente** a `/admin/password_change/`
4. **Bloquea acceso** a cualquier otra parte del sistema

### **Paso 4: Cambio de Contraseña**
1. Empleado **DEBE** cambiar su contraseña
2. **No puede continuar** hasta completar el cambio
3. Sistema valida nueva contraseña

### **Paso 5: Acceso al Sistema**
1. **Después del cambio**: `force_password_change = False`
2. Empleado puede usar el sistema normalmente
3. **Seguridad garantizada**

## 🛡️ Características de Seguridad

### **Protecciones Implementadas**
- ✅ **Middleware activo**: Bloquea todas las rutas hasta cambio de contraseña
- ✅ **API protegida**: Endpoints devuelven error 403 si no cambió contraseña
- ✅ **Redirección automática**: No hay forma de evadir el cambio
- ✅ **Logging completo**: Registra todos los intentos de acceso

### **URLs Exentas**
- `/admin/logout/` - Para poder cerrar sesión
- `/admin/password_change/` - Para cambiar contraseña
- `/admin/password_change/done/` - Confirmación de cambio
- `/api/auth/logout/` - Logout de API
- `/api/auth/password/change/` - Cambio de contraseña por API

## 📱 Uso en Frontend

### **Verificar Estado de Contraseña**
```javascript
// Verificar si debe cambiar contraseña
const checkPasswordChange = async () => {
  try {
    const response = await fetch('/api/auth/check-password-change/', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    const data = await response.json();
    
    if (data.force_password_change) {
      // Redirigir al cambio de contraseña
      window.location.href = '/admin/password_change/';
    }
  } catch (error) {
    console.error('Error verificando contraseña:', error);
  }
};
```

### **Manejo de Error 403**
```javascript
// Interceptar respuestas de API
if (response.status === 403 && data.error === 'password_change_required') {
  // Usuario debe cambiar contraseña
  showPasswordChangeModal();
  return;
}
```

## 🔧 Configuración

### **Settings.py**
```python
MIDDLEWARE = [
    # ... otros middlewares ...
    'core.middleware.ForcePasswordChangeMiddleware',  # Añadido
]
```

### **Modelo User**
```python
class User(AbstractUser):
    # ... otros campos ...
    force_password_change = models.BooleanField(
        default=True, 
        verbose_name='Forzar Cambio de Contraseña',
        help_text='¿El usuario debe cambiar su contraseña en el próximo login?'
    )
```

## 📊 Beneficios de Seguridad

### **1. Cumplimiento de Estándares**
- ✅ **ISO 27001**: Gestión de contraseñas
- ✅ **NIST**: Cambio obligatorio en primer login
- ✅ **GDPR**: Protección de datos personales

### **2. Prevención de Riesgos**
- 🚫 **Credenciales temporales** no pueden ser usadas permanentemente
- 🚫 **Acceso no autorizado** bloqueado hasta cambio de contraseña
- 🚫 **Reutilización de contraseñas** del correo imposible

### **3. Auditoría y Trazabilidad**
- 📝 **Log completo** de cambios de contraseña
- 📝 **Registro** de intentos de acceso
- 📝 **Historial** de modificaciones de seguridad

## 🧪 Pruebas

### **Escenario 1: Usuario Nuevo**
1. Crear empleado
2. Verificar `force_password_change = True`
3. Intentar acceder al sistema
4. Confirmar redirección a cambio de contraseña

### **Escenario 2: Usuario Existente**
1. Usuario ya cambió contraseña
2. Verificar `force_password_change = False`
3. Confirmar acceso normal al sistema

### **Escenario 3: API Protection**
1. Usuario con contraseña sin cambiar
2. Intentar llamar API
3. Confirmar error 403 con mensaje apropiado

## 🚀 Próximos Pasos

### **Mejoras Futuras**
- 🔐 **Política de contraseñas** configurable
- 📅 **Expiración automática** de contraseñas
- 🔔 **Notificaciones** antes de expiración
- 📊 **Dashboard de seguridad** para administradores

### **Integración Frontend**
- 🎨 **Modal de cambio** de contraseña en Vue.js
- 🔄 **Verificación automática** en cada login
- 📱 **Responsive design** para móviles

## 📞 Soporte

Para dudas o problemas con la implementación:
- **Revisar logs** de Django
- **Verificar middleware** en settings.py
- **Comprobar migraciones** aplicadas
- **Testear endpoints** de API

---

**🎯 Resultado**: Sistema completamente seguro que **fuerza el cambio de contraseña** en el primer login, cumpliendo estándares internacionales de seguridad.
