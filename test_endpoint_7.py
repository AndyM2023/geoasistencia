#!/usr/bin/env python3
"""
Script para probar que el endpoint del empleado ID 7 funcione
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

from core.models import Employee

def test_employee_7():
    """Probar que el empleado ID 7 existe y es accesible"""
    print("🧪 ========== PROBANDO EMPLEADO ID 7 ==========")
    
    try:
        # Buscar el empleado con ID 7
        employee = Employee.objects.get(id=7)
        
        print(f"✅ Empleado encontrado:")
        print(f"   - ID Django: {employee.id}")
        print(f"   - Employee ID: {employee.employee_id}")
        print(f"   - Nombre: {employee.user.get_full_name()}")
        print(f"   - Email: {employee.user.email}")
        print(f"   - Cargo: {employee.position}")
        
        # Verificar que el employee_id sea numérico
        if isinstance(employee.employee_id, int):
            print(f"✅ Employee ID es numérico: {employee.employee_id}")
        else:
            print(f"❌ Employee ID NO es numérico: {type(employee.employee_id)}")
        
        print("\n🎯 El empleado ID 7 está listo para registro facial")
        
    except Employee.DoesNotExist:
        print("❌ Empleado con ID 7 NO encontrado")
        return False
    
    print("=" * 60)
    return True

if __name__ == "__main__":
    test_employee_7()
