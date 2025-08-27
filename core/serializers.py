from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from .models import User, Employee, Area, Attendance, AreaSchedule
from .models import PasswordResetToken
from .services.employee_welcome_service import EmployeeWelcomeService
from datetime import time
import os

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Serializer para el modelo User"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'role', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_full_name(self, obj):
        return obj.get_full_name()

class AreaSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Area"""
    employee_count = serializers.ReadOnlyField()
    schedule = serializers.JSONField(write_only=True, required=False)
    
    class Meta:
        model = Area
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'employee_count']
    
    def create(self, validated_data):
        """Crear área con estado activo por defecto y schedule"""
        print(f"🔍 AreaSerializer.create() - Datos recibidos:")
        print(f"   - Validated data: {validated_data}")
        
        # Extraer el schedule del validated_data
        schedule_data = validated_data.pop('schedule', None)
        print(f"🔍 Schedule data extraído: {schedule_data}")
        
        # Si no se proporciona status, establecer como activo
        if 'status' not in validated_data:
            validated_data['status'] = 'active'
        
        # Crear el área
        area = super().create(validated_data)
        print(f"✅ Área creada: {area.id} - {area.name}")
        
        # Si hay schedule data, crear el AreaSchedule
        if schedule_data:
            try:
                from .models import AreaSchedule
                
                # Determinar el tipo de schedule basado en scheduleType.value
                schedule_type = 'default'  # Por defecto
                if hasattr(self, 'context') and self.context.get('schedule_type'):
                    schedule_type = self.context['schedule_type']
                elif 'schedule_type' in schedule_data:
                    schedule_type = schedule_data['schedule_type']
                
                print(f"🔍 Creando AreaSchedule con tipo: {schedule_type}")
                
                # Crear el schedule con los datos recibidos
                schedule = AreaSchedule.objects.create(
                    area=area,
                    schedule_type=schedule_type,
                    monday_start=schedule_data.get('monday_start', '08:00'),
                    monday_end=schedule_data.get('monday_end', '17:00'),
                    monday_active=schedule_data.get('monday_active', True),
                    tuesday_start=schedule_data.get('tuesday_start', '08:00'),
                    tuesday_end=schedule_data.get('tuesday_end', '17:00'),
                    tuesday_active=schedule_data.get('tuesday_active', True),
                    wednesday_start=schedule_data.get('wednesday_start', '08:00'),
                    wednesday_end=schedule_data.get('wednesday_end', '17:00'),
                    wednesday_active=schedule_data.get('wednesday_active', True),
                    thursday_start=schedule_data.get('thursday_start', '08:00'),
                    thursday_end=schedule_data.get('thursday_end', '17:00'),
                    thursday_active=schedule_data.get('thursday_active', True),
                    friday_start=schedule_data.get('friday_start', '08:00'),
                    friday_end=schedule_data.get('friday_end', '17:00'),
                    friday_active=schedule_data.get('friday_active', True),
                    saturday_start=schedule_data.get('saturday_start'),
                    saturday_end=schedule_data.get('saturday_end'),
                    saturday_active=schedule_data.get('saturday_active', False),
                    sunday_start=schedule_data.get('sunday_start'),
                    sunday_end=schedule_data.get('sunday_end'),
                    sunday_active=schedule_data.get('sunday_active', False),
                    grace_period_minutes=schedule_data.get('grace_period_minutes', 15)
                )
                print(f"✅ AreaSchedule creado: {schedule.id} para área {area.id}")
                
            except Exception as e:
                print(f"❌ Error creando AreaSchedule: {e}")
                # No fallar la creación del área si falla el schedule
                pass
        
        return area
    
    def update(self, instance, validated_data):
        """Actualizar área con validación personalizada y schedule"""
        print(f"🔍 AreaSerializer.update() - Datos recibidos:")
        print(f"   - Instance ID: {instance.id}")
        print(f"   - Validated data: {validated_data}")
        print(f"   - Keys en validated_data: {list(validated_data.keys())}")
        
        # Extraer el schedule del validated_data
        schedule_data = validated_data.pop('schedule', None)
        print(f"🔍 Schedule data extraído: {schedule_data}")
        print(f"🔍 Schedule data tipo: {type(schedule_data)}")
        if schedule_data:
            print(f"🔍 Schedule data keys: {list(schedule_data.keys())}")
            print(f"🔍 monday_start en schedule_data: {schedule_data.get('monday_start')} (tipo: {type(schedule_data.get('monday_start'))})")
            print(f"🔍 monday_end en schedule_data: {schedule_data.get('monday_end')} (tipo: {type(schedule_data.get('monday_end'))})")
            print(f"🔍 monday_active en schedule_data: {schedule_data.get('monday_active')} (tipo: {type(schedule_data.get('monday_active'))})")
        
        # Validar coordenadas antes de actualizar
        if 'latitude' in validated_data:
            lat = validated_data['latitude']
            if not (-90 <= float(lat) <= 90):
                raise serializers.ValidationError({
                    'latitude': 'La latitud debe estar entre -90 y 90 grados'
                })
            print(f"✅ Latitud válida: {lat}")
        
        if 'longitude' in validated_data:
            lng = validated_data['longitude']
            if not (-180 <= float(lng) <= 180):
                raise serializers.ValidationError({
                    'longitude': 'La longitud debe estar entre -180 y 180 grados'
                })
            print(f"✅ Longitud válida: {lng}")
        
        if 'radius' in validated_data:
            radius = validated_data['radius']
            if not (10 <= int(radius) <= 10000):
                raise serializers.ValidationError({
                    'radius': 'El radio debe estar entre 10 y 10000 metros'
                })
            print(f"✅ Radio válido: {radius}")
        
        # Actualizar la instancia del área
        area = super().update(instance, validated_data)
        print(f"✅ Área actualizada: {area.id} - {area.name}")
        
        # Si hay schedule data, actualizar o crear el AreaSchedule
        if schedule_data:
            try:
                from .models import AreaSchedule
                
                # Obtener el schedule existente o crear uno nuevo
                schedule, created = AreaSchedule.objects.get_or_create(
                    area=area,
                    defaults={
                        'schedule_type': schedule_data.get('schedule_type', 'default'),
                        'monday_start': time(8, 0),
                        'monday_end': time(17, 0),
                        'monday_active': True,
                        'tuesday_start': time(8, 0),
                        'tuesday_end': time(17, 0),
                        'tuesday_active': True,
                        'wednesday_start': time(8, 0),
                        'wednesday_end': time(17, 0),
                        'wednesday_active': True,
                        'thursday_start': time(8, 0),
                        'thursday_end': time(17, 0),
                        'thursday_active': True,
                        'friday_start': time(8, 0),
                        'friday_end': time(17, 0),
                        'friday_active': True,
                        'saturday_start': None,
                        'saturday_end': None,
                        'saturday_active': False,
                        'sunday_start': None,
                        'sunday_end': None,
                        'sunday_active': False,
                        'grace_period_minutes': 15
                    }
                )
                
                print(f"🔍 Schedule existente: {schedule.id}, creado: {created}")
                print(f"🔍 Schedule type actual: {schedule.schedule_type}")
                print(f"🔍 Schedule type nuevo: {schedule_data.get('schedule_type')}")
                
                # ✅ ACTUALIZAR EXPLÍCITAMENTE el schedule_type SIEMPRE que se reciba
                if 'schedule_type' in schedule_data:
                    schedule.schedule_type = schedule_data['schedule_type']
                    print(f"✅ Schedule type actualizado a: {schedule.schedule_type}")
                
                # Actualizar horarios según el tipo
                if schedule_data.get('schedule_type') == 'default':
                    # Horario por defecto - sobrescribir completamente con valores válidos
                    # SOLO si es un horario NUEVO o si se cambia EXPLÍCITAMENTE a default
                    if created or schedule_data.get('force_default', False):
                        schedule.monday_start = time(8, 0)
                        schedule.monday_end = time(17, 0)
                        schedule.monday_active = True
                        schedule.tuesday_start = time(8, 0)
                        schedule.tuesday_end = time(17, 0)
                        schedule.tuesday_active = True
                        schedule.wednesday_start = time(8, 0)
                        schedule.wednesday_end = time(17, 0)
                        schedule.wednesday_active = True
                        schedule.thursday_start = time(8, 0)
                        schedule.thursday_end = time(17, 0)
                        schedule.thursday_active = True
                        schedule.friday_start = time(8, 0)
                        schedule.friday_end = time(17, 0)
                        schedule.friday_active = True
                        schedule.saturday_start = None
                        schedule.saturday_end = None
                        schedule.saturday_active = False
                        schedule.sunday_start = None
                        schedule.sunday_end = None
                        schedule.sunday_active = False
                        schedule.grace_period_minutes = 15
                        print(f"✅ Horarios actualizados a por defecto")
                    else:
                        print(f"ℹ️ Horario existente mantenido, no se sobrescribe con valores por defecto")
                elif schedule_data.get('schedule_type') == 'custom':
                    # Horario personalizado - actualizar solo los campos proporcionados
                    print(f"🔍 Actualizando horarios personalizados")
                    print(f"🔍 Horarios actuales: monday_active={schedule.monday_active}, tuesday_active={schedule.tuesday_active}")
                    print(f"🔍 Schedule data recibido: {schedule_data}")
                    print(f"🔍 monday_start recibido: {schedule_data.get('monday_start')} (tipo: {type(schedule_data.get('monday_start'))})")
                    print(f"🔍 monday_end recibido: {schedule_data.get('monday_end')} (tipo: {type(schedule_data.get('monday_end'))})")
                    print(f"🔍 monday_active recibido: {schedule_data.get('monday_active')} (tipo: {type(schedule_data.get('monday_active'))})")
                    
                    # ✅ Actualizar campos de lunes a viernes - SOLO los que se envían
                    for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:
                        # Solo actualizar si el campo está presente en schedule_data
                        if f'{day}_active' in schedule_data:
                            schedule.__setattr__(f'{day}_active', schedule_data[f'{day}_active'])
                            print(f"✅ {day}_active actualizado a: {schedule_data[f'{day}_active']}")
                        
                        if f'{day}_start' in schedule_data and schedule_data[f'{day}_start']:
                            try:
                                # Convertir string de tiempo a objeto time
                                time_str = schedule_data[f'{day}_start']
                                if isinstance(time_str, str):
                                    # Manejar formato HH:MM:SS o HH:MM
                                    time_parts = time_str.split(':')
                                    if len(time_parts) >= 2:
                                        hour = int(time_parts[0])
                                        minute = int(time_parts[1])
                                        schedule.__setattr__(f'{day}_start', time(hour, minute))
                                        print(f"✅ {day}_start actualizado a: {time(hour, minute)}")
                                    else:
                                        print(f"❌ Formato de tiempo inválido para {day}_start: {time_str}")
                                else:
                                    schedule.__setattr__(f'{day}_start', time_str)
                                    print(f"✅ {day}_start actualizado a: {time_str}")
                            except (ValueError, TypeError) as e:
                                print(f"❌ Error convirtiendo {day}_start: {e}")
                        
                        if f'{day}_end' in schedule_data and schedule_data[f'{day}_end']:
                            try:
                                # Convertir string de tiempo a objeto time
                                time_str = schedule_data[f'{day}_end']
                                if isinstance(time_str, str):
                                    # Manejar formato HH:MM:SS o HH:MM
                                    time_parts = time_str.split(':')
                                    if len(time_parts) >= 2:
                                        hour = int(time_parts[0])
                                        minute = int(time_parts[1])
                                        schedule.__setattr__(f'{day}_end', time(hour, minute))
                                        print(f"✅ {day}_end actualizado a: {time(hour, minute)}")
                                    else:
                                        print(f"❌ Formato de tiempo inválido para {day}_end: {time_str}")
                                else:
                                    schedule.__setattr__(f'{day}_end', time_str)
                                    print(f"✅ {day}_end actualizado a: {time_str}")
                            except (ValueError, TypeError) as e:
                                print(f"❌ Error convirtiendo {day}_end: {e}")
                    
                    # ✅ Actualizar campos de fin de semana - SOLO los que se envían
                    for day in ['saturday', 'sunday']:
                        # Solo actualizar si el campo está presente en schedule_data
                        if f'{day}_active' in schedule_data:
                            schedule.__setattr__(f'{day}_active', schedule_data[f'{day}_active'])
                            print(f"✅ {day}_active actualizado a: {schedule_data[f'{day}_active']}")
                        
                        if f'{day}_start' in schedule_data and schedule_data[f'{day}_start']:
                            try:
                                # Convertir string de tiempo a objeto time
                                time_str = schedule_data[f'{day}_start']
                                if isinstance(time_str, str):
                                    # Manejar formato HH:MM:SS o HH:MM
                                    time_parts = time_str.split(':')
                                    if len(time_parts) >= 2:
                                        hour = int(time_parts[0])
                                        minute = int(time_parts[1])
                                        schedule.__setattr__(f'{day}_start', time(hour, minute))
                                        print(f"✅ {day}_start actualizado a: {time(hour, minute)}")
                                    else:
                                        print(f"❌ Formato de tiempo inválido para {day}_start: {time_str}")
                                else:
                                    schedule.__setattr__(f'{day}_start', time_str)
                                    print(f"✅ {day}_start actualizado a: {time_str}")
                            except (ValueError, TypeError) as e:
                                print(f"❌ Error convirtiendo {day}_start: {e}")
                        
                        if f'{day}_end' in schedule_data and schedule_data[f'{day}_end']:
                            try:
                                # Convertir string de tiempo a objeto time
                                time_str = schedule_data[f'{day}_end']
                                if isinstance(time_str, str):
                                    # Manejar formato HH:MM:SS o HH:MM
                                    time_parts = time_str.split(':')
                                    if len(time_parts) >= 2:
                                        hour = int(time_parts[0])
                                        minute = int(time_parts[1])
                                        schedule.__setattr__(f'{day}_end', time(hour, minute))
                                        print(f"✅ {day}_end actualizado a: {time(hour, minute)}")
                                    else:
                                        print(f"❌ Formato de tiempo inválido para {day}_end: {time_str}")
                                else:
                                    schedule.__setattr__(f'{day}_end', time_str)
                                    print(f"✅ {day}_end actualizado a: {time_str}")
                            except (ValueError, TypeError) as e:
                                print(f"❌ Error convirtiendo {day}_end: {e}")
                    
                    # ✅ Actualizar tolerancia
                    if 'grace_period_minutes' in schedule_data:
                        schedule.grace_period_minutes = schedule_data['grace_period_minutes']
                    
                    # ✅ Preservar valores existentes para campos no enviados
                    print(f"🔍 Preservando valores existentes para campos no enviados:")
                    for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
                        if f'{day}_start' not in schedule_data:
                            print(f"   - {day}_start preservado: {getattr(schedule, f'{day}_start')}")
                        if f'{day}_end' not in schedule_data:
                            print(f"   - {day}_end preservado: {getattr(schedule, f'{day}_end')}")
                        if f'{day}_active' not in schedule_data:
                            print(f"   - {day}_active preservado: {getattr(schedule, f'{day}_active')}")
                    
                    print(f"✅ Horarios personalizados actualizados")
                    print(f"🔍 Horarios finales: monday_active={schedule.monday_active}, tuesday_active={schedule.tuesday_active}")
                    print(f"🔍 Horarios finales del lunes:")
                    print(f"   - monday_start: {schedule.monday_start} (tipo: {type(schedule.monday_start)})")
                    print(f"   - monday_end: {schedule.monday_end} (tipo: {type(schedule.monday_end)})")
                    print(f"   - monday_active: {schedule.monday_active} (tipo: {type(schedule.monday_active)})")
                elif schedule_data.get('schedule_type') == 'none':
                    # Sin horario - eliminar el schedule
                    schedule.delete()
                    print(f"✅ Schedule eliminado (sin horario)")
                    return area
                
                schedule.save()
                
                # ✅ VERIFICAR QUE SE GUARDÓ CORRECTAMENTE
                print(f"🔍 VERIFICACIÓN POST-SAVE:")
                print(f"   - monday_start guardado: {schedule.monday_start}")
                print(f"   - monday_end guardado: {schedule.monday_end}")
                print(f"   - monday_active guardado: {schedule.monday_active}")
                
                action = "creado" if created else "actualizado"
                print(f"✅ AreaSchedule {action}: {schedule.id} para área {area.id}")
                print(f"✅ Schedule type final: {schedule.schedule_type}")
                
            except Exception as e:
                print(f"❌ Error actualizando AreaSchedule: {e}")
                # No fallar la actualización del área si falla el schedule
                pass
        
        return area
    
    def validate(self, data):
        """Validación personalizada para el serializer"""
        print(f"🔍 AreaSerializer.validate() - Validando datos:")
        print(f"   - Datos recibidos: {data}")
        
        # Validar que el nombre no esté vacío
        if 'name' in data and not data['name'].strip():
            raise serializers.ValidationError({
                'name': 'El nombre del área no puede estar vacío'
            })
        
        # Validar que el status sea válido
        if 'status' in data and data['status'] not in ['active', 'inactive']:
            raise serializers.ValidationError({
                'status': 'El status debe ser "active" o "inactive"'
            })
        
        print(f"✅ Validación exitosa")
        return data
    
    def to_representation(self, instance):
        """Incluir el schedule en la respuesta si está disponible"""
        data = super().to_representation(instance)
        
        # Agregar información del schedule si existe
        try:
            if hasattr(instance, 'schedule') and instance.schedule:
                schedule_data = {
                    'schedule_type': instance.schedule.schedule_type,
                    'monday_start': instance.schedule.monday_start.strftime('%H:%M') if instance.schedule.monday_start else None,
                    'monday_end': instance.schedule.monday_end.strftime('%H:%M') if instance.schedule.monday_end else None,
                    'monday_active': instance.schedule.monday_active,
                    'tuesday_start': instance.schedule.tuesday_start.strftime('%H:%M') if instance.schedule.tuesday_start else None,
                    'tuesday_end': instance.schedule.tuesday_end.strftime('%H:%M') if instance.schedule.tuesday_end else None,
                    'tuesday_active': instance.schedule.tuesday_active,
                    'wednesday_start': instance.schedule.wednesday_start.strftime('%H:%M') if instance.schedule.wednesday_start else None,
                    'wednesday_end': instance.schedule.wednesday_end.strftime('%H:%M') if instance.schedule.wednesday_end else None,
                    'wednesday_active': instance.schedule.wednesday_active,
                    'thursday_start': instance.schedule.thursday_start.strftime('%H:%M') if instance.schedule.thursday_start else None,
                    'thursday_end': instance.schedule.thursday_end.strftime('%H:%M') if instance.schedule.thursday_end else None,
                    'thursday_active': instance.schedule.thursday_active,
                    'friday_start': instance.schedule.friday_start.strftime('%H:%M') if instance.schedule.friday_start else None,
                    'friday_end': instance.schedule.friday_end.strftime('%H:%M') if instance.schedule.friday_end else None,
                    'friday_active': instance.schedule.friday_active,
                    'saturday_start': instance.schedule.saturday_start.strftime('%H:%M') if instance.schedule.saturday_start else None,
                    'saturday_end': instance.schedule.saturday_end.strftime('%H:%M') if instance.schedule.saturday_end else None,
                    'saturday_active': instance.schedule.saturday_active,
                    'sunday_start': instance.schedule.sunday_start.strftime('%H:%M') if instance.schedule.sunday_start else None,
                    'sunday_end': instance.schedule.sunday_end.strftime('%H:%M') if instance.schedule.sunday_end else None,
                    'sunday_active': instance.schedule.sunday_active,
                    'grace_period_minutes': instance.schedule.grace_period_minutes
                }
                data['schedule'] = schedule_data
                data['schedule_id'] = instance.schedule.id
                data['has_schedule'] = True
            else:
                data['schedule'] = None
                data['schedule_id'] = None
                data['has_schedule'] = False
        except Exception as e:
            print(f"❌ Error obteniendo schedule en to_representation: {e}")
            data['schedule'] = None
            data['schedule_id'] = None
            data['has_schedule'] = False
        
        return data

class EmployeeSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Employee"""
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='employee'),
        source='user',
        write_only=True,
        required=False
    )
    # Campos para crear usuario
    first_name = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True, max_length=50)
    last_name = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True, max_length=50)
    email = serializers.EmailField(write_only=True, required=False, allow_blank=True, allow_null=True, max_length=254)
    cedula = serializers.CharField(write_only=True, required=True, allow_blank=False, allow_null=False, max_length=20)
    
    # Campo para la foto del empleado
    photo = serializers.ImageField(required=False, allow_null=True)
    
    # Campo para indicar que se debe eliminar la foto
    delete_photo = serializers.BooleanField(required=False, write_only=True)
    
    # Validación personalizada para position
    def validate_position(self, value):
        """Validar que el position sea una opción válida"""
        valid_positions = [
            'desarrollador', 'disenador', 'secretario', 'gerente', 'analista',
            'ingeniero', 'contador', 'recursos_humanos', 'marketing', 'ventas',
            'soporte', 'administrativo', 'operativo', 'otro'
        ]
        
        if value not in valid_positions:
            raise serializers.ValidationError(
                f'"{value}" no es una opción válida. Opciones disponibles: {", ".join(valid_positions)}'
            )
        return value

    # Utilidad: validar cédula ecuatoriana (10 dígitos con dígito verificador)
    @staticmethod
    def _is_valid_ecuadorian_cedula(cedula: str) -> bool:
        try:
            if not cedula or len(cedula) != 10 or not cedula.isdigit():
                return False
            total = 0
            for i in range(9):
                num = int(cedula[i])
                if i % 2 == 0:
                    num = num * 2
                    if num >= 10:
                        num = (num // 10) + (num % 10)
                total += num
            verificador = int(cedula[9])
            modulo = total % 10
            calculado = 0 if modulo == 0 else 10 - modulo
            return verificador == calculado
        except Exception:
            return False

    def validate_cedula(self, value):
        """Validar formato de cédula (obligatoria)."""
        if value in [None, ""]:
            raise serializers.ValidationError('La cédula es requerida')
        cedula_str = str(value)
        if len(cedula_str) != 10 or not cedula_str.isdigit():
            raise serializers.ValidationError('La cédula debe tener 10 dígitos numéricos')
        if not self._is_valid_ecuadorian_cedula(cedula_str):
            raise serializers.ValidationError('Cédula ecuatoriana inválida')

        # Validar duplicado en creación
        try:
            existing = User.objects.filter(cedula=cedula_str)
            # En update, excluir el usuario actual si existe
            if self.instance and getattr(self.instance, 'user_id', None):
                existing = existing.exclude(id=self.instance.user_id)
            if existing.exists():
                raise serializers.ValidationError('Esta cédula ya está registrada para otro usuario')
        except Exception:
            # Si algo falla, no ocultar errores de validación, relanzar
            raise
        return cedula_str
    
    def validate_first_name(self, value):
        """Capitalizar automáticamente el primer nombre"""
        if value:
            return value.strip().title()
        return value
    
    def validate_last_name(self, value):
        """Capitalizar automáticamente el apellido"""
        if value:
            return value.strip().title()
        return value
    
    # Campo para leer la cédula del usuario
    cedula_display = serializers.CharField(source='user.cedula', read_only=True)
    
    area_name = serializers.CharField(source='area.name', read_only=True)
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    email_display = serializers.CharField(source='user.email', read_only=True)
    
    # Campo para la URL de la foto
    photo_url = serializers.SerializerMethodField()
    
    def get_photo_url(self, obj):
        """Obtener la URL completa de la foto del empleado"""
        if obj.photo and hasattr(obj.photo, 'url'):
            # En desarrollo, devolver URL relativa que se puede usar directamente
            return obj.photo.url
        return None
    
    class Meta:
        model = Employee
        fields = [
            'id', 'user', 'user_id', 'employee_id', 'cedula', 'cedula_display', 'position', 'area', 'area_name',
            'hire_date', 'photo', 'photo_url', 'full_name', 'email_display', 'created_at', 'updated_at',
            'first_name', 'last_name', 'email', 'delete_photo'  # Campos para crear usuario
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'full_name', 'email_display', 'area_name', 'cedula_display']
    
    def create(self, validated_data):
        """Crear empleado y usuario asociado con usuario y contraseña automáticos"""
        # Extraer datos del usuario
        first_name = validated_data.pop('first_name', '')
        last_name = validated_data.pop('last_name', '')
        email = validated_data.pop('email', '')
        cedula = validated_data.pop('cedula', '')
        
        # Remover campos que no pertenecen al modelo Employee
        validated_data.pop('delete_photo', None)  # Campo solo para update, no para create
        
        # Si no se proporciona user_id, crear un nuevo usuario
        if 'user' not in validated_data:
            # Generar username automático: inicial del primer nombre + primer apellido + inicial del segundo apellido
            if first_name and last_name:
                # Limpiar y separar nombres y apellidos
                first_name_clean = first_name.strip().split()[0] if first_name.strip() else ''
                apellidos = last_name.strip().split()
                primer_apellido = apellidos[0] if apellidos else ''
                segundo_apellido = apellidos[1] if len(apellidos) > 1 else ''
                
                if first_name_clean and primer_apellido:
                    # Formato: inicial del primer nombre + primer apellido + inicial del segundo apellido
                    username = f"{first_name_clean[0].lower()}{primer_apellido.lower()}{segundo_apellido[0].lower() if segundo_apellido else ''}"
                else:
                    username = f"user_{User.objects.count() + 1}"
            else:
                username = f"user_{User.objects.count() + 1}"
            
            # Asegurar username único con manejo de colisiones
            counter = 1
            original_username = username
            while User.objects.filter(username=username).exists():
                username = f"{original_username}{counter}"
                counter += 1
            
            # Generar contraseña automática: usar cédula o generar una por defecto
            password = cedula if cedula else f"pass{User.objects.count() + 1}"
            
            # Crear usuario
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password,
                role='employee',
                cedula=cedula
            )
            validated_data['user'] = user
            
            print(f"✅ Usuario creado automáticamente:")
            print(f"   - Username: {username}")
            print(f"   - Contraseña: {password}")
            print(f"   - Nombre: {first_name} {last_name}")
            print(f"   - Cédula: {cedula}")
            print(f"   - Formato aplicado: inicial del primer nombre + primer apellido + inicial del segundo apellido")
        
        # Asegurar que hire_date esté presente
        if 'hire_date' not in validated_data:
            from django.utils import timezone
            validated_data['hire_date'] = timezone.localtime().date()
        
        # NO asignar la cédula al empleado - solo al usuario
        # La cédula ya se asignó al usuario en la línea anterior
        
        # Crear empleado
        employee = Employee.objects.create(**validated_data)
        
        # NO enviar email aquí - se enviará después del registro facial
        print(f"✅ Empleado creado exitosamente: {employee.full_name}")
        
        return employee
    
    def update(self, instance, validated_data):
        """Actualizar empleado y usuario asociado"""
        print(f"🔍 EmployeeSerializer.update() - Datos recibidos:")
        print(f"   - Instance ID: {instance.id}")
        print(f"   - Instance user: {instance.user.username}")
        print(f"   - Validated data: {validated_data}")
        
        try:
            # Extraer datos del usuario de forma segura
            first_name = validated_data.pop('first_name', None)
            last_name = validated_data.pop('last_name', None)
            email = validated_data.pop('email', None)
            cedula = validated_data.pop('cedula', None)
            
            # Extraer la foto si está presente
            photo = validated_data.pop('photo', None)
            
            # Verificar si se debe eliminar la foto
            delete_photo = validated_data.pop('delete_photo', False)
            
            print(f"   - Campos extraídos del usuario:")
            print(f"     - first_name: '{first_name}' (tipo: {type(first_name)})")
            print(f"     - last_name: '{last_name}' (tipo: {type(last_name)})")
            print(f"     - email: '{email}' (tipo: {type(email)})")
            print(f"     - cedula: '{cedula}' (tipo: {type(cedula)})")
            print(f"     - photo: {type(photo)} - {'Presente' if photo else 'No presente'}")
            print(f"     - delete_photo: {delete_photo}")
            
            # Actualizar usuario solo si se proporcionan datos válidos
            if any([first_name is not None, last_name is not None, email is not None, cedula is not None]):
                user = instance.user
                if first_name is not None:
                    user.first_name = first_name
                if last_name is not None:
                    user.last_name = last_name
                if email is not None:
                    # Verificar que el email no esté duplicado
                    if email != user.email:  # Solo verificar si cambió
                        try:
                            from core.models import User
                            existing_user = User.objects.filter(email=email).exclude(id=user.id).first()
                            if existing_user:
                                print(f"❌ Email duplicado: {email} ya existe para usuario {existing_user.username}")
                                raise serializers.ValidationError({
                                    'email': f'El email {email} ya está registrado para otro usuario'
                                })
                            print(f"✅ Email válido: {email}")
                        except Exception as e:
                            print(f"❌ Error verificando email: {e}")
                            raise
                    user.email = email
                if cedula is not None:
                    # Verificar que la cédula no esté duplicada
                    if cedula != user.cedula:  # Solo verificar si cambió
                        try:
                            from core.models import User
                            existing_user = User.objects.filter(cedula=cedula).exclude(id=user.id).first()
                            if existing_user:
                                print(f"❌ Cédula duplicada: {cedula} ya existe para usuario {existing_user.username}")
                                raise serializers.ValidationError({
                                    'cedula': f'La cédula {cedula} ya está registrada para otro usuario'
                                })
                            print(f"✅ Cédula válida: {cedula}")
                        except Exception as e:
                            print(f"❌ Error verificando cédula: {e}")
                            raise
                    user.cedula = cedula
                user.save()
                print(f"✅ Usuario actualizado: {user.username}")
            
            # Actualizar empleado
            print(f"   - Campos restantes para empleado: {list(validated_data.keys())}")
            for attr, value in validated_data.items():
                print(f"     - {attr}: {value}")
                setattr(instance, attr, value)
            
            # Actualizar foto si se proporciona
            if photo is not None:
                print(f"   - Actualizando foto del empleado")
                instance.photo = photo
            elif delete_photo:
                print(f"   - Eliminando foto del empleado")
                # Eliminar la foto existente del sistema de archivos
                if instance.photo:
                    try:
                        # Eliminar el archivo físico del sistema
                        if os.path.exists(instance.photo.path):
                            os.remove(instance.photo.path)
                            print(f"   - Archivo físico eliminado: {instance.photo.path}")
                        # Limpiar el campo del modelo
                        instance.photo = None
                        print(f"   - Campo photo establecido a None")
                    except Exception as e:
                        print(f"   - Error eliminando archivo físico: {e}")
                        # Aún así, limpiar el campo del modelo
                        instance.photo = None
                else:
                    print(f"   - No había foto para eliminar")
                    instance.photo = None
            
            instance.save()
            print(f"✅ Empleado actualizado: {instance.id}")
            return instance
            
        except Exception as e:
            print(f"❌ Error en update: {e}")
            import traceback
            traceback.print_exc()
            raise

class AttendanceSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Attendance"""
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    area_name = serializers.CharField(source='area.name', read_only=True)
    hours_worked = serializers.ReadOnlyField()
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'employee', 'employee_name', 'date', 'check_in', 'check_out',
            'status', 'area', 'area_name', 'latitude', 'longitude',
            'face_verified', 'hours_worked', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'employee_name', 'area_name', 'hours_worked']
    
    def validate(self, attrs):
        """Validación personalizada para el modelo Attendance"""
        # Validar que si hay check_out, también debe haber check_in
        if attrs.get('check_out') and not attrs.get('check_in'):
            raise serializers.ValidationError(
                'No puedes marcar salida sin haber marcado entrada primero.'
            )
        
        # Validar que la fecha de check_out no sea anterior a la fecha de check_in
        if attrs.get('check_in') and attrs.get('check_out'):
            if attrs['check_in'] > attrs['check_out']:
                raise serializers.ValidationError(
                    'La hora de salida no puede ser anterior a la hora de entrada.'
                )
        
        # Validar hora de salida contra horario esperado (si se está actualizando)
        if self.instance and attrs.get('check_out'):
            # Si es una actualización y se está cambiando la hora de salida
            if self.instance.check_out != attrs['check_out']:
                # Usar el método de validación del modelo
                is_valid, error_message, error_details = self.instance.validate_check_out_time()
                if not is_valid:
                    raise serializers.ValidationError(error_message)
        
        return attrs

class LoginSerializer(serializers.Serializer):
    """Serializer para autenticación - SOLO ADMINISTRADORES (Panel Admin)"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Credenciales inválidas.')
            if not user.is_active:
                raise serializers.ValidationError('Usuario inactivo.')
            
            # 🔒 RESTRICCIÓN: Solo permitir login a administradores en el panel admin
            if user.role != 'admin':
                raise serializers.ValidationError(
                    'Acceso denegado. Solo los administradores pueden acceder al panel de administración. '
                    
                )
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Debe incluir "username" y "password".')

class EmployeeLoginSerializer(serializers.Serializer):
    """Serializer para autenticación de empleados - USADO EN RECONOCIMIENTO FACIAL"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Credenciales inválidas.')
            if not user.is_active:
                raise serializers.ValidationError('Usuario inactivo.')
            
            # ✅ PERMITIR: Tanto empleados como administradores pueden usar el reconocimiento facial
            # Los administradores también son empleados del sistema
            if user.role not in ['admin', 'employee']:
                raise serializers.ValidationError('Usuario con rol inválido.')
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Debe incluir "username" y "password".')

class DashboardStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas del dashboard"""
    totalEmployees = serializers.IntegerField()
    totalAreas = serializers.IntegerField()
    activeAreas = serializers.IntegerField()
    todayAttendance = serializers.IntegerField()
    pendingAttendance = serializers.IntegerField()
    attendanceRate = serializers.FloatField()
    monthAttendance = serializers.IntegerField()
    workingDays = serializers.IntegerField()

class AttendanceReportSerializer(serializers.Serializer):
    """Serializer para reportes de asistencia"""
    employee = serializers.IntegerField(required=False)
    area = serializers.IntegerField(required=False)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    status = serializers.ChoiceField(
        choices=[('all', 'Todos'), ('present', 'Presente'), ('absent', 'Ausente'), ('late', 'Tarde')],
        required=False
    )

class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer para solicitar recuperación de contraseña"""
    email = serializers.EmailField()
    
    def validate_email(self, value):
        """Validar que el email existe y pertenece a un administrador"""
        try:
            user = User.objects.get(email=value, role='admin', is_active=True)
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "No se encontró una cuenta de administrador activa con este email."
            )

class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer para confirmar y cambiar la contraseña"""
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8, write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """Validar que las contraseñas coincidan"""
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Las contraseñas no coinciden.")
        return attrs
    
    def validate_token(self, value):
        """Validar que el token sea válido"""
        try:
            token_obj = PasswordResetToken.objects.get(token=value)
            if not token_obj.is_valid:
                raise serializers.ValidationError("El token ha expirado o ya ha sido usado.")
            return value
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError("Token inválido.")


class EmployeePasswordResetRequestSerializer(serializers.Serializer):
    """Serializer para solicitar recuperación de contraseña de empleados"""
    email = serializers.EmailField()
    
    def validate_email(self, value):
        """Validar que el email existe y pertenece a un empleado"""
        try:
            user = User.objects.get(email=value, role='employee', is_active=True)
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "No se encontró una cuenta de empleado activa con este email."
            )

class AreaScheduleSerializer(serializers.ModelSerializer):
    """Serializer para el horario de un área"""
    area_name = serializers.CharField(source='area.name', read_only=True)
    
    class Meta:
        model = AreaSchedule
        fields = [
            'id', 'area', 'area_name', 'schedule_type',
            'monday_start', 'monday_end', 'monday_active',
            'tuesday_start', 'tuesday_end', 'tuesday_active',
            'wednesday_start', 'wednesday_end', 'wednesday_active',
            'thursday_start', 'thursday_end', 'thursday_active',
            'friday_start', 'friday_end', 'friday_active',
            'saturday_start', 'saturday_end', 'saturday_active',
            'sunday_start', 'sunday_end', 'sunday_active',
            'grace_period_minutes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Validar que los horarios sean consistentes"""
        # Validar que si un día está activo, tenga horarios
        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
            active = data.get(f'{day}_active', False)
            start = data.get(f'{day}_start')
            end = data.get(f'{day}_end')
            
            if active and (start is None or end is None):
                raise serializers.ValidationError(
                    f"Si {day} está activo, debe tener hora de inicio y fin"
                )
            
            if start and end and start >= end:
                raise serializers.ValidationError(
                    f"La hora de inicio de {day} debe ser menor que la hora de fin"
                )
        
        return data

class AreaWithScheduleSerializer(serializers.ModelSerializer):
    """Serializer para área con su horario incluido"""
    schedule = AreaScheduleSerializer(read_only=True)
    schedule_id = serializers.IntegerField(source='schedule.id', read_only=True)
    has_schedule = serializers.SerializerMethodField()
    employee_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Area
        fields = [
            'id', 'name', 'description', 'latitude', 'longitude', 'radius', 'status',
            'schedule', 'schedule_id', 'has_schedule', 'employee_count', 'created_at', 'updated_at'
        ]
    
    def get_has_schedule(self, obj):
        """Verificar si el área tiene horario configurado"""
        return hasattr(obj, 'schedule')
    
    def to_representation(self, instance):
        """Incluir el schedule_type en la respuesta"""
        data = super().to_representation(instance)
        
        # Agregar información del schedule si existe
        try:
            if hasattr(instance, 'schedule') and instance.schedule:
                # ✅ INCLUIR schedule_type en el schedule
                if hasattr(instance.schedule, 'schedule_type'):
                    data['schedule']['schedule_type'] = instance.schedule.schedule_type
                else:
                    data['schedule']['schedule_type'] = 'default'  # Fallback
                
                data['schedule_id'] = instance.schedule.id
                data['has_schedule'] = True
            else:
                data['schedule'] = None
                data['schedule_id'] = None
                data['has_schedule'] = False
        except Exception as e:
            print(f"❌ Error obteniendo schedule en AreaWithScheduleSerializer: {e}")
            data['schedule'] = None
            data['schedule_id'] = None
            data['has_schedule'] = False
        
        return data
