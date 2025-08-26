from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import time, datetime, timedelta
from core.models import Employee, Area, Attendance
from core.services.schedule_service import ScheduleService


class Command(BaseCommand):
    help = 'Prueba la validación de salida prematura (no permitir marcar salida antes de la hora esperada)'

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
        self.stdout.write(self.style.SUCCESS('🧪 Iniciando pruebas de validación de salida prematura...'))
        
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
        
        # Probar diferentes escenarios de salida
        test_scenarios = [
            ('SALIDA PREMATURA (1 hora antes)', 
             (datetime.combine(today, expected_check_out) - timedelta(hours=1)).time()),
            ('SALIDA PREMATURA (30 min antes)', 
             (datetime.combine(today, expected_check_out) - timedelta(minutes=30)).time()),
            ('SALIDA PREMATURA (15 min antes)', 
             (datetime.combine(today, expected_check_out) - timedelta(minutes=15)).time()),
            ('SALIDA A TIEMPO (exacta)', expected_check_out),
            ('SALIDA TARDÍA (15 min después)', 
             (datetime.combine(today, expected_check_out) + timedelta(minutes=15)).time()),
            ('SALIDA TARDÍA (1 hora después)', 
             (datetime.combine(today, expected_check_out) + timedelta(hours=1)).time()),
        ]
        
        self.stdout.write('\n🔍 Probando diferentes escenarios de salida:')
        
        for test_name, test_time in test_scenarios:
            self.stdout.write(f'\n📋 {test_name}: {test_time}')
            
            # Crear asistencia de prueba
            try:
                # Limpiar asistencia anterior si existe
                Attendance.objects.filter(employee=employee, date=today).delete()
                
                # Crear entrada a una hora razonable
                check_in_time = (datetime.combine(today, expected_check_in) - timedelta(minutes=30)).time()
                
                attendance = Attendance.objects.create(
                    employee=employee,
                    date=today,
                    area=area,
                    check_in=check_in_time,
                    status='present'
                )
                
                self.stdout.write(f'   ✅ Entrada creada: {check_in_time}')
                
                # Intentar marcar salida
                try:
                    attendance.check_out = test_time
                    attendance.save()
                    
                    # Si llegó aquí, la validación pasó
                    if test_time < expected_check_out:
                        self.stdout.write(self.style.ERROR(f'   ❌ ERROR: Se permitió salida prematura'))
                        self.stdout.write(f'      - Hora salida: {test_time}')
                        self.stdout.write(f'      - Hora esperada: {expected_check_out}')
                    else:
                        self.stdout.write(self.style.SUCCESS(f'   ✅ SALIDA PERMITIDA: {test_time}'))
                        
                except Exception as e:
                    if test_time < expected_check_out:
                        self.stdout.write(self.style.SUCCESS(f'   ✅ VALIDACIÓN FUNCIONA: {str(e)}'))
                    else:
                        self.stdout.write(self.style.ERROR(f'   ❌ ERROR INESPERADO: {str(e)}'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'   ❌ Error creando asistencia: {e}'))
        
        # Limpiar datos de prueba
        Attendance.objects.filter(employee=employee, date=today).delete()
        self.stdout.write('\n🧹 Datos de prueba limpiados')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Pruebas de validación de salida prematura completadas'))
