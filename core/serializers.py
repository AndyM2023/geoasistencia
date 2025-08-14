from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from .models import User, Employee, Area, Attendance

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Serializer para el modelo User"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'role', 'phone', 'is_active', 'created_at']
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
    
    area_name = serializers.CharField(source='area.name', read_only=True)
    full_name = serializers.ReadOnlyField()
    email_display = serializers.ReadOnlyField(source='email')
    
    class Meta:
        model = Employee
        fields = [
            'id', 'user', 'user_id', 'employee_id', 'position', 'area', 'area_name',
            'hire_date', 'photo', 'full_name', 'email_display', 'created_at', 'updated_at',
            'first_name', 'last_name', 'email'  # Campos para crear usuario
        ]
        read_only_fields = ['id', 'employee_id', 'created_at', 'updated_at', 'full_name', 'email_display', 'area_name']
    
    def create(self, validated_data):
        """Crear empleado y usuario asociado"""
        # Extraer datos del usuario
        first_name = validated_data.pop('first_name', '')
        last_name = validated_data.pop('last_name', '')
        email = validated_data.pop('email', '')
        
        # Si no se proporciona user_id, crear un nuevo usuario
        if 'user' not in validated_data:
            # Generar username único basado en email
            username = email.split('@')[0] if email else f"user_{User.objects.count() + 1}"
            
            # Asegurar username único
            counter = 1
            original_username = username
            while User.objects.filter(username=username).exists():
                username = f"{original_username}{counter}"
                counter += 1
            
            # Crear usuario
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                role='employee'
            )
            validated_data['user'] = user
        
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
            'face_verified', 'notes', 'hours_worked', 'created_at', 'updated_at'
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
    total_employees = serializers.IntegerField()
    total_areas = serializers.IntegerField()
    today_attendance = serializers.IntegerField()
    pending_attendance = serializers.IntegerField()
    recent_activities = serializers.ListField()

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
