#!/usr/bin/env python
"""
Script para verificar la existencia de usuarios administradores
y crear uno si no existe.
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

from core.models import User

def check_admin_users():
    """Verificar usuarios administradores existentes"""
    print("🔍 Verificando usuarios administradores...")
    
    # Buscar usuarios administradores activos
    admin_users = User.objects.filter(role='admin', is_active=True)
    
    if admin_users.exists():
        print(f"✅ Se encontraron {admin_users.count()} usuario(s) administrador(es):")
        for user in admin_users:
            print(f"   - Usuario: {user.username}")
            print(f"     Email: {user.email}")
            print(f"     Activo: {user.is_active}")
            print(f"     Último login: {user.last_login}")
            print()
        return True
    else:
        print("❌ No se encontraron usuarios administradores activos.")
        return False

def create_admin_user():
    """Crear un usuario administrador si no existe"""
    print("🔧 Creando usuario administrador...")
    
    try:
        # Crear usuario administrador
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@geoasistencia.com',
            password='admin123456',
            role='admin',
            is_active=True
        )
        
        print(f"✅ Usuario administrador creado exitosamente:")
        print(f"   - Usuario: {admin_user.username}")
        print(f"   - Email: {admin_user.email}")
        print(f"   - Contraseña: admin123456")
        print()
        print("⚠️  IMPORTANTE: Cambia la contraseña después del primer login!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando usuario administrador: {e}")
        return False

def main():
    """Función principal"""
    print("=" * 60)
    print("🔐 VERIFICACIÓN DE USUARIOS ADMINISTRADORES")
    print("=" * 60)
    print()
    
    # Verificar si existen usuarios administradores
    has_admin = check_admin_users()
    
    if not has_admin:
        print("¿Deseas crear un usuario administrador? (s/n): ", end="")
        response = input().lower().strip()
        
        if response in ['s', 'si', 'sí', 'y', 'yes']:
            create_admin_user()
        else:
            print("❌ No se creó ningún usuario administrador.")
            print("   El sistema de recuperación de contraseña no funcionará sin un admin.")
    
    print()
    print("=" * 60)
    print("✅ VERIFICACIÓN COMPLETADA")
    print("=" * 60)

if __name__ == '__main__':
    main()
