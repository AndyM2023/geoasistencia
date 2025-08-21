from datetime import datetime, time
from django.utils import timezone
from ..models import Area, AreaSchedule, Attendance


class ScheduleService:
    """Servicio para manejar horarios de áreas y cálculo de asistencias"""
    
    @staticmethod
    def get_expected_times(area, date):
        """Obtiene las horas esperadas de entrada y salida para un área en una fecha específica"""
        if not hasattr(area, 'schedule'):
            return None, None
        
        schedule = area.schedule
        return schedule.get_expected_times(date)
    
    @staticmethod
    def create_default_schedule(area):
        """Crea un horario por defecto para un área (8:00 AM - 5:00 PM, L-V)"""
        default_time_start = time(8, 0)  # 8:00 AM
        default_time_end = time(17, 0)   # 5:00 PM
        
        schedule, created = AreaSchedule.objects.get_or_create(
            area=area,
            defaults={
                'monday_start': default_time_start,
                'monday_end': default_time_end,
                'monday_active': True,
                'tuesday_start': default_time_start,
                'tuesday_end': default_time_end,
                'tuesday_active': True,
                'wednesday_start': default_time_start,
                'wednesday_end': default_time_end,
                'wednesday_active': True,
                'thursday_start': default_time_start,
                'thursday_end': default_time_end,
                'thursday_active': True,
                'friday_start': default_time_start,
                'friday_end': default_time_end,
                'friday_active': True,
                'saturday_start': None,
                'saturday_end': None,
                'saturday_active': False,
                'sunday_start': None,
                'sunday_end': None,
                'sunday_active': False,
                'grace_period_minutes': 15
            }
        )
        return schedule
    
    @staticmethod
    def update_attendance_with_schedule(attendance):
        """Actualiza un registro de asistencia con las horas esperadas según el horario del área"""
        if not attendance.expected_check_in and hasattr(attendance.area, 'schedule'):
            expected_check_in, expected_check_out = attendance.area.schedule.get_expected_times(attendance.date)
            if expected_check_in:
                attendance.expected_check_in = expected_check_in
                attendance.expected_check_out = expected_check_out
                attendance.save()
        return attendance
    
    @staticmethod
    def get_area_schedule_summary(area):
        """Obtiene un resumen del horario de un área"""
        if not hasattr(area, 'schedule'):
            return None
        
        schedule = area.schedule
        summary = {
            'area_name': area.name,
            'grace_period': schedule.grace_period_minutes,
            'weekdays': {}
        }
        
        # Lunes a Viernes
        weekdays = [
            ('monday', 'Lunes'),
            ('tuesday', 'Martes'),
            ('wednesday', 'Miércoles'),
            ('thursday', 'Jueves'),
            ('friday', 'Viernes'),
            ('saturday', 'Sábado'),
            ('sunday', 'Domingo')
        ]
        
        for day_key, day_name in weekdays:
            active = getattr(schedule, f'{day_key}_active', False)
            start_time = getattr(schedule, f'{day_key}_start', None)
            end_time = getattr(schedule, f'{day_key}_end', None)
            
            summary['weekdays'][day_name] = {
                'active': active,
                'start': start_time.strftime('%H:%M') if start_time else None,
                'end': end_time.strftime('%H:%M') if end_time else None
            }
        
        return summary
    
    @staticmethod
    def is_workday(area, date):
        """Verifica si una fecha es un día laboral para el área"""
        if not hasattr(area, 'schedule'):
            return True  # Si no hay horario configurado, considerar todos los días como laborales
        
        expected_check_in, expected_check_out = area.schedule.get_expected_times(date)
        return expected_check_in is not None and expected_check_out is not None
