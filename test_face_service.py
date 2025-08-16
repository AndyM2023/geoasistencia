#!/usr/bin/env python3
"""
Script de prueba para verificar el servicio facial
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

from core.services.face_service_singleton import face_service_singleton
from core.models import Employee

def test_face_service():
    """Prueba el servicio facial"""
    print("🧪 ========== PRUEBA DEL SERVICIO FACIAL ==========")
    
    # Verificar que el servicio esté disponible
    if not face_service_singleton._service.facial_system:
        print("❌ Sistema facial no disponible")
        return False
    
    print("✅ Sistema facial disponible")
    
    # Verificar que el método extract_face_features funcione
    try:
        import numpy as np
        # Crear una imagen de prueba (dummy)
        dummy_image = np.ones((224, 224, 3), dtype=np.uint8) * 128
        
        print("🧠 Probando extracción de características...")
        features = face_service_singleton._service.facial_system.extract_face_features(dummy_image)
        
        if features is not None:
            print(f"✅ Características extraídas: {len(features)} dimensiones")
        else:
            print("❌ No se pudieron extraer características")
            return False
            
    except Exception as e:
        print(f"❌ Error probando extracción de características: {e}")
        return False
    
    # Verificar que el método detect_faces funcione
    try:
        print("🔍 Probando detección de rostros...")
        faces = face_service_singleton._service.facial_system.detect_faces(dummy_image)
        
        if faces is not None:
            print(f"✅ Detección de rostros funcionando: {len(faces)} rostros detectados")
            if len(faces) > 0:
                print(f"   Estructura del primer rostro: {faces[0]}")
        else:
            print("❌ Error en detección de rostros")
            return False
            
    except Exception as e:
        print(f"❌ Error probando detección de rostros: {e}")
        return False
    
    # Verificar que el método list_all_persons funcione
    try:
        print("📋 Probando listado de personas...")
        result = face_service_singleton._service.facial_system.list_all_persons()
        
        if result.get('success'):
            print(f"✅ Listado de personas funcionando: {result.get('total_persons', 0)} personas")
        else:
            print(f"⚠️ Listado de personas con advertencia: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Error probando listado de personas: {e}")
        return False
    
    print("🎉 ========== TODAS LAS PRUEBAS PASARON ==========")
    return True

if __name__ == "__main__":
    success = test_face_service()
    if success:
        print("✅ Servicio facial funcionando correctamente")
        sys.exit(0)
    else:
        print("❌ Servicio facial con problemas")
        sys.exit(1)
