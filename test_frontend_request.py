#!/usr/bin/env python3
"""
Script que simula exactamente la petición del frontend
"""

import os
import sys
import django
import base64
import requests
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

def test_frontend_request():
    """Simula exactamente la petición del frontend"""
    print("🧪 ========== SIMULANDO PETICIÓN DEL FRONTEND ==========")
    
    # URL que está usando el frontend
    url = "http://localhost:8000/app/employees/7/register_face/"
    
    # Crear datos de prueba similares a los del frontend
    test_photos = []
    
    # Crear 15 fotos dummy (como hace el frontend)
    for i in range(15):
        # Simular una foto en base64 (muy simple)
        dummy_image = b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        photo_data = {
            "photo": f"data:image/jpeg;base64,{dummy_image.decode('utf-8')}",
            "timestamp": f"2025-08-16T10:52:{i:02d}.000Z"
        }
        test_photos.append(photo_data)
    
    # Datos que envía el frontend
    request_data = {
        "photos": test_photos,
        "employee_id": 7
    }
    
    print(f"📤 Enviando petición a: {url}")
    print(f"📊 Datos enviados: {json.dumps(request_data, indent=2)}")
    
    try:
        # Hacer la petición POST
        response = requests.post(
            url,
            json=request_data,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        )
        
        print(f"📥 Respuesta del servidor:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        print(f"   Body: {response.text}")
        
        if response.status_code == 200:
            print("✅ Petición exitosa!")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error en la petición: {e}")
    
    print("=" * 60)

if __name__ == "__main__":
    test_frontend_request()
