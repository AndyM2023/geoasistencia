#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

from core.models import Area, AreaSchedule

print("🔍 VERIFICANDO SCHEDULE_TYPES EN LA BASE DE DATOS")
print("=" * 60)

# Verificar todas las áreas con schedule
areas_with_schedule = Area.objects.filter(schedule__isnull=False).select_related('schedule')

print(f"📊 Total de áreas con schedule: {areas_with_schedule.count()}")
print()

for area in areas_with_schedule:
    schedule = area.schedule
    print(f"🏢 Área: {area.name} (ID: {area.id})")
    print(f"   📅 Schedule ID: {schedule.id}")
    print(f"   🎯 Schedule Type: {schedule.schedule_type}")
    print(f"   📋 Días activos:")
    
    # Verificar días activos
    active_days = []
    for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
        if getattr(schedule, f'{day}_active'):
            active_days.append(day)
    
    print(f"      ✅ {', '.join(active_days)}")
    print(f"   ⏰ Grace Period: {schedule.grace_period_minutes} minutos")
    print()

# Verificar específicamente BLOQUE AA
print("🔍 VERIFICACIÓN ESPECÍFICA DE BLOQUE AA")
print("=" * 40)

try:
    bloque_aa = Area.objects.get(name="BLOQUE AA")
    if hasattr(bloque_aa, 'schedule') and bloque_aa.schedule:
        schedule = bloque_aa.schedule
        print(f"🏢 Área: {bloque_aa.name}")
        print(f"   📅 Schedule ID: {schedule.id}")
        print(f"   🎯 Schedule Type: {schedule.schedule_type}")
        print(f"   📋 Días activos:")
        
        active_days = []
        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
            if getattr(schedule, f'{day}_active'):
                active_days.append(day)
        
        print(f"      ✅ {', '.join(active_days)}")
        print(f"   ⏰ Grace Period: {schedule.grace_period_minutes} minutos")
    else:
        print("❌ BLOQUE AA no tiene schedule")
except Area.DoesNotExist:
    print("❌ BLOQUE AA no encontrado")

print()
print("🔍 VERIFICACIÓN DE TODOS LOS SCHEDULE_TYPES")
print("=" * 50)

# Contar por tipo
schedule_types = AreaSchedule.objects.values_list('schedule_type', flat=True)
type_counts = {}
for st in schedule_types:
    type_counts[st] = type_counts.get(st, 0) + 1

for schedule_type, count in type_counts.items():
    print(f"   {schedule_type}: {count} áreas")

print()
print("✅ Verificación completada")
