#!/usr/bin/env python
"""
Script para probar si el problema de codificación Unicode está resuelto
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

from core.models import User
from core.services.password_reset_service import PasswordResetService

def test_email_encoding():
    """Probar envío de email con caracteres especiales"""
    print("🧪 PROBANDO CODIFICACIÓN DE EMAIL")
    print("=" * 50)
    
    try:
        # Buscar usuario administrador
        user = User.objects.filter(role='admin', is_active=True).first()
        
        if not user:
            print("❌ No se encontró usuario administrador activo")
            return
        
        print(f"👤 Usuario encontrado: {user.username}")
        print(f"📧 Email: {user.email}")
        print(f"🔐 Rol: {user.role}")
        
        print(f"\n🔧 Creando token de recuperación...")
        
        # Crear token
        token = PasswordResetService.create_reset_token(user)
        print(f"✅ Token creado: {token.token[:20]}...")
        
        print(f"\n📧 Enviando email de recuperación...")
        
        # Intentar enviar email
        result = PasswordResetService.send_reset_email(user, token)
        
        if result:
            print("✅ ¡ÉXITO! Email enviado correctamente")
            print("   El problema de codificación Unicode está resuelto")
        else:
            print("❌ Error enviando email")
            
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        print(f"   Tipo de error: {type(e)}")
        
        import traceback
        print(f"\n🔍 TRACEBACK:")
        traceback.print_exc()
        
        # Verificar si es error de codificación
        if "UnicodeEncodeError" in str(e) or "ascii" in str(e).lower():
            print(f"\n🚨 PROBLEMA DE CODIFICACIÓN DETECTADO:")
            print(f"   - Error: {e}")
            print(f"   - Necesita corrección adicional")
        else:
            print(f"\n🔍 OTRO TIPO DE ERROR:")
            print(f"   - Error: {e}")

def check_user_passwords():
    """Verificar si hay contraseñas con caracteres especiales"""
    print("\n🔍 VERIFICANDO CONTRASEÑAS DE USUARIOS")
    print("=" * 50)
    
    try:
        users = User.objects.all()
        
        print(f"👥 Total de usuarios: {users.count()}")
        
        for user in users:
            print(f"\n👤 Usuario: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Rol: {user.role}")
            print(f"   Activo: {user.is_active}")
            
            # Verificar si la contraseña tiene caracteres especiales
            try:
                # Intentar verificar la contraseña (esto puede fallar si hay caracteres especiales)
                user.check_password("test_password")
                print(f"   ✅ Contraseña verificable")
            except Exception as pwd_error:
                print(f"   ⚠️  Problema con contraseña: {pwd_error}")
                
    except Exception as e:
        print(f"❌ Error verificando usuarios: {e}")

if __name__ == '__main__':
    print("🔧 PRUEBA DE CODIFICACIÓN UNICODE EN EMAILS")
    print("=" * 60)
    
    # Verificar usuarios primero
    check_user_passwords()
    
    # Probar envío de email
    test_email_encoding()
    
    print("\n" + "=" * 60)
    print("✅ PRUEBA COMPLETADA")
