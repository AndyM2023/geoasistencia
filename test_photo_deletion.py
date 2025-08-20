#!/usr/bin/env python3
"""
Script de prueba para verificar la eliminación de fotos de empleados
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

from core.models import Employee, User
from core.serializers import EmployeeSerializer

def test_photo_deletion():
    """Probar la eliminación de fotos de empleados"""
    print("🧪 INICIANDO PRUEBA DE ELIMINACIÓN DE FOTOS")
    print("=" * 50)
    
    # Buscar un empleado con foto
    try:
        employee_with_photo = Employee.objects.filter(photo__isnull=False, photo__gt='').first()
        
        if not employee_with_photo:
            print("❌ No se encontró ningún empleado con foto para probar")
            return
        
        print(f"✅ Empleado encontrado: {employee_with_photo.full_name}")
        print(f"   - ID: {employee_with_photo.id}")
        print(f"   - Foto actual: {employee_with_photo.photo}")
        print(f"   - Ruta de foto: {employee_with_photo.photo.path if employee_with_photo.photo else 'N/A'}")
        
        # Verificar si el archivo físico existe
        if employee_with_photo.photo:
            file_exists = os.path.exists(employee_with_photo.photo.path)
            print(f"   - Archivo físico existe: {file_exists}")
            if file_exists:
                file_size = os.path.getsize(employee_with_photo.photo.path)
                print(f"   - Tamaño del archivo: {file_size} bytes")
        
        # Simular actualización con delete_photo=True
        print("\n🔄 Simulando eliminación de foto...")
        
        # Crear datos de prueba
        test_data = {
            'first_name': employee_with_photo.user.first_name,
            'last_name': employee_with_photo.user.last_name,
            'email': employee_with_photo.user.email,
            'position': employee_with_photo.position.lower() if employee_with_photo.position else 'desarrollador',
            'area': employee_with_photo.area.id if employee_with_photo.area else None,
            'delete_photo': True
        }
        
        print(f"📤 Datos de prueba: {test_data}")
        
        # Crear serializer y actualizar
        serializer = EmployeeSerializer(employee_with_photo, data=test_data, partial=True)
        
        if serializer.is_valid():
            print("✅ Datos válidos, procediendo con actualización...")
            
            # Actualizar el empleado
            updated_employee = serializer.save()
            
            print(f"✅ Empleado actualizado: {updated_employee.full_name}")
            print(f"   - Foto después de actualizar: {updated_employee.photo}")
            
            # Verificar si la foto se eliminó
            print(f"🔍 Verificando estado de la foto después de actualizar...")
            print(f"   - updated_employee.photo: {updated_employee.photo}")
            print(f"   - updated_employee.photo type: {type(updated_employee.photo)}")
            
            if updated_employee.photo is None:
                print("✅ Foto eliminada correctamente del modelo")
                
                # Verificar si el archivo físico se eliminó
                if 'employee_with_photo' in locals() and employee_with_photo.photo:
                    old_photo_path = employee_with_photo.photo.path
                    file_still_exists = os.path.exists(old_photo_path)
                    print(f"   - Archivo físico aún existe: {file_still_exists}")
                    
                    if not file_still_exists:
                        print("✅ Archivo físico eliminado correctamente")
                    else:
                        print("⚠️ ADVERTENCIA: El archivo físico aún existe")
                        
                # Verificar en la base de datos
                try:
                    # Recargar el empleado desde la base de datos
                    refreshed_employee = Employee.objects.get(id=updated_employee.id)
                    print(f"   - Empleado recargado desde BD: {refreshed_employee.full_name}")
                    print(f"   - Foto en BD: {refreshed_employee.photo}")
                    
                    if refreshed_employee.photo is None:
                        print("✅ Foto eliminada correctamente de la base de datos")
                    else:
                        print("❌ La foto aún aparece en la base de datos")
                        
                except Exception as e:
                    print(f"   - Error recargando empleado: {e}")
            else:
                print("❌ La foto no se eliminó del modelo")
                
        else:
            print("❌ Error de validación:")
            print(serializer.errors)
            
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()

def list_employees_with_photos():
    """Listar todos los empleados con fotos"""
    print("\n📋 EMPLEADOS CON FOTOS:")
    print("=" * 30)
    
    employees_with_photos = Employee.objects.filter(photo__isnull=False)
    
    if not employees_with_photos:
        print("No hay empleados con fotos")
        return
    
    for emp in employees_with_photos:
        print(f"👤 {emp.full_name}")
        print(f"   - ID: {emp.id}")
        print(f"   - Foto: {emp.photo}")
        if emp.photo:
            try:
                file_exists = os.path.exists(emp.photo.path)
                file_size = os.path.getsize(emp.photo.path) if file_exists else 0
                print(f"   - Archivo existe: {file_exists}")
                print(f"   - Tamaño: {file_size} bytes")
            except Exception as e:
                print(f"   - Error verificando archivo: {e}")
        print()

if __name__ == "__main__":
    print("🚀 Script de prueba de eliminación de fotos")
    print()
    
    # Listar empleados con fotos
    list_employees_with_photos()
    
    # Probar eliminación
    test_photo_deletion()
    
    print("\n🏁 Prueba completada")
