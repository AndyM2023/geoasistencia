from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import time, datetime, timedelta
from core.models import Employee, Area, Attendance
from core.services.schedule_service import ScheduleService


class Command(BaseCommand):
    help = 'Prueba la nueva lógica de validación de asistencia'

    def add_arguments(self, parser):
        parser.add_argument(
            '--employee-id',
            type=int,
            help='ID del empleado para probar',
        )
        parser.add_argument(
            '--area-id',
            type=int,
            help='ID del área para probar',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🧪 Iniciando pruebas de validación de asistencia...'))
        
        # Obtener empleado y área
        try:
            if options['employee_id']:
                employee = Employee.objects.get(id=options['employee_id'])
            else:
                employee = Employee.objects.first()
            
            if options['area_id']:
                area = Area.objects.get(id=options['area_id'])
            else:
                area = Area.objects.first()
            
            if not employee or not area:
                self.stdout.write(self.style.ERROR('❌ No se encontraron empleados o áreas'))
                return
            
            self.stdout.write(f'👤 Empleado: {employee.full_name}')
            self.stdout.write(f'🏢 Área: {area.name}')
            
        except (Employee.DoesNotExist, Area.DoesNotExist) as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {e}'))
            return
        
        # Obtener horarios del área
        today = timezone.now().date()
        expected_check_in, expected_check_out = ScheduleService.get_expected_times(area, today)
        grace_period = ScheduleService.get_grace_period(area)
        
        self.stdout.write(f'📅 Fecha: {today}')
        self.stdout.write(f'⏰ Hora entrada esperada: {expected_check_in}')
        self.stdout.write(f'⏰ Hora salida esperada: {expected_check_out}')
        self.stdout.write(f'⏰ Período de gracia: {grace_period} minutos')
        
        if not expected_check_in or not expected_check_out:
            self.stdout.write(self.style.WARNING('⚠️ Área sin horario definido'))
            return
        
        # Probar diferentes horarios de entrada
        test_times = [
            ('A TIEMPO', expected_check_in),
            ('TARDE (dentro tolerancia)', 
             (datetime.combine(today, expected_check_in) + timedelta(minutes=grace_period)).time()),
            ('TARDE (fuera tolerancia)', 
             (datetime.combine(today, expected_check_in) + timedelta(minutes=grace_period + 5)).time()),
            ('MUY TARDE (después de salida)', 
             (datetime.combine(today, expected_check_out) + timedelta(minutes=30)).time()),
        ]
        
        self.stdout.write('\n🔍 Probando diferentes horarios de entrada:')
        
        for test_name, test_time in test_times:
            self.stdout.write(f'\n📋 {test_name}:')
            self.stdout.write(f'   - Hora: {test_time}')
            
            # Calcular hora límite con tolerancia
            limit_time = datetime.combine(today, expected_check_in)
            limit_time = limit_time + timedelta(minutes=grace_period)
            limit_time = limit_time.time()
            
            # Verificar si es tarde
            if test_time > expected_check_out:
                self.stdout.write(f'   - ❌ MUY TARDE: Después de hora de salida')
                self.stdout.write(f'   - Estado: No permitido')
            elif test_time > limit_time:
                self.stdout.write(f'   - ⚠️ TARDE: Fuera de tolerancia')
                self.stdout.write(f'   - Estado: late (Tardanza)')
            else:
                self.stdout.write(f'   - ✅ A TIEMPO: Dentro de tolerancia')
                self.stdout.write(f'   - Estado: present (Presente)')
        
        # Verificar asistencias existentes
        existing_attendance = Attendance.objects.filter(
            employee=employee, 
            date=today
        ).first()
        
        if existing_attendance:
            self.stdout.write(f'\n📊 Asistencia existente para hoy:')
            self.stdout.write(f'   - Entrada: {existing_attendance.check_in}')
            self.stdout.write(f'   - Salida: {existing_attendance.check_out}')
            self.stdout.write(f'   - Status: {existing_attendance.status}')
            self.stdout.write(f'   - Es tarde: {existing_attendance.is_late}')
        else:
            self.stdout.write(f'\n📊 No hay asistencia registrada para hoy')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Pruebas completadas'))
