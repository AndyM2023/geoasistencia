#!/usr/bin/env python3
"""
Script para verificar qué empleados existen en la base de datos
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

from core.models import Employee, User

def check_employees():
    """Verificar todos los empleados en la base de datos"""
    print("🔍 ========== VERIFICANDO EMPLEADOS EN LA BASE DE DATOS ==========")
    
    # Obtener todos los empleados
    employees = Employee.objects.all().select_related('user')
    
    if not employees.exists():
        print("❌ No hay empleados en la base de datos")
        return
    
    print(f"✅ Total de empleados: {employees.count()}")
    print("\n📋 LISTA DE EMPLEADOS:")
    print("-" * 80)
    print(f"{'ID Django':<10} {'Employee ID':<15} {'Nombre':<30} {'Email':<30}")
    print("-" * 80)
    
    for emp in employees:
        print(f"{emp.id:<10} {emp.employee_id:<15} {emp.user.get_full_name():<30} {emp.user.email:<30}")
    
    print("-" * 80)
    
    # Verificar si existe el empleado con ID 7
    try:
        employee_7 = Employee.objects.get(id=7)
        print(f"\n✅ Empleado con ID Django 7 encontrado:")
        print(f"   - Employee ID: {employee_7.employee_id}")
        print(f"   - Nombre: {employee_7.user.get_full_name()}")
        print(f"   - Email: {employee_7.user.email}")
    except Employee.DoesNotExist:
        print(f"\n❌ NO existe empleado con ID Django 7")
        print("   Este es el problema: el frontend está enviando ID 7 pero no existe")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    check_employees()
