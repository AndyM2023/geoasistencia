from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.utils import timezone
from datetime import date, timedelta
from .models import User, Employee, Area, Attendance, FaceProfile
from .serializers import (
    UserSerializer, EmployeeSerializer, AreaSerializer, AttendanceSerializer,
    LoginSerializer, DashboardStatsSerializer, AttendanceReportSerializer
)
from .services.face_service_singleton import face_service_singleton

User = get_user_model()

class AuthViewSet(viewsets.ViewSet):
    """ViewSet para autenticación"""
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """Endpoint para login de usuarios"""
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
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Obtener información del usuario autenticado"""
        if request.user.is_authenticated:
            return Response(UserSerializer(request.user).data)
        return Response({'error': 'No autenticado'}, status=status.HTTP_401_UNAUTHORIZED)

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
        print(f"   - photos_base64 type: {type(request.data.get('photos_base64'))}")
        print(f"   - photos_base64 length: {len(request.data.get('photos_base64', []))}")
        
        photos_base64 = request.data.get('photos_base64', [])
        
        if not photos_base64:
            print("❌ No se recibieron fotos")
            return Response(
                {'error': 'Se requieren fotos para el registro'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        print(f"✅ Fotos recibidas: {len(photos_base64)}")
        
        try:
            print(f"🚀 Llamando a face_service.register_face...")
            print(f"   - Employee: {employee.full_name}")
            print(f"   - Photos count: {len(photos_base64)}")
            
            result = face_service_singleton.register_face(employee, photos_base64)
            
            print(f"📊 Resultado del face_service:")
            print(f"   - Success: {result.get('success')}")
            print(f"   - Message: {result.get('message')}")
            print(f"   - Photos count: {result.get('photos_count')}")
            
            if result['success']:
                return Response({
                    'success': True,
                    'message': result['message'],
                    'photos_count': result['photos_count'],
                    'employee_id': employee.id
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'message': result.get('error', 'Error desconocido')
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
    serializer_class = AreaSerializer
    permission_classes = [permissions.AllowAny]  # TEMPORAL: Permitir sin autenticación para pruebas
    
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
        
        # Filtros
        employee = self.request.query_params.get('employee', None)
        area = self.request.query_params.get('area', None)
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        status = self.request.query_params.get('status', None)
        
        if employee:
            queryset = queryset.filter(employee_id=employee)
        
        if area:
            queryset = queryset.filter(area_id=area)
        
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        if status and status != 'all':
            queryset = queryset.filter(status=status)
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def mark_attendance(self, request):
        """Marcar asistencia de un empleado"""
        print("🎯 MARK_ATTENDANCE - Datos recibidos:")
        print(f"   - Request data: {request.data}")
        print(f"   - Employee ID: {request.data.get('employee_id')}")
        print(f"   - Area ID: {request.data.get('area_id')}")
        print(f"   - Latitude: {request.data.get('latitude')}")
        print(f"   - Longitude: {request.data.get('longitude')}")
        print(f"   - Face verified: {request.data.get('face_verified')}")
        
        employee_id = request.data.get('employee_id')
        area_id = request.data.get('area_id')
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        face_verified = request.data.get('face_verified', False)
        
        try:
            # Buscar empleado por ID de base de datos, no por employee_id
            employee = Employee.objects.get(id=employee_id)
            print(f"✅ Empleado encontrado: {employee.full_name} (ID: {employee.id})")
            
            area = Area.objects.get(id=area_id)
            print(f"✅ Área encontrada: {area.name} (ID: {area.id})")
            
            # Verificar si ya tiene asistencia hoy
            today = timezone.now().date()
            print(f"📅 Fecha actual: {today}")
            
            attendance, created = Attendance.objects.get_or_create(
                employee=employee,
                date=today,
                defaults={
                    'area': area,
                    'check_in': timezone.now().time(),
                    'status': 'present',
                    'latitude': latitude,
                    'longitude': longitude,
                    'face_verified': face_verified
                }
            )
            
            if created:
                print(f"✅ NUEVA asistencia creada para {employee.full_name}")
                message = f"Entrada registrada exitosamente para {employee.full_name}"
                action_type = "entrada"
            else:
                print(f"🔄 Asistencia existente encontrada para {employee.full_name}")
                # Verificar si ya tiene hora de salida
                if attendance.check_out is None:
                    # Solo actualizar si no tiene hora de salida
                    attendance.check_out = timezone.now().time()
                    attendance.save()
                    print(f"⏰ Hora de salida actualizada: {attendance.check_out}")
                    message = f"Salida registrada exitosamente para {employee.full_name}"
                    action_type = "salida"
                else:
                    print(f"ℹ️ Empleado ya tiene entrada y salida registradas para hoy")
                    print(f"   Entrada: {attendance.check_in}")
                    print(f"   Salida: {attendance.check_out}")
                    message = f"{employee.full_name} ya tiene entrada y salida registradas para hoy"
                    action_type = "completo"
                    
                    # Cuando ya está completo, devolver error informativo
                    return Response({
                        'success': False,
                        'message': message,
                        'action_type': action_type,
                        'check_in': attendance.check_in,
                        'check_out': attendance.check_out,
                        'employee_name': employee.full_name,
                        'error_type': 'already_complete'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            print(f"📊 Asistencia final: {attendance}")
            serializer = AttendanceSerializer(attendance)
            
            # Crear respuesta personalizada
            response_data = {
                'attendance': serializer.data,
                'message': message,
                'action_type': action_type,
                'check_in': attendance.check_in,
                'check_out': attendance.check_out,
                'employee_name': employee.full_name
            }
            
            print(f"🎯 RESPUESTA COMPLETA que se envía al frontend:")
            print(f"   - action_type: {action_type}")
            print(f"   - employee_name: {employee.full_name}")
            print(f"   - message: {message}")
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
