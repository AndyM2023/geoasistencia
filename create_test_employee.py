#!/usr/bin/env python3
"""
Script para crear un empleado de prueba con foto
"""

import os
import sys
import django
from django.core.files import File

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

from core.models import Employee, User, Area
from core.serializers import EmployeeSerializer

def create_test_employee_with_photo():
    """Crear un empleado de prueba con foto"""
    print("🧪 CREANDO EMPLEADO DE PRUEBA CON FOTO")
    print("=" * 50)
    
    try:
        # Crear un usuario de prueba
        username = "test_photo_user"
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            print(f"✅ Usuario existente: {user.username}")
        else:
            user = User.objects.create_user(
                username=username,
                email="test_photo@example.com",
                password="12345678",
                first_name="Test",
                last_name="Photo",
                role="employee"
            )
            print(f"✅ Usuario creado: {user.username}")
        
        # Obtener un área
        area = Area.objects.first()
        if not area:
            print("❌ No hay áreas disponibles")
            return None
        
        # Crear un empleado de prueba
        if Employee.objects.filter(user=user).exists():
            employee = Employee.objects.get(user=user)
            print(f"✅ Empleado existente: {employee.full_name}")
        else:
            employee = Employee.objects.create(
                user=user,
                position="desarrollador",
                area=area
            )
            print(f"✅ Empleado creado: {employee.full_name}")
        
        # Crear un archivo de foto de prueba
        test_photo_path = "test_photo.txt"
        with open(test_photo_path, "w") as f:
            f.write("Esta es una foto de prueba")
        
        # Asignar la foto al empleado
        with open(test_photo_path, "rb") as f:
            employee.photo.save("test_photo.jpg", File(f), save=True)
        
        print(f"✅ Foto asignada: {employee.photo}")
        print(f"   - Ruta: {employee.photo.path}")
        print(f"   - Existe: {os.path.exists(employee.photo.path)}")
        
        # Limpiar archivo temporal
        if os.path.exists(test_photo_path):
            os.remove(test_photo_path)
        
        return employee
        
    except Exception as e:
        print(f"❌ Error creando empleado de prueba: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("🚀 Script para crear empleado de prueba con foto")
    print()
    
    employee = create_test_employee_with_photo()
    
    if employee:
        print(f"\n✅ Empleado de prueba creado exitosamente:")
        print(f"   - ID: {employee.id}")
        print(f"   - Nombre: {employee.full_name}")
        print(f"   - Foto: {employee.photo}")
        print(f"   - Archivo existe: {os.path.exists(employee.photo.path) if employee.photo else False}")
    
    print("\n🏁 Script completado")
