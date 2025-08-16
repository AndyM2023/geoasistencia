#!/usr/bin/env python3
"""
Script para probar el endpoint de registro facial
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

def create_dummy_photo():
    """Crear una foto dummy en base64"""
    import cv2
    
    # Crear una imagen de prueba (dummy) con un rostro simulado
    dummy_image = np.ones((480, 640, 3), dtype=np.uint8) * 128
    
    # Simular un rostro en el centro
    center_x, center_y = 320, 240
    face_size = 100
    
    # Dibujar un "rostro" simple
    cv2.rectangle(dummy_image, 
                  (center_x - face_size//2, center_y - face_size//2),
                  (center_x + face_size//2, center_y + face_size//2),
                  (255, 255, 255), -1)
    
    # Convertir a base64
    _, buffer = cv2.imencode('.jpg', dummy_image)
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
    
    # Agregar prefijo data URL
    return f"data:image/jpeg;base64,{jpg_as_text}"

def test_face_registration_endpoint():
    """Probar el endpoint de registro facial"""
    print("🧪 ========== PROBANDO ENDPOINT DE REGISTRO FACIAL ==========")
    
    # 1. Obtener token de autenticación
    print("\n🔐 1. OBTENIENDO TOKEN DE AUTENTICACIÓN:")
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
    
    # 2. Probar registro facial para MARCELA MUÑOZ (ID 7)
    print("\n👤 2. PROBANDO REGISTRO FACIAL PARA MARCELA MUÑOZ:")
    employee_id = 7
    register_face_url = f"http://localhost:8000/app/employees/{employee_id}/register_face/"
    
    # Crear 15 fotos dummy
    photos_data = []
    for i in range(15):
        photo_data = {
            "photo": create_dummy_photo(),
            "timestamp": f"2025-08-16T12:02:{i:02d}.000Z"
        }
        photos_data.append(photo_data)
    
    # Datos para el registro facial
    face_data = {
        "photos_base64": photos_data,
        "employee_id": employee_id
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
        
        print(f"📥 Respuesta del servidor:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Body: {response.text}")
        
        if response.status_code == 201:
            print("✅ Registro facial exitoso!")
            data = response.json()
            print(f"   - Success: {data.get('success')}")
            print(f"   - Message: {data.get('message')}")
            print(f"   - Photos count: {data.get('photos_count')}")
            print(f"   - Employee ID: {data.get('employee_id')}")
            return True
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en la petición: {e}")
        return False

if __name__ == "__main__":
    success = test_face_registration_endpoint()
    if success:
        print(f"\n🎯 Registro facial probado exitosamente!")
    else:
        print(f"\n❌ Error en el registro facial")
