#!/usr/bin/env python3
"""
Script simple para probar la actualización de empleado
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

from core.models import Employee, User, Area
from core.serializers import EmployeeSerializer
from rest_framework.test import APIRequestFactory
from django.contrib.auth import get_user_model

def test_employee_update():
    """Probar la actualización de empleado"""
    print("🔍 Probando actualización de empleado...")
    
    try:
        # Obtener el empleado con ID 21
        employee = Employee.objects.get(id=21)
        print(f"✅ Empleado encontrado: {employee.full_name}")
        print(f"   - User: {employee.user.username}")
        print(f"   - Area: {employee.area}")
        print(f"   - Position: {employee.position}")
        
        # Simular datos de actualización (como los envía el frontend)
        update_data = {
            "first_name": "Test",
            "last_name": "User", 
            "email": "test@example.com",
            "cedula": "1234567890",
            "position": "desarrollador",
            "area": 1,  # Asumiendo que existe área con ID 1
            "photo": None
        }
        
        print(f"\n📤 Datos de actualización:")
        for key, value in update_data.items():
            print(f"   - {key}: {value} (tipo: {type(value)})")
        
        # Verificar que el área existe
        try:
            area = Area.objects.get(id=1)
            print(f"✅ Área encontrada: {area.name}")
        except Area.DoesNotExist:
            print(f"❌ Área con ID 1 no existe")
            # Usar la primera área disponible
            first_area = Area.objects.first()
            if first_area:
                update_data['area'] = first_area.id
                print(f"✅ Usando área alternativa: {first_area.name} (ID: {first_area.id})")
            else:
                print(f"❌ No hay áreas disponibles")
                return
        
        # Crear serializer y probar validación
        print(f"\n🔍 Probando validación del serializer...")
        serializer = EmployeeSerializer(instance=employee, data=update_data, partial=True)
        
        if serializer.is_valid():
            print("✅ Serializer válido")
            print("   - Datos validados:", serializer.validated_data)
            
            # Intentar actualizar
            print(f"\n🔄 Intentando actualizar...")
            updated_employee = serializer.save()
            print(f"✅ Empleado actualizado exitosamente: {updated_employee.id}")
            
        else:
            print("❌ Serializer inválido")
            print("   - Errores:", serializer.errors)
            
            # Mostrar errores detallados
            for field, errors in serializer.errors.items():
                print(f"   - Campo '{field}': {errors}")
    
    except Employee.DoesNotExist:
        print(f"❌ Empleado con ID 21 no encontrado")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_employee_update()
