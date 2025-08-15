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
from .services.face_service import FaceRecognitionService

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
        
        # Contar áreas
        total_areas = Area.objects.count()
        
        # Asistencias de hoy
        today_attendance = Attendance.objects.filter(date=today).count()
        
        # Empleados pendientes (sin asistencia hoy)
        pending_attendance = total_employees - today_attendance
        
        # Actividades recientes
        recent_attendances = Attendance.objects.select_related('employee__user').order_by('-created_at')[:5]
        recent_activities = []
        
        for attendance in recent_attendances:
            if attendance.check_in:
                activity = {
                    'id': attendance.id,
                    'title': f"{attendance.employee.full_name} marcó asistencia",
                    'time': 'Hace 5 minutos',  # TODO: Calcular tiempo real
                    'icon': 'mdi-check-circle',
                    'color': 'success'
                }
                recent_activities.append(activity)
        
        stats = {
            'total_employees': total_employees,
            'total_areas': total_areas,
            'today_attendance': today_attendance,
            'pending_attendance': pending_attendance,
            'recent_activities': recent_activities
        }
        
        serializer = DashboardStatsSerializer(stats)
        return Response(serializer.data)

class EmployeeViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de empleados"""
    queryset = Employee.objects.select_related('user', 'area').all()
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.AllowAny]  # TEMPORAL: Permitir sin autenticación
    
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
        employee = self.get_object()
        photos = request.data.get('photos', [])
        
        if not photos:
            return Response(
                {'error': 'Se requieren fotos para el registro'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        face_service = FaceRecognitionService()
        result = face_service.register_employee_face(employee, photos)
        
        if result['success']:
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def face_status(self, request, pk=None):
        """Obtener estado del perfil facial del empleado"""
        employee = self.get_object()
        face_service = FaceRecognitionService()
        status_data = face_service.get_employee_face_status(employee)
        
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
        
        face_service = FaceRecognitionService()
        result = face_service.verify_face(employee, photo)
        
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
        employee_id = request.data.get('employee_id')
        area_id = request.data.get('area_id')
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        face_verified = request.data.get('face_verified', False)
        
        try:
            employee = Employee.objects.get(employee_id=employee_id)
            area = Area.objects.get(id=area_id)
            
            # Verificar si ya tiene asistencia hoy
            today = timezone.now().date()
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
            
            if not created:
                # Ya existe, actualizar hora de salida
                attendance.check_out = timezone.now().time()
                attendance.save()
            
            serializer = AttendanceSerializer(attendance)
            return Response(serializer.data)
            
        except (Employee.DoesNotExist, Area.DoesNotExist):
            return Response(
                {'error': 'Empleado o área no encontrada'}, 
                status=status.HTTP_404_NOT_FOUND
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
