#!/usr/bin/env python3
"""
Script simple para probar el login del empleado
"""

import requests
import json

# Configuración
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/auth/employee_login/"

def test_login():
    """Probar login simple"""
    print("🧪 Probando login simple...")
    print("=" * 50)
    
    # Credenciales correctas
    login_data = {
        "username": "lmendieta",
        "password": "test123"
    }
    
    print(f"🔑 Intentando login con:")
    print(f"   Username: {login_data['username']}")
    print(f"   Password: {login_data['password']}")
    print(f"   URL: {LOGIN_URL}")
    
    try:
        response = requests.post(LOGIN_URL, json=login_data)
        print(f"\n📡 Respuesta del servidor:")
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Login exitoso!")
            print(f"   Token: {data.get('token', 'N/A')[:20]}...")
            print(f"   Usuario: {data.get('user', {}).get('username', 'N/A')}")
        else:
            print(f"   ❌ Error en login:")
            print(f"   Respuesta: {response.text}")
            
    except requests.exceptions.ConnectionError as e:
        print(f"   ❌ Error de conexión: {e}")
    except Exception as e:
        print(f"   ❌ Error inesperado: {e}")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    test_login()
