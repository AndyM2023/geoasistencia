#!/usr/bin/env python
"""
Script de debug para identificar problemas en el sistema de recuperación de contraseña
"""

import os
import django
import traceback

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

from core.models import User
from core.services.password_reset_service import PasswordResetService

def debug_password_reset():
    """Debug paso a paso del sistema de recuperación de contraseña"""
    print("🔍 DEBUG DEL SISTEMA DE RECUPERACIÓN DE CONTRASEÑA")
    print("=" * 60)
    
    try:
        # Paso 1: Verificar usuario administrador
        print("1️⃣ Verificando usuario administrador...")
        admin_user = User.objects.filter(role='admin', is_active=True).first()
        if admin_user:
            print(f"   ✅ Usuario encontrado: {admin_user.username} ({admin_user.email})")
        else:
            print("   ❌ No se encontró usuario administrador")
            return
        
        # Paso 2: Crear token
        print("\n2️⃣ Creando token de recuperación...")
        try:
            token = PasswordResetService.create_reset_token(admin_user)
            print(f"   ✅ Token creado: {token.token[:20]}...")
            print(f"   ✅ Expira: {token.expires_at}")
        except Exception as e:
            print(f"   ❌ Error creando token: {e}")
            traceback.print_exc()
            return
        
        # Paso 3: Validar token
        print("\n3️⃣ Validando token...")
        try:
            is_valid = PasswordResetService.validate_token(token.token)
            if is_valid:
                print(f"   ✅ Token válido: {is_valid}")
            else:
                print(f"   ❌ Token inválido: {is_valid}")
        except Exception as e:
            print(f"   ❌ Error validando token: {e}")
            traceback.print_exc()
        
        # Paso 4: Enviar email (sin enviar realmente)
        print("\n4️⃣ Simulando envío de email...")
        try:
            # Verificar configuración de email
            from django.conf import settings
            print(f"   📧 EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
            print(f"   📧 EMAIL_HOST: {settings.EMAIL_HOST}")
            print(f"   📧 EMAIL_PORT: {settings.EMAIL_PORT}")
            print(f"   📧 EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
            print(f"   📧 EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
            print(f"   📧 EMAIL_HOST_PASSWORD: {'Configurado' if settings.EMAIL_HOST_PASSWORD else 'NO CONFIGURADO'}")
            
            if not settings.EMAIL_HOST_PASSWORD or settings.EMAIL_HOST_PASSWORD == 'tu_contraseña_de_aplicacion':
                print("   ⚠️  EMAIL_HOST_PASSWORD no está configurado correctamente")
                print("   📝 Edita el archivo .env con tus credenciales reales")
            
            # Verificar template
            from django.template.loader import render_to_string
            try:
                context = {
                    'user': admin_user,
                    'reset_url': f"http://localhost:5173/reset-password?token={token.token}",
                    'expires_at': token.expires_at,
                    'app_name': 'Geoasistencia Admin'
                }
                html_message = render_to_string('core/emails/password_reset_email.html', context)
                print(f"   ✅ Template renderizado correctamente ({len(html_message)} caracteres)")
            except Exception as e:
                print(f"   ❌ Error renderizando template: {e}")
                traceback.print_exc()
            
        except Exception as e:
            print(f"   ❌ Error en configuración de email: {e}")
            traceback.print_exc()
        
        # Paso 5: Limpiar
        print("\n5️⃣ Limpiando token de prueba...")
        try:
            token.delete()
            print("   ✅ Token eliminado")
        except Exception as e:
            print(f"   ❌ Error eliminando token: {e}")
        
        print("\n" + "=" * 60)
        print("✅ DEBUG COMPLETADO")
        
    except Exception as e:
        print(f"❌ Error general en debug: {e}")
        traceback.print_exc()

if __name__ == '__main__':
    debug_password_reset()
