#!/usr/bin/env python3
"""
Script de prueba que simula exactamente el endpoint de Django
"""

import os
import sys
import django
import base64
import numpy as np

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

from core.services.face_service_singleton import face_service_singleton
from core.models import Employee

def create_dummy_photo():
    """Crea una foto dummy en base64"""
    import cv2
    
    # Crear una imagen de prueba (dummy) con un rostro simulado
    dummy_image = np.ones((480, 640, 3), dtype=np.uint8) * 128
    
    # Simular un rostro en el centro
    center_x, center_y = 320, 240
    face_size = 100
    
    # Dibujar un "rostro" simple
    cv2.rectangle(dummy_image, 
                  (center_x - face_size//2, center_y - face_size//2),
                  (center_x + face_size//2, center_y + face_size//2),
                  (255, 255, 255), -1)
    
    # Convertir a base64
    _, buffer = cv2.imencode('.jpg', dummy_image)
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
    
    # Agregar prefijo data URL
    return f"data:image/jpeg;base64,{jpg_as_text}"

def test_django_endpoint_simulation():
    """Simula exactamente lo que hace el endpoint de Django"""
    print("🧪 ========== SIMULACIÓN DEL ENDPOINT DE DJANGO ==========")
    
    try:
        # Obtener un empleado de prueba
        print("👤 Buscando empleado de prueba...")
        try:
            employee = Employee.objects.first()
            if not employee:
                print("❌ No hay empleados en la base de datos")
                return False
            print(f"✅ Empleado encontrado: {employee.full_name} (ID: {employee.id})")
        except Exception as e:
            print(f"❌ Error obteniendo empleado: {e}")
            return False
        
        # Crear fotos dummy
        print("📸 Creando fotos dummy...")
        photos_base64 = [create_dummy_photo() for _ in range(3)]  # Solo 3 fotos para prueba
        print(f"✅ {len(photos_base64)} fotos dummy creadas")
        
        # Simular exactamente la llamada del endpoint
        print("🚀 Llamando a face_service.register_face...")
        print(f"   - Employee: {employee.full_name}")
        print(f"   - Photos count: {len(photos_base64)}")
        
        try:
            result = face_service_singleton.register_face(employee, photos_base64)
            
            print(f"📊 Resultado del face_service:")
            print(f"   - Success: {result.get('success')}")
            print(f"   - Message: {result.get('message')}")
            print(f"   - Photos count: {result.get('photos_count')}")
            
            if result['success']:
                print("✅ Registro facial exitoso")
                return True
            else:
                print(f"❌ Registro facial falló: {result.get('message')}")
                return False
                
        except Exception as e:
            print(f"❌ Error en register_face: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_django_endpoint_simulation()
    if success:
        print("🎉 ========== SIMULACIÓN EXITOSA ==========")
        sys.exit(0)
    else:
        print("❌ ========== SIMULACIÓN FALLÓ ==========")
        sys.exit(1)
