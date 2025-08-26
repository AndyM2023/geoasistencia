import logging
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from ..models import User, PasswordResetToken

logger = logging.getLogger(__name__)

class PasswordResetService:
    """Servicio para manejar la recuperación de contraseña del administrador"""
    
    @staticmethod
    def create_reset_token(user):
        """Crear un token de recuperación para el usuario"""
        try:
            # Invalidar tokens anteriores del usuario
            PasswordResetToken.objects.filter(user=user, is_used=False).update(is_used=True)
            
            # Crear nuevo token
            token = PasswordResetToken.objects.create(
                user=user,
                expires_at=timezone.localtime() + timedelta(hours=1)
            )
            
            logger.info(f"Token de recuperación creado para usuario {user.username}")
            return token
            
        except Exception as e:
            logger.error(f"Error creando token de recuperación: {str(e)}")
            raise
    
    @staticmethod
    def send_reset_email(user, token):
        """Enviar email de recuperación de contraseña"""
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
                logger.warning(f"Usuario {user.username} ya tiene un token reciente. Evitando envío duplicado.")
                return True  # Retornar True para evitar error, pero no enviar email
            
            # URL del frontend para reset de contraseña
            frontend_url = "http://localhost:5173"  # Cambiar en producción
            reset_url = f"{frontend_url}/reset-password?token={token.token}"
            
            # Contexto para el template
            context = {
                'user': user,
                'reset_url': reset_url,
                'expires_at': token.expires_at,
                'app_name': 'Geoasistencia Admin'
            }
            
            # Renderizar template HTML
            html_message = render_to_string('core/emails/password_reset_email.html', context)
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
            
            logger.info(f"Email de recuperación enviado a {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email de recuperación: {str(e)}")
            raise
    
    @staticmethod
    def validate_token(token_string):
        """Validar un token de recuperación"""
        try:
            token = PasswordResetToken.objects.get(token=token_string)
            return token if token.is_valid else None
        except PasswordResetToken.DoesNotExist:
            return None
    
    @staticmethod
    def reset_password(token_string, new_password):
        """Resetear la contraseña usando el token"""
        try:
            token = PasswordResetToken.objects.get(token=token_string)
            
            if not token.is_valid:
                raise ValueError("Token inválido o expirado")
            
            # Cambiar contraseña del usuario
            user = token.user
            user.set_password(new_password)
            user.save()
            
            # Marcar token como usado
            token.mark_as_used()
            
            logger.info(f"Contraseña reseteada exitosamente para usuario {user.username}")
            return True
            
        except Exception as e:
            logger.error(f"Error reseteando contraseña: {str(e)}")
            raise
    
    @staticmethod
    def cleanup_expired_tokens():
        """Limpiar tokens expirados"""
        try:
            expired_tokens = PasswordResetToken.objects.filter(
                expires_at__lt=timezone.localtime()
            )
            count = expired_tokens.count()
            expired_tokens.delete()
            
            if count > 0:
                logger.info(f"Se limpiaron {count} tokens expirados")
            
            return count
            
        except Exception as e:
            logger.error(f"Error limpiando tokens expirados: {str(e)}")
            return 0
