#!/usr/bin/env python3
"""
Script para verificar el estado del empleado 11 y su perfil facial
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

from core.models import Employee, FaceProfile

def check_employee_11():
    """Verificar el estado del empleado 11"""
    print("🔍 ========== VERIFICANDO EMPLEADO 11 ==========")
    
    try:
        employee = Employee.objects.get(id=11)
        print(f"✅ Empleado encontrado: {employee.full_name}")
        print(f"   - ID Django: {employee.id}")
        print(f"   - Employee ID: {employee.employee_id}")
        print(f"   - Email: {employee.user.email}")
        print(f"   - Activo: {employee.user.is_active}")
        
        # Verificar perfil facial
        try:
            face_profile = employee.face_profile
            print(f"\n👤 PERFIL FACIAL:")
            print(f"   - Existe: ✅ SÍ")
            print(f"   - Fotos: {face_profile.photos_count}")
            print(f"   - Entrenado: {face_profile.is_trained}")
            print(f"   - Creado: {face_profile.created_at}")
            print(f"   - Actualizado: {face_profile.updated_at}")
            
            # Verificar carpeta de faces
            faces_dir = f"face_recognition/faces/{employee.employee_id}{employee.user.first_name}{employee.user.last_name}".replace(" ", "")
            if os.path.exists(faces_dir):
                files = os.listdir(faces_dir)
                jpg_files = [f for f in files if f.endswith('.jpg')]
                npy_files = [f for f in files if f.endswith('.npy')]
                print(f"\n📁 CARPETA DE FACES:")
                print(f"   - Ruta: {faces_dir}")
                print(f"   - Existe: ✅ SÍ")
                print(f"   - Archivos JPG: {len(jpg_files)}")
                print(f"   - Archivos NPY: {len(npy_files)}")
                print(f"   - Total archivos: {len(files)}")
                
                if jpg_files:
                    print(f"   - Primer JPG: {jpg_files[0]}")
                if npy_files:
                    print(f"   - Primer NPY: {npy_files[0]}")
            else:
                print(f"\n📁 CARPETA DE FACES:")
                print(f"   - Ruta: {faces_dir}")
                print(f"   - Existe: ❌ NO")
                
        except FaceProfile.DoesNotExist:
            print(f"\n👤 PERFIL FACIAL:")
            print(f"   - Existe: ❌ NO")
            
    except Employee.DoesNotExist:
        print("❌ Empleado no encontrado")
        return False
    
    print("\n" + "=" * 80)
    return True

if __name__ == "__main__":
    check_employee_11()
