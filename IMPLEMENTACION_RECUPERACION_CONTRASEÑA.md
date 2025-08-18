# 🔐 Implementación de Recuperación de Contraseña - Geoasistencia Admin

## 📋 Resumen

Se ha implementado un sistema completo de recuperación de contraseña para administradores que incluye:

- **Backend Django**: Endpoints para solicitar y confirmar recuperación de contraseña
- **Frontend Vue.js**: Vistas para solicitar recuperación y cambiar contraseña
- **Sistema de Email**: Envío automático de emails con enlaces de recuperación
- **Tokens Seguros**: Sistema de tokens únicos con expiración automática

## 🏗️ Arquitectura del Sistema

### Backend (Django)
```
core/
├── models.py                    # Modelo PasswordResetToken
├── serializers.py              # Serializers para validación
├── services/
│   └── password_reset_service.py  # Lógica de negocio
├── views.py                    # Endpoints de la API
└── urls.py                     # Rutas del backend
```

### Frontend (Vue.js)
```
admin-frontend/src/
├── views/
│   ├── ForgotPassword.vue      # Solicitar recuperación
│   └── ResetPassword.vue       # Cambiar contraseña
├── services/
│   └── authService.js          # Servicios de autenticación
└── router/
    └── index.js                # Rutas del frontend
```

## 🚀 Endpoints de la API

### 1. Solicitar Recuperación de Contraseña
```
POST /api/password-reset/request_reset/
Content-Type: application/json

{
  "email": "admin@ejemplo.com"
}
```

**Respuesta Exitosa:**
```json
{
  "message": "Se ha enviado un email con instrucciones para recuperar tu contraseña.",
  "email": "admin@ejemplo.com"
}
```

### 2. Validar Token de Recuperación
```
GET /api/password-reset/validate_token/?token=uuid-token
```

**Respuesta Exitosa:**
```json
{
  "valid": true,
  "user_email": "admin@ejemplo.com",
  "expires_at": "2025-08-17T21:40:00Z"
}
```

### 3. Confirmar Cambio de Contraseña
```
POST /api/password-reset/confirm_reset/
Content-Type: application/json

{
  "token": "uuid-token",
  "new_password": "nueva_contraseña123",
  "confirm_password": "nueva_contraseña123"
}
```

**Respuesta Exitosa:**
```json
{
  "message": "Tu contraseña ha sido cambiada exitosamente. Ya puedes iniciar sesión con tu nueva contraseña."
}
```

## ⚙️ Configuración de Email

### 1. Variables de Entorno
Crea un archivo `.env` en la raíz del proyecto con:

```bash
# Configuración SMTP
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False

# Credenciales
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=tu_contraseña_de_aplicacion

# Remitente
DEFAULT_FROM_EMAIL=tu_email@gmail.com
SERVER_EMAIL=tu_email@gmail.com
```

### 2. Configuración para Gmail
1. Activa la verificación en dos pasos en tu cuenta de Google
2. Ve a "Seguridad" > "Contraseñas de aplicación"
3. Genera una nueva contraseña para "Django"
4. Usa esa contraseña en `EMAIL_HOST_PASSWORD`

### 3. Configuración para Otros Proveedores

#### Outlook/Hotmail
```bash
EMAIL_HOST=smtp-mail.outlook.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

#### Yahoo
```bash
EMAIL_HOST=smtp.mail.yahoo.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

## 🔒 Seguridad del Sistema

### Características de Seguridad
- **Tokens Únicos**: Cada solicitud genera un token UUID único
- **Expiración Automática**: Los tokens expiran en 1 hora
- **Uso Único**: Los tokens se invalidan después del primer uso
- **Validación de Email**: Solo funciona con cuentas de administrador activas
- **Limpieza Automática**: Los tokens expirados se eliminan automáticamente

### Flujo de Seguridad
1. Usuario solicita recuperación con email
2. Sistema valida que el email pertenezca a un administrador activo
3. Se genera un token único con expiración
4. Se envía email con enlace seguro
5. Usuario hace clic en el enlace y valida el token
6. Se permite cambiar la contraseña solo si el token es válido
7. El token se invalida después del uso

## 📱 Flujo de Usuario

### 1. Solicitar Recuperación
1. Usuario hace clic en "¿Olvidaste tu contraseña?" en el login
2. Se redirige a `/forgot-password`
3. Usuario ingresa su email de administrador
4. Sistema valida el email y envía instrucciones por correo

### 2. Recibir Email
1. Usuario recibe email con enlace de recuperación
2. El email incluye:
   - Botón de acción directa
   - Enlace copiable
   - Información de expiración
   - Advertencias de seguridad

### 3. Cambiar Contraseña
1. Usuario hace clic en el enlace del email
2. Se redirige a `/reset-password?token=uuid`
3. Sistema valida el token automáticamente
4. Si es válido, se muestra formulario de nueva contraseña
5. Usuario ingresa y confirma nueva contraseña
6. Sistema cambia la contraseña y redirige al login

## 🛠️ Instalación y Configuración

### 1. Backend
```bash
# Aplicar migraciones
python manage.py migrate

# Verificar que el modelo PasswordResetToken se creó
python manage.py shell
>>> from core.models import PasswordResetToken
>>> PasswordResetToken.objects.all()
```

### 2. Frontend
```bash
# Las nuevas vistas ya están incluidas
# Verificar que las rutas funcionen
npm run dev
# Navegar a /forgot-password y /reset-password
```

### 3. Configuración de Email
```bash
# Copiar configuración de ejemplo
cp email_config_example.txt .env

# Editar .env con tus credenciales
# Reiniciar Django después de cambios
```

## 🧪 Pruebas del Sistema

### 1. Prueba de Solicitud
```bash
# Usar curl o Postman
curl -X POST http://localhost:8000/api/password-reset/request_reset/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@ejemplo.com"}'
```

### 2. Prueba de Validación
```bash
# Obtener token del email o base de datos
curl "http://localhost:8000/api/password-reset/validate_token/?token=TOKEN_AQUI"
```

### 3. Prueba de Confirmación
```bash
curl -X POST http://localhost:8000/api/password-reset/confirm_reset/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "TOKEN_AQUI",
    "new_password": "nueva123",
    "confirm_password": "nueva123"
  }'
```

## 🔍 Monitoreo y Logs

### Logs del Sistema
El sistema registra todas las operaciones importantes:

```python
# Ejemplos de logs
logger.info(f"Token de recuperación creado para usuario {user.username}")
logger.info(f"Email de recuperación enviado a {user.email}")
logger.info(f"Contraseña reseteada exitosamente para usuario {user.username}")
logger.error(f"Error enviando email de recuperación: {str(e)}")
```

### Métricas de Uso
- Tokens creados por día
- Emails enviados exitosamente
- Contraseñas reseteadas
- Errores de validación

## 🚨 Solución de Problemas

### Problemas Comunes

#### 1. Email no se envía
- Verificar configuración SMTP
- Revisar credenciales de email
- Verificar logs de Django
- Comprobar firewall/antivirus

#### 2. Token inválido
- Verificar que no haya expirado
- Comprobar que no se haya usado
- Revisar formato del token en la URL

#### 3. Error de migración
- Eliminar migraciones problemáticas
- Crear migración limpia solo para PasswordResetToken
- Verificar consistencia del modelo

### Debug del Sistema
```python
# En Django shell
from core.services.password_reset_service import PasswordResetService
from core.models import User, PasswordResetToken

# Verificar usuario administrador
admin_user = User.objects.filter(role='admin', is_active=True).first()
print(f"Admin encontrado: {admin_user.email}")

# Verificar tokens existentes
tokens = PasswordResetToken.objects.all()
print(f"Tokens existentes: {tokens.count()}")
```

## 📈 Mejoras Futuras

### Funcionalidades Adicionales
- **Notificaciones SMS**: Envío de códigos por SMS
- **Preguntas de Seguridad**: Verificación adicional con preguntas
- **Historial de Cambios**: Registro de cambios de contraseña
- **Políticas de Contraseña**: Validación de fortaleza de contraseña
- **Autenticación de Dos Factores**: 2FA para administradores

### Optimizaciones
- **Cache de Tokens**: Almacenamiento en Redis para mejor rendimiento
- **Rate Limiting**: Límites de solicitudes por IP
- **Webhooks**: Notificaciones en tiempo real
- **Analytics**: Métricas detalladas de uso

## 📞 Soporte

Para problemas o preguntas sobre la implementación:

1. Revisar logs del sistema
2. Verificar configuración de email
3. Comprobar que las migraciones se aplicaron correctamente
4. Validar que el usuario sea administrador activo

---

**Nota**: Este sistema está diseñado específicamente para administradores del sistema Geoasistencia. Los empleados regulares no pueden usar esta funcionalidad.
