#!/usr/bin/env python
import os
import sys
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from core.models import Employee, Area
from core.views import EmployeeViewSet
from core.services.face_service_singleton import face_service_singleton

print("🔍 SIMULATING EXACT HTTP REQUEST FLOW")
print("=" * 50)

# Create a mock request
factory = RequestFactory()

try:
    # Get or create test data
    area, created = Area.objects.get_or_create(
        name="Test Area",
        defaults={'description': 'Test area for debugging'}
    )
    
    User = get_user_model()
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'is_active': True
        }
    )
    
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
    
    # Create photos data in the EXACT format the frontend sends
    photos_data = [
        'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k='
    ]
    
    # Create the request data exactly as the frontend sends it
    request_data = {
        'photos_base64': photos_data
    }
    
    print(f"\n🔍 REQUEST DATA FORMAT:")
    print(f"   - Type: {type(request_data)}")
    print(f"   - Keys: {list(request_data.keys())}")
    print(f"   - photos_base64 type: {type(request_data['photos_base64'])}")
    print(f"   - photos_base64 length: {len(request_data['photos_base64'])}")
    print(f"   - First photo type: {type(request_data['photos_base64'][0])}")
    
    # Create the request
    request = factory.post(
        f'/employees/{employee.id}/register_face/',
        data=json.dumps(request_data),
        content_type='application/json'
    )
    
    # Mock the user authentication
    request.user = user
    
    print(f"\n🔍 REQUEST DETAILS:")
    print(f"   - Method: {request.method}")
    print(f"   - URL: {request.path}")
    print(f"   - Content-Type: {request.content_type}")
    print(f"   - User: {request.user.username}")
    
    # Parse the JSON data (simulating Django's request.data)
    import json
    request.data = json.loads(request.body)
    print(f"   - Parsed data keys: {list(request.data.keys())}")
    print(f"   - photos_base64 from request: {type(request.data.get('photos_base64'))}")
    
    # Now simulate the exact logic from the register_face view
    print(f"\n🔍 SIMULATING VIEW LOGIC:")
    
    # Extract photos_base64 exactly as the view does
    photos_base64 = request.data.get('photos_base64', [])
    if not photos_base64:
        photos_base64 = request.data.get('photos', [])
    
    print(f"   - photos_base64 extracted: {type(photos_base64)}")
    print(f"   - photos_base64 length: {len(photos_base64) if photos_base64 else 0}")
    
    if photos_base64:
        print(f"   - First photo sample: {str(photos_base64[0])[:100]}...")
    
    if not photos_base64:
        print("❌ No se recibieron fotos")
        print("❌ Campos disponibles en request.data:")
        for key, value in request.data.items():
            print(f"   - {key}: {type(value)} - {len(value) if hasattr(value, '__len__') else 'N/A'}")
        result = {'error': 'Se requieren fotos para el registro'}
    else:
        print(f"✅ Fotos recibidas: {len(photos_base64)}")
        
        # Check face service status
        print(f"\n🔍 FACE SERVICE STATUS DURING REQUEST:")
        service = face_service_singleton.get_service()
        print(f"   - Service: {service}")
        print(f"   - facial_system: {service.facial_system}")
        print(f"   - facial_system is None: {service.facial_system is None}")
        
        if service.facial_system:
            print(f"   - facial_system methods: {[m for m in dir(service.facial_system) if not m.startswith('_')]}")
        
        # Now call the face service
        print(f"\n🔍 CALLING FACE SERVICE:")
        try:
            result = face_service_singleton.register_face(employee, photos_base64)
            print(f"✅ Face service call successful: {result}")
        except Exception as e:
            print(f"❌ Face service call failed: {e}")
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
