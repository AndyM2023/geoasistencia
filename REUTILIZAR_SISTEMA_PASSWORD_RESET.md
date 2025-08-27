# 🔄 Reutilizar Sistema de Recuperación de Contraseña Existente

## 🎯 Objetivo
Reutilizar el sistema de recuperación de contraseña que ya tienes implementado para el cambio obligatorio de contraseña de empleados.

## ✅ Ventajas de Reutilizar el Sistema Existente

1. **No duplicar código** - Aprovechar la funcionalidad ya probada
2. **Consistencia** - Mismo flujo para recuperación y cambio obligatorio
3. **Mantenimiento** - Un solo lugar para actualizaciones
4. **Seguridad** - Mismos estándares de seguridad ya implementados

## 🔍 Sistema Actual Disponible

### **Endpoints Existentes:**
- `POST /api/employees/password-reset/request/` - Solicitar reset
- `POST /api/employees/password-reset/confirm/` - Confirmar reset
- `GET /api/employees/password-reset/validate/` - Validar token

### **Servicios Disponibles:**
- `EmployeePasswordResetService.create_reset_token()`
- `EmployeePasswordResetService.send_reset_email()`
- `EmployeePasswordResetService.reset_password()`

## 🚀 Implementación Recomendada

### **Opción 1: Reutilizar Endpoint Existente (RECOMENDADA)**

El empleado hace clic en el enlace del correo que lleva a:
```
http://localhost:5173/change-password?token=ABC123&force_change=true
```

**En el frontend:**
1. **Detectar parámetro `force_change=true`**
2. **Usar el componente existente** de cambio de contraseña
3. **Mostrar mensaje específico** para cambio obligatorio
4. **Usar el endpoint existente** `/api/employees/password-reset/confirm/`

### **Opción 2: Crear Endpoint Específico**

Si prefieres separar la lógica, crear:
```
POST /api/employees/force-password-change/
```

## 💡 Implementación en el Frontend

### **Componente Vue.js:**
```vue
<template>
  <div class="password-change-form">
    <!-- Detectar si es cambio obligatorio -->
    <div v-if="isForceChange" class="force-change-alert">
      <h2>🔒 Cambio Obligatorio de Contraseña</h2>
      <p>Por seguridad, debes cambiar tu contraseña antes de usar el sistema.</p>
    </div>
    
    <!-- Usar el formulario existente -->
    <PasswordResetForm 
      :token="token"
      :is-force-change="isForceChange"
      @success="handlePasswordChanged"
    />
  </div>
</template>

<script>
export default {
  data() {
    return {
      token: null,
      isForceChange: false
    }
  },
  mounted() {
    // Obtener parámetros de la URL
    const urlParams = new URLSearchParams(window.location.search)
    this.token = urlParams.get('token')
    this.isForceChange = urlParams.get('force_change') === 'true'
  },
  methods: {
    handlePasswordChanged() {
      if (this.isForceChange) {
        // Redirigir al dashboard o login
        this.$router.push('/dashboard')
      }
    }
  }
}
</script>
```

### **Composables:**
```javascript
// usePasswordReset.js - Reutilizar el existente
export const usePasswordReset = () => {
  const resetPassword = async (token, newPassword) => {
    try {
      const response = await api.post('/employees/password-reset/confirm/', {
        token,
        new_password: newPassword
      })
      
      // Si es cambio obligatorio, actualizar estado del usuario
      if (response.data.force_change_resolved) {
        // Marcar que ya no necesita cambiar contraseña
        await api.post('/auth/update-password-status/', {
          force_password_change: false
        })
      }
      
      return response
    } catch (error) {
      throw error
    }
  }
  
  return { resetPassword }
}
```

## 🔧 Modificaciones Necesarias

### **1. Backend - Marcar contraseña como cambiada:**
```python
# En el endpoint de confirmación existente
@action(detail=False, methods=['post'])
def confirm_reset(self, request):
    try:
        # ... código existente ...
        
        # Resetear contraseña
        EmployeePasswordResetService.reset_password(token_string, new_password)
        
        # Si es cambio obligatorio, marcar como resuelto
        if request.data.get('force_change'):
            user.force_password_change = False
            user.save(update_fields=['force_password_change'])
        
        return Response({
            'message': 'Contraseña cambiada exitosamente',
            'force_change_resolved': request.data.get('force_change', False)
        })
        
    except Exception as e:
        # ... manejo de errores ...
```

### **2. Frontend - Detectar cambio obligatorio:**
```javascript
// En el componente de cambio de contraseña
const handleSubmit = async () => {
  try {
    const response = await resetPassword(token, newPassword, {
      force_change: isForceChange
    })
    
    if (response.data.force_change_resolved) {
      showSuccess('✅ Contraseña cambiada. Ya puedes usar el sistema.')
      // Redirigir al dashboard
      router.push('/dashboard')
    } else {
      showSuccess('✅ Contraseña cambiada exitosamente.')
      // Redirigir al login
      router.push('/login')
    }
  } catch (error) {
    showError('Error al cambiar contraseña')
  }
}
```

## 🎨 Personalización del UI

### **Estilos para Cambio Obligatorio:**
```css
.force-change-alert {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
  color: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  text-align: center;
}

.force-change-alert h2 {
  margin: 0 0 10px 0;
  font-size: 24px;
}

.force-change-alert p {
  margin: 0;
  opacity: 0.9;
}
```

## 🔐 Flujo Completo

1. **Empleado recibe correo** con enlace: `/change-password?token=ABC&force_change=true`
2. **Frontend detecta** `force_change=true`
3. **Muestra mensaje** de cambio obligatorio
4. **Usa formulario existente** de cambio de contraseña
5. **Llama endpoint existente** `/employees/password-reset/confirm/`
6. **Backend marca** `force_password_change = False`
7. **Frontend redirige** al dashboard
8. **Empleado puede usar** el sistema normalmente

## ✅ Beneficios de esta Implementación

- **Reutiliza código** existente y probado
- **Mantiene consistencia** en el flujo de cambio de contraseña
- **Fácil mantenimiento** - un solo lugar para cambios
- **Misma seguridad** - mismos estándares ya implementados
- **Rápida implementación** - solo modificaciones menores

## 🚀 Próximos Pasos

1. **Implementar detección** de `force_change` en el frontend
2. **Modificar endpoint** existente para manejar cambio obligatorio
3. **Actualizar UI** para mostrar mensaje específico
4. **Probar flujo completo** desde correo hasta dashboard
5. **Verificar bloqueo** del sistema hasta cambio de contraseña
