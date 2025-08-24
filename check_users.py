#!/usr/bin/env python3
"""
Script para verificar usuarios en la base de datos
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

from core.models import User, Employee

def check_users():
    """Verificar usuarios en la base de datos"""
    print("👥 Verificando usuarios en la base de datos...")
    print("=" * 60)
    
    # Obtener todos los usuarios
    users = User.objects.all()
    print(f"Total de usuarios: {users.count()}")
    print()
    
    for user in users:
        print(f"👤 Usuario: {user.username}")
        print(f"   - Nombre completo: {user.get_full_name()}")
        print(f"   - Email: {user.email}")
        print(f"   - Rol: {user.role}")
        print(f"   - Activo: {user.is_active}")
        print(f"   - Fecha creación: {user.created_at}")
        
        # Verificar si tiene perfil de empleado
        try:
            employee = user.employee_profile
            print(f"   - ID Empleado: {employee.employee_id}")
            print(f"   - Cargo: {employee.position}")
            print(f"   - Área: {employee.area.name if employee.area else 'Sin área'}")
            print(f"   - Fecha contratación: {employee.hire_date}")
        except Employee.DoesNotExist:
            print(f"   - ❌ No tiene perfil de empleado")
        
        print("-" * 40)
    
    print("\n🔑 Para probar el login, usa las credenciales de cualquier usuario activo")
    print("   Ejemplo: username y password del usuario que quieras probar")

if __name__ == "__main__":
    check_users()
