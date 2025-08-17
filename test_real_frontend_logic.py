#!/usr/bin/env python
"""
Script para simular exactamente la lógica real del frontend
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

def simulate_real_frontend_logic():
    """Simular exactamente la lógica real del frontend"""
    print("🔍 === SIMULACIÓN DE LÓGICA REAL DEL FRONTEND ===")
    
    # Simular las fechas que selecciona el usuario
    print("📅 FECHAS SELECCIONADAS EN EL FRONTEND:")
    print("   - dateFrom: 2025-08-12")
    print("   - dateTo: 2025-08-13")
    
    # Simular la función formatDateToISO del frontend (código real)
    def formatDateToISO(date_str):
        """Simular la función formatDateToISO del frontend"""
        try:
            # Simular: new Date(dateString)
            parsed_date = datetime.strptime(date_str, '%Y-%m-%d')
            
            # Simular: date.getFullYear()
            year = parsed_date.year
            
            # Simular: date.getMonth() + 1 (JavaScript: 0-11, Python: 1-12)
            # En JavaScript: getMonth() devuelve 0-11, por eso se suma 1
            # En Python: month ya es 1-12, NO necesitamos sumar 1
            month = parsed_date.month  # NO sumar 1 en Python
            
            # Simular: date.getDate()
            day = parsed_date.day
            
            # Simular: String(date.getMonth() + 1).padStart(2, '0')
            month_str = str(month).zfill(2)
            day_str = str(day).zfill(2)
            
            result = f"{year}-{month_str}-{day_str}"
            print(f"     → {date_str} → {result} (month: {month}, day: {day})")
            return result
            
        except Exception as e:
            print(f"     ❌ Error convirtiendo {date_str}: {e}")
            return date_str
    
    # Simular la conversión
    print("\n🔍 CONVERSIÓN A FORMATO ISO (LÓGICA CORREGIDA):")
    converted_from = formatDateToISO('2025-08-12')
    converted_to = formatDateToISO('2025-08-13')
    
    print(f"\n📅 FECHAS CONVERTIDAS:")
    print(f"   - date_from: {converted_from}")
    print(f"   - date_to: {converted_to}")
    
    # Ahora simular la petición al backend
    print(f"\n🔍 SIMULANDO PETICIÓN AL BACKEND:")
    print(f"   - URL: /attendance/?date_from={converted_from}&date_to={converted_to}")
    
    # Aplicar los filtros como lo hace el backend
    queryset = Attendance.objects.select_related('employee__user', 'area').all()
    
    # Filtro desde
    if converted_from:
        queryset = queryset.filter(date__gte=converted_from)
        print(f"✅ Filtro desde aplicado: date__gte={converted_from}")
    
    # Filtro hasta
    if converted_to:
        try:
            date_to_obj = datetime.strptime(converted_to, '%Y-%m-%d').date()
            next_day = date_to_obj + timedelta(days=1)
            queryset = queryset.filter(date__lt=next_day)
            print(f"✅ Filtro hasta aplicado: date__lt={next_day}")
        except Exception as e:
            print(f"❌ Error en filtro hasta: {e}")
    
    print(f"📊 Total de registros después de filtros: {queryset.count()}")
    
    # Serializar los datos
    serializer = AttendanceSerializer(queryset, many=True)
    serialized_data = serializer.data
    
    print(f"✅ Datos serializados: {len(serialized_data)} registros")
    
    # Mostrar los datos que se envían al frontend
    print(f"\n📋 DATOS ENVIADOS AL FRONTEND:")
    for i, item in enumerate(serialized_data):
        print(f"   {i+1}. {item.get('employee_name', 'N/A')}: {item.get('date', 'N/A')} - {item.get('check_in', 'N/A')}")
    
    # Verificar fechas únicas
    dates_in_response = set()
    for item in serialized_data:
        if item.get('date'):
            dates_in_response.add(item['date'])
    
    print(f"\n📅 FECHAS EN LA RESPUESTA:")
    for date in sorted(dates_in_response):
        print(f"   - {date}")
    
    return serialized_data

def check_why_frontend_shows_wrong_data():
    """Verificar por qué el frontend muestra datos incorrectos"""
    print("\n🔍 === VERIFICACIÓN DE POR QUÉ EL FRONTEND MUESTRA DATOS INCORRECTOS ===")
    
    # Obtener datos del 13 de agosto
    august_13_data = Attendance.objects.filter(date='2025-08-13').select_related('employee__user', 'area')
    serializer = AttendanceSerializer(august_13_data, many=True)
    data = serializer.data
    
    print(f"📊 Datos del 13 de agosto en backend: {len(data)} registros")
    
    if data:
        print(f"\n📋 DATOS REALES DEL BACKEND:")
        for item in data:
            print(f"   - {item.get('employee_name')}: {item.get('date')} - {item.get('check_in')}")
        
        # Simular la función formatDate del frontend
        def simulate_formatDate(date_string):
            """Simular la función formatDate del frontend"""
            try:
                # Simular: new Date(dateString).toLocaleDateString('es-ES')
                parsed_date = datetime.strptime(date_string, '%Y-%m-%d')
                # En JavaScript: toLocaleDateString('es-ES') podría mostrar 12/08/2025 en lugar de 13/08/2025
                formatted = parsed_date.strftime('%d/%m/%Y')
                return formatted
            except Exception as e:
                return f"Error: {e}"
        
        print(f"\n🔍 SIMULANDO FORMATO DEL FRONTEND:")
        for item in data:
            date_str = item.get('date', '')
            employee_name = item.get('employee_name', 'N/A')
            formatted_date = simulate_formatDate(date_str)
            
            print(f"   - {employee_name}: {date_str} → {formatted_date}")
            
            # Verificar si hay problema
            if date_str == '2025-08-13' and '12/08/2025' in formatted_date:
                print("     ❌ PROBLEMA: Fecha del 13 se muestra como 12")
            elif date_str == '2025-08-13' and '13/08/2025' in formatted_date:
                print("     ✅ CORRECTO: Fecha del 13 se muestra correctamente")

def check_if_there_are_other_records():
    """Verificar si hay otros registros que podrían estar causando confusión"""
    print("\n🔍 === VERIFICACIÓN DE OTROS REGISTROS ===")
    
    # Verificar si hay registros del 12 de agosto
    august_12_data = Attendance.objects.filter(date='2025-08-12').select_related('employee__user', 'area')
    print(f"📊 Registros del 12 de agosto: {august_12_data.count()}")
    
    if august_12_data.count() > 0:
        print(f"❌ PROBLEMA ENCONTRADO: Hay registros del 12 de agosto")
        for item in august_12_data:
            print(f"   - {item.employee.full_name}: {item.date} - {item.check_in}")
    else:
        print(f"✅ No hay registros del 12 de agosto")
    
    # Verificar si hay registros del 14 de agosto
    august_14_data = Attendance.objects.filter(date='2025-08-14').select_related('employee__user', 'area')
    print(f"📊 Registros del 14 de agosto: {august_14_data.count()}")
    
    if august_14_data.count() > 0:
        print(f"📋 Registros del 14 de agosto:")
        for item in august_14_data:
            print(f"   - {item.employee.full_name}: {item.date} - {item.check_in}")
    
    # Verificar si hay registros del 16 de agosto
    august_16_data = Attendance.objects.filter(date='2025-08-16').select_related('employee__user', 'area')
    print(f"📊 Registros del 16 de agosto: {august_16_data.count()}")
    
    if august_16_data.count() > 0:
        print(f"📋 Registros del 16 de agosto:")
        for item in august_16_data:
            print(f"   - {item.employee.full_name}: {item.date} - {item.check_in}")

if __name__ == '__main__':
    print("🚀 Iniciando simulación de la lógica real del frontend...")
    
    # Simular lógica real del frontend
    simulate_real_frontend_logic()
    
    # Verificar por qué el frontend muestra datos incorrectos
    check_why_frontend_shows_wrong_data()
    
    # Verificar si hay otros registros
    check_if_there_are_other_records()
    
    print("\n✅ Simulación completada")


