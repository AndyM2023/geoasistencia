from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from core.models import Employee, Area, Attendance
from core.services.schedule_service import ScheduleService


class Command(BaseCommand):
    help = 'Prueba la nueva lógica de validación de entrada temprana'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🧪 Probando validación de entrada temprana...'))
        
        # Obtener área y empleado de prueba
        try:
            area = Area.objects.first()
            employee = Employee.objects.first()
            
            if not area or not employee:
                self.stdout.write(self.style.ERROR('❌ No hay áreas o empleados para probar'))
                return
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error obteniendo datos: {e}'))
            return
        
        # Obtener horarios esperados
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
        
        # Calcular rangos de tiempo
        min_time = (datetime.combine(today, expected_check_in) - timedelta(minutes=grace_period)).time()
        max_time = (datetime.combine(today, expected_check_in) + timedelta(minutes=grace_period)).time()
        
        self.stdout.write(f'⏰ Hora mínima permitida: {min_time}')
        self.stdout.write(f'⏰ Hora máxima permitida: {max_time}')
        
        # Probar diferentes horarios de entrada
        test_times = [
            ('MUY TEMPRANO (antes del rango)', 
             (datetime.combine(today, expected_check_in) - timedelta(minutes=grace_period + 30)).time()),
            ('TEMPRANO (dentro tolerancia)', 
             (datetime.combine(today, expected_check_in) - timedelta(minutes=grace_period - 5)).time()),
            ('A TIEMPO', expected_check_in),
            ('TARDE (dentro tolerancia)', 
             (datetime.combine(today, expected_check_in) + timedelta(minutes=grace_period - 5)).time()),
            ('TARDE (fuera tolerancia)', 
             (datetime.combine(today, expected_check_in) + timedelta(minutes=grace_period + 5)).time()),
        ]
        
        self.stdout.write('\n🔍 Probando diferentes horarios de entrada:')
        
        for test_name, test_time in test_times:
            self.stdout.write(f'\n📋 {test_name}: {test_time}')
            
            # Limpiar asistencia anterior si existe
            Attendance.objects.filter(employee=employee, date=today).delete()
            
            # Simular intento de marcar entrada
            try:
                # Crear asistencia de prueba
                attendance = Attendance.objects.create(
                    employee=employee,
                    date=today,
                    area=area,
                    check_in=test_time,
                    status='present'
                )
                
                # Determinar si debería haber sido permitido
                if test_time < min_time:
                    self.stdout.write(self.style.ERROR(f'   ❌ ERROR: Se permitió entrada muy temprana'))
                    self.stdout.write(f'      - Hora entrada: {test_time}')
                    self.stdout.write(f'      - Hora mínima: {min_time}')
                elif test_time > max_time:
                    self.stdout.write(self.style.ERROR(f'   ❌ ERROR: Se permitió entrada muy tarde'))
                    self.stdout.write(f'      - Hora entrada: {test_time}')
                    self.stdout.write(f'      - Hora máxima: {max_time}')
                else:
                    self.stdout.write(self.style.SUCCESS(f'   ✅ ENTRADA PERMITIDA: {test_time}'))
                    
            except Exception as e:
                # Si se lanzó una excepción, verificar si era la esperada
                if test_time < min_time and 'too_early_for_entry' in str(e):
                    self.stdout.write(self.style.SUCCESS(f'   ✅ VALIDACIÓN FUNCIONA (entrada temprana): {str(e)}'))
                elif test_time > max_time and 'too_late_for_entry' in str(e):
                    self.stdout.write(self.style.SUCCESS(f'   ✅ VALIDACIÓN FUNCIONA (entrada tarde): {str(e)}'))
                else:
                    self.stdout.write(self.style.ERROR(f'   ❌ ERROR INESPERADO: {str(e)}'))
        
        self.stdout.write('\n✅ Prueba completada')
