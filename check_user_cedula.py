#!/usr/bin/env python3
"""
Script para verificar la cédula del usuario lmendieta
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

from core.models import User

def check_user_cedula():
    """Verificar la cédula del usuario lmendieta"""
    print("🔍 Verificando cédula del usuario lmendieta...")
    print("=" * 60)
    
    try:
        user = User.objects.get(username="lmendieta")
        print(f"👤 Usuario: {user.username}")
        print(f"   - Nombre completo: {user.get_full_name()}")
        print(f"   - Email: {user.email}")
        print(f"   - Cédula: {user.cedula or 'NO TIENE CÉDULA'}")
        print(f"   - Rol: {user.role}")
        
        if user.cedula:
            print(f"✅ El usuario tiene cédula: {user.cedula}")
            print(f"🔑 La contraseña original debería ser: {user.cedula}")
        else:
            print("❌ El usuario NO tiene cédula asignada")
            print("💡 Necesitas asignarle una cédula o usar otra contraseña")
            
    except User.DoesNotExist:
        print(f"❌ Usuario 'lmendieta' no encontrado")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_user_cedula()
