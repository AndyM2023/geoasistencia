#!/usr/bin/env python3
"""
Script para probar la creación de empleados y identificar el error 400
"""

import os
import sys
import django
import requests
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

from core.models import Employee, User, Area

def test_create_employee():
    """Probar la creación de empleados"""
    print("🧪 ========== PROBANDO CREACIÓN DE EMPLEADO ==========")
    
    # URL del endpoint
    url = "http://localhost:8000/app/employees/"
    
    # Datos de prueba (similares a los del frontend)
    test_data = {
        "first_name": "TEST",
        "last_name": "USER",
        "email": "test@example.com",
        "position": "Analista",
        "area": 1  # ID del área
    }
    
    print(f"📤 Enviando petición a: {url}")
    print(f"📊 Datos enviados: {json.dumps(test_data, indent=2)}")
    
    try:
        # Hacer la petición POST
        response = requests.post(
            url,
            json=test_data,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        )
        
        print(f"📥 Respuesta del servidor:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        print(f"   Body: {response.text}")
        
        if response.status_code == 201:
            print("✅ Empleado creado exitosamente!")
            
            # Verificar que se creó en la base de datos
            try:
                employee = Employee.objects.latest('id')
                print(f"✅ Empleado en BD:")
                print(f"   - ID Django: {employee.id}")
                print(f"   - Employee ID: {employee.employee_id}")
                print(f"   - Nombre: {employee.user.get_full_name()}")
                print(f"   - Email: {employee.user.email}")
            except Exception as e:
                print(f"❌ Error verificando BD: {e}")
                
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error en la petición: {e}")
    
    print("=" * 60)

def test_django_create():
    """Probar creación directamente en Django"""
    print("\n🧪 ========== PROBANDO CREACIÓN DIRECTA EN DJANGO ==========")
    
    try:
        # Verificar que el área existe
        area = Area.objects.first()
        if not area:
            print("❌ No hay áreas en la base de datos")
            return
        
        print(f"✅ Área encontrada: {area.name} (ID: {area.id})")
        
        # Crear usuario
        user = User.objects.create_user(
            username="test_user_django",
            email="testdjango@example.com",
            first_name="TEST",
            last_name="DJANGO",
            role='employee'
        )
        print(f"✅ Usuario creado: {user.get_full_name()}")
        
        # Crear empleado
        employee = Employee.objects.create(
            user=user,
            position="Analista Django",
            area=area,
            hire_date="2025-08-16"
        )
        print(f"✅ Empleado creado:")
        print(f"   - ID Django: {employee.id}")
        print(f"   - Employee ID: {employee.employee_id}")
        print(f"   - Nombre: {employee.full_name}")
        
        # Limpiar datos de prueba
        employee.delete()
        user.delete()
        print("✅ Datos de prueba limpiados")
        
    except Exception as e:
        print(f"❌ Error en Django: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 60)

if __name__ == "__main__":
    test_create_employee()
    test_django_create()
