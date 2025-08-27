from django.test import TestCase
from django.utils import timezone
from datetime import datetime, timedelta, time
from core.models import Employee, Area, Attendance, AreaSchedule
from core.services.schedule_service import ScheduleService


class AttendanceValidationTests(TestCase):
    """Tests para validar la lógica de entrada temprana y tardía"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        # Crear área de prueba
        self.area = Area.objects.create(
            name="Área de Prueba",
            latitude=0.0,
            longitude=0.0,
            radius=100
        )
        
        # Crear usuario de prueba
        from core.models import User
        self.user = User.objects.create_user(
            username="juanperez",
            email="juan@test.com",
            first_name="Juan",
            last_name="Pérez",
            password="testpass123"
        )
        
        # Crear empleado de prueba
        self.employee = Employee.objects.create(
            user=self.user,
            employee_id=12345
        )
        
        # Crear horario de prueba: 8:00 AM - 5:00 PM con 15 min de tolerancia
        self.schedule = AreaSchedule.objects.create(
            area=self.area,
            monday_active=True,
            monday_start=time(8, 0),  # 8:00 AM
            monday_end=time(17, 0),   # 5:00 PM
            tuesday_active=True,
            tuesday_start=time(8, 0),  # 8:00 AM
            tuesday_end=time(17, 0),  # 5:00 PM
            wednesday_active=True,
            wednesday_start=time(8, 0),  # 8:00 AM
            wednesday_end=time(17, 0),  # 5:00 PM
            thursday_active=True,
            thursday_start=time(8, 0),  # 8:00 AM
            thursday_end=time(17, 0),  # 5:00 PM
            friday_active=True,
            friday_start=time(8, 0),  # 8:00 AM
            friday_end=time(17, 0),  # 5:00 PM
            saturday_active=False,
            sunday_active=False,
            grace_period_minutes=15
        )
        
        self.today = timezone.now().date()
    
    def test_early_entry_validation(self):
        """Test para validar entrada muy temprana"""
        # Hora de entrada esperada: 8:00 AM
        # Tolerancia: 15 minutos
        # Hora mínima permitida: 7:45 AM
        
        # Intentar entrada muy temprana (7:15 AM)
        early_time = time(7, 15)
        
        # Simular la validación que se hace en la vista
        expected_check_in, expected_check_out = ScheduleService.get_expected_times(self.area, self.today)
        grace_period = ScheduleService.get_grace_period(self.area)
        
        # Calcular hora mínima permitida
        min_time = (datetime.combine(self.today, expected_check_in) - timedelta(minutes=grace_period)).time()
        
        # Verificar que la validación funcione
        self.assertLess(early_time, min_time, 
                       f"7:15 AM debería ser menor que {min_time}")
        
        # Verificar que se calcule correctamente el rango
        self.assertEqual(min_time, time(7, 45), 
                        f"Hora mínima debería ser 7:45 AM, pero es {min_time}")
        
        # Verificar que 7:45 AM esté permitido
        allowed_time = time(7, 45)
        self.assertGreaterEqual(allowed_time, min_time,
                              f"7:45 AM debería estar permitido")
    
    def test_late_entry_validation(self):
        """Test para validar entrada tardía"""
        # Hora de entrada esperada: 8:00 AM
        # Tolerancia: 15 minutos
        # Hora máxima permitida: 8:15 AM
        
        expected_check_in, expected_check_out = ScheduleService.get_expected_times(self.area, self.today)
        grace_period = ScheduleService.get_grace_period(self.area)
        
        # Calcular hora límite con tolerancia
        limit_time = (datetime.combine(self.today, expected_check_in) + timedelta(minutes=grace_period)).time()
        
        # Verificar que se calcule correctamente
        self.assertEqual(limit_time, time(8, 15), 
                        f"Hora límite debería ser 8:15 AM, pero es {limit_time}")
        
        # Verificar que 8:10 AM esté permitido (dentro de tolerancia)
        allowed_time = time(8, 10)
        self.assertLessEqual(allowed_time, limit_time,
                           f"8:10 AM debería estar permitido")
        
        # Verificar que 8:20 AM NO esté permitido (fuera de tolerancia)
        late_time = time(8, 20)
        self.assertGreater(late_time, limit_time,
                          f"8:20 AM NO debería estar permitido")
    
    def test_valid_entry_times(self):
        """Test para verificar que los horarios válidos estén permitidos"""
        expected_check_in, expected_check_out = ScheduleService.get_expected_times(self.area, self.today)
        grace_period = ScheduleService.get_grace_period(self.area)
        
        # Calcular rangos válidos
        min_time = (datetime.combine(self.today, expected_check_in) - timedelta(minutes=grace_period)).time()
        max_time = (datetime.combine(self.today, expected_check_in) + timedelta(minutes=grace_period)).time()
        
        # Horarios que deberían estar permitidos
        valid_times = [
            time(7, 45),  # Límite mínimo
            time(7, 50),  # Dentro del rango
            time(8, 0),   # Hora exacta
            time(8, 10),  # Dentro del rango
            time(8, 15),  # Límite máximo
        ]
        
        for valid_time in valid_times:
            with self.subTest(valid_time=valid_time):
                self.assertGreaterEqual(valid_time, min_time,
                                      f"{valid_time} debería ser >= {min_time}")
                self.assertLessEqual(valid_time, max_time,
                                   f"{valid_time} debería ser <= {max_time}")
    
    def test_invalid_entry_times(self):
        """Test para verificar que los horarios inválidos NO estén permitidos"""
        expected_check_in, expected_check_out = ScheduleService.get_expected_times(self.area, self.today)
        grace_period = ScheduleService.get_grace_period(self.area)
        
        # Calcular rangos válidos
        min_time = (datetime.combine(self.today, expected_check_in) - timedelta(minutes=grace_period)).time()
        max_time = (datetime.combine(self.today, expected_check_in) + timedelta(minutes=grace_period)).time()
        
        # Horarios que NO deberían estar permitidos
        invalid_times = [
            time(7, 30),  # Muy temprano
            time(7, 40),  # Temprano
            time(8, 20),  # Tarde
            time(8, 30),  # Muy tarde
        ]
        
        for invalid_time in invalid_times:
            with self.subTest(invalid_time=invalid_time):
                is_too_early = invalid_time < min_time
                is_too_late = invalid_time > max_time
                
                self.assertTrue(is_too_early or is_too_late,
                              f"{invalid_time} debería estar fuera del rango válido ({min_time} - {max_time})")
