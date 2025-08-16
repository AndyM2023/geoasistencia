#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

from core.services.face_service_singleton import face_service_singleton
from core.models import User, Employee, Area

print("🔍 TESTING WITH CORRECT FRONTEND DATA FORMAT")
print("=" * 50)

try:
    # Get or create test data
    area, created = Area.objects.get_or_create(
        name="Test Area",
        defaults={'description': 'Test area for debugging'}
    )
    
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
    # The frontend sends: photos_base64: [base64string1, base64string2, ...]
    photos_data = [
        'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k='
    ]
    
    print(f"\n🔍 PHOTOS DATA FORMAT:")
    print(f"   - Type: {type(photos_data)}")
    print(f"   - Length: {len(photos_data)}")
    print(f"   - First photo type: {type(photos_data[0])}")
    print(f"   - First photo sample: {photos_data[0][:100]}...")
    
    # Check face service status
    print(f"\n🔍 FACE SERVICE STATUS:")
    service = face_service_singleton.get_service()
    print(f"   - Service: {service}")
    print(f"   - facial_system: {service.facial_system}")
    print(f"   - facial_system is None: {service.facial_system is None}")
    
    if service.facial_system:
        print(f"   - facial_system methods: {[m for m in dir(service.facial_system) if not m.startswith('_')]}")
    
    # Now test the exact method that gets called
    print(f"\n🔍 TESTING register_employee_face METHOD:")
    
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
    
    # If successful, check if files were created
    if result.get('success'):
        employee_id = str(employee.employee_id or employee.id)
        employee_name = f"{employee.user.first_name}{employee.user.last_name}".replace(" ", "")
        employee_folder = os.path.join(service.faces_dir, f"{employee_id}{employee_name}")
        
        print(f"\n🔍 CHECKING CREATED FILES:")
        print(f"   - Folder path: {employee_folder}")
        print(f"   - Folder exists: {os.path.exists(employee_folder)}")
        
        if os.path.exists(employee_folder):
            files = os.listdir(employee_folder)
            print(f"   - Files in folder: {files}")
            for file in files:
                file_path = os.path.join(employee_folder, file)
                file_size = os.path.getsize(file_path)
                print(f"     - {file}: {file_size} bytes")
    
except Exception as e:
    print(f"❌ Error during test: {e}")
    import traceback
    traceback.print_exc()
