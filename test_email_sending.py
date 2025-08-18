#!/usr/bin/env python
"""
Script para probar el envío real de email y identificar el problema
"""

import os
import django
import traceback

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

from core.models import User
from core.services.password_reset_service import PasswordResetService

def test_real_email_sending():
    """Probar el envío real de email"""
    print("🧪 PRUEBA REAL DE ENVÍO DE EMAIL")
    print("=" * 50)
    
    try:
        # Obtener usuario administrador
        admin_user = User.objects.filter(role='admin', is_active=True).first()
        if not admin_user:
            print("❌ No se encontró usuario administrador")
            return
        
        print(f"✅ Usuario de prueba: {admin_user.username} ({admin_user.email})")
        
        # Crear token
        print("\n🔧 Creando token...")
        token = PasswordResetService.create_reset_token(admin_user)
        print(f"✅ Token creado: {token.token[:20]}...")
        
        # Intentar enviar email REAL
        print("\n📧 Intentando enviar email REAL...")
        try:
            result = PasswordResetService.send_reset_email(admin_user, token)
            print(f"✅ Email enviado exitosamente: {result}")
        except Exception as e:
            print(f"❌ Error enviando email: {e}")
            print("\n🔍 Detalles del error:")
            traceback.print_exc()
            
            # Verificar configuración específica
            print("\n📋 Verificando configuración de email...")
            from django.conf import settings
            print(f"   EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
            print(f"   EMAIL_HOST_PASSWORD: {'Configurado' if settings.EMAIL_HOST_PASSWORD else 'NO CONFIGURADO'}")
            print(f"   DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
            
            # Verificar si las credenciales son válidas
            if settings.EMAIL_HOST_PASSWORD:
                print(f"   Longitud de contraseña: {len(settings.EMAIL_HOST_PASSWORD)} caracteres")
                if len(settings.EMAIL_HOST_PASSWORD) < 10:
                    print("   ⚠️  La contraseña parece ser muy corta")
                elif 'tu_contraseña' in settings.EMAIL_HOST_PASSWORD.lower():
                    print("   ⚠️  La contraseña parece ser un placeholder")
        
        # Limpiar
        print("\n🧹 Limpiando...")
        token.delete()
        print("✅ Token eliminado")
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        traceback.print_exc()

if __name__ == '__main__':
    test_real_email_sending()

