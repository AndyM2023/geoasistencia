#!/usr/bin/env python3
"""
Script que simula exactamente el contexto HTTP para identificar la diferencia
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

from core.services.face_service_singleton import face_service_singleton
from core.models import Employee

def test_http_context_difference():
    """Simular exactamente el contexto HTTP para identificar la diferencia"""
    print("🧪 ========== SIMULANDO CONTEXTO HTTP COMPLETO ==========")
    
    # 1. Verificar el servicio facial ANTES de la simulación
    print("\n🔍 1. ESTADO ANTES DE LA SIMULACIÓN:")
    if hasattr(face_service_singleton._service, 'facial_system'):
        facial_system = face_service_singleton._service.facial_system
        print(f"   - facial_system disponible: {facial_system is not None}")
        if facial_system:
            print("   - ✅ Sistema facial disponible")
        else:
            print("   - ❌ Sistema facial NO disponible")
    else:
        print("   - ❌ No tiene atributo facial_system")
    
    # 2. Simular llamada HTTP (crear un contexto similar)
    print("\n🔍 2. SIMULANDO LLAMADA HTTP:")
    print("   - Llamando a face_service_singleton.register_face...")
    
    try:
        # Obtener empleado
        employee = Employee.objects.get(id=5)  # Hola User
        print(f"   - Empleado: {employee.full_name}")
        
        # Crear foto dummy
        import numpy as np
        import cv2
        import base64
        
        dummy_image = np.ones((100, 100, 3), dtype=np.uint8) * 128
        _, buffer = cv2.imencode('.jpg', dummy_image)
        jpg_as_text = base64.b64encode(buffer).decode('utf-8')
        dummy_photo = f"data:image/jpeg;base64,{jpg_as_text}"
        
        photos_data = [dummy_photo]
        print(f"   - Fotos dummy creadas: {len(photos_data)}")
        
        # Verificar estado ANTES de la llamada
        print("\n🔍 3. ESTADO ANTES DE REGISTER_FACE:")
        if hasattr(face_service_singleton._service, 'facial_system'):
            facial_system = face_service_singleton._service.facial_system
            print(f"   - facial_system disponible: {facial_system is not None}")
            if facial_system:
                print("   - ✅ Sistema facial disponible")
            else:
                print("   - ❌ Sistema facial NO disponible")
        else:
            print("   - ❌ No tiene atributo facial_system")
        
        # Llamar al método
        print("\n🚀 4. LLAMANDO A REGISTER_FACE:")
        result = face_service_singleton.register_face(employee, photos_data)
        print(f"   - Resultado: {result}")
        
        # Verificar estado DESPUÉS de la llamada
        print("\n🔍 5. ESTADO DESPUÉS DE REGISTER_FACE:")
        if hasattr(face_service_singleton._service, 'facial_system'):
            facial_system = face_service_singleton._service.facial_system
            print(f"   - facial_system disponible: {facial_system is not None}")
            if facial_system:
                print("   - ✅ Sistema facial disponible")
            else:
                print("   - ❌ Sistema facial NO disponible")
        else:
            print("   - ❌ No tiene atributo facial_system")
        
    except Exception as e:
        print(f"   - ❌ Error en la simulación: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    test_http_context_difference()
