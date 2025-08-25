#!/usr/bin/env python3
"""
Script de prueba para verificar el registro facial
"""

import os
import sys
import cv2
import numpy as np
from advanced_face_system import FacialRecognition

def test_face_registration():
    """Prueba el sistema de registro facial"""
    print("🧪 PRUEBA DEL SISTEMA DE RECONOCIMIENTO FACIAL")
    print("=" * 50)
    
    try:
        # 1. Inicializar sistema
        print("1️⃣ Inicializando sistema facial...")
        fr = FacialRecognition()
        print(f"✅ Sistema inicializado en: {fr.face_dir}")
        print(f"✅ Directorio faces existe: {os.path.exists(fr.face_dir)}")
        
        # 2. Verificar directorios
        print("\n2️⃣ Verificando estructura de directorios...")
        print(f"📁 Directorio base: {fr.base_dir}")
        print(f"📁 Directorio faces: {fr.face_dir}")
        print(f"📁 Contenido de faces: {os.listdir(fr.face_dir)}")
        
        # 3. Crear imagen de prueba
        print("\n3️⃣ Creando imagen de prueba...")
        # Crear una imagen sintética con un "rostro" (rectángulo)
        test_image = np.ones((480, 640, 3), dtype=np.uint8) * 128  # Gris medio
        
        # Dibujar un "rostro" simple (rectángulo)
        cv2.rectangle(test_image, (200, 150), (440, 330), (255, 255, 255), -1)
        cv2.rectangle(test_image, (200, 150), (440, 330), (0, 0, 0), 2)
        
        # Agregar "ojos"
        cv2.circle(test_image, (280, 200), 20, (0, 0, 0), -1)
        cv2.circle(test_image, (360, 200), 20, (0, 0, 0), -1)
        
        # Agregar "boca"
        cv2.ellipse(test_image, (320, 280), (40, 20), 0, 0, 180, (0, 0, 0), 2)
        
        print(f"✅ Imagen de prueba creada: {test_image.shape}")
        
        # 4. Probar detección de rostros
        print("\n4️⃣ Probando detección de rostros...")
        faces = fr.detect_faces(test_image)
        print(f"🔍 Rostros detectados: {len(faces)}")
        for i, face in enumerate(faces):
            print(f"   Rostro {i+1}: {face}")
        
        # 5. Probar registro de persona
        print("\n5️⃣ Probando registro de persona...")
        test_person_id = "TEST001"
        test_person_name = "UsuarioPrueba"
        
        result = fr.register_person(test_person_id, test_person_name, test_image, max_faces=5)
        print(f"📝 Resultado del registro: {result}")
        
        # 6. Verificar archivos guardados
        print("\n6️⃣ Verificando archivos guardados...")
        expected_folder = f"{test_person_id}{test_person_name}"
        expected_path = os.path.join(fr.face_dir, expected_folder)
        
        if os.path.exists(expected_path):
            print(f"✅ Carpeta creada: {expected_path}")
            files = os.listdir(expected_path)
            print(f"📁 Archivos en la carpeta: {files}")
            
            jpg_files = [f for f in files if f.endswith('.jpg')]
            npy_files = [f for f in files if f.endswith('.npy')]
            
            print(f"🖼️  Imágenes (.jpg): {len(jpg_files)}")
            print(f"🧠 Embeddings (.npy): {len(npy_files)}")
            
        else:
            print(f"❌ Carpeta NO creada: {expected_path}")
        
        # 7. Probar identificación
        print("\n7️⃣ Probando identificación...")
        if os.path.exists(expected_path) and len(jpg_files) > 0:
            # Cargar la primera imagen guardada
            first_image_path = os.path.join(expected_path, jpg_files[0])
            test_image_for_id = cv2.imread(first_image_path)
            
            if test_image_for_id is not None:
                id_result = fr.identify_person(test_image_for_id, similarity_threshold=0.5)
                print(f"🆔 Resultado de identificación: {id_result}")
            else:
                print("❌ No se pudo cargar la imagen para identificación")
        else:
            print("⚠️ No hay imágenes para probar identificación")
        
        # 8. Limpiar archivos de prueba
        print("\n8️⃣ Limpiando archivos de prueba...")
        if os.path.exists(expected_path):
            import shutil
            shutil.rmtree(expected_path)
            print(f"🗑️ Carpeta de prueba eliminada: {expected_path}")
        
        print("\n✅ PRUEBA COMPLETADA EXITOSAMENTE")
        
    except Exception as e:
        print(f"\n❌ ERROR EN LA PRUEBA: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_camera_capture():
    """Prueba la captura desde cámara"""
    print("\n📹 PRUEBA DE CAPTURA DESDE CÁMARA")
    print("=" * 40)
    
    try:
        # Intentar acceder a la cámara
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("❌ No se pudo acceder a la cámara")
            return False
        
        print("✅ Cámara accesible")
        
        # Capturar una foto
        ret, frame = cap.read()
        if ret:
            print(f"✅ Foto capturada: {frame.shape}")
            
            # Guardar foto de prueba
            test_photo_path = "test_camera_capture.jpg"
            cv2.imwrite(test_photo_path, frame)
            print(f"💾 Foto guardada en: {test_photo_path}")
            
            # Verificar que se guardó
            if os.path.exists(test_photo_path):
                print("✅ Archivo de foto creado correctamente")
                # Limpiar
                os.remove(test_photo_path)
                print("🗑️ Archivo de prueba eliminado")
            else:
                print("❌ No se pudo crear el archivo de foto")
        
        cap.release()
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de cámara: {e}")
        return False

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBAS DEL SISTEMA FACIAL")
    print("=" * 60)
    
    # Prueba 1: Sistema básico
    success1 = test_face_registration()
    
    # Prueba 2: Cámara
    success2 = test_camera_capture()
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS:")
    print(f"   Sistema básico: {'✅ EXITOSO' if success1 else '❌ FALLÓ'}")
    print(f"   Cámara: {'✅ EXITOSO' if success2 else '❌ FALLÓ'}")
    
    if success1 and success2:
        print("\n🎉 TODAS LAS PRUEBAS PASARON - SISTEMA FUNCIONAL")
    else:
        print("\n⚠️ ALGUNAS PRUEBAS FALLARON - REVISAR ERRORES")
    
    print("=" * 60)










