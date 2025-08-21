from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import User, Employee, Area

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
