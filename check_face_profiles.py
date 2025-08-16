#!/usr/bin/env python3
"""
Script para verificar el estado de todos los perfiles faciales
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

from core.models import Employee, FaceProfile

def check_face_profiles():
    """Verificar el estado de todos los perfiles faciales"""
    print("👤 ========== VERIFICANDO PERFILES FACIALES ==========")
    
    # Obtener todos los empleados
    employees = Employee.objects.all().select_related('user', 'area')
    
    print(f"👥 Total de empleados: {employees.count()}")
    
    print("\n📋 ESTADO DE PERFILES FACIALES:")
    print("-" * 100)
    print(f"{'ID':<5} {'Employee ID':<15} {'Nombre':<25} {'Perfil Facial':<15} {'Fotos':<8} {'Entrenado':<12} {'Área':<20}")
    print("-" * 100)
    
    total_with_face = 0
    total_without_face = 0
    
    for emp in employees:
        try:
            face_profile = emp.face_profile
            has_face = "✅ SÍ"
            photos_count = face_profile.photos_count
            is_trained = "✅ SÍ" if face_profile.is_trained else "❌ NO"
            total_with_face += 1
        except FaceProfile.DoesNotExist:
            has_face = "❌ NO"
            photos_count = 0
            is_trained = "❌ NO"
            total_without_face += 1
        
        area_name = emp.area.name if emp.area else "Sin área"
        
        print(f"{emp.id:<5} {emp.employee_id:<15} {emp.user.get_full_name():<25} {has_face:<15} {photos_count:<8} {is_trained:<12} {area_name:<20}")
    
    print("-" * 100)
    
    print(f"\n📊 RESUMEN:")
    print(f"   - Total empleados: {employees.count()}")
    print(f"   - Con perfil facial: {total_with_face}")
    print(f"   - Sin perfil facial: {total_without_face}")
    print(f"   - Porcentaje con rostro: {(total_with_face/employees.count())*100:.1f}%")
    
    # Verificar carpetas de faces
    faces_dir = "face_recognition/faces"
    if os.path.exists(faces_dir):
        face_folders = [d for d in os.listdir(faces_dir) if os.path.isdir(os.path.join(faces_dir, d))]
        print(f"\n📁 CARPETAS DE FACES:")
        print(f"   - Directorio: {faces_dir}")
        print(f"   - Total carpetas: {len(face_folders)}")
        for folder in face_folders:
            folder_path = os.path.join(faces_dir, folder)
            files = os.listdir(folder_path)
            jpg_files = [f for f in files if f.endswith('.jpg')]
            npy_files = [f for f in files if f.endswith('.npy')]
            print(f"   - {folder}: {len(jpg_files)} fotos, {len(npy_files)} embeddings")
    else:
        print(f"\n❌ Directorio de faces no existe: {faces_dir}")
    
    print("\n" + "=" * 100)

if __name__ == "__main__":
    check_face_profiles()
