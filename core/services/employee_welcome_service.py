import logging
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from ..models import Employee, User

logger = logging.getLogger(__name__)

class EmployeeWelcomeService:
    """Servicio para enviar emails de bienvenida a empleados con sus credenciales"""
    
    @staticmethod
    def send_welcome_email(employee, username, password):
        """Enviar email de bienvenida completo con credenciales después del registro facial"""
        try:
            # Verificar que el empleado tenga email
            if not employee.user.email:
                logger.warning(f"Empleado {employee.full_name} no tiene email configurado")
                return False
            
            # Contexto para el template
            context = {
                'employee': employee,
                'username': username,
                'password': password,
                'app_name': 'GEOASISTENCIA ADMIN',
                'login_url': 'http://localhost:5173/admin/login'  # Cambiar en producción
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
            
            logger.info(f"Email de bienvenida enviado a {employee.user.email} para empleado {employee.full_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email de bienvenida: {str(e)}")
            raise
