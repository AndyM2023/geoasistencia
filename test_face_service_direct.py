#!/usr/bin/env python3
"""
Script para probar el servicio facial directamente y identificar el error
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

from core.models import Employee
from core.services.face_service_singleton import face_service_singleton

def test_face_service_direct():
    """Probar el servicio facial directamente"""
    print("🧪 ========== PRUEBA DIRECTA DEL SERVICIO FACIAL ==========")
    
    # 1. Verificar que el servicio esté disponible
    print("\n🔍 1. VERIFICANDO SERVICIO FACIAL:")
    if not face_service_singleton._service.facial_system:
        print("❌ Sistema facial no disponible")
        return False
    
    print("✅ Sistema facial disponible")
    
    # 2. Verificar empleado
    print("\n👤 2. VERIFICANDO EMPLEADO:")
    try:
        employee = Employee.objects.get(id=11)  # vvvvvvvvvv v
        print(f"✅ Empleado encontrado: {employee.full_name}")
        print(f"   - ID Django: {employee.id}")
        print(f"   - Employee ID: {employee.employee_id}")
    except Employee.DoesNotExist:
        print("❌ Empleado no encontrado")
        return False
    
    # 3. Crear fotos de prueba
    print("\n📸 3. CREANDO FOTOS DE PRUEBA:")
    import cv2
    import numpy as np
    import base64
    from io import BytesIO
    from PIL import Image
    
    def create_test_photo():
        """Crear una foto de prueba simple"""
        # Crear imagen simple
        image = np.ones((480, 640, 3), dtype=np.uint8) * 128
        
        # Agregar un rectángulo simple (simulando rostro)
        cv2.rectangle(image, (200, 150), (440, 330), (255, 255, 255), -1)
        
        # Convertir a base64
        _, buffer = cv2.imencode('.jpg', image)
        jpg_as_text = base64.b64encode(buffer).decode('utf-8')
        
        return f"data:image/jpeg;base64,{jpg_as_text}"
    
    # Crear 3 fotos de prueba (menos para debug)
    photos_data = []
    for i in range(3):
        photo = create_test_photo()
        photos_data.append(photo)
        print(f"   - Foto {i+1}: {len(photo)} caracteres")
    
    # 4. Probar registro facial directamente
    print("\n🚀 4. PROBANDO REGISTRO FACIAL DIRECTO:")
    try:
        print(f"   - Llamando a face_service.register_face...")
        print(f"   - Employee: {employee.full_name}")
        print(f"   - Photos count: {len(photos_data)}")
        
        # Llamar al servicio directamente
        result = face_service_singleton.register_face(employee, photos_data)
        
        print(f"   - Resultado: {result}")
        
        if result.get('success'):
            print("✅ Registro facial exitoso!")
            return True
        else:
            print(f"❌ Error en registro facial: {result.get('message', 'Error desconocido')}")
            return False
            
    except Exception as e:
        print(f"❌ Excepción en registro facial: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_face_service_direct()
    if success:
        print(f"\n🎯 Servicio facial probado exitosamente!")
    else:
        print(f"\n❌ Error en el servicio facial")
