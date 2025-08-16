#!/usr/bin/env python
"""
Script para crear usuario para Diana Vas (empleado existente)
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

from core.models import User, Employee
from django.contrib.auth.hashers import make_password

def create_diana_user():
    """Crear usuario para Diana Vas (empleado existente)"""
    
    print("🔧 CREANDO USUARIO PARA DIANA VAS (EMPLEADO EXISTENTE)")
    print("=" * 60)
    
    # Buscar el empleado existente por nombre
    try:
        employee = Employee.objects.get(first_name='Diana', last_name='Vas')
        print(f"✅ Empleado encontrado:")
        print(f"   - ID: {employee.id}")
        print(f"   - Nombre: {employee.first_name} {employee.last_name}")
        print(f"   - Employee ID: {employee.employee_id}")
        print(f"   - Posición: {employee.position}")
        print(f"   - Área: {employee.area}")
    except Employee.DoesNotExist:
        print("❌ No se encontró el empleado 'Diana Vas'")
        print("🔍 Empleados disponibles:")
        employees = Employee.objects.all()
        for emp in employees:
            print(f"   - {emp.first_name} {emp.last_name} (ID: {emp.id})")
        return None
    
    # Verificar si ya existe un usuario
    if User.objects.filter(username='diana.vas').exists():
        print("⚠️ El usuario 'diana.vas' ya existe")
        user = User.objects.get(username='diana.vas')
        print(f"   - Username: {user.username}")
        print(f"   - Email: {user.email}")
        print(f"   - Is Staff: {user.is_staff}")
        print(f"   - Is Superuser: {user.is_superuser}")
        
        # Verificar si está conectado con el empleado
        if hasattr(user, 'employee'):
            print("✅ Usuario ya está conectado con el empleado")
        else:
            print("⚠️ Usuario no está conectado con el empleado")
        
        return user
    
    # Crear usuario
    try:
        user = User.objects.create(
            username='diana.vas',
            email='dian@ddd.co',  # Email del empleado (si lo tiene)
            password=make_password('diana123'),  # Contraseña: diana123
            first_name='Diana',
            last_name='Vas',  # Sin tilde
            is_staff=False,        # NO es admin
            is_superuser=False,    # NO es superusuario
            is_active=True
        )
        
        print("✅ Usuario creado exitosamente:")
        print(f"   - Username: {user.username}")
        print(f"   - Contraseña: diana123")
        print(f"   - Email: {user.email}")
        print(f"   - Nombre: {user.first_name} {user.last_name}")
        print(f"   - Rol: EMPLEADO (no admin)")
        print(f"   - ID: {user.id}")
        
        # Conectar con el empleado existente
        employee.user = user
        employee.save()
        
        print("✅ Usuario conectado con el empleado existente")
        
        return user
        
    except Exception as e:
        print(f"❌ Error creando usuario: {e}")
        return None

def main():
    """Función principal"""
    print("🎯 SISTEMA DE CONEXIÓN DE USUARIOS")
    print("=" * 40)
    
    user = create_diana_user()
    
    if user:
        print("\n📋 RESUMEN:")
        print(f"   - Usuario: diana.vas")
        print(f"   - Contraseña: diana123")
        print(f"   - Rol: EMPLEADO")
        print(f"   - Estado: ACTIVO")
        print(f"   - Conectado con: Diana Vas (empleado existente)")
        print("\n🚀 Ahora puedes:")
        print("   1. Iniciar sesión en el frontend con diana.vas / diana123")
        print("   2. Acceder al empleado Diana Vas existente")
        print("   3. Probar el reconocimiento facial")
    else:
        print("❌ No se pudo crear el usuario")

if __name__ == "__main__":
    main()
