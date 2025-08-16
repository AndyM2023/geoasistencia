#!/usr/bin/env python3
"""
Script para verificar el estado de autenticación
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import Employee

User = get_user_model()

def check_auth_status():
    """Verificar el estado de autenticación"""
    print("🔐 ========== VERIFICANDO ESTADO DE AUTENTICACIÓN ==========")
    
    # Verificar usuarios existentes
    users = User.objects.all()
    print(f"👥 Total de usuarios: {users.count()}")
    
    print("\n📋 LISTA DE USUARIOS:")
    print("-" * 80)
    print(f"{'ID':<5} {'Username':<20} {'Email':<30} {'Role':<15} {'Active':<10}")
    print("-" * 80)
    
    for user in users:
        print(f"{user.id:<5} {user.username:<20} {user.email:<30} {user.role:<15} {user.is_active:<10}")
    
    print("-" * 80)
    
    # Verificar si hay usuarios admin
    admin_users = users.filter(role='admin', is_active=True)
    if admin_users.exists():
        print(f"\n✅ Usuarios admin disponibles:")
        for admin in admin_users:
            print(f"   - {admin.username} ({admin.email})")
    else:
        print(f"\n❌ NO hay usuarios admin activos")
    
    # Verificar empleados
    employees = Employee.objects.all()
    print(f"\n👷 Total de empleados: {employees.count()}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    check_auth_status()
