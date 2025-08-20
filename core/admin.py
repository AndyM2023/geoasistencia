from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Employee, Area, Attendance

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

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """Admin para el modelo Employee"""
    list_display = ('employee_id', 'full_name', 'email', 'position', 'area', 'hire_date', 'is_active')
    list_filter = ('area', 'hire_date', 'user__is_active')
    search_fields = ('employee_id', 'user__first_name', 'user__last_name', 'user__email')
    ordering = ('user__first_name', 'user__last_name')
    
    fieldsets = (
        ('Información del Usuario', {'fields': ('user', 'employee_id')}),
        ('Información Laboral', {'fields': ('position', 'area', 'hire_date')}),
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

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    """Admin para el modelo Attendance"""
    list_display = ('employee_name', 'date', 'check_in', 'check_out', 'status', 'area', 'face_verified', 'hours_worked')
    list_filter = ('status', 'date', 'area', 'face_verified')
    search_fields = ('employee__user__first_name', 'employee__user__last_name', 'employee__employee_id')
    ordering = ('-date', '-check_in')
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Información de Asistencia', {'fields': ('employee', 'date', 'status')}),
        ('Horarios', {'fields': ('check_in', 'check_out')}),
        ('Ubicación', {'fields': ('area', 'latitude', 'longitude')}),
        ('Verificación', {'fields': ('face_verified',)}),
    )
    
    def employee_name(self, obj):
        return obj.employee.full_name
    employee_name.short_description = 'Empleado'
    
    def hours_worked(self, obj):
        hours = obj.hours_worked
        return f"{hours:.2f}h" if hours else "--"
    hours_worked.short_description = 'Horas Trabajadas'
