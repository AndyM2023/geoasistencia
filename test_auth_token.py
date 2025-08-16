#!/usr/bin/env python3
"""
Script para probar la autenticación y obtener un token JWT válido
"""

import os
import sys
import django
import requests
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

def test_auth_login():
    """Probar el login y obtener token JWT"""
    print("🔐 ========== PROBANDO AUTENTICACIÓN ==========")
    
    # URL del endpoint de login
    login_url = "http://localhost:8000/app/auth/login/"
    
    # Credenciales de admin (usar las que configuraste)
    test_credentials = [
        {"username": "admin", "password": "admin123"},
        {"username": "andy", "password": "andy123"},
        {"username": "dmejiac", "password": "dmejiac123"},
    ]
    
    for creds in test_credentials:
        print(f"\n🧪 Probando credenciales: {creds['username']}")
        
        try:
            # Hacer la petición POST de login
            response = requests.post(
                login_url,
                json=creds,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            )
            
            print(f"📥 Respuesta del servidor:")
            print(f"   Status Code: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Login exitoso!")
                print(f"   - Token: {data.get('token', 'No token')[:50]}...")
                print(f"   - Usuario: {data.get('user', {}).get('username', 'No user')}")
                print(f"   - Role: {data.get('user', {}).get('role', 'No role')}")
                
                # Probar crear empleado con el token
                test_create_employee_with_token(data.get('token'))
                return data.get('token')
                
            else:
                print(f"❌ Login falló: {response.text}")
                
        except Exception as e:
            print(f"❌ Error en login: {e}")
    
    print("\n❌ No se pudo obtener un token válido")
    return None

def test_create_employee_with_token(token):
    """Probar crear empleado con el token JWT"""
    print(f"\n🧪 ========== PROBANDO CREACIÓN DE EMPLEADO CON TOKEN ==========")
    
    # URL del endpoint de empleados
    url = "http://localhost:8000/app/employees/"
    
    # Datos de prueba
    test_data = {
        "first_name": "TEST",
        "last_name": "AUTH",
        "email": "testauth@example.com",
        "position": "Analista",
        "area": 1
    }
    
    print(f"📤 Enviando petición a: {url}")
    print(f"📊 Datos enviados: {json.dumps(test_data, indent=2)}")
    print(f"🔑 Token: {token[:50]}...")
    
    try:
        # Hacer la petición POST con el token
        response = requests.post(
            url,
            json=test_data,
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
            print("✅ Empleado creado exitosamente con autenticación!")
            return True
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en la petición: {e}")
        return False

if __name__ == "__main__":
    token = test_auth_login()
    if token:
        print(f"\n🎯 Token obtenido exitosamente: {token[:50]}...")
    else:
        print("\n❌ No se pudo obtener token válido")
