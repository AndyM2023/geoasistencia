#!/usr/bin/env python
import os
import sys
import django
from unittest.mock import Mock

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

from django.test import RequestFactory
from core.models import User, Employee, Area
from core.views import EmployeeViewSet
from core.services.face_service_singleton import face_service_singleton

print("🔍 SIMULATING HTTP REQUEST CONTEXT")
print("=" * 50)

# Create a mock request
factory = RequestFactory()

# Create test data
try:
    # Get or create a test area
    area, created = Area.objects.get_or_create(
        name="Test Area",
        defaults={'description': 'Test area for debugging'}
    )
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'is_active': True
        }
    )
    
    # Get or create a test employee
    employee, created = Employee.objects.get_or_create(
        user=user,
        defaults={
            'position': 'Test Position',
            'area': area
        }
    )
    
    print(f"✅ Test data created/retrieved:")
    print(f"   - User: {user.username}")
    print(f"   - Employee: {employee.full_name}")
    print(f"   - Employee ID: {employee.id}")
    
    # Create a mock request with photos data
    photos_data = [
        {
            'photo': 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k='
        }
    ]
    
    # Create the request
    request = factory.post(
        f'/employees/{employee.id}/register_face/',
        data={'photos_base64': photos_data},
        content_type='application/json'
    )
    
    # Mock the user authentication
    request.user = user
    
    print(f"\n🔍 REQUEST DETAILS:")
    print(f"   - Method: {request.method}")
    print(f"   - URL: {request.path}")
    print(f"   - Content-Type: {request.content_type}")
    print(f"   - User: {request.user.username}")
    print(f"   - Data keys: {list(request.data.keys()) if hasattr(request, 'data') else 'No data'}")
    
    # Check face service status before the request
    print(f"\n🔍 FACE SERVICE STATUS BEFORE REQUEST:")
    service = face_service_singleton.get_service()
    print(f"   - Service: {service}")
    print(f"   - facial_system: {service.facial_system}")
    print(f"   - facial_system is None: {service.facial_system is None}")
    
    if service.facial_system:
        print(f"   - facial_system methods: {[m for m in dir(service.facial_system) if not m.startswith('_')]}")
    
    # Now simulate the exact check that happens in register_face
    print(f"\n🔍 SIMULATING THE EXACT CHECK FROM register_face:")
    
    # This is the exact check from the face service
    if not service.facial_system:
        print("❌ Sistema facial no disponible - facial_system is False/None")
        result = {
            'success': False,
            'message': 'Sistema de reconocimiento facial no disponible'
        }
    else:
        print("✅ Sistema facial disponible - facial_system is not False/None")
        # Try to call the actual method
        try:
            result = service.register_employee_face(employee, photos_data)
            print(f"✅ Method call successful: {result}")
        except Exception as e:
            print(f"❌ Method call failed: {e}")
            import traceback
            traceback.print_exc()
            result = {'success': False, 'error': str(e)}
    
    print(f"\n🔍 FINAL RESULT:")
    print(f"   - Success: {result.get('success')}")
    print(f"   - Message: {result.get('message')}")
    print(f"   - Error: {result.get('error')}")
    
except Exception as e:
    print(f"❌ Error during test: {e}")
    import traceback
    traceback.print_exc()
