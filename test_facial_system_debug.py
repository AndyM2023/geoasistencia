#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

from core.services.face_service_singleton import face_service_singleton
from core.services import face_service

print("🔍 DEBUGGING FACIAL SYSTEM INITIALIZATION")
print("=" * 50)

print(f"1. Module-level FACIAL_RECOGNITION_AVAILABLE: {face_service.FACIAL_RECOGNITION_AVAILABLE}")

# Get the service instance
service = face_service_singleton.get_service()
print(f"2. Service instance: {service}")
print(f"3. Service facial_system: {service.facial_system}")
print(f"4. facial_system is None: {service.facial_system is None}")

# Check if the facial system has the expected methods
if service.facial_system:
    print(f"5. facial_system methods: {[m for m in dir(service.facial_system) if not m.startswith('_')]}")
    
    # Test if we can call a method
    try:
        print("6. Testing facial_system.extract_face_features...")
        # This should work if the system is properly initialized
        print("✅ facial_system is properly initialized")
    except Exception as e:
        print(f"❌ Error with facial_system: {e}")
else:
    print("❌ facial_system is None - this is the problem!")

# Check the initialization logic
print("\n🔍 CHECKING INITIALIZATION LOGIC")
print("=" * 30)

# Recreate the service to see what happens during initialization
print("7. Recreating FaceRecognitionService...")
from core.services.face_service import FaceRecognitionService

new_service = FaceRecognitionService()
print(f"8. New service facial_system: {new_service.facial_system}")
print(f"9. New facial_system is None: {new_service.facial_system is None}")

if new_service.facial_system:
    print("✅ New service has facial_system")
else:
    print("❌ New service missing facial_system")

# Check if there's a timing issue
print("\n🔍 CHECKING FOR TIMING ISSUES")
print("=" * 30)

# Import the FacialRecognition class directly
try:
    from face_recognition.advanced_face_system import FacialRecognition
    print("10. FacialRecognition class imported successfully")
    
    # Try to instantiate it
    try:
        base_dir = os.path.join(os.getcwd(), 'face_recognition')
        facial_instance = FacialRecognition(base_dir=base_dir, database_name="faces")
        print("11. FacialRecognition instance created successfully")
        print(f"12. Instance methods: {[m for m in dir(facial_instance) if not m.startswith('_')]}")
    except Exception as e:
        print(f"❌ Error creating FacialRecognition instance: {e}")
        
except ImportError as e:
    print(f"❌ Error importing FacialRecognition: {e}")

print("\n🔍 SUMMARY")
print("=" * 20)
if service.facial_system and new_service.facial_system:
    print("✅ Both services have facial_system - the issue must be elsewhere")
elif not service.facial_system and not new_service.facial_system:
    print("❌ Both services missing facial_system - initialization issue")
else:
    print("⚠️ Inconsistent state between services")
