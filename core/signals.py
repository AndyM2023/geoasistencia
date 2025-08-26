from django.db.models.signals import post_save, post_init
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
from .models import User, Employee, Area, Attendance
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

@receiver(post_save, sender=User)
def create_employee_for_admin(sender, instance, created, **kwargs):
    """
    Señal que se ejecuta automáticamente cuando se crea o actualiza un usuario.
    Si el usuario es administrador y no tiene perfil de empleado, se crea automáticamente.
    """
    
    # Solo procesar si el usuario es administrador
    if instance.role == 'admin':
        
        # Verificar si ya tiene perfil de empleado
        try:
            existing_employee = Employee.objects.get(user=instance)
            # Si ya existe, no hacer nada
            return
        except Employee.DoesNotExist:
            # Si no existe, crear el perfil de empleado
            pass
        
        # Buscar un área activa para asignar por defecto
        try:
            default_area = Area.objects.filter(status='active').first()
        except:
            default_area = None
        
        # Crear el perfil de empleado automáticamente
        try:
            Employee.objects.create(
                user=instance,
                position='otro',  # Cargo genérico - se actualizará desde el formulario
                has_admin_access=True,      # Acceso administrativo por defecto
                area=default_area,
                hire_date=instance.date_joined.date() if instance.date_joined else None
            )
            print(f"✅ Empleado creado automáticamente para administrador: {instance.username}")
            print(f"   - Cargo temporal: 'otro' (se actualizará desde el formulario)")
            print(f"   - Acceso administrativo: HABILITADO")
            
        except Exception as e:
            print(f"❌ Error creando empleado para {instance.username}: {e}")

@receiver(post_save, sender=User)
def update_employee_for_admin(sender, instance, created, **kwargs):
    """
    Señal que se ejecuta cuando se actualiza un usuario.
    Si se cambia el rol a 'admin', crear perfil de empleado si no existe.
    """
    
    # Solo procesar si NO es una creación nueva y el rol es admin
    if not created and instance.role == 'admin':
        
        # Verificar si ya tiene perfil de empleado
        try:
            existing_employee = Employee.objects.get(user=instance)
            # Si ya existe, no hacer nada
            return
        except Employee.DoesNotExist:
            # Si no existe, crear el perfil de empleado
            pass
        
        # Buscar un área activa para asignar por defecto
        try:
            default_area = Area.objects.filter(status='active').first()
        except:
            default_area = None
        
        # Crear el perfil de empleado automáticamente
        try:
            Employee.objects.create(
                user=instance,
                position='otro',  # Cargo genérico - se actualizará desde el formulario
                has_admin_access=True,      # Acceso administrativo por defecto
                area=default_area,
                hire_date=instance.date_joined.date() if instance.date_joined else None
            )
            print(f"✅ Empleado creado automáticamente para administrador actualizado: {instance.username}")
            print(f"   - Cargo temporal: 'otro' (se actualizará desde el formulario)")
            print(f"   - Acceso administrativo: HABILITADO")
            
        except Exception as e:
            print(f"❌ Error creando empleado para {instance.username}: {e}")

@receiver(post_save, sender=Employee)
def auto_promote_to_admin_by_access(sender, instance, created, **kwargs):
    """
    Señal que se ejecuta cuando se crea o actualiza un empleado.
    Si tiene acceso administrativo, automáticamente promueve al usuario a administrador.
    """
    
    # Solo procesar si el empleado tiene acceso administrativo
    if instance.has_admin_access:
        
        user = instance.user
        
        # Verificar si ya es administrador
        if user.role == 'admin':
            print(f"✅ Usuario {user.username} ya es administrador (acceso: {instance.has_admin_access})")
            return
        
        # Promover automáticamente a administrador
        try:
            old_role = user.role
            user.role = 'admin'
            user.save()
            
            print(f"🎉 Usuario {user.username} promovido automáticamente a administrador!")
            print(f"   - Cargo: {instance.position}")
            print(f"   - Acceso administrativo: {instance.has_admin_access}")
            print(f"   - Rol anterior: {old_role}")
            print(f"   - Rol nuevo: {user.role}")
            print(f"   - Employee ID: {instance.employee_id}")
            
        except Exception as e:
            print(f"❌ Error promoviendo a administrador: {e}")
    
    # Si NO tiene acceso administrativo, verificar si debe ser degradado a empleado
    else:
        user = instance.user
        
        # Solo procesar si actualmente es administrador
        if user.role == 'admin':
            
            # Verificar si tiene otros perfiles con acceso administrativo
            try:
                other_admin_profiles = Employee.objects.filter(
                    user=user,
                    has_admin_access=True
                ).exclude(id=instance.id)
                
                # Si no tiene otros perfiles administrativos, degradar a empleado
                if not other_admin_profiles.exists():
                    try:
                        old_role = user.role
                        user.role = 'employee'
                        user.save()
                        
                        print(f"📉 Usuario {user.username} degradado a empleado")
                        print(f"   - Cargo actual: {instance.position}")
                        print(f"   - Acceso administrativo: {instance.has_admin_access}")
                        print(f"   - Rol anterior: {old_role}")
                        print(f"   - Rol nuevo: {user.role}")
                        
                    except Exception as e:
                        print(f"❌ Error degradando a empleado: {e}")
                else:
                    print(f"✅ Usuario {user.username} mantiene rol de administrador (otros perfiles administrativos)")
                    
            except Exception as e:
                print(f"❌ Error verificando otros perfiles: {e}")

@receiver(post_save, sender=Attendance)
def process_incomplete_attendance_after_save(sender, instance, created, **kwargs):
    """
    Signal que se ejecuta automáticamente después de guardar una asistencia
    Procesa asistencias incompletas del día anterior
    """
    try:
        # Solo procesar si es una asistencia nueva o si se actualizó el check_out
        if created or kwargs.get('update_fields') and 'check_out' in kwargs['update_fields']:
            # Procesar asistencias incompletas del día anterior
            yesterday = timezone.now().date() - timedelta(days=1)
            process_incomplete_attendance_for_date(yesterday)
            
    except Exception as e:
        logger.error(f"Error procesando asistencia incompleta automáticamente: {e}")

def process_incomplete_attendance_for_date(target_date):
    """
    Procesa asistencias incompletas para una fecha específica
    """
    try:
        # Obtener asistencias incompletas del día objetivo
        incomplete_attendances = Attendance.objects.filter(
            date=target_date,
            check_in__isnull=False,
            check_out__isnull=True,
            status__in=['present', 'late']  # Solo los que aún no son ausentes
        )
        
        if not incomplete_attendances.exists():
            return
        
        updated_count = 0
        for attendance in incomplete_attendances:
            try:
                old_status = attendance.status
                
                # Marcar como ausente
                if attendance.mark_as_absent_if_incomplete():
                    updated_count += 1
                    logger.info(f"🔄 {attendance.employee.full_name} ({target_date}): {old_status} → ausente (automático)")
                    
            except Exception as e:
                logger.error(f"Error procesando {attendance.employee.full_name}: {e}")
        
        if updated_count > 0:
            logger.info(f"✅ Procesamiento automático completado para {target_date}: {updated_count} estados actualizados")
            
    except Exception as e:
        logger.error(f"Error en procesamiento automático para {target_date}: {e}")

@receiver(post_init, sender=Attendance)
def process_incomplete_attendance_on_access(sender, instance, **kwargs):
    """
    Signal que se ejecuta cuando se accede a una asistencia
    Útil para procesar automáticamente al cargar reportes
    """
    try:
        # Solo procesar si es una asistencia del día anterior o anterior
        if instance.date and instance.date < timezone.now().date():
            # Procesar asistencias incompletas para esa fecha
            process_incomplete_attendance_for_date(instance.date)
            
    except Exception as e:
        logger.error(f"Error procesando asistencia al acceder: {e}")

def auto_process_all_incomplete_attendances():
    """
    Función que se puede llamar manualmente o programar
    Procesa todas las asistencias incompletas de días anteriores
    """
    try:
        today = timezone.now().date()
        
        # Procesar los últimos 7 días
        for days_back in range(1, 8):
            target_date = today - timedelta(days=days_back)
            process_incomplete_attendance_for_date(target_date)
            
        logger.info("✅ Procesamiento automático de todas las asistencias incompletas completado")
        
    except Exception as e:
        logger.error(f"Error en procesamiento automático general: {e}")
