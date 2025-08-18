from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AuthViewSet, DashboardViewSet, EmployeeViewSet, 
    AreaViewSet, AttendanceViewSet, ChangePasswordView
)

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'dashboard', DashboardViewSet, basename='dashboard')
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'areas', AreaViewSet, basename='area')
router.register(r'attendance', AttendanceViewSet, basename='attendance')

urlpatterns = [
    path('', include(router.urls)),
    # URL para cambio de contraseña (fuera del router porque es una vista individual)
    path('auth/change-password/', ChangePasswordView.as_view(), name='change_password'),
]
