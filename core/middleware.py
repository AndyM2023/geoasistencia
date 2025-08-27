from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from rest_framework import status

class ForcePasswordChangeMiddleware(MiddlewareMixin):
    """
    Middleware para forzar el cambio de contraseña en el primer login
    """
    
    def process_request(self, request):
        # Solo verificar para usuarios autenticados
        if not request.user.is_authenticated:
            return None
            
        # URLs que están exentas de la verificación de cambio de contraseña
        exempt_urls = [
            '/admin/logout/',
            '/admin/password_change/',
            '/admin/password_change/done/',
            '/api/auth/logout/',
            '/api/auth/password/change/',
            '/api/auth/password/reset/',
            '/api/auth/password/reset/confirm/',
            '/api/auth/password/reset/validate/',
            '/api/employees/password-reset/',
            '/api/employees/password-reset/confirm/',
            '/api/employees/password-reset/validate/',
        ]
        
        # Verificar si la URL actual está exenta
        current_path = request.path
        if any(current_path.startswith(url) for url in exempt_urls):
            return None
            
        # Verificar si el usuario debe cambiar su contraseña
        force_change = getattr(request.user, 'force_password_change', False)
        
        if force_change:
            # URLs específicas que deben ser bloqueadas para usuarios con contraseña temporal
            blocked_urls = [
                '/api/attendance/mark_attendance/',  # Bloquear registro de asistencia
                '/api/attendance/',  # Bloquear acceso a asistencias
                '/api/dashboard/',  # Bloquear acceso al dashboard
                '/api/employees/me/',  # Bloquear información del empleado
            ]
            
            # Si es una API call a una URL bloqueada, devolver error JSON
            if current_path.startswith('/api/') and any(current_path.startswith(url) for url in blocked_urls):
                return JsonResponse({
                    'error': 'Cambio de contraseña requerido',
                    'message': 'Debes cambiar tu contraseña antes de poder usar el sistema',
                    'force_password_change': True,
                    'blocked_action': 'attendance_registration' if 'attendance' in current_path else 'system_access',
                    'details': 'Por seguridad, no puedes registrar asistencia ni acceder al sistema hasta cambiar tu contraseña temporal'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Para otras URLs, redirigir al cambio de contraseña
            if current_path.startswith('/api/'):
                return JsonResponse({
                    'error': 'Cambio de contraseña requerido',
                    'message': 'Debes cambiar tu contraseña antes de continuar',
                    'force_password_change': True
                }, status=status.HTTP_403_FORBIDDEN)
            else:
                # Para URLs no-API, redirigir al cambio de contraseña
                messages.warning(request, 'Debes cambiar tu contraseña antes de continuar')
                return redirect('admin:password_change')
        
        return None
