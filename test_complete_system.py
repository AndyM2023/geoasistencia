#!/usr/bin/env python3
"""
Script para probar el sistema completo de reconocimiento facial
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

from core.models import Employee, FaceProfile
from core.services.face_service_singleton import face_service_singleton

def test_complete_system():
    """Probar el sistema completo de reconocimiento facial"""
    print("🧪 ========== PRUEBA COMPLETA DEL SISTEMA ==========")
    
    # 1. Verificar el servicio facial
    print("\n🔍 1. VERIFICANDO SERVICIO FACIAL:")
    if face_service_singleton._service.facial_system:
        print("✅ Sistema facial disponible")
        
        # Verificar modelos cargados
        try:
            result = face_service_singleton._service.facial_system.list_all_persons()
            if result.get('success'):
                print(f"✅ Modelos funcionando: {result.get('total_persons', 0)} personas registradas")
            else:
                print(f"❌ Error en modelos: {result.get('error')}")
        except Exception as e:
            print(f"❌ Error verificando modelos: {e}")
    else:
        print("❌ Sistema facial NO disponible")
        return False
    
    # 2. Verificar empleados con rostro
    print("\n👤 2. VERIFICANDO EMPLEADOS CON ROSTRO:")
    try:
        employee_with_face = Employee.objects.get(id=6)  # Andyyy Mendieta
        print(f"✅ Empleado con rostro: {employee_with_face.full_name}")
        
        # Verificar perfil facial
        try:
            face_profile = employee_with_face.face_profile
            print(f"✅ Perfil facial: {face_profile.photos_count} fotos, Entrenado: {face_profile.is_trained}")
        except FaceProfile.DoesNotExist:
            print("❌ No tiene perfil facial")
            
    except Employee.DoesNotExist:
        print("❌ Empleado con rostro no encontrado")
    
    # 3. Verificar empleados sin rostro
    print("\n👤 3. VERIFICANDO EMPLEADOS SIN ROSTRO:")
    try:
        employee_without_face = Employee.objects.get(id=7)  # MARCELA MUÑOZ
        print(f"✅ Empleado sin rostro: {employee_without_face.full_name}")
        
        # Verificar si puede registrar rostro
        try:
            face_profile = employee_without_face.face_profile
            print(f"⚠️ Ya tiene perfil facial: {face_profile.photos_count} fotos")
        except FaceProfile.DoesNotExist:
            print("✅ Listo para registro facial")
            
    except Employee.DoesNotExist:
        print("❌ Empleado sin rostro no encontrado")
    
    # 4. Verificar estado del sistema
    print("\n📊 4. ESTADO DEL SISTEMA:")
    total_employees = Employee.objects.count()
    employees_with_face = FaceProfile.objects.count()
    employees_without_face = total_employees - employees_with_face
    
    print(f"   - Total empleados: {total_employees}")
    print(f"   - Con rostro: {employees_with_face}")
    print(f"   - Sin rostro: {employees_without_face}")
    print(f"   - Porcentaje con rostro: {(employees_with_face/total_employees)*100:.1f}%")
    
    # 5. Verificar carpetas de faces
    print("\n📁 5. VERIFICANDO CARPETAS DE FACES:")
    faces_dir = "face_recognition/faces"
    if os.path.exists(faces_dir):
        face_folders = [d for d in os.listdir(faces_dir) if os.path.isdir(os.path.join(faces_dir, d))]
        print(f"   - Directorio: {faces_dir}")
        print(f"   - Total carpetas: {len(face_folders)}")
        
        for folder in face_folders:
            folder_path = os.path.join(faces_dir, folder)
            files = os.listdir(folder_path)
            jpg_files = [f for f in files if f.endswith('.jpg')]
            npy_files = [f for f in files if f.endswith('.npy')]
            print(f"   - {folder}: {len(jpg_files)} fotos, {len(npy_files)} embeddings")
    else:
        print(f"   ❌ Directorio no existe: {faces_dir}")
    
    print("\n" + "=" * 80)
    return True

if __name__ == "__main__":
    test_complete_system()
