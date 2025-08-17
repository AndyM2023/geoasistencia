#!/usr/bin/env python
"""
Script para simular exactamente lo que hace el frontend y encontrar el bug
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
from django.test import RequestFactory
from django.contrib.auth import get_user_model

def simulate_frontend_request():
    """Simular exactamente la petición del frontend"""
    print("🔍 === SIMULACIÓN DE PETICIÓN DEL FRONTEND ===")
    
    # Simular parámetros del frontend
    date_from = '2025-08-12'
    date_to = '2025-08-13'
    
    print(f"📅 Parámetros del frontend:")
    print(f"   - date_from: {date_from}")
    print(f"   - date_to: {date_to}")
    
    # Crear request simulada (como lo hace el frontend)
    factory = RequestFactory()
    request = factory.get(f'/attendance/?date_from={date_from}&date_to={date_to}')
    
    # Simular usuario autenticado
    User = get_user_model()
    user = User.objects.first()
    if user:
        request.user = user
        print(f"✅ Usuario autenticado: {user.username}")
    else:
        print("❌ No hay usuarios")
        return
    
    # Simular el ViewSet del backend
    from core.views import AttendanceViewSet
    viewset = AttendanceViewSet()
    viewset.request = request
    
    print("\n🔍 Aplicando filtros en el backend...")
    
    try:
        # Obtener queryset con filtros (como lo hace el backend)
        queryset = viewset.get_queryset()
        
        print(f"✅ Queryset obtenido del backend: {queryset.count()} registros")
        
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
        
        # Simular lo que hace el frontend con estos datos
        print(f"\n🔍 SIMULANDO PROCESAMIENTO DEL FRONTEND:")
        
        # Verificar si hay registros del 12 de agosto
        august_12_count = sum(1 for item in serialized_data if item.get('date') == '2025-08-12')
        august_13_count = sum(1 for item in serialized_data if item.get('date') == '2025-08-13')
        
        print(f"   - Registros del 12 de agosto: {august_12_count}")
        print(f"   - Registros del 13 de agosto: {august_13_count}")
        
        # Verificar si hay discrepancia
        if august_12_count > 0 and august_13_count == 0:
            print("❌ PROBLEMA: El frontend solo muestra registros del 12 de agosto")
        elif august_13_count > 0 and august_12_count == 0:
            print("✅ CORRECTO: El frontend muestra registros del 13 de agosto")
        elif august_12_count > 0 and august_13_count > 0:
            print("⚠️ AMBIGUO: El frontend muestra registros de ambas fechas")
        else:
            print("❌ PROBLEMA: No hay registros en ninguna fecha")
            
    except Exception as e:
        print(f"❌ Error en la simulación: {e}")
        import traceback
        traceback.print_exc()

def check_serializer_data():
    """Verificar qué datos produce el serializer"""
    print("\n🔍 === VERIFICACIÓN DEL SERIALIZER ===")
    
    try:
        # Obtener registros del 13 de agosto
        august_13_attendances = Attendance.objects.filter(date='2025-08-13').select_related('employee__user', 'area')
        
        print(f"📊 Registros del 13 de agosto en base: {august_13_attendances.count()}")
        
        if august_13_attendances.count() > 0:
            print(f"\n📋 DATOS EN BASE (13 de agosto):")
            for attendance in august_13_attendances:
                print(f"   - {attendance.employee.full_name}: {attendance.date} - {attendance.check_in}")
            
            # Serializar estos datos
            serializer = AttendanceSerializer(august_13_attendances, many=True)
            serialized_data = serializer.data
            
            print(f"\n📋 DATOS SERIALIZADOS (13 de agosto):")
            for i, item in enumerate(serialized_data):
                print(f"   {i+1}. {item.get('employee_name', 'N/A')}: {item.get('date', 'N/A')} - {item.get('check_in', 'N/A')}")
                
            # Verificar campos específicos
            if serialized_data:
                first_item = serialized_data[0]
                print(f"\n🔍 CAMPOS DEL PRIMER REGISTRO:")
                for key, value in first_item.items():
                    print(f"   - {key}: {value}")
                    
    except Exception as e:
        print(f"❌ Error verificando serializer: {e}")
        import traceback
        traceback.print_exc()

def check_date_format_issues():
    """Verificar problemas de formato de fecha"""
    print("\n🔍 === VERIFICACIÓN DE FORMATOS DE FECHA ===")
    
    try:
        # Obtener un registro del 13 de agosto
        attendance = Attendance.objects.filter(date='2025-08-13').first()
        
        if attendance:
            print(f"📅 Registro de ejemplo del 13 de agosto:")
            print(f"   - ID: {attendance.id}")
            print(f"   - Empleado: {attendance.employee.full_name}")
            print(f"   - Fecha (date): {attendance.date}")
            print(f"   - Fecha (date) tipo: {type(attendance.date)}")
            print(f"   - Fecha (date) str: {str(attendance.date)}")
            print(f"   - Fecha (date) isoformat: {attendance.date.isoformat()}")
            
            # Verificar si hay problemas de zona horaria
            from django.utils import timezone
            print(f"   - Timezone actual: {timezone.get_current_timezone()}")
            print(f"   - Fecha con timezone: {timezone.localtime(attendance.created_at).date()}")
            
    except Exception as e:
        print(f"❌ Error verificando formato de fecha: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("🚀 Iniciando simulación del frontend para encontrar el bug...")
    
    # Verificar datos del serializer
    check_serializer_data()
    
    # Verificar formatos de fecha
    check_date_format_issues()
    
    # Simular petición del frontend
    simulate_frontend_request()
    
    print("\n✅ Simulación completada")

