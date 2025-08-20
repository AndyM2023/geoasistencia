from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from .models import User, Employee, Area, Attendance
from .models import PasswordResetToken
from .services.employee_welcome_service import EmployeeWelcomeService
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
    
    class Meta:
        model = Area
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'employee_count']
    
    def create(self, validated_data):
        """Crear área con estado activo por defecto"""
        # Si no se proporciona status, establecer como activo
        if 'status' not in validated_data:
            validated_data['status'] = 'active'
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Actualizar área con validación personalizada"""
        print(f"🔍 AreaSerializer.update() - Datos recibidos:")
        print(f"   - Instance ID: {instance.id}")
        print(f"   - Validated data: {validated_data}")
        
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
        
        # Actualizar la instancia
        return super().update(instance, validated_data)
    
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
    cedula = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True, max_length=20)
    
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
            validated_data['hire_date'] = timezone.now().date()
        
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

class LoginSerializer(serializers.Serializer):
    """Serializer para autenticación"""
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
