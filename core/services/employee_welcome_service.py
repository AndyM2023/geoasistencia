import logging
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from ..models import Employee, User, PasswordResetToken
from ..services.password_reset_service import PasswordResetService

logger = logging.getLogger(__name__)

class EmployeeWelcomeService:
    """Servicio para enviar emails de bienvenida a empleados con sus credenciales"""
    
    @staticmethod
    def send_welcome_email(employee, username, password):
        """Enviar email de bienvenida completo con credenciales y enlace de cambio de contraseña"""
        try:
            # Verificar que el empleado tenga email
            if not employee.user.email:
                logger.warning(f"Empleado {employee.full_name} no tiene email configurado")
                return False
            
            # Crear token de cambio de contraseña obligatorio
            try:
                # Usar el servicio existente de PasswordResetService para crear el token
                token = PasswordResetService.create_reset_token(employee.user)
                
                # Generar URL para cambio de contraseña
                reset_url = f"{settings.FRONTEND_URL}/change-password?token={token.token}&force_change=true"
                
                logger.info(f"✅ Token de cambio de contraseña creado para {employee.full_name}")
                
            except Exception as token_error:
                logger.error(f"❌ Error creando token de cambio de contraseña: {token_error}")
                # Si falla la creación del token, continuar sin él
                reset_url = None
            
            # Preparar contexto para el template
            context = {
                'employee': employee,
                'username': username,
                'password': password,
                'app_name': 'GEOASISTENCIA ADMIN',
                'login_url': 'http://localhost:5173/admin/login',  # Cambiar en producción
                'force_password_change': True,
                'reset_url': reset_url
            }
            
            # Renderizar template HTML
            html_message = render_to_string('core/emails/employee_welcome_email.html', context)
            plain_message = strip_tags(html_message)
            
            # Enviar email usando la misma configuración que password_reset_service
            send_mail(
                subject=f'¡Bienvenido a {context["app_name"]}! - Tus Credenciales de Acceso',
                message=plain_message,
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[employee.user.email],
                fail_silently=False,
            )
            
            # Marcar que el usuario debe cambiar su contraseña
            employee.user.force_password_change = True
            employee.user.save(update_fields=['force_password_change'])
            
            logger.info(f"✅ Email de bienvenida enviado exitosamente a {employee.user.email}")
            print(f"📧 Email de bienvenida enviado a {employee.user.email}")
            print(f"🔐 Usuario marcado para cambio obligatorio de contraseña")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error enviando email de bienvenida: {str(e)}")
            print(f"❌ Error enviando email de bienvenida: {str(e)}")
            return False
