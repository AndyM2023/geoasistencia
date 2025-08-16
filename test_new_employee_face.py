#!/usr/bin/env python3
"""
Script para probar el registro facial con un empleado que no tenga perfil facial
"""

import os
import sys
import django
import requests
import json
import base64
import numpy as np

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

from core.models import Employee, FaceProfile

def create_realistic_photo():
    """Crear una foto más realista con un rostro simulado"""
    import cv2
    
    # Crear una imagen más realista (640x480)
    image = np.ones((480, 640, 3), dtype=np.uint8) * 128
    
    # Simular un rostro más complejo
    center_x, center_y = 320, 240
    
    # Cabeza (círculo)
    cv2.circle(image, (center_x, center_y), 80, (255, 220, 177), -1)
    
    # Ojos
    cv2.circle(image, (center_x - 25, center_y - 20), 15, (255, 255, 255), -1)
    cv2.circle(image, (center_x + 25, center_y - 20), 15, (255, 255, 255), -1)
    cv2.circle(image, (center_x - 25, center_y - 20), 8, (0, 0, 0), -1)
    cv2.circle(image, (center_x + 25, center_y - 20), 8, (0, 0, 0), -1)
    
    # Nariz
    cv2.ellipse(image, (center_x, center_y + 10), (15, 8), 0, 0, 180, (255, 200, 150), -1)
    
    # Boca
    cv2.ellipse(image, (center_x, center_y + 40), (30, 15), 0, 0, 180, (255, 100, 100), -1)
    
    # Convertir a base64
    _, buffer = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, 85])
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
    
    # Agregar prefijo data URL (como hace el frontend)
    return f"data:image/jpeg;base64,{jpg_as_text}"

def find_employee_without_face():
    """Encontrar un empleado que no tenga perfil facial"""
    print("🔍 Buscando empleado sin perfil facial...")
    
    employees = Employee.objects.all()
    for emp in employees:
        try:
            face_profile = emp.face_profile
            print(f"   - {emp.full_name}: ✅ Tiene perfil facial ({face_profile.photos_count} fotos)")
        except FaceProfile.DoesNotExist:
            print(f"   - {emp.full_name}: ❌ Sin perfil facial")
            return emp
    
    print("❌ Todos los empleados tienen perfil facial")
    return None

def test_new_employee_face():
    """Probar el registro facial con un empleado nuevo"""
    print("🧪 ========== PRUEBA CON EMPLEADO SIN PERFIL FACIAL ==========")
    
    # 1. Encontrar empleado sin perfil facial
    print("\n👤 1. BUSCANDO EMPLEADO SIN PERFIL FACIAL:")
    employee = find_employee_without_face()
    if not employee:
        print("❌ No hay empleados sin perfil facial para probar")
        return False
    
    print(f"✅ Empleado seleccionado: {employee.full_name}")
    print(f"   - ID Django: {employee.id}")
    print(f"   - Employee ID: {employee.employee_id}")
    
    # 2. Obtener token de autenticación
    print("\n🔐 2. OBTENIENDO TOKEN DE AUTENTICACIÓN:")
    login_url = "http://localhost:8000/app/auth/login/"
    login_data = {"username": "admin", "password": "admin123"}
    
    try:
        login_response = requests.post(login_url, json=login_data)
        if login_response.status_code == 200:
            token = login_response.json().get('token')
            print(f"✅ Token obtenido: {token[:50]}...")
        else:
            print(f"❌ Error en login: {login_response.text}")
            return False
    except Exception as e:
        print(f"❌ Error obteniendo token: {e}")
        return False
    
    # 3. Probar registro facial
    print("\n📸 3. PROBANDO REGISTRO FACIAL:")
    register_face_url = f"http://localhost:8000/app/employees/{employee.id}/register_face/"
    
    # Crear 3 fotos realistas (menos para debug)
    photos_data = []
    for i in range(3):
        photo_data = {
            "photo": create_realistic_photo(),
            "timestamp": f"2025-08-16T12:17:{i:02d}.000Z"
        }
        photos_data.append(photo_data)
    
    # Datos para el registro facial
    face_data = {
        "photos_base64": photos_data,
        "employee_id": employee.id
    }
    
    print(f"📤 Enviando petición a: {register_face_url}")
    print(f"📊 Fotos enviadas: {len(photos_data)}")
    print(f"🔑 Token: {token[:50]}...")
    
    try:
        # Hacer la petición POST con el token
        response = requests.post(
            register_face_url,
            json=face_data,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {token}'
            }
        )
        
        print(f"\n📥 Respuesta del servidor:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Body: {response.text}")
        
        if response.status_code == 201:
            print("✅ Registro facial exitoso!")
            data = response.json()
            print(f"   - Success: {data.get('success')}")
            print(f"   - Message: {data.get('message')}")
            print(f"   - Photos count: {data.get('photos_count')}")
            return True
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en la petición: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_new_employee_face()
    if success:
        print(f"\n🎯 Registro facial probado exitosamente!")
    else:
        print(f"\n❌ Error en el registro facial")
