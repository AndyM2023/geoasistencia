#!/usr/bin/env python3
"""
Script de prueba para verificar el procesamiento de fotos reales
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

def test_photo_processing():
    """Prueba el procesamiento de fotos"""
    print("🧪 ========== PRUEBA DE PROCESAMIENTO DE FOTOS ==========")
    
    try:
        import cv2
    except ImportError:
        print("❌ OpenCV no disponible")
        return False
    
    # Verificar que el servicio esté disponible
    if not face_service_singleton._service.facial_system:
        print("❌ Sistema facial no disponible")
        return False
    
    print("✅ Sistema facial disponible")
    
    # Crear foto dummy
    print("📸 Creando foto dummy...")
    dummy_photo = create_dummy_photo()
    print(f"✅ Foto dummy creada: {len(dummy_photo)} caracteres")
    
    # Probar decodificación de la foto
    print("🔓 Probando decodificación de foto...")
    try:
        decoded_image = face_service_singleton._service._decode_base64_image(dummy_photo)
        
        if decoded_image is not None:
            print(f"✅ Foto decodificada exitosamente: {decoded_image.shape}")
        else:
            print("❌ Error decodificando foto")
            return False
            
    except Exception as e:
        print(f"❌ Error en decodificación: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Probar extracción de rostro
    print("✂️ Probando extracción de rostro...")
    try:
        face_image = face_service_singleton._service._extract_face_region(decoded_image)
        
        if face_image is not None:
            print(f"✅ Rostro extraído exitosamente: {face_image.shape}")
        else:
            print("❌ Error extrayendo rostro")
            return False
            
    except Exception as e:
        print(f"❌ Error en extracción de rostro: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Probar generación de embedding
    print("🧠 Probando generación de embedding...")
    try:
        embedding = face_service_singleton._service.facial_system.extract_face_features(face_image)
        
        if embedding is not None:
            print(f"✅ Embedding generado exitosamente: {len(embedding)} dimensiones")
        else:
            print("❌ Error generando embedding")
            return False
            
    except Exception as e:
        print(f"❌ Error en generación de embedding: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("🎉 ========== PROCESAMIENTO DE FOTOS FUNCIONANDO ==========")
    return True

if __name__ == "__main__":
    success = test_photo_processing()
    if success:
        print("✅ Procesamiento de fotos funcionando correctamente")
        sys.exit(0)
    else:
        print("❌ Procesamiento de fotos con problemas")
        sys.exit(1)
