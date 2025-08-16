#!/usr/bin/env python3
"""
Script para probar con un empleado que tenga un nombre simple sin caracteres especiales
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

from core.services.face_service_singleton import face_service_singleton
from core.models import Employee

def test_simple_name_employee():
    """Probar con un empleado que tenga un nombre simple"""
    print("🧪 ========== PROBANDO CON NOMBRE SIMPLE ==========")
    
    # 1. Buscar empleado con nombre simple
    print("\n🔍 1. BUSCANDO EMPLEADO CON NOMBRE SIMPLE:")
    employees = Employee.objects.all()
    
    simple_name_employee = None
    for emp in employees:
        # Verificar si el nombre tiene caracteres especiales
        name = f"{emp.user.first_name}{emp.user.last_name}"
        if name.isascii() and name.replace(" ", "").isalnum():
            print(f"   - {emp.full_name}: ✅ Nombre simple ({name})")
            simple_name_employee = emp
            break
        else:
            print(f"   - {emp.full_name}: ❌ Nombre con caracteres especiales ({name})")
    
    if not simple_name_employee:
        print("❌ No hay empleados con nombres simples")
        return False
    
    print(f"✅ Empleado seleccionado: {simple_name_employee.full_name}")
    print(f"   - ID Django: {simple_name_employee.id}")
    print(f"   - Employee ID: {simple_name_employee.employee_id}")
    
    # 2. Crear foto dummy simple
    print("\n📸 2. CREANDO FOTO DUMMY SIMPLE:")
    import numpy as np
    import cv2
    import base64
    
    # Crear imagen simple (cuadrado blanco)
    dummy_image = np.ones((100, 100, 3), dtype=np.uint8) * 255  # Blanco puro
    dummy_image[25:75, 25:75] = [0, 0, 0]  # Cuadrado negro en el centro
    
    # Convertir a base64
    _, buffer = cv2.imencode('.jpg', dummy_image)
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
    dummy_photo = f"data:image/jpeg;base64,{jpg_as_text}"
    
    photos_data = [dummy_photo]
    print(f"   - Fotos dummy creadas: {len(photos_data)}")
    print(f"   - Imagen: 100x100, blanco con cuadrado negro")
    
    # 3. Probar registro facial
    print("\n🚀 3. PROBANDO REGISTRO FACIAL:")
    try:
        print(f"   - Llamando a face_service_singleton.register_face...")
        result = face_service_singleton.register_face(simple_name_employee, photos_data)
        print(f"   - Resultado: {result}")
        
        if result.get('success'):
            print("✅ Registro facial exitoso!")
            return True
        else:
            print(f"❌ Error en registro facial: {result.get('message', 'Error desconocido')}")
            return False
            
    except Exception as e:
        print(f"   - ❌ Excepción en registro facial: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    success = test_simple_name_employee()
    if success:
        print(f"\n🎯 Registro facial con nombre simple exitoso!")
    else:
        print(f"\n❌ Error en el registro facial con nombre simple")
