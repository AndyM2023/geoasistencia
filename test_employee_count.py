#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

from core.models import Area, Employee
from core.serializers import AreaWithScheduleSerializer

def test_employee_count():
    """Probar que el campo employee_count funcione correctamente"""
    print("🔍 Probando employee_count en áreas...")
    
    # Obtener todas las áreas
    areas = Area.objects.all()
    print(f"📊 Total de áreas encontradas: {areas.count()}")
    
    for area in areas:
        print(f"\n📍 Área: {area.name}")
        print(f"   - ID: {area.id}")
        print(f"   - Empleados asignados: {area.employee_count}")
        
        # Verificar empleados directamente
        employees = area.employees.all()
        print(f"   - Empleados directos: {employees.count()}")
        
        # Verificar con serializer
        serializer = AreaWithScheduleSerializer(area)
        serialized_data = serializer.data
        print(f"   - employee_count en serializer: {serialized_data.get('employee_count')}")
        
        # Verificar que los campos estén presentes
        print(f"   - Campos en serializer: {list(serialized_data.keys())}")

if __name__ == '__main__':
    test_employee_count()
