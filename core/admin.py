from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Employee, Area, AreaSchedule, Attendance

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Admin para el modelo User personalizado"""
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permisos', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )

@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    """Admin para el modelo Area"""
    list_display = ('name', 'description', 'latitude', 'longitude', 'radius', 'status', 'employee_count', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)
    
    fieldsets = (
        ('Información Básica', {'fields': ('name', 'description', 'status')}),
        ('Ubicación', {'fields': ('latitude', 'longitude', 'radius')}),
    )

@admin.register(AreaSchedule)
class AreaScheduleAdmin(admin.ModelAdmin):
    """Admin para el modelo AreaSchedule"""
    list_display = ('area', 'grace_period_minutes', 'weekdays_active', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('area__name',)
    ordering = ('area__name',)
    
    fieldsets = (
        ('Área', {'fields': ('area',)}),
        ('Horarios de Lunes a Viernes', {
            'fields': (
                ('monday_start', 'monday_end', 'monday_active'),
                ('tuesday_start', 'tuesday_end', 'tuesday_active'),
                ('wednesday_start', 'wednesday_end', 'wednesday_active'),
                ('thursday_start', 'thursday_end', 'thursday_active'),
                ('friday_start', 'friday_end', 'friday_active'),
            )
        }),
        ('Horarios de Fin de Semana', {
            'fields': (
                ('saturday_start', 'saturday_end', 'saturday_active'),
                ('sunday_start', 'sunday_end', 'sunday_active'),
            )
        }),
        ('Configuración', {'fields': ('grace_period_minutes',)}),
    )
    
    def weekdays_active(self, obj):
        """Muestra los días activos de forma resumida"""
        active_days = []
        if obj.monday_active: active_days.append('Lun')
        if obj.tuesday_active: active_days.append('Mar')
        if obj.wednesday_active: active_days.append('Mié')
        if obj.thursday_active: active_days.append('Jue')
        if obj.friday_active: active_days.append('Vie')
        if obj.saturday_active: active_days.append('Sáb')
        if obj.sunday_active: active_days.append('Dom')
        return ', '.join(active_days) if active_days else 'Ninguno'
    weekdays_active.short_description = 'Días Activos'

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """Admin para el modelo Employee"""
    list_display = ('employee_id', 'full_name', 'email', 'position', 'has_admin_access', 'area', 'hire_date', 'is_active')
    list_filter = ('area', 'hire_date', 'user__is_active', 'has_admin_access', 'position')
    search_fields = ('employee_id', 'user__first_name', 'user__last_name', 'user__email')
    ordering = ('user__first_name', 'user__last_name')
    
    fieldsets = (
        ('Información del Usuario', {'fields': ('user', 'employee_id')}),
        ('Información Laboral', {'fields': ('position', 'area', 'hire_date')}),
        ('Acceso Administrativo', {
            'fields': ('has_admin_access',),
            'description': 'Controla si este empleado puede acceder al panel administrativo'
        }),
        ('Foto', {'fields': ('photo',)}),
    )
    
    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Nombre Completo'
    
    def email(self, obj):
        return obj.email
    email.short_description = 'Email'
    
    def is_active(self, obj):
        return obj.user.is_active
    is_active.short_description = 'Activo'
    is_active.boolean = True
    
    def has_admin_access_display(self, obj):
        """Mostrar el acceso administrativo de forma más clara"""
        if obj.has_admin_access:
            return "✅ SÍ"
        return "❌ NO"
    has_admin_access_display.short_description = 'Acceso Admin'

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    """Admin para el modelo Attendance"""
    list_display = ('employee_name', 'date', 'check_in', 'check_out', 'expected_times', 'status', 'area', 'face_verified', 'hours_worked', 'is_late_display')
    list_filter = ('status', 'date', 'area', 'face_verified')
    search_fields = ('employee__user__first_name', 'employee__user__last_name', 'employee__employee_id')
    ordering = ('-date', '-check_in')
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Información de Asistencia', {'fields': ('employee', 'date', 'status')}),
        ('Horarios Reales', {'fields': ('check_in', 'check_out')}),
        ('Horarios Esperados', {'fields': ('expected_check_in', 'expected_check_out')}),
        ('Ubicación', {'fields': ('area', 'latitude', 'longitude')}),
        ('Verificación', {'fields': ('face_verified',)}),
    )
    
    def employee_name(self, obj):
        return obj.employee.full_name
    employee_name.short_description = 'Empleado'
    
    def expected_times(self, obj):
        """Muestra los horarios esperados de forma resumida"""
        if obj.expected_check_in and obj.expected_check_out:
            return f"{obj.expected_check_in.strftime('%H:%M')} - {obj.expected_check_out.strftime('%H:%M')}"
        return "--"
    expected_times.short_description = 'Horario Esperado'
    
    def is_late_display(self, obj):
        """Muestra si llegó tarde de forma visual"""
        if obj.is_late:
            return "🕐 Tarde"
        elif obj.check_in and obj.expected_check_in:
            return "✅ A tiempo"
        return "--"
    is_late_display.short_description = 'Estado'
    
    def hours_worked(self, obj):
        hours = obj.hours_worked
        return f"{hours:.2f}h" if hours else "--"
