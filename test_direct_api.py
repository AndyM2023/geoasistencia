#!/usr/bin/env python
"""
Script para probar directamente la API y encontrar el bug
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

def test_direct_filter():
    """Probar el filtro directamente sin ViewSet"""
    print("🔍 === PRUEBA DIRECTA DEL FILTRO ===")
    
    # Parámetros de fecha
    date_from = '2025-08-12'
    date_to = '2025-08-13'
    
    print(f"📅 Fechas de prueba:")
    print(f"   - Desde: {date_from}")
    print(f"   - Hasta: {date_to}")
    
    # Obtener queryset base
    queryset = Attendance.objects.select_related('employee__user', 'area').all()
    print(f"📊 Total de registros ANTES de filtros: {queryset.count()}")
    
    # Aplicar filtro desde
    if date_from:
        queryset = queryset.filter(date__gte=date_from)
        print(f"✅ Filtro por fecha desde aplicado: {date_from}")
        print(f"📊 Registros después del filtro desde: {queryset.count()}")
    
    # Aplicar filtro hasta (como lo hace el backend)
    if date_to:
        try:
            # Convertir la fecha a datetime y agregar 1 día
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            next_day = date_to_obj + timedelta(days=1)
            
            print(f"🔍 DEBUG FECHA HASTA:")
            print(f"   - Fecha original: {date_to}")
            print(f"   - Fecha convertida: {date_to_obj}")
            print(f"   - Día siguiente: {next_day}")
            print(f"   - Filtro aplicado: date__lt={next_day}")
            
            queryset = queryset.filter(date__lt=next_day)
            print(f"✅ Filtro por fecha hasta aplicado: {date_to} (incluye día completo hasta {next_day})")
            
            # Verificar registros después del filtro
            print(f"📊 Registros después del filtro fecha hasta: {queryset.count()}")
            
        except ValueError as e:
            print(f"⚠️ Error en formato de fecha: {e}")
            queryset = queryset.filter(date__lte=date_to)
            print(f"✅ Filtro por fecha hasta aplicado (fallback): {date_to}")
    
    print(f"📊 Total de registros DESPUÉS de todos los filtros: {queryset.count()}")
    
    # Serializar los datos (como los envía el backend al frontend)
    serializer = AttendanceSerializer(queryset, many=True)
    serialized_data = serializer.data
    
    print(f"✅ Datos serializados: {len(serialized_data)} registros")
    
    # Mostrar los datos que se envían al frontend
    print(f"\n📋 DATOS ENVIADOS AL FRONTEND:")
    for i, item in enumerate(serialized_data):
        print(f"   {i+1}. {item.get('employee_name', 'N/A')}: {item.get('date', 'N/A')} - {item.get('check_in', 'N/A')}")
    
    # Verificar fechas en los datos serializados
    dates_in_response = set()
    for item in serialized_data:
        if item.get('date'):
            dates_in_response.add(item['date'])
    
    print(f"\n📅 FECHAS EN LA RESPUESTA DEL BACKEND:")
    for date in sorted(dates_in_response):
        print(f"   - {date}")
    
    # Verificar si hay registros del 12 de agosto
    august_12_count = sum(1 for item in serialized_data if item.get('date') == '2025-08-12')
    august_13_count = sum(1 for item in serialized_data if item.get('date') == '2025-08-13')
    
    print(f"\n🔍 ANÁLISIS DE FECHAS ESPECÍFICAS:")
    print(f"   - Registros del 12 de agosto: {august_12_count}")
    print(f"   - Registros del 13 de agosto: {august_13_count}")
    
    # Verificar si hay discrepancia
    if august_12_count > 0 and august_13_count == 0:
        print("❌ PROBLEMA: El frontend solo muestra registros del 12 de agosto")
    elif august_13_count > 0 and august_12_count == 0:
        print("✅ CORRECTO: El frontend debería mostrar registros del 13 de agosto")
    elif august_12_count > 0 and august_13_count > 0:
        print("⚠️ AMBIGUO: El frontend muestra registros de ambas fechas")
    else:
        print("❌ PROBLEMA: No hay registros en ninguna fecha")
    
    return serialized_data

def check_frontend_display_issue():
    """Verificar si hay un problema en cómo el frontend procesa las fechas"""
    print("\n🔍 === VERIFICACIÓN DE PROBLEMA EN FRONTEND ===")
    
    # Obtener datos del 13 de agosto
    august_13_data = Attendance.objects.filter(date='2025-08-13').select_related('employee__user', 'area')
    serializer = AttendanceSerializer(august_13_data, many=True)
    data = serializer.data
    
    print(f"📊 Datos del 13 de agosto serializados: {len(data)} registros")
    
    if data:
        print(f"\n📋 PRIMER REGISTRO DEL 13 DE AGOSTO:")
        first_item = data[0]
        for key, value in first_item.items():
            print(f"   - {key}: {value}")
        
        # Verificar si hay algún problema con el formato de fecha
        date_value = first_item.get('date')
        print(f"\n🔍 ANÁLISIS DE LA FECHA:")
        print(f"   - Valor: {date_value}")
        print(f"   - Tipo: {type(date_value)}")
        print(f"   - String: {str(date_value)}")
        
        # Verificar si el frontend podría estar interpretando mal esta fecha
        if date_value:
            try:
                # Simular lo que podría estar haciendo el frontend
                parsed_date = datetime.strptime(str(date_value), '%Y-%m-%d')
                print(f"   - Parseado como: {parsed_date}")
                print(f"   - Día del mes: {parsed_date.day}")
                print(f"   - Mes: {parsed_date.month}")
                print(f"   - Año: {parsed_date.year}")
                
                # Verificar si hay algún problema de zona horaria o formato
                if parsed_date.day == 12:
                    print("⚠️ ADVERTENCIA: La fecha se está interpretando como día 12")
                elif parsed_date.day == 13:
                    print("✅ CORRECTO: La fecha se interpreta como día 13")
                else:
                    print(f"❌ PROBLEMA: La fecha se interpreta como día {parsed_date.day}")
                    
            except Exception as e:
                print(f"❌ Error parseando fecha: {e}")
    
    return data

def simulate_frontend_processing():
    """Simular exactamente cómo procesa el frontend los datos"""
    print("\n🔍 === SIMULACIÓN DEL PROCESAMIENTO DEL FRONTEND ===")
    
    # Obtener datos filtrados
    filtered_data = test_direct_filter()
    
    print(f"\n🔍 SIMULANDO PROCESAMIENTO DEL FRONTEND:")
    
    # Simular lo que hace el frontend con estos datos
    for item in filtered_data:
        date_str = item.get('date', '')
        employee_name = item.get('employee_name', 'N/A')
        check_in = item.get('check_in', 'N/A')
        
        print(f"   - Procesando: {employee_name} - {date_str} - {check_in}")
        
        # Simular formateo de fecha como lo hace el frontend
        if date_str:
            try:
                # Simular el formateo que hace el frontend
                parsed_date = datetime.strptime(str(date_str), '%Y-%m-%d')
                formatted_date = parsed_date.strftime('%d/%m/%Y')
                print(f"     → Fecha parseada: {parsed_date}")
                print(f"     → Fecha formateada: {formatted_date}")
                print(f"     → Día del mes: {parsed_date.day}")
                
            except Exception as e:
                print(f"     ❌ Error formateando fecha: {e}")

if __name__ == '__main__':
    print("🚀 Iniciando pruebas directas para encontrar el bug del frontend...")
    
    # Probar filtro directo
    test_direct_filter()
    
    # Verificar problema en frontend
    check_frontend_display_issue()
    
    # Simular procesamiento del frontend
    simulate_frontend_processing()
    
    print("\n✅ Pruebas completadas")

