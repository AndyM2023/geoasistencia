#!/usr/bin/env python
"""
Script para arreglar el error 401 y el problema del horario
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

from core.models import Area, AreaSchedule
from datetime import date, time

def main():
    print("🚀 ARREGLANDO ERROR 401 Y HORARIO DE SÁBADO...")
    print("=" * 60)
    
    try:
        # 1. Buscar el área BLOQUE A
        print("🔍 Buscando área 'BLOQUE A'...")
        area = Area.objects.get(name='BLOQUE A')
        print(f"✅ Área encontrada: {area.name} (ID: {area.id})")
        
        # 2. Verificar si tiene schedule
        if hasattr(area, 'schedule'):
            schedule = area.schedule
            print(f"📅 Schedule existente encontrado (ID: {schedule.id})")
        else:
            print(f"❌ No tiene schedule, creando uno...")
            schedule = AreaSchedule.objects.create(
                area=area,
                schedule_type='custom',
                monday_start=time(8, 0),
                monday_end=time(17, 0),
                monday_active=True,
                tuesday_start=time(8, 0),
                tuesday_end=time(17, 0),
                tuesday_active=True,
                wednesday_start=time(8, 0),
                wednesday_end=time(17, 0),
                wednesday_active=True,
                thursday_start=time(8, 0),
                thursday_end=time(17, 0),
                thursday_active=True,
                friday_start=time(8, 0),
                friday_end=time(17, 0),
                friday_active=True,
                saturday_start=time(8, 0),
                saturday_end=time(17, 0),
                saturday_active=True,  # ¡SÁBADO ACTIVO!
                sunday_start=None,
                sunday_end=None,
                sunday_active=False,
                grace_period_minutes=15
            )
            print(f"✅ Schedule creado con ID: {schedule.id}")
        
        # 3. Asegurar que sábado esté activo
        print(f"\n🔧 Activando sábado...")
        schedule.saturday_active = True
        schedule.saturday_start = time(8, 0)
        schedule.saturday_end = time(17, 0)
        schedule.schedule_type = 'custom'
        schedule.save()
        
        print(f"✅ Sábado activado:")
        print(f"   - Sábado activo: {schedule.saturday_active}")
        print(f"   - Horario: {schedule.saturday_start} - {schedule.saturday_end}")
        
        # 4. Verificar que funcione
        today = date.today()
        weekday = today.weekday()
        weekday_names = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        current_weekday = weekday_names[weekday]
        
        print(f"\n📅 Verificación:")
        print(f"   - Fecha actual: {today}")
        print(f"   - Día: {current_weekday} (weekday: {weekday})")
        
        from core.services.schedule_service import ScheduleService
        is_work_day = ScheduleService.is_work_day(area, today)
        print(f"   - ¿Es día laboral?: {is_work_day}")
        
        if is_work_day:
            expected_start, expected_end = ScheduleService.get_expected_times(area, today)
            print(f"   - Horario esperado: {expected_start} - {expected_end}")
            print(f"✅ ¡PROBLEMA RESUELTO! Ahora es día laboral")
        else:
            print(f"❌ Aún no es día laboral - revisando configuración...")
            print(f"   - Lunes: {schedule.monday_active}")
            print(f"   - Martes: {schedule.tuesday_active}")
            print(f"   - Miércoles: {schedule.wednesday_active}")
            print(f"   - Jueves: {schedule.thursday_active}")
            print(f"   - Viernes: {schedule.friday_active}")
            print(f"   - Sábado: {schedule.saturday_active}")
            print(f"   - Domingo: {schedule.sunday_active}")
        
        # 5. Verificar todas las áreas
        print(f"\n📋 VERIFICANDO TODAS LAS ÁREAS:")
        areas = Area.objects.all()
        for a in areas:
            has_schedule = hasattr(a, 'schedule')
            print(f"   - {a.name}: {'✅ Con horario' if has_schedule else '❌ Sin horario'}")
        
        print(f"\n✅ DIAGNÓSTICO COMPLETADO")
        
    except Area.DoesNotExist:
        print(f"❌ ERROR: No se encontró el área 'BLOQUE A'")
        print(f"📋 ÁREAS DISPONIBLES:")
        areas = Area.objects.all()
        for a in areas:
            print(f"   - {a.name} (ID: {a.id})")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
