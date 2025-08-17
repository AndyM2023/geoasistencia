#!/usr/bin/env python
"""
Script para probar el parsing de fechas como lo hace el frontend
"""
import os
import sys
import django
from datetime import datetime, timedelta
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

from core.models import Attendance, Employee, Area, User
from core.serializers import AttendanceSerializer

def test_frontend_date_parsing():
    """Probar cómo el frontend parsea las fechas"""
    print("🔍 === PRUEBA DE PARSING DE FECHAS DEL FRONTEND ===")
    
    # Obtener datos del 13 de agosto
    august_13_data = Attendance.objects.filter(date='2025-08-13').select_related('employee__user', 'area')
    serializer = AttendanceSerializer(august_13_data, many=True)
    data = serializer.data
    
    print(f"📊 Datos del 13 de agosto: {len(data)} registros")
    
    if data:
        first_item = data[0]
        date_string = first_item.get('date')
        
        print(f"\n📅 DATOS DEL REGISTRO:")
        print(f"   - Empleado: {first_item.get('employee_name')}")
        print(f"   - Fecha en backend: {date_string}")
        print(f"   - Tipo de fecha: {type(date_string)}")
        
        # Simular exactamente lo que hace el frontend
        print(f"\n🔍 SIMULANDO FRONTEND (JavaScript):")
        
        # Simular: new Date(dateString)
        try:
            # En JavaScript: new Date('2025-08-13')
            # Esto puede causar problemas de zona horaria
            parsed_date = datetime.strptime(date_string, '%Y-%m-%d')
            print(f"   - Fecha parseada: {parsed_date}")
            print(f"   - Día del mes: {parsed_date.day}")
            print(f"   - Mes: {parsed_date.month}")
            print(f"   - Año: {parsed_date.year}")
            
            # Simular: toLocaleDateString('es-ES')
            # En JavaScript esto podría mostrar 12/08/2025 en lugar de 13/08/2025
            formatted_date = parsed_date.strftime('%d/%m/%Y')
            print(f"   - Fecha formateada (DD/MM/YYYY): {formatted_date}")
            
            # Verificar si hay problema
            if parsed_date.day == 13:
                print("✅ CORRECTO: La fecha se interpreta como día 13")
            else:
                print(f"❌ PROBLEMA: La fecha se interpreta como día {parsed_date.day}")
                
        except Exception as e:
            print(f"❌ Error parseando fecha: {e}")
        
        # Probar con diferentes formatos de fecha
        print(f"\n🔍 PRUEBAS CON DIFERENTES FORMATOS:")
        
        test_dates = [
            '2025-08-13',
            '2025-08-13T00:00:00',
            '2025-08-13T00:00:00Z',
            '2025-08-13T00:00:00-05:00'
        ]
        
        for test_date in test_dates:
            try:
                parsed = datetime.strptime(test_date.split('T')[0], '%Y-%m-%d')
                print(f"   - {test_date} → {parsed.day}/{parsed.month}/{parsed.year}")
            except Exception as e:
                print(f"   - {test_date} → Error: {e}")

def test_timezone_issues():
    """Probar problemas de zona horaria"""
    print("\n🔍 === PRUEBA DE PROBLEMAS DE ZONA HORARIA ===")
    
    # Obtener un registro del 13 de agosto
    attendance = Attendance.objects.filter(date='2025-08-13').first()
    
    if attendance:
        print(f"📅 Registro de ejemplo:")
        print(f"   - ID: {attendance.id}")
        print(f"   - Empleado: {attendance.employee.full_name}")
        print(f"   - Fecha: {attendance.date}")
        print(f"   - Created at: {attendance.created_at}")
        
        # Verificar si hay problemas de zona horaria
        from django.utils import timezone
        print(f"   - Timezone actual: {timezone.get_current_timezone()}")
        
        # Simular diferentes interpretaciones de zona horaria
        print(f"\n🔍 SIMULANDO DIFERENTES ZONAS HORARIAS:")
        
        # UTC
        utc_date = attendance.date
        print(f"   - UTC: {utc_date}")
        
        # Local (Ecuador)
        local_date = attendance.date
        print(f"   - Local (Ecuador): {local_date}")
        
        # Verificar si hay diferencia
        if utc_date != local_date:
            print("⚠️ ADVERTENCIA: Hay diferencia entre UTC y local")
        else:
            print("✅ No hay diferencia entre UTC y local")

if __name__ == '__main__':
    print("🚀 Iniciando pruebas de parsing de fechas del frontend...")
    
    # Probar parsing de fechas
    test_frontend_date_parsing()
    
    # Probar problemas de zona horaria
    test_timezone_issues()
    
    print("\n✅ Pruebas completadas")

