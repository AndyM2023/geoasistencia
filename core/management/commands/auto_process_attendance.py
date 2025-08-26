from django.core.management.base import BaseCommand
from django.utils import timezone
from core.signals import auto_process_all_incomplete_attendances
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Procesar automáticamente asistencias incompletas (se ejecuta automáticamente)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--auto',
            action='store_true',
            help='Ejecutar en modo automático (por defecto)'
        )
        parser.add_argument(
            '--date',
            type=str,
            help='Fecha específica para procesar (YYYY-MM-DD)'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Número de días hacia atrás para procesar (por defecto: 7)'
        )

    def handle(self, *args, **options):
        if options['auto'] or not options['date']:
            # Modo automático: procesar los últimos días
            self.stdout.write("🤖 MODO AUTOMÁTICO: Procesando asistencias incompletas...")
            
            try:
                auto_process_all_incomplete_attendances()
                self.stdout.write(
                    self.style.SUCCESS(
                        "✅ Procesamiento automático completado exitosamente"
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"❌ Error durante el procesamiento automático: {e}"
                    )
                )
                return
        
        if options['date']:
            # Fecha específica
            try:
                target_date = date.fromisoformat(options['date'])
                self.stdout.write(f"📅 Procesando fecha específica: {target_date}")
                
                from core.signals import process_incomplete_attendance_for_date
                process_incomplete_attendance_for_date(target_date)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Procesamiento completado para {target_date}"
                    )
                )
                
            except ValueError:
                self.stdout.write(
                    self.style.ERROR(
                        "❌ Formato de fecha inválido. Use YYYY-MM-DD"
                    )
                )
                return
        
        # Mostrar estadísticas del día actual
        today = timezone.now().date()
        self.stdout.write(f"\n📊 ESTADÍSTICAS DEL DÍA {today}:")
        
        from core.models import Attendance
        total_attendances = Attendance.objects.filter(date=today).count()
        present_attendances = Attendance.objects.filter(date=today, status='present').count()
        late_attendances = Attendance.objects.filter(date=today, status='late').count()
        absent_attendances = Attendance.objects.filter(date=today, status='absent').count()
        
        self.stdout.write(f"   📈 Total de asistencias: {total_attendances}")
        self.stdout.write(f"   ✅ Presentes: {present_attendances}")
        self.stdout.write(f"   ⚠️ Tardanzas: {late_attendances}")
        self.stdout.write(f"   ❌ Ausentes: {absent_attendances}")
        
        # Mostrar asistencias incompletas restantes
        incomplete_attendances = Attendance.objects.filter(
            date=today,
            check_in__isnull=False,
            check_out__isnull=True
        ).count()
        
        if incomplete_attendances > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"   ⚠️ Asistencias incompletas restantes: {incomplete_attendances}"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "   ✅ Todas las asistencias están completas"
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                "\n🎯 Comando de procesamiento automático ejecutado exitosamente"
            )
        )
