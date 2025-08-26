from django.core.management.base import BaseCommand
from core.models import Attendance, Employee, Area
from django.utils import timezone

class Command(BaseCommand):
    help = 'Mostrar todas las asistencias en la base de datos'

    def handle(self, *args, **options):
        self.stdout.write('🎯 ASISTENCIAS EN LA BASE DE DATOS:')
        self.stdout.write('=' * 60)
        
        # Obtener todas las asistencias
        attendances = Attendance.objects.select_related('employee__user', 'area').all().order_by('-date', '-check_in')
        
        if not attendances.exists():
            self.stdout.write(self.style.WARNING('❌ No hay asistencias registradas'))
            return
        
        for attendance in attendances:
            self.stdout.write(f'📅 Fecha: {attendance.date}')
            self.stdout.write(f'👤 Empleado: {attendance.employee.full_name} (ID: {attendance.employee.id})')
            self.stdout.write(f'🏢 Área: {attendance.area.name}')
            self.stdout.write(f'⏰ Entrada: {attendance.check_in}')
            self.stdout.write(f'⏰ Salida: {attendance.check_out or "No registrada"}')
            self.stdout.write(f'📍 Ubicación: {attendance.latitude}, {attendance.longitude}')
            self.stdout.write(f'🎯 Rostro verificado: {"✅ Sí" if attendance.face_verified else "❌ No"}')
            self.stdout.write(f'📊 Estado: {attendance.get_status_display()}')
            self.stdout.write(f'🆔 ID Asistencia: {attendance.id}')
            self.stdout.write('-' * 40)
        
        # Contar totales
        total_attendances = attendances.count()
        today = timezone.localtime().date()
        today_attendances = attendances.filter(date=today).count()
        
        self.stdout.write(f'\n📊 RESUMEN:')
        self.stdout.write(f'   - Total de asistencias: {total_attendances}')
        self.stdout.write(f'   - Asistencias de hoy ({today}): {today_attendances}')
        
        # Mostrar empleado específico (ID: 6)
        employee_6_attendances = attendances.filter(employee_id=6)
        if employee_6_attendances.exists():
            self.stdout.write(f'\n👤 ASISTENCIAS DEL EMPLEADO ID 6:')
            for att in employee_6_attendances:
                self.stdout.write(f'   - {att.date}: {att.check_in} (Rostro: {"✅" if att.face_verified else "❌"})')

