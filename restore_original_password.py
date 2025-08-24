#!/usr/bin/env python3
"""
Script para restaurar la contraseña original del usuario lmendieta
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

from core.models import User

def restore_original_password():
    """Restaurar la contraseña original del usuario lmendieta"""
    print("🔧 Restaurando contraseña original del usuario...")
    print("=" * 60)
    
    username = "lmendieta"
    
    try:
        user = User.objects.get(username=username)
        print(f"👤 Usuario encontrado: {user.username}")
        print(f"   - Nombre completo: {user.get_full_name()}")
        print(f"   - Email: {user.email}")
        print(f"   - Cédula: {user.cedula}")
        
        # Restaurar contraseña a la cédula
        original_password = user.cedula
        user.set_password(original_password)
        user.save()
        
        print(f"✅ Contraseña restaurada a la cédula: {original_password}")
        print(f"🔑 Ahora puedes hacer login con:")
        print(f"   Username: {username}")
        print(f"   Password: {original_password}")
        print(f"   (Que es la cédula original)")
        
    except User.DoesNotExist:
        print(f"❌ Usuario '{username}' no encontrado")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    restore_original_password()
