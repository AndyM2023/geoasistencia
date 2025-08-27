from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Employee, Attendance
from datetime import date


class Command(BaseCommand):
    help = 'Prueba la nueva lógica de conteo de días ausentes'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🧪 Probando nueva lógica de días ausentes...'))
        
        # Obtener empleado de prueba
        try:
            employee = Employee.objects.first()
            if not employee:
                self.stdout.write(self.style.ERROR('❌ No hay empleados para probar'))
                return
            
            self.stdout.write(f'👤 Empleado: {employee.full_name}')
            
            # Obtener todas las asistencias del empleado
            attendances = Attendance.objects.filter(employee=employee)
            total_days = attendances.count()
            
            self.stdout.write(f'📊 Total de asistencias: {total_days}')
            
            # Contar por estado
            status_counts = {}
            for attendance in attendances:
                status = attendance.status
                if status not in status_counts:
                    status_counts[status] = 0
                status_counts[status] += 1
            
            self.stdout.write('\n📋 Conteo por estado:')
            for status, count in status_counts.items():
                self.stdout.write(f'   - {status}: {count}')
            
            # NUEVA LÓGICA: Contar solo registros con estado "ausente"
            absent_days = attendances.filter(status='absent').count()
            self.stdout.write(f'\n✅ Días ausentes (nueva lógica): {absent_days}')
            
            # LÓGICA ANTERIOR (para comparar)
            current_month = timezone.localtime().month
            current_year = timezone.localtime().year
            from calendar import monthrange
            _, days_in_month = monthrange(current_year, current_month)
            
            # Calcular días laborables reales del mes
            working_days = 0
            for day in range(1, days_in_month + 1):
                date_obj = date(current_year, current_month, day)
                if date_obj.weekday() < 5:  # Lunes a Viernes
                    working_days += 1
            
            old_absent_days = max(0, working_days - total_days)
            self.stdout.write(f'❌ Días ausentes (lógica anterior): {old_absent_days}')
            
            # Mostrar diferencia
            difference = absent_days - old_absent_days
            if difference != 0:
                self.stdout.write(self.style.WARNING(f'⚠️ Diferencia: {difference} días'))
                if difference > 0:
                    self.stdout.write('   - La nueva lógica muestra MÁS días ausentes')
                else:
                    self.stdout.write('   - La nueva lógica muestra MENOS días ausentes')
            else:
                self.stdout.write(self.style.SUCCESS('✅ Ambas lógicas coinciden'))
            
            # Mostrar algunos ejemplos de asistencias
            self.stdout.write('\n📋 Ejemplos de asistencias:')
            for attendance in attendances[:5]:  # Solo las primeras 5
                self.stdout.write(f'   - {attendance.date}: {attendance.status}')
            
            self.stdout.write('\n✅ Prueba completada')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {e}'))
            import traceback
            traceback.print_exc()
