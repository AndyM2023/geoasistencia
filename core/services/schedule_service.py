from datetime import datetime, timedelta
from django.utils import timezone
from core.models import Area, AreaSchedule


class ScheduleService:
    """Servicio para manejar horarios de áreas y empleados"""
    
    @staticmethod
    def get_expected_times(area, date):
        """
        Obtiene las horas esperadas de entrada y salida para un área en una fecha específica
        
        Args:
            area: Instancia del modelo Area
            date: Fecha para la cual obtener el horario
            
        Returns:
            tuple: (hora_entrada_esperada, hora_salida_esperada) o (None, None) si no hay horario
        """
        if not hasattr(area, 'schedule'):
            return None, None
        
        schedule = area.schedule
        weekday = date.weekday()  # 0=Lunes, 6=Domingo
        
        if weekday == 0 and schedule.monday_active:
            return schedule.monday_start, schedule.monday_end
        elif weekday == 1 and schedule.tuesday_active:
            return schedule.tuesday_start, schedule.tuesday_end
        elif weekday == 2 and schedule.wednesday_active:
            return schedule.wednesday_start, schedule.wednesday_end
        elif weekday == 3 and schedule.thursday_active:
            return schedule.thursday_start, schedule.thursday_end
        elif weekday == 4 and schedule.friday_active:
            return schedule.friday_start, schedule.friday_end
        elif weekday == 5 and schedule.saturday_active:
            return schedule.saturday_start, schedule.saturday_end
        elif weekday == 6 and schedule.sunday_active:
            return schedule.sunday_start, schedule.sunday_end
        
        return None, None
    
    @staticmethod
    def create_default_schedule(area):
        """
        Crea un horario por defecto para un área (8:00 AM - 5:00 PM, L-V)
        
        Args:
            area: Instancia del modelo Area
            
        Returns:
            AreaSchedule: Instancia del horario creado
        """
        from datetime import time
        
        schedule, created = AreaSchedule.objects.get_or_create(
            area=area,
            defaults={
                'monday_start': time(8, 0),
                'monday_end': time(17, 0),
                'monday_active': True,
                'tuesday_start': time(8, 0),
                'tuesday_end': time(17, 0),
                'tuesday_active': True,
                'wednesday_start': time(8, 0),
                'wednesday_end': time(17, 0),
                'wednesday_active': True,
                'thursday_start': time(8, 0),
                'thursday_end': time(17, 0),
                'thursday_active': True,
                'friday_start': time(8, 0),
                'friday_end': time(17, 0),
                'friday_active': True,
                'saturday_active': False,
                'sunday_active': False,
                'grace_period_minutes': 15
            }
        )
        return schedule
    
    @staticmethod
    def is_work_day(area, date):
        """
        Verifica si una fecha es un día laboral para un área
        
        Args:
            area: Instancia del modelo Area
            date: Fecha a verificar
            
        Returns:
            bool: True si es día laboral, False en caso contrario
        """
        if not hasattr(area, 'schedule'):
            return False
        
        schedule = area.schedule
        weekday = date.weekday()
        
        if weekday == 0:
            return schedule.monday_active
        elif weekday == 1:
            return schedule.tuesday_active
        elif weekday == 2:
            return schedule.wednesday_active
        elif weekday == 3:
            return schedule.thursday_active
        elif weekday == 4:
            return schedule.friday_active
        elif weekday == 5:
            return schedule.saturday_active
        elif weekday == 6:
            return schedule.sunday_active
        
        return False
    
    @staticmethod
    def get_grace_period(area):
        """
        Obtiene el período de gracia para un área
        
        Args:
            area: Instancia del modelo Area
            
        Returns:
            int: Minutos de tolerancia
        """
        if hasattr(area, 'schedule'):
            return area.schedule.grace_period_minutes
        return 15  # Valor por defecto
