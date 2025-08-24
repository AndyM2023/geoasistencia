#!/usr/bin/env python3
"""
Script para establecer contraseña a un usuario
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

from core.models import User

def set_user_password():
    """Establecer contraseña a un usuario"""
    print("🔑 Estableciendo contraseña al usuario...")
    print("=" * 60)
    
    username = "lmendieta"
    password = "test123"
    
    try:
        user = User.objects.get(username=username)
        print(f"👤 Usuario encontrado: {user.username}")
        print(f"   - Nombre completo: {user.get_full_name()}")
        print(f"   - Email: {user.email}")
        print(f"   - Rol: {user.role}")
        
        # Establecer contraseña
        user.set_password(password)
        user.save()
        
        print(f"✅ Contraseña '{password}' establecida para el usuario {username}")
        print(f"🔑 Ahora puedes hacer login con:")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        
    except User.DoesNotExist:
        print(f"❌ Usuario '{username}' no encontrado")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    set_user_password()
