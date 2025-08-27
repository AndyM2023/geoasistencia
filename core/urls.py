from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AuthViewSet, DashboardViewSet, EmployeeViewSet, 
    AreaViewSet, AttendanceViewSet, ChangePasswordView, PasswordResetViewSet,
    EmployeePasswordResetViewSet, AreaScheduleViewSet, check_password_change_required,
    check_attendance_permission
)

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'dashboard', DashboardViewSet, basename='dashboard')
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'areas', AreaViewSet, basename='area')
router.register(r'area-schedules', AreaScheduleViewSet, basename='area-schedule')
router.register(r'attendance', AttendanceViewSet, basename='attendance')
router.register(r'password-reset', PasswordResetViewSet, basename='password-reset')
router.register(r'employees/password-reset', EmployeePasswordResetViewSet, basename='employee-password-reset')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/password/change/', ChangePasswordView.as_view(), name='change-password'),
    path('check-password-change/', check_password_change_required, name='check-password-change'),
    path('check-attendance-permission/', check_attendance_permission, name='check-attendance-permission'),
]
