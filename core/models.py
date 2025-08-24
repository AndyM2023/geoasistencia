from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid
from datetime import timedelta, time

class User(AbstractUser):
    """Usuario base del sistema (Admin o Empleado)"""
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('employee', 'Empleado'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='employee')

    cedula = models.CharField(max_length=20, unique=True, blank=True, null=True, verbose_name='ID Card Number')
    # position removido - se usa solo en Employee para evitar redundancia
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

# class Position(models.Model):
#     """Posición/Cargo del sistema - Tabla centralizada"""
#     name = models.CharField(max_length=100, unique=True, verbose_name='Nombre de la Posición')
#     description = models.TextField(blank=True, verbose_name='Descripción')
#     has_admin_access = models.BooleanField(
#         default=False, 
#         verbose_name='Acceso Administrativo',
#         help_text='¿Esta posición tiene acceso al panel administrativo?'
#     )
#     is_active = models.BooleanField(default=True, verbose_name='Activa')
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     
#     class Meta:
#         verbose_name = 'Posición'
#         verbose_name_plural = 'Posiciones'
#     ordering = ['name']
#     
#     def __str__(self):
#         admin_status = " (Admin)" if self.has_admin_access else ""
#         return f"{self.name}{admin_status}"
#     
#     @property
#     def is_admin_position(self):
#         """Verificar si es una posición administrativa"""
#         return self.has_admin_access
#     
#     def get_employees_count(self):
#         """Número de empleados con esta posición"""
#         return self.employees.count()

class Area(models.Model):
    """Área de trabajo con coordenadas geográficas"""
    name = models.CharField(max_length=100, verbose_name='Nombre del Área')
    description = models.TextField(blank=True, verbose_name='Descripción')
    latitude = models.DecimalField(
        max_digits=20, 
        decimal_places=18, 
        verbose_name='Latitud',
        validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    longitude = models.DecimalField(
        max_digits=20, 
        decimal_places=18, 
        verbose_name='Longitud',
        validators=[MinValueValidator(-180), MaxValueValidator(180)]
    )
    radius = models.PositiveIntegerField(
        verbose_name='Radio (metros)',
        validators=[MinValueValidator(10), MaxValueValidator(10000)],
        help_text='Radio en metros (10m - 10km)'
    )
    status = models.CharField(
        max_length=10,
        choices=[('active', 'Activa'), ('inactive', 'Inactiva')],
        default='active',
        verbose_name='Estado'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Área'
        verbose_name_plural = 'Áreas'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def employee_count(self):
        """Número de empleados asignados a esta área"""
        return self.employees.count()
    
    def deactivate(self):
        """Desactivar área (soft delete)"""
        self.status = 'inactive'
        self.save()
    
    def activate(self):
        """Reactivar área"""
        self.status = 'active'
        self.save()
    
    def is_active(self):
        """Verificar si el área está activa"""
        return self.status == 'active'
    
    def clean(self):
        """Validación personalizada del modelo"""
        from django.core.exceptions import ValidationError
        
        # Validar coordenadas
        if self.latitude is not None:
            if not (-90 <= float(self.latitude) <= 90):
                raise ValidationError({
                    'latitude': 'La latitud debe estar entre -90 y 90 grados'
                })
        
        if self.longitude is not None:
            if not (-180 <= float(self.longitude) <= 180):
                raise ValidationError({
                    'longitude': 'La longitud debe estar entre -180 y 180 grados'
                })
        
        # Validar radio
        if self.radius is not None:
            if not (10 <= int(self.radius) <= 10000):
                raise ValidationError({
                    'radius': 'El radio debe estar entre 10 y 10000 metros'
                })
    
    def save(self, *args, **kwargs):
        """Guardar con validación personalizada"""
        self.clean()
        super().save(*args, **kwargs)

class AreaSchedule(models.Model):
    """Horario de trabajo para un área específica"""
    SCHEDULE_TYPE_CHOICES = [
        ('default', 'Horario por Defecto'),
        ('custom', 'Horario Personalizado'),
        ('none', 'Sin Horario'),
    ]
    
    area = models.OneToOneField(Area, on_delete=models.CASCADE, related_name='schedule')
    schedule_type = models.CharField(
        max_length=10,
        choices=SCHEDULE_TYPE_CHOICES,
        default='default',
        verbose_name='Tipo de Horario'
    )
    
    # Horarios de lunes a viernes
    monday_start = models.TimeField(verbose_name='Lunes - Hora de Entrada')
    monday_end = models.TimeField(verbose_name='Lunes - Hora de Salida')
    monday_active = models.BooleanField(default=True, verbose_name='Lunes Activo')
    
    tuesday_start = models.TimeField(verbose_name='Martes - Hora de Entrada')
    tuesday_end = models.TimeField(verbose_name='Martes - Hora de Salida')
    tuesday_active = models.BooleanField(default=True, verbose_name='Martes Activo')
    
    wednesday_start = models.TimeField(verbose_name='Miércoles - Hora de Entrada')
    wednesday_end = models.TimeField(verbose_name='Miércoles - Hora de Salida')
    wednesday_active = models.BooleanField(default=True, verbose_name='Miércoles Activo')
    
    thursday_start = models.TimeField(verbose_name='Jueves - Hora de Entrada')
    thursday_end = models.TimeField(verbose_name='Jueves - Hora de Salida')
    thursday_active = models.BooleanField(default=True, verbose_name='Jueves Activo')
    
    friday_start = models.TimeField(verbose_name='Viernes - Hora de Entrada')
    friday_end = models.TimeField(verbose_name='Viernes - Hora de Salida')
    friday_active = models.BooleanField(default=True, verbose_name='Viernes Activo')
    
    # Horarios de fin de semana (opcional)
    saturday_start = models.TimeField(null=True, blank=True, verbose_name='Sábado - Hora de Entrada')
    saturday_end = models.TimeField(null=True, blank=True, verbose_name='Sábado - Hora de Salida')
    saturday_active = models.BooleanField(default=False, verbose_name='Sábado Activo')
    
    sunday_start = models.TimeField(null=True, blank=True, verbose_name='Domingo - Hora de Entrada')
    sunday_end = models.TimeField(null=True, blank=True, verbose_name='Domingo - Hora de Salida')
    sunday_active = models.BooleanField(default=False, verbose_name='Domingo Activo')
    
    # Configuraciones adicionales
    grace_period_minutes = models.PositiveIntegerField(
        default=15, 
        verbose_name='Tolerancia (minutos)',
        help_text='Minutos de tolerancia antes de considerar llegada tarde'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Horario del Área'
        verbose_name_plural = 'Horarios de las Áreas'
    
    def __str__(self):
        return f"Horario - {self.area.name}"
class Employee(models.Model):
    """Empleado del sistema"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    employee_id = models.PositiveIntegerField(unique=True, blank=True, null=True, verbose_name='ID de Empleado')
    # Removido campo cedula - la cédula está en el modelo User
    POSITION_CHOICES = [
        ('desarrollador', 'Desarrollador'),
        ('disenador', 'Diseñador'),
        ('secretario', 'Secretario/a'),
        ('gerente', 'Gerente'),
        ('analista', 'Analista'),
        ('ingeniero', 'Ingeniero'),
        ('contador', 'Contador'),
        ('recursos_humanos', 'Recursos Humanos'),
        ('marketing', 'Marketing'),
        ('ventas', 'Ventas'),
        ('soporte', 'Soporte Técnico'),
        ('administrativo', 'Administrativo'),
        ('operativo', 'Operativo'),
        # Nuevos cargos específicos del formulario
        ('administrador_personal', 'Administrador de Personal'),
        ('asistente_rrhh', 'Asistente de RR. HH.'),
        ('tecnico_rrhh', 'Técnico de RR. HH.'),
        ('otro', 'Otro'),
    ]
    
    position = models.CharField(
        max_length=50, 
        choices=POSITION_CHOICES,
        default='otro',
        verbose_name='Cargo'
    )
    
    has_admin_access = models.BooleanField(
        default=False,
        verbose_name='Acceso Administrativo',
        help_text='¿Este empleado tiene acceso al panel administrativo?'
    )
    
    area = models.ForeignKey(
        Area, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='employees',
        verbose_name='Área de Trabajo'
    )
    hire_date = models.DateField(default=timezone.now, verbose_name='Fecha de Contratación')
    photo = models.ImageField(
        upload_to='employee_photos/', 
        null=True, 
        blank=True, 
        verbose_name='Foto del Empleado',
        help_text='Foto principal del empleado para identificación'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'
        ordering = ['user__first_name', 'user__last_name']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.employee_id}"
    
    @property
    def full_name(self):
        return self.user.get_full_name()
    
    @property
    def email(self):
        return self.user.email
    
    @property
    def is_admin_position(self):
        """Verificar si el cargo es administrativo por defecto"""
        return self.position in [
            'gerente', 
            'administrativo', 
            'recursos_humanos', 
            'contador', 
            'analista',
            'administrador_personal',  # Nuevo cargo administrativo
            'asistente_rrhh',         # Nuevo cargo administrativo
            'tecnico_rrhh'            # Nuevo cargo administrativo
        ]
    
    def get_position_display(self):
        """Obtener el nombre legible del cargo"""
        return dict(self.POSITION_CHOICES).get(self.position, self.position)
    
    def save(self, *args, **kwargs):
        """Generar employee_id automáticamente si no existe y configurar acceso administrativo por defecto"""
        if not self.employee_id:
            # Obtener el último número de empleado
            last_employee = Employee.objects.filter(
                employee_id__isnull=False
            ).order_by('employee_id').last()
            
            if last_employee and last_employee.employee_id:
                new_number = last_employee.employee_id + 1
            else:
                new_number = 1
            
            # Generar el nuevo employee_id numérico
            self.employee_id = new_number
        
        # Configurar acceso administrativo por defecto según el cargo
        if not self.has_admin_access and self.is_admin_position:
            self.has_admin_access = True
        
        super().save(*args, **kwargs)

class FaceProfile(models.Model):
    """Perfil facial del empleado"""
    employee = models.OneToOneField(
        Employee, 
        on_delete=models.CASCADE, 
        related_name='face_profile'
    )
    face_embeddings_path = models.CharField(
        max_length=255, 
        blank=True, 
        verbose_name='Ruta de Embeddings'
    )
    photos_count = models.IntegerField(default=0, verbose_name='Número de Fotos')
    is_trained = models.BooleanField(default=False, verbose_name='Entrenado')
    confidence_threshold = models.FloatField(default=0.90, verbose_name='Umbral de Confianza')
    last_training = models.DateTimeField(null=True, blank=True, verbose_name='Último Entrenamiento')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Perfil Facial'
        verbose_name_plural = 'Perfiles Faciales'
    
    def __str__(self):
        return f"Perfil Facial - {self.employee.full_name}"

class Attendance(models.Model):
    """Registro de asistencia del empleado"""
    STATUS_CHOICES = [
        ('present', 'Presente'),
        ('late', 'Llegada Tarde'),
        ('absent', 'Ausente'),
        ('half_day', 'Medio Día'),
    ]
    
    employee = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE, 
        related_name='attendances',
        verbose_name='Empleado'
    )
    date = models.DateField(verbose_name='Fecha')
    check_in = models.TimeField(null=True, blank=True, verbose_name='Hora de Entrada')
    check_out = models.TimeField(null=True, blank=True, verbose_name='Hora de Salida')
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='present',
        verbose_name='Estado'
    )
    area = models.ForeignKey(
        Area, 
        on_delete=models.CASCADE, 
        related_name='attendances',
        verbose_name='Área de Trabajo'
    )
    latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        verbose_name='Latitud de Entrada'
    )
    longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        verbose_name='Longitud de Entrada'
    )
    face_verified = models.BooleanField(default=False, verbose_name='Rostro Verificado')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Asistencia'
        verbose_name_plural = 'Asistencias'
        ordering = ['-date', '-check_in']
        unique_together = ['employee', 'date']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.date} ({self.get_status_display()})"
    
    @property
    def hours_worked(self):
        """Calcula las horas trabajadas"""
        if self.check_in and self.check_out:
            from datetime import datetime
            start = datetime.combine(self.date, self.check_in)
            end = datetime.combine(self.date, self.check_out)
            duration = end - start
            return round(duration.total_seconds() / 3600, 2)
        return None
    
    def update_status_based_on_schedule(self):
        """Actualiza el status basado en el horario del área y la hora de entrada"""
        if not self.check_in:
            return
        
        # Verificar si es un día laboral
        from core.services.schedule_service import ScheduleService
        if not ScheduleService.is_work_day(self.area, self.date):
            self.status = 'absent'
            return
        
        # Obtener horarios esperados del área para esta fecha
        expected_check_in, expected_check_out = ScheduleService.get_expected_times(self.area, self.date)
        
        if not expected_check_in:
            # Sin horario definido, mantener status actual
            return
        
        # Obtener período de gracia del área
        grace_period = ScheduleService.get_grace_period(self.area)
        
        # Calcular hora límite con tolerancia
        from datetime import datetime, timedelta
        limit_time = datetime.combine(self.date, expected_check_in)
        limit_time = limit_time + timedelta(minutes=grace_period)
        limit_time = limit_time.time()
        
        # Crear datetime para comparar
        check_in_datetime = datetime.combine(self.date, self.check_in)
        limit_datetime = datetime.combine(self.date, limit_time)
        
        # Actualizar status basado en la hora de entrada
        if check_in_datetime > limit_datetime:
            self.status = 'late'
        else:
            self.status = 'present'
        
        print(f"🔄 Status actualizado para {self.employee.full_name}:")
        print(f"   - Hora entrada: {self.check_in}")
        print(f"   - Hora esperada: {expected_check_in}")
        print(f"   - Hora límite con tolerancia: {limit_time}")
        print(f"   - Status final: {self.status}")
    
    def update_status_dynamically(self):
        """Actualizar el estado de asistencia dinámicamente basado en la hora actual"""
        if not self.area or not self.date:
            return
        
        from core.services.schedule_service import ScheduleService
        from django.utils import timezone
        from datetime import datetime, timedelta
        
        # Obtener horarios esperados
        expected_check_in, expected_check_out = ScheduleService.get_expected_times(self.area, self.date)
        if not expected_check_in or not expected_check_out:
            return
        
        # Obtener período de gracia
        grace_period = ScheduleService.get_grace_period(self.area)
        
        # Hora actual
        current_time = timezone.now().time()
        current_date = timezone.now().date()
        
        # Si es un día diferente, no actualizar
        if current_date != self.date:
            return
        
        # Si no tiene entrada, verificar si ya es muy tarde
        if not self.check_in:
            # Calcular hora límite con tolerancia
            limit_datetime = datetime.combine(self.date, expected_check_in)
            limit_datetime = limit_datetime + timedelta(minutes=grace_period)
            limit_time = limit_datetime.time()
            
            # Si ya pasó la hora límite y no marcó entrada, es ausente
            if current_time > limit_time:
                self.status = 'absent'
                self.save()
            return
        
        # Si tiene entrada pero no salida
        if self.check_in and not self.check_out:
            # Si ya pasó la hora de salida esperada, marcar como "presente" (completado)
            if current_time > expected_check_out:
                self.status = 'present'
                self.save()
            return
        
        # Si tiene entrada y salida, el estado ya está definido
        if self.check_in and self.check_out:
            return
    
    def save(self, *args, **kwargs):
        """Guardar y actualizar status automáticamente"""
        # Actualizar status antes de guardar
        if self.check_in and not self.check_out:
            self.update_status_based_on_schedule()
        
        super().save(*args, **kwargs)
    
    @property
    def is_late(self):
        """Verifica si llegó tarde según el horario del área"""
        if not self.check_in:
            return False
            
        # Usar ScheduleService para obtener horarios esperados
        from core.services.schedule_service import ScheduleService
        expected_check_in, _ = ScheduleService.get_expected_times(self.area, self.date)
        
        if not expected_check_in:
            # Sin horario definido, usar fallback (8:30 AM)
            from datetime import time
            return self.check_in > time(8, 30)
        
        # Obtener período de gracia del área
        grace_period = ScheduleService.get_grace_period(self.area)
        
        # Calcular hora límite con tolerancia
        from datetime import datetime, timedelta
        limit_time = datetime.combine(self.date, expected_check_in)
        limit_time = limit_time + timedelta(minutes=grace_period)
        
        check_in_datetime = datetime.combine(self.date, self.check_in)
        return check_in_datetime > limit_time

class PasswordResetToken(models.Model):
    """Token para recuperación de contraseña del administrador"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Token de Recuperación'
        verbose_name_plural = 'Tokens de Recuperación'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Token para {self.user.username} - Expira: {self.expires_at}"
    
    def save(self, *args, **kwargs):
        if not self.token:
            self.token = str(uuid.uuid4())
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=1)
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        """Verificar si el token ha expirado"""
        return timezone.now() > self.expires_at
    
    @property
    def is_valid(self):
        """Verificar si el token es válido y no ha sido usado"""
        return not self.is_expired and not self.is_used
    
    def mark_as_used(self):
        """Marcar el token como usado"""
        self.is_used = True
        self.save()
