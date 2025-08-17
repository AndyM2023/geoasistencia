#!/usr/bin/env python
"""
Script de prueba para verificar el filtro de fechas del backend
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

from core.models import Attendance, Employee, Area, User
from core.views import AttendanceViewSet
from django.test import RequestFactory
from django.contrib.auth import get_user_model

def test_date_filter():
    """Probar el filtro de fechas del backend"""
    print("🔍 === PRUEBA DEL FILTRO DE FECHAS ===")
    
    # Crear request factory para simular peticiones
    factory = RequestFactory()
    
    # Simular parámetros de fecha
    date_from = '2025-08-12'
    date_to = '2025-08-13'
    
    print(f"📅 Fechas de prueba:")
    print(f"   - Desde: {date_from}")
    print(f"   - Hasta: {date_to}")
    
    # Crear request simulada
    request = factory.get(f'/attendance/?date_from={date_from}&date_to={date_to}')
    
    # Simular usuario autenticado
    User = get_user_model()
    try:
        user = User.objects.first()
        if user:
            request.user = user
            print(f"✅ Usuario autenticado: {user.username}")
        else:
            print("⚠️ No hay usuarios en la base de datos")
            return
    except Exception as e:
        print(f"❌ Error obteniendo usuario: {e}")
        return
    
    # Crear instancia del ViewSet
    viewset = AttendanceViewSet()
    viewset.request = request
    
    print("\n🔍 Aplicando filtros...")
    
    try:
        # Obtener queryset con filtros
        queryset = viewset.get_queryset()
        
        print(f"✅ Queryset obtenido exitosamente")
        print(f"📊 Total de registros después de filtros: {queryset.count()}")
        
        # Mostrar registros encontrados
        if queryset.count() > 0:
            print(f"\n📋 REGISTROS ENCONTRADOS:")
            for attendance in queryset:
                print(f"   - {attendance.employee.full_name}: {attendance.date} - {attendance.check_in}")
            
            # Verificar fechas únicas
            dates = queryset.values_list('date', flat=True).distinct().order_by('date')
            print(f"\n📅 FECHAS ÚNICAS EN RESULTADOS:")
            for date in dates:
                print(f"   - {date}")
        else:
            print("❌ No se encontraron registros")
            
    except Exception as e:
        print(f"❌ Error en get_queryset: {e}")
        import traceback
        traceback.print_exc()

def check_database_data():
    """Verificar qué datos hay en la base de datos"""
    print("\n🔍 === VERIFICACIÓN DE DATOS EN BASE ===")
    
    try:
        # Verificar empleados
        employees_count = Employee.objects.count()
        print(f"👥 Total de empleados: {employees_count}")
        
        # Verificar asistencias
        attendances_count = Attendance.objects.count()
        print(f"📊 Total de asistencias: {attendances_count}")
        
        if attendances_count > 0:
            # Mostrar últimas asistencias
            print(f"\n📋 ÚLTIMAS ASISTENCIAS:")
            latest_attendances = Attendance.objects.select_related('employee').order_by('-date', '-created_at')[:10]
            for attendance in latest_attendances:
                print(f"   - {attendance.employee.full_name}: {attendance.date} - {attendance.check_in}")
            
            # Verificar fechas disponibles
            dates = Attendance.objects.values_list('date', flat=True).distinct().order_by('date')
            print(f"\n📅 FECHAS DISPONIBLES EN BASE:")
            for date in dates:
                print(f"   - {date}")
                
    except Exception as e:
        print(f"❌ Error verificando base de datos: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("🚀 Iniciando pruebas del filtro de fechas...")
    
    # Verificar datos en base
    check_database_data()
    
    # Probar filtro de fechas
    test_date_filter()
    
    print("\n✅ Pruebas completadas")

