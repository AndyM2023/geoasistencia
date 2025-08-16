#!/usr/bin/env python3
"""
Script para probar específicamente el guardado de imágenes
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

from core.services.face_service_singleton import face_service_singleton
from core.models import Employee

def test_image_saving():
    """Probar específicamente el guardado de imágenes"""
    print("🧪 ========== PROBANDO GUARDADO DE IMÁGENES ==========")
    
    # 1. Verificar carpeta de faces
    print("\n🔍 1. VERIFICANDO CARPETA DE FACES:")
    faces_dir = "face_recognition/faces"
    print(f"   - Ruta: {faces_dir}")
    print(f"   - Existe: {os.path.exists(faces_dir)}")
    print(f"   - Es directorio: {os.path.isdir(faces_dir) if os.path.exists(faces_dir) else 'N/A'}")
    
    if os.path.exists(faces_dir):
        print(f"   - Permisos: {oct(os.stat(faces_dir).st_mode)[-3:]}")
        print(f"   - Contenido: {os.listdir(faces_dir)}")
    
    # 2. Crear carpeta de prueba
    print("\n🔍 2. CREANDO CARPETA DE PRUEBA:")
    test_folder = os.path.join(faces_dir, "test_folder")
    print(f"   - Ruta: {test_folder}")
    
    try:
        os.makedirs(test_folder, exist_ok=True)
        print(f"   - ✅ Carpeta creada: {os.path.exists(test_folder)}")
        print(f"   - Permisos: {oct(os.stat(test_folder).st_mode)[-3:]}")
    except Exception as e:
        print(f"   - ❌ Error creando carpeta: {e}")
    
    # 3. Probar guardado de imagen simple
    print("\n🔍 3. PROBANDO GUARDADO DE IMAGEN SIMPLE:")
    try:
        import cv2
        import numpy as np
        
        # Crear imagen simple
        test_image = np.ones((100, 100, 3), dtype=np.uint8) * 128
        test_image_path = os.path.join(test_folder, "test_image.jpg")
        
        print(f"   - Imagen creada: {test_image.shape}")
        print(f"   - Ruta de guardado: {test_image_path}")
        
        # Intentar guardar
        success = cv2.imwrite(test_image_path, test_image)
        print(f"   - Guardado exitoso: {success}")
        
        if success:
            print(f"   - Archivo existe: {os.path.exists(test_image_path)}")
            print(f"   - Tamaño: {os.path.getsize(test_image_path)} bytes")
        else:
            print(f"   - ❌ Error en cv2.imwrite")
            
    except Exception as e:
        print(f"   - ❌ Error en guardado simple: {e}")
        import traceback
        traceback.print_exc()
    
    # 4. Probar guardado usando el servicio facial
    print("\n🔍 4. PROBANDO GUARDADO CON SERVICIO FACIAL:")
    try:
        # Obtener empleado
        employee = Employee.objects.get(id=3)  # Carlos López
        print(f"   - Empleado: {employee.full_name}")
        
        # Crear foto dummy
        dummy_image = np.ones((100, 100, 3), dtype=np.uint8) * 128
        _, buffer = cv2.imencode('.jpg', dummy_image)
        jpg_as_text = base64.b64encode(buffer).decode('utf-8')
        dummy_photo = f"data:image/jpeg;base64,{jpg_as_text}"
        
        photos_data = [dummy_photo]
        print(f"   - Fotos dummy creadas: {len(photos_data)}")
        
        # Llamar al método
        result = face_service_singleton.register_face(employee, photos_data)
        print(f"   - Resultado: {result}")
        
    except Exception as e:
        print(f"   - ❌ Error en guardado con servicio: {e}")
        import traceback
        traceback.print_exc()
    
    # 5. Limpiar carpeta de prueba
    print("\n🔍 5. LIMPIANDO CARPETA DE PRUEBA:")
    try:
        import shutil
        if os.path.exists(test_folder):
            shutil.rmtree(test_folder)
            print(f"   - ✅ Carpeta de prueba eliminada")
    except Exception as e:
        print(f"   - ❌ Error eliminando carpeta: {e}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    test_image_saving()
