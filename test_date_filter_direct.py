#!/usr/bin/env python
"""
Script de prueba directa para verificar el filtro de fechas
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

from core.models import Attendance, Employee, Area, User
from django.db.models import Q

def test_date_filter_direct():
    """Probar el filtro de fechas directamente en la base de datos"""
    print("🔍 === PRUEBA DIRECTA DEL FILTRO DE FECHAS ===")
    
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
            
        # Verificar si hay registros del 13 de agosto
        august_13_count = queryset.filter(date='2025-08-13').count()
        august_12_count = queryset.filter(date='2025-08-12').count()
        
        print(f"\n🔍 ANÁLISIS DE FECHAS ESPECÍFICAS:")
        print(f"   - Registros del 12 de agosto: {august_12_count}")
        print(f"   - Registros del 13 de agosto: {august_13_count}")
        
    else:
        print("❌ No se encontraron registros")
    
    return queryset

def check_specific_dates():
    """Verificar registros en fechas específicas"""
    print("\n🔍 === VERIFICACIÓN DE FECHAS ESPECÍFICAS ===")
    
    # Verificar registros del 12 de agosto
    august_12 = Attendance.objects.filter(date='2025-08-12').select_related('employee__user')
    print(f"📅 Registros del 12 de agosto: {august_12.count()}")
    if august_12.count() > 0:
        for attendance in august_12:
            print(f"   - {attendance.employee.full_name}: {attendance.check_in}")
    
    # Verificar registros del 13 de agosto
    august_13 = Attendance.objects.filter(date='2025-08-13').select_related('employee__user')
    print(f"📅 Registros del 13 de agosto: {august_13.count()}")
    if august_13.count() > 0:
        for attendance in august_13:
            print(f"   - {attendance.employee.full_name}: {attendance.check_in}")
    
    # Verificar registros del 14 de agosto
    august_14 = Attendance.objects.filter(date='2025-08-14').select_related('employee__user')
    print(f"📅 Registros del 14 de agosto: {august_14.count()}")
    if august_14.count() > 0:
        for attendance in august_14:
            print(f"   - {attendance.employee.full_name}: {attendance.check_in}")

if __name__ == '__main__':
    print("🚀 Iniciando pruebas directas del filtro de fechas...")
    
    # Verificar fechas específicas
    check_specific_dates()
    
    # Probar filtro de fechas
    result_queryset = test_date_filter_direct()
    
    print("\n✅ Pruebas completadas")

