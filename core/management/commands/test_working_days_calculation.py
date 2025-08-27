from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date
from calendar import monthrange


class Command(BaseCommand):
    help = 'Prueba el cálculo de días laborables del mes'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🧪 Probando cálculo de días laborables...'))
        
        # Obtener mes y año actual
        current_month = timezone.localtime().month
        current_year = timezone.localtime().year
        
        self.stdout.write(f'📅 Mes: {current_month} ({current_year})')
        
        # Obtener total de días en el mes
        _, days_in_month = monthrange(current_year, current_month)
        self.stdout.write(f'📊 Total días en el mes: {days_in_month}')
        
        # Calcular días laborables reales (excluyendo fines de semana)
        working_days = 0
        weekend_days = 0
        
        for day in range(1, days_in_month + 1):
            date_obj = date(current_year, current_month, day)
            weekday = date_obj.weekday()  # 0=Lunes, 6=Domingo
            
            if weekday < 5:  # Lunes a Viernes
                working_days += 1
            else:  # Sábado o Domingo
                weekend_days += 1
        
        self.stdout.write(f'✅ Días laborables (L-V): {working_days}')
        self.stdout.write(f'🌅 Días de fin de semana: {weekend_days}')
        self.stdout.write(f'📈 Total días: {working_days + weekend_days}')
        
        # Mostrar algunos ejemplos de fechas
        self.stdout.write('\n📋 Ejemplos de fechas:')
        for day in [1, 15, days_in_month]:
            if day <= days_in_month:
                date_obj = date(current_year, current_month, day)
                weekday_name = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'][date_obj.weekday()]
                is_working = date_obj.weekday() < 5
                status = "✅ LABORABLE" if is_working else "🌅 FIN DE SEMANA"
                self.stdout.write(f'   {date_obj.strftime("%d/%m/%Y")} - {weekday_name} - {status}')
        
        # Comparar con el método anterior (asumir 22 días)
        old_method = min(22, days_in_month)
        self.stdout.write(f'\n🔍 Comparación:')
        self.stdout.write(f'   - Método anterior (asumir 22): {old_method} días')
        self.stdout.write(f'   - Método nuevo (real): {working_days} días')
        self.stdout.write(f'   - Diferencia: {working_days - old_method} días')
        
        if working_days != old_method:
            self.stdout.write(self.style.WARNING(f'⚠️ Los métodos dan resultados diferentes'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✅ Los métodos coinciden'))
        
        self.stdout.write('\n✅ Prueba completada')
