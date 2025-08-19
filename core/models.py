from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid
from datetime import timedelta

class User(AbstractUser):
    """Usuario base del sistema (Admin o Empleado)"""
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('employee', 'Empleado'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='employee')

    cedula = models.CharField(max_length=20, unique=True, blank=True, null=True, verbose_name='ID Card Number')
    position = models.CharField(max_length=100, blank=True, null=True, verbose_name='Position')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

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
        ('otro', 'Otro'),
    ]
    
    position = models.CharField(
        max_length=50, 
        choices=POSITION_CHOICES,
        default='otro',
        verbose_name='Cargo'
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
    
    def get_position_display(self):
        """Obtener el nombre legible del cargo"""
        return dict(self.POSITION_CHOICES).get(self.position, self.position)
    
    def save(self, *args, **kwargs):
        """Generar employee_id automáticamente si no existe"""
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
            from datetime import datetime, time
            start = datetime.combine(self.date, self.check_in)
            end = datetime.combine(self.date, self.check_out)
            duration = end - start
            return round(duration.total_seconds() / 3600, 2)
        return None
    
    @property
    def is_late(self):
        """Verifica si llegó tarde (después de las 8:30 AM)"""
        if self.check_in:
            from datetime import time
            return self.check_in > time(8, 30)
        return False

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
