import logging
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from ..models import User, PasswordResetToken

logger = logging.getLogger(__name__)

class EmployeePasswordResetService:
    """Servicio para manejar la recuperación de contraseña de empleados"""
    
    @staticmethod
    def create_reset_token(user):
        """Crear un token de recuperación para el empleado"""
        try:
            # Verificar que el usuario sea un empleado
            if user.role != 'employee':
                raise ValueError('Solo los empleados pueden solicitar recuperación de contraseña')
            
            # Invalidar tokens anteriores del usuario
            PasswordResetToken.objects.filter(user=user, is_used=False).update(is_used=True)
            
            # Crear nuevo token
            token = PasswordResetToken.objects.create(
                user=user,
                expires_at=timezone.localtime() + timedelta(hours=1)
            )
            
            logger.info(f"Token de recuperación creado para empleado {user.username}")
            return token
            
        except Exception as e:
            logger.error(f"Error creando token de recuperación para empleado: {str(e)}")
            raise
    
    @staticmethod
    def send_reset_email(user, token):
        """Enviar email de recuperación de contraseña para empleados"""
        try:
            # Verificar si ya se envió un email recientemente para este usuario
            from django.utils import timezone
            from datetime import timedelta
            
            # Buscar tokens recientes del mismo usuario (últimos 5 minutos)
            recent_tokens = PasswordResetToken.objects.filter(
                user=user,
                created_at__gte=timezone.localtime() - timedelta(minutes=5)
            ).order_by('-created_at')
            
            if recent_tokens.count() > 1:
                logger.warning(f"Empleado {user.username} ya tiene un token reciente. Evitando envío duplicado.")
                return True  # Retornar True para evitar error, pero no enviar email
            
            # URL del frontend para reset de contraseña de empleados
            frontend_url = "http://localhost:5173"  # Cambiar en producción
            reset_url = f"{frontend_url}/employee/reset-password?token={token.token}"
            
            # Contexto para el template
            context = {
                'user': user,
                'reset_url': reset_url,
                'expires_at': token.expires_at,
                'app_name': 'GEOASISTENCIA EMPLEADOS'
            }
            
            # Renderizar template HTML
            html_message = render_to_string('core/emails/employee_password_reset_email.html', context)
            plain_message = strip_tags(html_message)
            
            # Enviar email usando send_mail con HTML
            from django.core.mail import send_mail
            
            # Enviar email con HTML y texto plano
            send_mail(
                subject=f'Recuperación de Contraseña - {context["app_name"]}',
                message=plain_message,  # Versión texto plano
                html_message=html_message,  # Versión HTML
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            
            logger.info(f"Email de recuperación enviado a empleado {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email de recuperación para empleado: {str(e)}")
            raise
    
    @staticmethod
    def validate_token(token_string):
        """Validar un token de recuperación de empleado"""
        try:
            token = PasswordResetToken.objects.get(token=token_string)
            
            # Verificar que el usuario sea un empleado
            if token.user.role != 'employee':
                logger.warning(f"Token de recuperación usado por usuario no empleado: {token.user.username}")
                return None
            
            return token if token.is_valid else None
        except PasswordResetToken.DoesNotExist:
            return None
    
    @staticmethod
    def reset_password(token_string, new_password):
        """Resetear la contraseña del empleado usando el token"""
        try:
            token = PasswordResetToken.objects.get(token=token_string)
            
            # Verificar que el usuario sea un empleado
            if token.user.role != 'employee':
                raise ValueError('Solo los empleados pueden usar este servicio')
            
            # Verificar que el token sea válido
            if not token.is_valid:
                raise ValueError('Token inválido o expirado')
            
            # Cambiar la contraseña
            user = token.user
            user.set_password(new_password)
            user.save()
            
            # Marcar el token como usado
            token.is_used = True
            token.save()
            
            logger.info(f"Contraseña reseteada exitosamente para empleado {user.username}")
            return True
            
        except Exception as e:
            logger.error(f"Error reseteando contraseña de empleado: {str(e)}")
            raise
    
    @staticmethod
    def verify_employee_email(email):
        """Verificar si un email pertenece a un empleado"""
        try:
            user = User.objects.get(email=email, is_active=True)
            
            if user.role == 'employee':
                return {
                    'is_employee': True,
                    'user': user
                }
            else:
                return {
                    'is_employee': False,
                    'user': None
                }
                
        except User.DoesNotExist:
            return {
                'is_employee': False,
                'user': None
            }
        except Exception as e:
            logger.error(f"Error verificando email de empleado: {str(e)}")
            raise
