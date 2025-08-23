from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.utils import timezone
from datetime import date, timedelta
from .models import User, Employee, Area, Attendance, FaceProfile, PasswordResetToken, AreaSchedule
from .serializers import (
    UserSerializer, EmployeeSerializer, AreaSerializer, AttendanceSerializer,
    LoginSerializer, DashboardStatsSerializer, AttendanceReportSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    EmployeePasswordResetRequestSerializer, AreaScheduleSerializer, AreaWithScheduleSerializer
)
from .services.face_service_singleton import face_service_singleton
from .services.password_reset_service import PasswordResetService
from .services.employee_welcome_service import EmployeeWelcomeService

from rest_framework.views import APIView
from django.contrib.auth import update_session_auth_hash
import logging
from django.conf import settings
from rest_framework.permissions import IsAuthenticated

# Configurar logging para debugging
logger = logging.getLogger(__name__)

User = get_user_model()

class AuthViewSet(viewsets.ViewSet):
    """ViewSet para autenticación"""
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """Endpoint para login de usuarios - SOLO ADMINISTRADORES (Panel Admin)"""
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'token': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def employee_login(self, request):
        """Endpoint para login de empleados - USADO EN RECONOCIMIENTO FACIAL"""
        from .serializers import EmployeeLoginSerializer
        
        serializer = EmployeeLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'token': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Obtener información del usuario autenticado"""
        if request.user.is_authenticated:
            return Response(UserSerializer(request.user).data)
        return Response({'error': 'No autenticado'}, status=status.HTTP_401_UNAUTHORIZED)
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """Endpoint para registro de administradores"""
        try:
            data = request.data.copy()
            
            # Validaciones básicas
            required_fields = ['first_name', 'last_name', 'email', 'cedula', 'username', 'password', 'position']
            for field in required_fields:
                if not data.get(field):
                    return Response(
                        {'error': f'El campo {field} es requerido'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Verificar que no exista usuario con el mismo username
            if User.objects.filter(username=data['username']).exists():
                return Response(
                    {'error': 'Ya existe un usuario con ese nombre de usuario'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Verificar que no exista usuario con el mismo email
            if User.objects.filter(email=data['email']).exists():
                return Response(
                    {'error': 'Ya existe un usuario con ese email'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Verificar que no exista usuario con la misma cédula
            if User.objects.filter(cedula=data['cedula']).exists():
                return Response(
                    {'error': 'Ya existe un usuario con esa cédula'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Crear el usuario administrador
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                cedula=data['cedula'],
                position=data['position'],
                password=data['password'],
                role='admin',
                is_active=True
            )
            
            return Response({
                'message': 'Administrador registrado exitosamente',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'Error durante el registro: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class DashboardViewSet(viewsets.ViewSet):
    """ViewSet para estadísticas del dashboard"""
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Obtener estadísticas del dashboard"""
        today = timezone.now().date()
        
        # Contar empleados
        total_employees = Employee.objects.count()
        
        # Contar áreas activas
        total_areas = Area.objects.filter(status='active').count()
        
        # Asistencias de hoy
        today_attendance = Attendance.objects.filter(date=today).count()
        
        # Empleados pendientes (sin asistencia hoy)
        pending_attendance = total_employees - today_attendance
        
        # Calcular tasa de asistencia del mes actual
        current_month = timezone.now().month
        current_year = timezone.now().year
        month_attendance = Attendance.objects.filter(
            date__month=current_month,
            date__year=current_year
        ).count()
        
        # Total de días laborables en el mes (aproximado)
        from calendar import monthrange
        _, days_in_month = monthrange(current_year, current_month)
        # Asumir 22 días laborables por mes (excluyendo fines de semana)
        working_days = min(22, days_in_month)
        total_possible_attendance = total_employees * working_days
        
        attendance_rate = 0
        if total_possible_attendance > 0:
            attendance_rate = round((month_attendance / total_possible_attendance) * 100, 1)
        
        stats = {
            'totalEmployees': total_employees,
            'totalAreas': total_areas,
            'activeAreas': total_areas,
            'todayAttendance': today_attendance,
            'pendingAttendance': pending_attendance,
            'attendanceRate': attendance_rate,
            'monthAttendance': month_attendance,
            'workingDays': working_days
        }
        
        serializer = DashboardStatsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def weekly_attendance(self, request):
        """Obtener datos de asistencia semanal para gráficos"""
        from datetime import timedelta
        
        # Obtener fecha de hace 7 días
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=6)
        
        # Generar lista de fechas de la semana
        dates = []
        current_date = start_date
        while current_date <= end_date:
            dates.append(current_date)
            current_date += timedelta(days=1)
        
        # Obtener datos de asistencia para cada día
        weekly_data = []
        for date in dates:
            attendance_count = Attendance.objects.filter(date=date).count()
            total_employees = Employee.objects.count()
            
            weekly_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'day': date.strftime('%A'),  # Nombre del día
                'shortDay': date.strftime('%a'),  # Día abreviado
                'attendance': attendance_count,
                'total': total_employees,
                'percentage': round((attendance_count / total_employees * 100) if total_employees > 0 else 0, 1)
            })
        
        return Response({
            'weeklyData': weekly_data,
            'startDate': start_date.strftime('%Y-%m-%d'),
            'endDate': end_date.strftime('%Y-%m-%d')
        })
    
    @action(detail=False, methods=['get'])
    def recent_activity(self, request):
        """Obtener actividad reciente del sistema"""
        from datetime import datetime, timedelta
        
        # Obtener actividades de las últimas 24 horas
        yesterday = timezone.now() - timedelta(days=1)
        
        # Asistencias recientes
        recent_attendances = Attendance.objects.select_related(
            'employee__user', 'area'
        ).filter(
            created_at__gte=yesterday
        ).order_by('-created_at')[:10]
        
        activities = []
        
        for attendance in recent_attendances:
            # Calcular tiempo transcurrido
            time_diff = timezone.now() - attendance.created_at
            
            if time_diff.days > 0:
                time_text = f"Hace {time_diff.days} día{'s' if time_diff.days > 1 else ''}"
            elif time_diff.seconds > 3600:
                hours = time_diff.seconds // 3600
                time_text = f"Hace {hours} hora{'s' if hours > 1 else ''}"
            elif time_diff.seconds > 60:
                minutes = time_diff.seconds // 60
                time_text = f"Hace {minutes} minuto{'s' if minutes > 1 else ''}"
            else:
                time_text = "Hace un momento"
            
            # Determinar tipo de actividad
            if attendance.check_in and not attendance.check_out:
                activity_type = "check_in"
                title = f"{attendance.employee.full_name} marcó entrada"
                icon = "mdi-login"
                color = "success"
                status = "Entrada"
            elif attendance.check_out:
                activity_type = "check_out"
                title = f"{attendance.employee.full_name} marcó salida"
                icon = "mdi-logout"
                color = "info"
                status = "Salida"
            else:
                activity_type = "other"
                title = f"{attendance.employee.full_name} - Actividad registrada"
                icon = "mdi-clock"
                color = "warning"
                status = "Registrado"
            
            activities.append({
                'id': attendance.id,
                'type': activity_type,
                'title': title,
                'time': time_text,
                'icon': icon,
                'color': color,
                'status': status,
                'employee': attendance.employee.full_name,
                'area': attendance.area.name if attendance.area else 'Sin área',
                'timestamp': attendance.created_at.isoformat()
            })
        
        # Si no hay actividades recientes, crear algunas de ejemplo
        if not activities:
            activities = [
                {
                    'id': 'demo-1',
                    'type': 'demo',
                    'title': 'Sistema iniciado correctamente',
                    'time': 'Hace 1 hora',
                    'icon': 'mdi-check-circle',
                    'color': 'success',
                    'status': 'Sistema',
                    'employee': 'Sistema',
                    'area': 'General',
                    'timestamp': timezone.now().isoformat()
                }
            ]
        
        return Response({
            'activities': activities,
            'total': len(activities),
            'lastUpdate': timezone.now().isoformat()
        })

class EmployeeViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de empleados"""
    queryset = Employee.objects.select_related('user', 'area').all()
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def update(self, request, *args, **kwargs):
        """Override update method to add debugging"""
        print(f"\n🔍 EmployeeViewSet.update() - Request data:")
        print(f"   - Method: {request.method}")
        print(f"   - URL: {request.path}")
        print(f"   - Data keys: {list(request.data.keys())}")
        print(f"   - Data: {request.data}")
        print(f"   - Content-Type: {request.content_type}")
        
        try:
            response = super().update(request, *args, **kwargs)
            print(f"✅ Update successful: {response.status_code}")
            return response
        except Exception as e:
            print(f"❌ Update failed with error: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def get_queryset(self):
        # Por defecto, solo mostrar empleados activos
        queryset = Employee.objects.select_related('user', 'area').filter(user__is_active=True)
        
        # Filtros
        search = self.request.query_params.get('search', None)
        area = self.request.query_params.get('area', None)
        status_param = self.request.query_params.get('status', None)
        
        # Permitir ver empleados inactivos si se especifica
        if status_param == 'all':
            queryset = Employee.objects.select_related('user', 'area').all()
        elif status_param == 'inactive':
            queryset = Employee.objects.select_related('user', 'area').filter(user__is_active=False)
        
        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(employee_id__icontains=search) |
                Q(user__email__icontains=search)
            )
        
        if area:
            queryset = queryset.filter(area_id=area)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def register_face(self, request, pk=None):
        """Registrar rostro de empleado"""
        print(f"\n🎯 ========== INICIO REGISTRO FACIAL ==========")
        print(f"🆔 Employee ID: {pk}")
        print(f"📤 Request method: {request.method}")
        print(f"📊 Request data keys: {list(request.data.keys())}")
        print(f"📝 Content-Type: {request.content_type}")
        employee = self.get_object()
        
        print(f"🔍 REGISTER_FACE - Datos recibidos:")
        print(f"   - Employee ID: {employee.id}")
        print(f"   - Request data keys: {list(request.data.keys())}")
        print(f"   - Request data completo: {request.data}")
        
        # Verificar diferentes posibles nombres de campo
        photos_base64 = request.data.get('photos_base64', [])
        if not photos_base64:
            photos_base64 = request.data.get('photos', [])
        
        print(f"   - photos_base64 type: {type(photos_base64)}")
        print(f"   - photos_base64 length: {len(photos_base64) if photos_base64 else 0}")
        
        if photos_base64:
            print(f"   - Primera foto sample: {str(photos_base64[0])[:100]}...")
        
        if not photos_base64:
            print("❌ No se recibieron fotos")
            print("❌ Campos disponibles en request.data:")
            for key, value in request.data.items():
                print(f"   - {key}: {type(value)} - {len(value) if hasattr(value, '__len__') else 'N/A'}")
            return Response(
                {'error': 'Se requieren fotos para el registro'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        print(f"✅ Fotos recibidas: {len(photos_base64)}")
        
        # 🔍 DEBUG: Verificar estado del servicio facial ANTES de llamarlo
        print(f"\n🔍 DEBUG: VERIFICANDO SERVICIO FACIAL ANTES DE LLAMARLO")
        try:
            from core.services.face_service_singleton import face_service_singleton
            service = face_service_singleton.get_service()
            print(f"   - Service instance: {service}")
            print(f"   - Service type: {type(service)}")
            print(f"   - facial_system: {service.facial_system}")
            print(f"   - facial_system type: {type(service.facial_system)}")
            print(f"   - facial_system is None: {service.facial_system is None}")
            print(f"   - facial_system bool evaluation: {bool(service.facial_system)}")
            
            if service.facial_system:
                print(f"   - facial_system methods: {[m for m in dir(service.facial_system) if not m.startswith('_')]}")
                print(f"   - facial_system base_dir: {getattr(service.facial_system, 'base_dir', 'N/A')}")
                print(f"   - facial_system face_dir: {getattr(service.facial_system, 'face_dir', 'N/A')}")
            else:
                print("   ❌ facial_system es None o False")
                
        except Exception as e:
            print(f"   ❌ Error verificando servicio facial: {e}")
            import traceback
            traceback.print_exc()
        
        try:
            print(f"🚀 Llamando a face_service.register_face...")
            print(f"   - Employee: {employee.full_name}")
            print(f"   - Photos count: {len(photos_base64)}")
            print(f"   - Tipo de photos_base64: {type(photos_base64)}")
            print(f"   - Primera foto tipo: {type(photos_base64[0]) if photos_base64 else 'N/A'}")
            
            # Verificar estructura de datos
            if photos_base64 and len(photos_base64) > 0:
                first_photo = photos_base64[0]
                print(f"   - Primera foto keys: {list(first_photo.keys()) if isinstance(first_photo, dict) else 'No es dict'}")
                if isinstance(first_photo, dict) and 'photo' in first_photo:
                    print(f"   - Primera foto photo length: {len(first_photo['photo'])}")
            
            result = face_service_singleton.register_face(employee, photos_base64)
            
            print(f"📊 Resultado del face_service:")
            print(f"   - Success: {result.get('success')}")
            print(f"   - Message: {result.get('message')}")
            print(f"   - Photos count: {result.get('photos_count')}")
            print(f"   - Result completo: {result}")
            
            if result.get('success'):
                print("✅ Registro facial exitoso")
                
                # Enviar email de bienvenida con credenciales
                try:
                    # Obtener credenciales del usuario
                    username = employee.user.username
                    password = None
                    
                    # Intentar obtener la contraseña (si está disponible)
                    if hasattr(employee.user, 'cedula') and employee.user.cedula:
                        # Usar la cédula como contraseña por defecto
                        password = employee.user.cedula
                    else:
                        password = f"pass{employee.user.id}"
                    
                    # Enviar email de bienvenida completo
                    EmployeeWelcomeService.send_welcome_email(employee, username, password)
                    print(f"✅ Email de bienvenida enviado a {employee.user.email}")
                    
                except Exception as email_error:
                    print(f"⚠️ ADVERTENCIA: No se pudo enviar email de bienvenida: {email_error}")
                    # No fallar el registro facial si el email falla
                
                print("📧 Enviando respuesta 201")
                return Response({
                    'success': True,
                    'message': result['message'],
                    'photos_count': result['photos_count'],
                    'employee_id': employee.id
                }, status=status.HTTP_201_CREATED)
            else:
                print(f"❌ Registro facial falló, enviando respuesta 400")
                error_message = result.get('error') or result.get('message') or 'Error desconocido'
                print(f"   - Error message: {error_message}")
                return Response({
                    'success': False,
                    'message': error_message
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            print(f"❌ Error en register_face: {e}")
            import traceback
            traceback.print_exc()
            return Response({
                'success': False,
                'message': f'Error interno: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def face_status(self, request, pk=None):
        """Obtener estado del perfil facial del empleado"""
        employee = self.get_object()
        status_data = face_service_singleton.get_employee_face_status(employee)
        
        return Response(status_data)
    
    @action(detail=True, methods=['post'])
    def verify_face(self, request, pk=None):
        """Verificar rostro para asistencia"""
        employee = self.get_object()
        photo = request.data.get('photo')
        
        if not photo:
            return Response(
                {'error': 'Se requiere una foto para verificación'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = face_service_singleton.verify_face(employee, photo)
        
        return Response(result)
    
    def destroy(self, request, pk=None):
        """Soft delete: Desactivar empleado en lugar de eliminarlo"""
        employee = self.get_object()
        
        # Desactivar usuario asociado (soft delete)
        employee.user.is_active = False
        employee.user.save()
        
        return Response(
            {'message': f'Empleado {employee.full_name} desactivado correctamente'}, 
            status=status.HTTP_204_NO_CONTENT
        )
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Reactivar empleado desactivado"""
        # Buscar empleado incluyendo inactivos
        try:
            employee = Employee.objects.select_related('user', 'area').get(pk=pk)
        except Employee.DoesNotExist:
            return Response(
                {'error': 'Empleado no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Reactivar usuario
        employee.user.is_active = True
        employee.user.save()
        
        return Response(
            {'message': f'Empleado {employee.full_name} reactivado correctamente'}, 
            status=status.HTTP_200_OK
        )

class AreaViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de áreas"""
    queryset = Area.objects.all()
    permission_classes = [permissions.AllowAny]  # TEMPORAL: Permitir sin autenticación para pruebas
    
    def get_serializer_class(self):
        """Usar AreaSerializer para crear/actualizar y AreaWithScheduleSerializer para listar"""
        if self.action in ['create', 'update', 'partial_update']:
            print(f"🔍 AreaViewSet usando AreaSerializer para {self.action}")
            return AreaSerializer
        else:
            print(f"🔍 AreaViewSet usando AreaWithScheduleSerializer para {self.action}")
            return AreaWithScheduleSerializer
    
    def update(self, request, *args, **kwargs):
        """Actualizar área con logging detallado"""
        print(f"🔍 AreaViewSet.update() - Request recibido:")
        print(f"   - Method: {request.method}")
        print(f"   - URL: {request.path}")
        print(f"   - Data: {request.data}")
        print(f"   - Content-Type: {request.content_type}")
        print(f"   - Data keys: {list(request.data.keys()) if hasattr(request.data, 'keys') else 'No keys'}")
        if 'schedule' in request.data:
            print(f"   - Schedule en request.data: {request.data['schedule']}")
            print(f"   - Schedule tipo: {type(request.data['schedule'])}")
            if isinstance(request.data['schedule'], dict):
                print(f"   - Schedule keys: {list(request.data['schedule'].keys())}")
                print(f"   - monday_start en request: {request.data['schedule'].get('monday_start')}")
                print(f"   - monday_end en request: {request.data['schedule'].get('monday_end')}")
                print(f"   - monday_active en request: {request.data['schedule'].get('monday_active')}")
        
        try:
            response = super().update(request, *args, **kwargs)
            print(f"✅ Área actualizada exitosamente")
            return response
        except Exception as e:
            print(f"❌ Error en AreaViewSet.update(): {e}")
            print(f"   - Tipo de error: {type(e).__name__}")
            print(f"   - Mensaje: {str(e)}")
            raise
    
    def get_queryset(self):
        queryset = Area.objects.all()
        
        # Filtros
        search = self.request.query_params.get('search', None)
        status = self.request.query_params.get('status', None)
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
        
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset
    
    def destroy(self, request, *args, **kwargs):
        """Soft delete: Desactivar área en lugar de eliminarla físicamente"""
        area = self.get_object()
        area.deactivate()
        
        return Response(
            {'message': f'Área {area.name} desactivada correctamente'}, 
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Reactivar área desactivada"""
        try:
            area = Area.objects.get(pk=pk)
            area.activate()
            
            return Response(
                {'message': f'Área {area.name} reactivada correctamente'}, 
                status=status.HTTP_200_OK
            )
        except Area.DoesNotExist:
            return Response(
                {'error': 'Área no encontrada'}, 
                status=status.HTTP_404_NOT_FOUND
            )

class AttendanceViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de asistencias"""
    queryset = Attendance.objects.select_related('employee__user', 'area').all()
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Attendance.objects.select_related('employee__user', 'area').all()
        
        # Filtros - aceptar tanto employee/area como employee_id/area_id
        employee = self.request.query_params.get('employee_id') or self.request.query_params.get('employee')
        area = self.request.query_params.get('area_id') or self.request.query_params.get('area')
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        status = self.request.query_params.get('status', None)
        
        print(f"🔍 FILTROS RECIBIDOS:")
        print(f"   - employee: {employee}")
        print(f"   - area: {area}")
        print(f"   - date_from: {date_from}")
        print(f"   - date_to: {date_to}")
        print(f"   - status: {status}")
        
        if employee:
            queryset = queryset.filter(employee_id=employee)
            print(f"✅ Filtro por empleado aplicado: employee_id={employee}")
        
        if area:
            queryset = queryset.filter(area_id=area)
            print(f"✅ Filtro por área aplicado: area_id={area}")
        
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
            print(f"✅ Filtro por fecha desde aplicado: {date_from}")
        
        if date_to:
            # Para incluir el día completo, usar date__lt del día siguiente
            from datetime import datetime, timedelta
            try:
                # Convertir la fecha a datetime y agregar 1 día
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                next_day = date_to_obj + timedelta(days=1)
                
                print(f"🔍 DEBUG FECHA HASTA:")
                print(f"   - Fecha original: {date_to}")
                print(f"   - Fecha convertida: {date_to_obj}")
                print(f"   - Día siguiente: {next_day}")
                print(f"   - Filtro aplicado: date__lt={next_day}")
                
                queryset = queryset.filter(date__lt=next_day)
                print(f"✅ Filtro por fecha hasta aplicado: {date_to} (incluye día completo hasta {next_day})")
                
                # Verificar registros después del filtro
                print(f"📊 Registros después del filtro fecha hasta: {queryset.count()}")
                
            except ValueError as e:
                # Si hay error en el formato, usar el filtro original
                print(f"⚠️ Error en formato de fecha: {e}")
                queryset = queryset.filter(date__lte=date_to)
                print(f"✅ Filtro por fecha hasta aplicado (fallback): {date_to}")
        
        if status and status != 'all':
            queryset = queryset.filter(status=status)
            print(f"✅ Filtro por estado aplicado: {status}")
        
        print(f"📊 Total de registros después de filtros: {queryset.count()}")
        
        # DEBUG: Mostrar fechas disponibles en los registros filtrados
        if queryset.count() > 0:
            print(f"🔍 FECHAS DISPONIBLES EN RESULTADOS:")
            dates_in_results = queryset.values_list('date', flat=True).distinct().order_by('date')
            for date_obj in dates_in_results:
                print(f"   - {date_obj}")
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def mark_attendance(self, request):
        """Marcar asistencia de un empleado"""
        try:
            # Obtener datos del request
            employee_id = request.data.get('employee_id')
            area_id = request.data.get('area_id')
            face_verified = request.data.get('face_verified', False)
            latitude = request.data.get('latitude')
            longitude = request.data.get('longitude')
            
            print(f"🔍 MARK_ATTENDANCE - Datos recibidos:")
            print(f"   - employee_id: {employee_id}")
            print(f"   - area_id: {area_id}")
            print(f"   - face_verified: {face_verified}")
            print(f"   - latitude: {latitude}")
            print(f"   - longitude: {longitude}")
            
            # Validar datos requeridos
            if not employee_id or not area_id:
                return Response({
                    'success': False,
                    'message': 'Se requiere employee_id y area_id',
                    'error_type': 'missing_required_fields'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Obtener empleado y área
            try:
                employee = Employee.objects.get(id=employee_id)
                area = Area.objects.get(id=area_id)
                print(f"✅ Empleado y área encontrados:")
                print(f"   - Empleado: {employee.full_name}")
                print(f"   - Área: {area.name}")
            except (Employee.DoesNotExist, Area.DoesNotExist) as e:
                print(f"❌ Error: {e}")
                return Response(
                    {'error': 'Empleado o área no encontrada'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Validar ubicación si se proporciona
            distance_meters = None
            if latitude and longitude:
                print(f"📍 Validando ubicación del empleado...")
                print(f"   - Coordenadas empleado: {latitude}, {longitude}")
                print(f"   - Coordenadas área: {area.latitude}, {area.longitude}")
                print(f"   - Radio del área: {area.radius}m")
                
                # Calcular distancia usando la fórmula de Haversine
                from math import radians, cos, sin, asin, sqrt
                
                lat1, lon1 = float(area.latitude), float(area.longitude)
                lat2, lon2 = float(latitude), float(longitude)
                
                # Convertir a radianes
                lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
                
                # Diferencias
                dlat = lat2 - lat1
                dlon = lon2 - lon1
                
                # Fórmula de Haversine
                a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
                c = 2 * asin(sqrt(a))
                r = 6371000  # Radio de la Tierra en metros
                distance_meters = c * r
                
                print(f"   - Distancia calculada: {distance_meters:.2f} metros")
                
                # Verificar si está dentro del radio del área
                if distance_meters > area.radius:
                    print(f"❌ EMPLEADO FUERA DEL ÁREA: Distancia {distance_meters:.2f}m > Radio {area.radius}m")
                    return Response({
                        'success': False,
                        'message': f'No puedes marcar asistencia desde esta ubicación. Debes estar en el área "{area.name}" (máximo {area.radius}m del centro).',
                        'error_type': 'location_out_of_range',
                        'distance_meters': round(distance_meters, 2),
                        'area_radius': area.radius,
                        'area_name': area.name
                    }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    print(f"✅ UBICACIÓN VÁLIDA: Empleado dentro del área (distancia: {distance_meters:.2f}m)")
            else:
                print(f"⚠️ ADVERTENCIA: No se recibieron coordenadas de ubicación")
                return Response({
                    'success': False,
                    'message': 'No se pudo obtener tu ubicación. Asegúrate de permitir el acceso a la ubicación en tu navegador.',
                    'error_type': 'location_not_available'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verificar si ya tiene asistencia hoy
            today = timezone.now().date()
            current_time = timezone.now().time()
            print(f"📅 Fecha actual: {today}")
            print(f"🕐 Hora actual: {current_time}")
            
            # Obtener horarios esperados del área
            from core.services.schedule_service import ScheduleService
            expected_check_in, expected_check_out = ScheduleService.get_expected_times(area, today)
            grace_period = ScheduleService.get_grace_period(area)
            
            print(f"⏰ Horarios esperados del área:")
            print(f"   - Hora entrada esperada: {expected_check_in}")
            print(f"   - Hora salida esperada: {expected_check_out}")
            print(f"   - Período de gracia: {grace_period} minutos")
            
            # Validar si es un día laboral
            if not ScheduleService.is_work_day(area, today):
                print(f"❌ NO ES DÍA LABORAL para el área {area.name}")
                return Response({
                    'success': False,
                    'message': f'Hoy no es un día laboral para el área "{area.name}". No puedes marcar asistencia.',
                    'error_type': 'not_work_day',
                    'area_name': area.name
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verificar si ya tiene asistencia hoy
            try:
                attendance = Attendance.objects.get(employee=employee, date=today)
                print(f"🔄 Asistencia existente encontrada para {employee.full_name}")
                print(f"   - Entrada: {attendance.check_in}")
                print(f"   - Salida: {attendance.check_out}")
                
                # Si ya tiene entrada y salida, no permitir más registros
                if attendance.check_in and attendance.check_out:
                    print(f"ℹ️ Empleado ya tiene entrada y salida registradas para hoy")
                    message = f"{employee.full_name} ya tiene entrada y salida registradas para hoy"
                    action_type = "completo"
                    
                    return Response({
                        'success': False,
                        'message': message,
                        'action_type': action_type,
                        'check_in': attendance.check_in,
                        'check_out': attendance.check_out,
                        'employee_name': employee.full_name,
                        'error_type': 'already_complete'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Si solo tiene entrada, registrar salida
                if attendance.check_in and not attendance.check_out:
                    # TEMPORALMENTE DESHABILITADO: Validación de tiempo mínimo de trabajo
                    # if expected_check_out and current_time < expected_check_out:
                    #     # Calcular tiempo mínimo de trabajo (ej: 1 hora)
                    #     from datetime import datetime, timedelta
                    #     min_work_time = timedelta(hours=1)
                    #     check_in_datetime = datetime.combine(today, attendance.check_in)
                    #     current_datetime = datetime.combine(today, current_time)
                    #     work_duration = current_datetime - check_in_datetime
                    #     
                    #     if work_duration < min_work_time:
                    #         print(f"❌ TIEMPO DE TRABAJO INSUFICIENTE: {work_duration}")
                    #         return Response({
                    #             'success': False,
                    #             'message': f'Debes trabajar al menos 1 hora antes de marcar salida. Tiempo actual: {work_duration}',
                    #             'error_type': 'insufficient_work_time',
                    #             'work_duration': str(work_duration),
                    #             'min_required': '1 hora'
                    #         }, status=status.HTTP_400_BAD_REQUEST)
                    
                    # Marcar salida
                    attendance.check_out = current_time
                    attendance.save()
                    print(f"⏰ Hora de salida actualizada: {attendance.check_out}")
                    message = f"Salida registrada exitosamente para {employee.full_name}"
                    action_type = "salida"
                    
                else:
                    # No debería llegar aquí, pero por seguridad
                    print(f"⚠️ Estado inconsistente de asistencia")
                    return Response({
                        'success': False,
                        'message': 'Estado inconsistente de asistencia. Contacta al administrador.',
                        'error_type': 'inconsistent_state'
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
            except Attendance.DoesNotExist:
                # Nueva asistencia - validar horarios antes de permitir entrada
                print(f"🆕 Creando nueva asistencia para {employee.full_name}")
                
                if expected_check_in and expected_check_out:
                    # Validar que no sea muy tarde para marcar entrada
                    from datetime import datetime, timedelta
                    
                    # Calcular hora límite con tolerancia
                    limit_time = datetime.combine(today, expected_check_in)
                    limit_time = limit_time + timedelta(minutes=grace_period)
                    limit_time = limit_time.time()
                    
                    print(f"🕐 Validación de horarios:")
                    print(f"   - Hora entrada esperada: {expected_check_in}")
                    print(f"   - Hora límite con tolerancia: {limit_time}")
                    print(f"   - Hora actual: {current_time}")
                    
                    # Si es muy tarde para marcar entrada
                    if current_time > expected_check_out:
                        print(f"❌ MUY TARDE PARA ENTRADA: Hora actual {current_time} > Hora salida {expected_check_out}")
                        return Response({
                            'success': False,
                            'message': f'Ya pasó la hora de salida ({expected_check_out.strftime("%H:%M")}). No puedes marcar entrada ahora.',
                            'error_type': 'too_late_for_entry',
                            'expected_check_out': expected_check_out.strftime("%H:%M"),
                            'current_time': current_time.strftime("%H:%M")
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    # Si es tarde pero dentro del horario laboral
                    elif current_time > limit_time:
                        print(f"⚠️ LLEGADA TARDE: Hora actual {current_time} > Hora límite {limit_time}")
                        initial_status = 'late'
                        message = f"Entrada registrada con tardanza para {employee.full_name}"
                    else:
                        print(f"✅ A TIEMPO: Hora actual {current_time} <= Hora límite {limit_time}")
                        initial_status = 'present'
                        message = f"Entrada registrada exitosamente para {employee.full_name}"
                else:
                    # Sin horario definido, marcar como presente
                    print(f"ℹ️ Sin horario definido para el área, marcando como presente")
                    initial_status = 'present'
                    message = f"Entrada registrada exitosamente para {employee.full_name}"
                
                # Crear nueva asistencia
                attendance = Attendance.objects.create(
                    employee=employee,
                    date=today,
                    area=area,
                    check_in=current_time,
                    status=initial_status,
                    latitude=latitude,
                    longitude=longitude,
                    face_verified=face_verified,
                    expected_check_in=expected_check_in,
                    expected_check_out=expected_check_out
                )
                
                print(f"✅ NUEVA asistencia creada para {employee.full_name}")
                print(f"   - Status inicial: {initial_status}")
                print(f"   - Hora entrada: {attendance.check_in}")
                action_type = "entrada"
            
            # Actualizar estado basado en horarios (por si cambió algo)
            attendance.update_status_based_on_schedule()
            attendance.save()
            
            print(f"📊 Asistencia final: {attendance}")
            print(f"   - Status final: {attendance.status}")
            print(f"   - Es tarde: {attendance.is_late}")
            
            serializer = AttendanceSerializer(attendance)
            
            # Crear respuesta personalizada
            response_data = {
                'attendance': serializer.data,
                'message': message,
                'location_info': {
                    'employee_lat': float(latitude),
                    'employee_lng': float(longitude),
                    'area_lat': float(area.latitude),
                    'area_lng': float(area.longitude),
                    'area_radius': area.radius,
                    'distance_meters': round(distance_meters, 2) if distance_meters else None
                },
                'action_type': action_type,
                'check_in': attendance.check_in,
                'check_out': attendance.check_out,
                'employee_name': employee.full_name,
                'status': attendance.status,
                'status_display': attendance.get_status_display(),
                'is_late': attendance.is_late,
                'expected_check_in': attendance.expected_check_in,
                'expected_check_out': attendance.expected_check_out
            }
            
            print(f"🎯 RESPUESTA COMPLETA que se envía al frontend:")
            print(f"   - action_type: {action_type}")
            print(f"   - employee_name: {employee.full_name}")
            print(f"   - message: {message}")
            print(f"   - status: {attendance.status}")
            print(f"   - is_late: {attendance.is_late}")
            print(f"   - response_data keys: {list(response_data.keys())}")
            
            return Response(response_data)
            
        except (Employee.DoesNotExist, Area.DoesNotExist) as e:
            print(f"❌ Error: {e}")
            return Response(
                {'error': 'Empleado o área no encontrada'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            import traceback
            traceback.print_exc()
            return Response(
                {'error': f'Error interno: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def report(self, request):
        """Generar reporte de asistencias"""
        serializer = AttendanceReportSerializer(data=request.query_params)
        if serializer.is_valid():
            queryset = self.get_queryset()
            
            # Aplicar filtros del serializer
            data = serializer.validated_data
            
            if data.get('employee'):
                queryset = queryset.filter(employee_id=data['employee'])
            
            if data.get('area'):
                queryset = queryset.filter(area_id=data['area'])
            
            if data.get('date_from'):
                queryset = queryset.filter(date__gte=data['date_from'])
            
            if data.get('date_to'):
                queryset = queryset.filter(date__lte=data['date_to'])
            
            if data.get('status') and data['status'] != 'all':
                queryset = queryset.filter(status=data['status'])
            
            # Serializar resultados
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = AttendanceSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = AttendanceSerializer(queryset, many=True)
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ============================================================================
# VISTAS PARA GESTIÓN DE HORARIOS DE ÁREAS
# ============================================================================

class AreaScheduleViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar horarios de áreas"""
    queryset = AreaSchedule.objects.all()
    serializer_class = AreaScheduleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtrar por área si se especifica"""
        queryset = AreaSchedule.objects.all()
        area_id = self.request.query_params.get('area_id', None)
        if area_id:
            queryset = queryset.filter(area_id=area_id)
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Crear horario para un área"""
        try:
            # Verificar que el área existe
            area_id = request.data.get('area')
            if not area_id:
                return Response(
                    {'error': 'Se debe especificar un área'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Verificar que no exista ya un horario para esta área
            if AreaSchedule.objects.filter(area_id=area_id).exists():
                return Response(
                    {'error': 'Esta área ya tiene un horario configurado'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            
            return Response({
                'message': 'Horario creado exitosamente',
                'schedule': serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'Error al crear horario: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def update(self, request, *args, **kwargs):
        """Actualizar horario existente"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            
            return Response({
                'message': 'Horario actualizado exitosamente',
                'schedule': serializer.data
            })
            
        except Exception as e:
            return Response(
                {'error': f'Error al actualizar horario: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def create_default(self, request, pk=None):
        """Crear horario por defecto para un área"""
        try:
            area = Area.objects.get(pk=pk)
            
            # Verificar que no tenga horario ya
            if hasattr(area, 'schedule'):
                return Response(
                    {'error': 'Esta área ya tiene un horario configurado'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Crear horario por defecto
            from core.services.schedule_service import ScheduleService
            schedule = ScheduleService.create_default_schedule(area)
            
            serializer = self.get_serializer(schedule)
            return Response({
                'message': 'Horario por defecto creado exitosamente',
                'schedule': serializer.data
            })
            
        except Area.DoesNotExist:
            return Response(
                {'error': 'Área no encontrada'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error al crear horario por defecto: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ============================================================================
# VISTA PARA CAMBIO DE CONTRASEÑA
# ============================================================================

class ChangePasswordView(APIView):
    """
    Vista para cambiar la contraseña del usuario autenticado.
    Requiere autenticación y valida la contraseña actual.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            logger.info(f"🔐 Cambio de contraseña solicitado para usuario: {request.user.username}")
            
            # Obtener datos del request
            current_password = request.data.get('current_password')
            new_password = request.data.get('new_password')
            
            logger.info(f"🔍 Datos recibidos - current_password: {'***' if current_password else 'vacío'}, new_password: {'***' if new_password else 'vacío'}")
            
            # Validar que se proporcionen ambos campos
            if not current_password or not new_password:
                logger.warning("⚠️ Campos de contraseña faltantes")
                return Response(
                    {
                        'error': 'Se requieren tanto la contraseña actual como la nueva',
                        'detail': 'Ambos campos current_password y new_password son obligatorios'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validar contraseña actual
            if not request.user.check_password(current_password):
                logger.warning(f"⚠️ Contraseña actual incorrecta para usuario: {request.user.username}")
                return Response(
                    {
                        'current_password': ['La contraseña actual es incorrecta'],
                        'detail': 'La contraseña actual proporcionada no coincide con la registrada'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validar nueva contraseña (mínimo 8 caracteres)
            if len(new_password) < 8:
                logger.warning(f"⚠️ Nueva contraseña muy corta para usuario: {request.user.username}")
                return Response(
                    {
                        'new_password': ['La contraseña debe tener al menos 8 caracteres'],
                        'detail': 'La nueva contraseña no cumple con los requisitos mínimos de seguridad'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validar que la nueva contraseña sea diferente a la actual
            if current_password == new_password:
                logger.warning(f"⚠️ Nueva contraseña igual a la actual para usuario: {request.user.username}")
                return Response(
                    {
                        'new_password': ['La nueva contraseña debe ser diferente a la actual'],
                        'detail': 'No puedes usar la misma contraseña'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Cambiar contraseña
            logger.info(f"🔄 Cambiando contraseña para usuario: {request.user.username}")
            request.user.set_password(new_password)
            request.user.save()
            
            # Actualizar sesión para evitar logout automático
            update_session_auth_hash(request, request.user)
            
            logger.info(f"✅ Contraseña cambiada exitosamente para usuario: {request.user.username}")
            
            return Response({
                'message': 'Contraseña cambiada exitosamente',
                'success': True,
                'detail': 'Tu contraseña ha sido actualizada. La sesión se mantendrá activa.'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"❌ Error inesperado cambiando contraseña: {str(e)}")
            return Response(
                {
                    'error': 'Error interno del servidor',
                    'detail': 'Ocurrió un error inesperado al cambiar la contraseña'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PasswordResetViewSet(viewsets.ViewSet):
    """ViewSet para recuperación de contraseña del administrador"""
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=['post'])
    def request_reset(self, request):
        """Solicitar recuperación de contraseña"""
        print(f"\n🔍 === DEBUG COMPLETO DE REQUEST_RESET ===")
        print(f"🔍 Timestamp: {timezone.now()}")
        print(f"🔍 Método: {request.method}")
        print(f"🔍 URL: {request.path}")
        print(f"🔍 Headers: {dict(request.headers)}")
        print(f"🔍 Content-Type: {request.content_type}")
        print(f"🔍 Datos recibidos: {request.data}")
        print(f"🔍 Query params: {request.query_params}")
        print(f"🔍 User: {request.user}")
        
        try:
            print(f"\n🔍 PASO 1: Validando serializer...")
            serializer = PasswordResetRequestSerializer(data=request.data)
            print(f"🔍 Serializer creado: {serializer}")
            
            if serializer.is_valid():
                print(f"🔍 ✅ Serializer válido")
                email = serializer.validated_data['email']
                print(f"🔍 Email validado: {email}")
                
                print(f"\n🔍 PASO 2: Buscando usuario...")
                user = User.objects.get(email=email, role='admin', is_active=True)
                print(f"🔍 ✅ Usuario encontrado: {user.username} (ID: {user.id})")
                
                print(f"\n🔍 PASO 3: Creando token...")
                try:
                    token = PasswordResetService.create_reset_token(user)
                    print(f"🔍 ✅ Token creado: {token.token[:20]}... (ID: {token.id})")
                except Exception as token_error:
                    print(f"🔍 ❌ Error creando token: {token_error}")
                    import traceback
                    print(f"🔍 Traceback del token: {traceback.format_exc()}")
                    raise token_error
                
                print(f"\n🔍 PASO 4: Enviando email...")
                try:
                    print(f"🔍 Llamando a PasswordResetService.send_reset_email...")
                    result = PasswordResetService.send_reset_email(user, token)
                    print(f"🔍 ✅ Email enviado exitosamente: {result}")
                except Exception as email_error:
                    print(f"🔍 ❌ Error enviando email: {email_error}")
                    print(f"🔍 Tipo de error: {type(email_error)}")
                    import traceback
                    print(f"🔍 Traceback del email: {traceback.format_exc()}")
                    
                    # Eliminar token si falla el email
                    print(f"🔍 Limpiando token fallido...")
                    token.delete()
                    print(f"🔍 ✅ Token eliminado")
                    raise email_error
                
                print(f"\n🔍 PASO 5: Enviando respuesta exitosa...")
                response_data = {
                    'message': 'Se ha enviado un email con instrucciones para recuperar tu contraseña.',
                    'email': email
                }
                print(f"🔍 Datos de respuesta: {response_data}")
                
                return Response(response_data, status=status.HTTP_200_OK)
            
            else:
                print(f"🔍 ❌ Serializer inválido")
                print(f"🔍 Errores: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except User.DoesNotExist:
            print(f"🔍 ❌ Usuario no encontrado para email: {request.data.get('email', 'N/A')}")
            return Response({
                'error': 'No se encontró una cuenta de administrador activa con este email.'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"\n🔍 ❌ ERROR GENERAL EN REQUEST_RESET")
            print(f"🔍 Tipo de error: {type(e)}")
            print(f"🔍 Mensaje: {str(e)}")
            print(f"🔍 Args: {e.args}")
            
            import traceback
            print(f"🔍 TRACEBACK COMPLETO:")
            traceback.print_exc()
            
            # Intentar usar logger si está disponible
            try:
                logger.error(f"Error en request_reset: {str(e)}")
                print(f"🔍 ✅ Logger funcionando")
            except Exception as log_error:
                print(f"🔍 ❌ Error en logger: {log_error}")
            
            return Response({
                'error': 'Ocurrió un error al procesar tu solicitud. Por favor intenta de nuevo.',
                'debug_info': str(e) if settings.DEBUG else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def confirm_reset(self, request):
        """Confirmar y cambiar la contraseña"""
        try:
            serializer = PasswordResetConfirmSerializer(data=request.data)
            if serializer.is_valid():
                token_string = serializer.validated_data['token']
                new_password = serializer.validated_data['new_password']
                
                # Resetear contraseña
                PasswordResetService.reset_password(token_string, new_password)
                
                return Response({
                    'message': 'Tu contraseña ha sido cambiada exitosamente. Ya puedes iniciar sesión con tu nueva contraseña.'
                }, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except ValueError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error en confirm_reset: {str(e)}")
            return Response({
                'error': 'Ocurrió un error al cambiar tu contraseña. Por favor intenta de nuevo.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def validate_token(self, request):
        """Validar un token de recuperación"""
        try:
            token_string = request.query_params.get('token')
            if not token_string:
                return Response({
                    'error': 'Token requerido'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            token = PasswordResetService.validate_token(token_string)
            if token:
                return Response({
                    'valid': True,
                    'user_email': token.user.email,
                    'expires_at': token.expires_at
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'valid': False,
                    'error': 'Token inválido o expirado'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error validando token: {str(e)}")
            return Response({
                'error': 'Error validando token'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EmployeePasswordResetViewSet(viewsets.ViewSet):
    """ViewSet para recuperación de contraseña de empleados"""
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=['post'])
    def request_reset(self, request):
        """Solicitar recuperación de contraseña para empleados"""
        try:
            serializer = EmployeePasswordResetRequestSerializer(data=request.data)
            if serializer.is_valid():
                email = serializer.validated_data['email']
                
                # Buscar usuario empleado
                user = User.objects.get(email=email, role='employee', is_active=True)
                
                # Crear token de recuperación
                from .services.employee_password_reset_service import EmployeePasswordResetService
                token = EmployeePasswordResetService.create_reset_token(user)
                
                # Enviar email
                EmployeePasswordResetService.send_reset_email(user, token)
                
                return Response({
                    'message': 'Se ha enviado un email con instrucciones para recuperar tu contraseña.',
                    'email': email
                }, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except User.DoesNotExist:
            return Response({
                'error': 'No se encontró una cuenta de empleado activa con este email.'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error en employee request_reset: {str(e)}")
            return Response({
                'error': 'Ocurrió un error al procesar tu solicitud. Por favor intenta de nuevo.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def confirm_reset(self, request):
        """Confirmar y cambiar la contraseña del empleado"""
        try:
            serializer = PasswordResetConfirmSerializer(data=request.data)
            if serializer.is_valid():
                token_string = serializer.validated_data['token']
                new_password = serializer.validated_data['new_password']
                
                # Resetear contraseña
                from .services.employee_password_reset_service import EmployeePasswordResetService
                EmployeePasswordResetService.reset_password(token_string, new_password)
                
                return Response({
                    'message': 'Tu contraseña ha sido cambiada exitosamente. Ya puedes iniciar sesión con tu nueva contraseña.'
                }, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except ValueError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error en employee confirm_reset: {str(e)}")
            return Response({
                'error': 'Ocurrió un error al cambiar tu contraseña. Por favor intenta de nuevo.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def validate_token(self, request):
        """Validar un token de recuperación de empleado"""
        try:
            token_string = request.query_params.get('token')
            if not token_string:
                return Response({
                    'error': 'Token requerido'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            from .services.employee_password_reset_service import EmployeePasswordResetService
            token = EmployeePasswordResetService.validate_token(token_string)
            if token:
                return Response({
                    'valid': True,
                    'user_email': token.user.email,
                    'expires_at': token.expires_at
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'valid': False,
                    'error': 'Token inválido o expirado'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error validando token de empleado: {str(e)}")
            return Response({
                'error': 'Error validando token'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def verify_email(self, request):
        """Verificar si un email pertenece a un empleado"""
        try:
            serializer = EmployeePasswordResetRequestSerializer(data=request.data)
            if serializer.is_valid():
                email = serializer.validated_data['email']
                
                from .services.employee_password_reset_service import EmployeePasswordResetService
                result = EmployeePasswordResetService.verify_employee_email(email)
                
                return Response({
                    'is_employee': result['is_employee'],
                    'email': email
                }, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error verificando email de empleado: {str(e)}")
            return Response({
                'error': 'Error verificando email'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
