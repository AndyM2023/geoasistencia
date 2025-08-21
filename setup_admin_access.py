#!/usr/bin/env python
"""
Script para configurar el acceso administrativo de empleados existentes
USANDO SOLO Employee.position (sin redundancia con User.position)
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

from core.models import Employee, User

def setup_admin_access():
    """Configurar acceso administrativo para empleados existentes"""
    print("🔧 CONFIGURANDO ACCESO ADMINISTRATIVO PARA EMPLEADOS EXISTENTES")
    print("📋 USANDO SOLO Employee.position (sin redundancia)")
    print("=" * 80)
    
    # Cargos que automáticamente dan acceso administrativo
    ADMIN_POSITIONS = ['gerente', 'administrativo', 'recursos_humanos', 'contador', 'analista']
    
    # Contadores
    updated_count = 0
    admin_count = 0
    employee_count = 0
    
    # Procesar todos los empleados
    employees = Employee.objects.all()
    
    for employee in employees:
        try:
            # Verificar si el cargo es administrativo (SOLO Employee.position)
            is_admin_position = employee.position in ADMIN_POSITIONS
            
            # Configurar acceso administrativo según el cargo
            if is_admin_position and not employee.has_admin_access:
                employee.has_admin_access = True
                employee.save()
                print(f"✅ {employee.full_name} - Cargo: {employee.position} → Acceso Admin: HABILITADO")
                updated_count += 1
                admin_count += 1
            elif not is_admin_position and employee.has_admin_access:
                employee.has_admin_access = False
                employee.save()
                print(f"📉 {employee.full_name} - Cargo: {employee.position} → Acceso Admin: DESHABILITADO")
                updated_count += 1
                employee_count += 1
            else:
                # Ya está configurado correctamente
                if employee.has_admin_access:
                    print(f"✅ {employee.full_name} - Cargo: {employee.position} → Acceso Admin: YA CONFIGURADO")
                    admin_count += 1
                else:
                    print(f"👤 {employee.full_name} - Cargo: {employee.position} → Acceso Admin: NO REQUERIDO")
                    employee_count += 1
                    
        except Exception as e:
            print(f"❌ Error procesando {employee.full_name}: {e}")
    
    print("\n📊 RESUMEN DE CONFIGURACIÓN:")
    print("=" * 50)
    print(f"✅ Empleados con acceso administrativo: {admin_count}")
    print(f"👤 Empleados sin acceso administrativo: {employee_count}")
    print(f"🔄 Empleados actualizados: {updated_count}")
    print(f"📊 Total de empleados procesados: {employees.count()}")
    
    print("\n🔒 CARGOS CON ACCESO ADMINISTRATIVO (Employee.position):")
    for position in ADMIN_POSITIONS:
        count = Employee.objects.filter(position=position, has_admin_access=True).count()
        print(f"   - {position}: {count} empleados")
    
    print("\n👤 CARGOS SIN ACCESO ADMINISTRATIVO (Employee.position):")
    non_admin_positions = ['desarrollador', 'disenador', 'secretario', 'ingeniero', 'marketing', 'ventas', 'soporte', 'operativo', 'otro']
    for position in non_admin_positions:
        count = Employee.objects.filter(position=position).count()
        admin_count = Employee.objects.filter(position=position, has_admin_access=True).count()
        if count > 0:
            print(f"   - {position}: {count} empleados ({admin_count} con acceso admin)")
    
    print("\n🎯 OPTIMIZACIÓN COMPLETADA:")
    print("   - ✅ User.position ELIMINADO (redundante)")
    print("   - ✅ Employee.position MANTENIDO (único)")
    print("   - ✅ has_admin_access AGREGADO (control granular)")
    
    print("\n" + "=" * 80)
    print("🔧 CONFIGURACIÓN COMPLETADA")

if __name__ == "__main__":
    setup_admin_access()
