#!/usr/bin/env python
"""
Script para probar específicamente con el usuario paola1
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

from core.models import User
from core.services.password_reset_service import PasswordResetService

def test_paola1_user():
    """Probar específicamente con el usuario paola1"""
    print("🧪 PROBANDO USUARIO PAOLA1")
    print("=" * 50)
    
    try:
        # Buscar específicamente el usuario paola1
        user = User.objects.filter(username='paola1', email='dmejiac@unemi.edu.ec').first()
        
        if not user:
            print("❌ No se encontró el usuario paola1")
            return
        
        print(f"👤 Usuario encontrado: {user.username}")
        print(f"📧 Email: {user.email}")
        print(f"🔐 Rol: {user.role}")
        print(f"🆔 ID: {user.id}")
        print(f"✅ Activo: {user.is_active}")
        
        print(f"\n🔧 Creando token de recuperación...")
        
        # Crear token
        token = PasswordResetService.create_reset_token(user)
        print(f"✅ Token creado: {token.token[:20]}... (ID: {token.id})")
        
        print(f"\n📧 Enviando email de recuperación...")
        
        # Intentar enviar email
        result = PasswordResetService.send_reset_email(user, token)
        
        if result:
            print("✅ ¡ÉXITO! Email enviado correctamente a paola1")
            print("   El problema de codificación Unicode está completamente resuelto")
            
            # Limpiar token de prueba
            print(f"\n🧹 Limpiando token de prueba...")
            token.delete()
            print(f"✅ Token eliminado")
        else:
            print("❌ Error enviando email")
            
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        print(f"   Tipo de error: {type(e)}")
        
        import traceback
        print(f"\n🔍 TRACEBACK:")
        traceback.print_exc()

def check_all_dmejiac_users():
    """Verificar todos los usuarios con email dmejiac@unemi.edu.ec"""
    print("\n🔍 VERIFICANDO TODOS LOS USUARIOS CON EMAIL dmejiac@unemi.edu.ec")
    print("=" * 70)
    
    try:
        users = User.objects.filter(email='dmejiac@unemi.edu.ec')
        
        print(f"👥 Usuarios encontrados: {users.count()}")
        
        for user in users:
            print(f"\n👤 Usuario: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Rol: {user.role}")
            print(f"   ID: {user.id}")
            print(f"   Activo: {user.is_active}")
            print(f"   Fecha de registro: {user.date_joined}")
            
    except Exception as e:
        print(f"❌ Error verificando usuarios: {e}")

if __name__ == '__main__':
    print("🔧 PRUEBA ESPECÍFICA DEL USUARIO PAOLA1")
    print("=" * 60)
    
    # Verificar todos los usuarios con ese email
    check_all_dmejiac_users()
    
    # Probar específicamente con paola1
    test_paola1_user()
    
    print("\n" + "=" * 60)
    print("✅ PRUEBA COMPLETADA")

