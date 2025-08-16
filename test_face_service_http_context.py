#!/usr/bin/env python3
"""
Script para verificar el estado del servicio facial en el contexto HTTP
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

from core.services.face_service_singleton import face_service_singleton

def test_face_service_http_context():
    """Probar el servicio facial en el contexto HTTP"""
    print("🧪 ========== VERIFICANDO SERVICIO FACIAL EN CONTEXTO HTTP ==========")
    
    # 1. Verificar el singleton
    print("\n🔍 1. VERIFICANDO SINGLETON:")
    print(f"   - face_service_singleton: {face_service_singleton}")
    print(f"   - Tipo: {type(face_service_singleton)}")
    
    # 2. Verificar el servicio interno
    print("\n🔍 2. VERIFICANDO SERVICIO INTERNO:")
    print(f"   - _service: {face_service_singleton._service}")
    print(f"   - Tipo: {type(face_service_singleton._service)}")
    
    # 3. Verificar el sistema facial
    print("\n🔍 3. VERIFICANDO SISTEMA FACIAL:")
    if hasattr(face_service_singleton._service, 'facial_system'):
        facial_system = face_service_singleton._service.facial_system
        print(f"   - facial_system: {facial_system}")
        print(f"   - Tipo: {type(facial_system)}")
        print(f"   - Es None: {facial_system is None}")
        
        if facial_system:
            print("   - ✅ Sistema facial disponible")
            
            # Probar método list_all_persons
            try:
                result = facial_system.list_all_persons()
                print(f"   - list_all_persons: {result}")
            except Exception as e:
                print(f"   - ❌ Error en list_all_persons: {e}")
        else:
            print("   - ❌ Sistema facial NO disponible")
    else:
        print("   - ❌ No tiene atributo facial_system")
    
    # 4. Verificar método register_face
    print("\n🔍 4. VERIFICANDO MÉTODO REGISTER_FACE:")
    if hasattr(face_service_singleton, 'register_face'):
        print("   - ✅ Método register_face existe")
        print(f"   - Tipo: {type(face_service_singleton.register_face)}")
    else:
        print("   - ❌ Método register_face NO existe")
    
    # 5. Verificar si el servicio está funcionando
    print("\n🔍 5. VERIFICANDO FUNCIONAMIENTO:")
    try:
        # Llamar al método register_face con datos dummy
        print("   - Llamando a register_face con datos dummy...")
        
        # Crear datos dummy
        from core.models import Employee
        employee = Employee.objects.first()
        if employee:
            print(f"   - Empleado de prueba: {employee.full_name}")
            
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
            
            # Llamar al método
            result = face_service_singleton.register_face(employee, photos_data)
            print(f"   - Resultado: {result}")
            
        else:
            print("   - ❌ No hay empleados para probar")
            
    except Exception as e:
        print(f"   - ❌ Error probando register_face: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    test_face_service_http_context()
