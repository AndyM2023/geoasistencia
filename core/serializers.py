from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from .models import User, Employee, Area, Attendance

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
    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    email = serializers.EmailField(write_only=True, required=False)
    cedula = serializers.CharField(write_only=True, required=False)
    
    area_name = serializers.CharField(source='area.name', read_only=True)
    full_name = serializers.ReadOnlyField()
    email_display = serializers.ReadOnlyField(source='email')
    
    class Meta:
        model = Employee
        fields = [
            'id', 'user', 'user_id', 'employee_id', 'cedula', 'position', 'area', 'area_name',
            'hire_date', 'photo', 'full_name', 'email_display', 'created_at', 'updated_at',
            'first_name', 'last_name', 'email'  # Campos para crear usuario
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'full_name', 'email_display', 'area_name']
    
    def create(self, validated_data):
        """Crear empleado y usuario asociado con usuario y contraseña automáticos"""
        # Extraer datos del usuario
        first_name = validated_data.pop('first_name', '')
        last_name = validated_data.pop('last_name', '')
        email = validated_data.pop('email', '')
        cedula = validated_data.pop('cedula', '')
        
        # Si no se proporciona user_id, crear un nuevo usuario
        if 'user' not in validated_data:
            # Generar username automático: primera letra del nombre + apellido completo
            if first_name and last_name:
                # Tomar primera letra del primer nombre y apellido completo
                first_name_clean = first_name.strip().split()[0] if first_name.strip() else ''
                last_name_clean = last_name.strip().replace(' ', '') if last_name.strip() else ''
                
                if first_name_clean and last_name_clean:
                    username = f"{first_name_clean[0].lower()}{last_name_clean.lower()}"
                else:
                    username = f"user_{User.objects.count() + 1}"
            else:
                username = f"user_{User.objects.count() + 1}"
            
            # Asegurar username único
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
        
        # Asegurar que hire_date esté presente
        if 'hire_date' not in validated_data:
            from django.utils import timezone
            validated_data['hire_date'] = timezone.now().date()
        
        # Crear empleado
        employee = Employee.objects.create(**validated_data)
        return employee
    
    def update(self, instance, validated_data):
        """Actualizar empleado y usuario asociado"""
        # Extraer datos del usuario
        first_name = validated_data.pop('first_name', '')
        last_name = validated_data.pop('last_name', '')
        email = validated_data.pop('email', '')
        
        # Actualizar usuario si se proporcionan datos
        if first_name or last_name or email:
            user = instance.user
            if first_name:
                user.first_name = first_name
            if last_name:
                user.last_name = last_name
            if email:
                user.email = email
            user.save()
        
        # Actualizar empleado
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

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
