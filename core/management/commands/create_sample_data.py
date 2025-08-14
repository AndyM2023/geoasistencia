from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta
from core.models import User, Employee, Area, Attendance

User = get_user_model()

class Command(BaseCommand):
    help = 'Crear datos de prueba para el sistema'

    def handle(self, *args, **options):
        self.stdout.write('Creando datos de prueba...')
        
        # Crear superusuario admin
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@geoasistencia.com',
                password='admin123',
                first_name='Administrador',
                last_name='Sistema',
                role='admin'
            )
            self.stdout.write(f'✓ Superusuario creado: {admin_user.username}')
        else:
            self.stdout.write('✓ Superusuario ya existe')
        
        # Crear áreas de trabajo
        areas_data = [
            {
                'name': 'Oficina Central',
                'description': 'Edificio principal de la empresa',
                'latitude': 19.4326,
                'longitude': -99.1332,
                'radius': 150,
                'status': 'active'
            },
            {
                'name': 'Almacén Norte',
                'description': 'Almacén de productos del norte',
                'latitude': 19.4426,
                'longitude': -99.1432,
                'radius': 200,
                'status': 'active'
            },
            {
                'name': 'Taller de Producción',
                'description': 'Área de producción y manufactura',
                'latitude': 19.4226,
                'longitude': -99.1232,
                'radius': 180,
                'status': 'active'
            }
        ]
        
        created_areas = []
        for area_data in areas_data:
            area, created = Area.objects.get_or_create(
                name=area_data['name'],
                defaults=area_data
            )
            if created:
                self.stdout.write(f'✓ Área creada: {area.name}')
            created_areas.append(area)
        
        # Crear usuarios empleados
        employees_data = [
            {
                'username': 'juan.perez',
                'email': 'juan.perez@empresa.com',
                'first_name': 'Juan',
                'last_name': 'Pérez',
                'role': 'employee',
                'employee_id': 'EMP001',
                'position': 'Desarrollador',
                'area': created_areas[0]  # Oficina Central
            },
            {
                'username': 'maria.garcia',
                'email': 'maria.garcia@empresa.com',
                'first_name': 'María',
                'last_name': 'García',
                'role': 'employee',
                'employee_id': 'EMP002',
                'position': 'Diseñadora',
                'area': created_areas[0]  # Oficina Central
            },
            {
                'username': 'carlos.lopez',
                'email': 'carlos.lopez@empresa.com',
                'first_name': 'Carlos',
                'last_name': 'López',
                'role': 'employee',
                'employee_id': 'EMP003',
                'position': 'Operario',
                'area': created_areas[2]  # Taller de Producción
            }
        ]
        
        for emp_data in employees_data:
            user_data = {k: v for k, v in emp_data.items() if k not in ['employee_id', 'position', 'area']}
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults=user_data
            )
            
            if created:
                user.set_password('empleado123')
                user.save()
                self.stdout.write(f'✓ Usuario creado: {user.username}')
            
            # Crear perfil de empleado
            employee, emp_created = Employee.objects.get_or_create(
                user=user,
                defaults={
                    'employee_id': emp_data['employee_id'],
                    'position': emp_data['position'],
                    'area': emp_data['area'],
                    'hire_date': date.today() - timedelta(days=30)
                }
            )
            
            if emp_created:
                self.stdout.write(f'✓ Empleado creado: {employee.employee_id}')
        
        # Crear algunas asistencias de ejemplo
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        for employee in Employee.objects.all():
            # Asistencia de ayer
            attendance, created = Attendance.objects.get_or_create(
                employee=employee,
                date=yesterday,
                defaults={
                    'area': employee.area,
                    'check_in': '08:30:00',
                    'check_out': '17:30:00',
                    'status': 'present',
                    'latitude': employee.area.latitude + Decimal('0.0001'),
                    'longitude': employee.area.longitude + Decimal('0.0001'),
                    'face_verified': True
                }
            )
            
            if created:
                self.stdout.write(f'✓ Asistencia creada para {employee.full_name} - {yesterday}')
        
        self.stdout.write(self.style.SUCCESS('¡Datos de prueba creados exitosamente!'))
        self.stdout.write('\nCredenciales de acceso:')
        self.stdout.write('Admin: admin / admin123')
        self.stdout.write('Empleados: empleado123 (para todos los usuarios)')
