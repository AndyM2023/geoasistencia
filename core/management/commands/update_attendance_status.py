from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Attendance
from datetime import date


class Command(BaseCommand):
    help = 'Actualizar estados de asistencia dinámicamente'

    def handle(self, *args, **options):
        today = date.today()
        self.stdout.write(f"🔄 Actualizando estados de asistencia para {today}...")
        
        # Obtener todas las asistencias de hoy
        attendances = Attendance.objects.filter(date=today)
        updated_count = 0
        
        for attendance in attendances:
            try:
                # Guardar estado anterior para comparar
                old_status = attendance.status
                
                # Actualizar estado dinámicamente
                attendance.update_status_dynamically()
                
                # Si el estado cambió, contar como actualizado
                if attendance.status != old_status:
                    updated_count += 1
                    self.stdout.write(
                        f"   ✅ {attendance.employee.full_name}: {old_status} → {attendance.status}"
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"   ❌ Error actualizando {attendance.employee.full_name}: {e}"
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Actualización completada. {updated_count} estados actualizados."
            )
        )
