#!/usr/bin/env python
"""
Script para probar si CORS está funcionando correctamente
"""

import requests
import json

def test_cors():
    """Probar configuración de CORS"""
    print("🧪 PROBANDO CONFIGURACIÓN DE CORS")
    print("=" * 50)
    
    # URL del endpoint
    url = "http://localhost:8000/api/password-reset/request_reset/"
    
    # Datos de prueba
    data = {
        "email": "dmejiac@unemi.edu.ec"
    }
    
    # Headers que simulan el frontend
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "http://localhost:5173",  # Origen del frontend
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        print(f"📡 Probando petición POST a: {url}")
        print(f"📧 Datos: {json.dumps(data, indent=2)}")
        print(f"🌐 Origen: {headers['Origin']}")
        
        # Hacer la petición
        response = requests.post(url, json=data, headers=headers)
        
        print(f"\n📊 RESPUESTA:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        
        # Verificar headers de CORS
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin', 'N/A'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods', 'N/A'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers', 'N/A'),
            'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials', 'N/A'),
        }
        
        print(f"\n🔒 HEADERS DE CORS:")
        for header, value in cors_headers.items():
            print(f"   {header}: {value}")
        
        try:
            response_data = response.json()
            print(f"\n📋 DATOS DE RESPUESTA:")
            print(f"   {json.dumps(response_data, indent=2)}")
        except:
            print(f"\n📋 TEXTO DE RESPUESTA:")
            print(f"   {response.text}")
        
        if response.status_code == 200:
            print("\n✅ ¡ÉXITO! CORS está funcionando correctamente")
        else:
            print(f"\n❌ Error: Status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión: No se puede conectar al servidor")
        print("   Asegúrate de que Django esté ejecutándose en localhost:8000")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def test_preflight():
    """Probar petición OPTIONS (preflight)"""
    print("\n🧪 PROBANDO PETICIÓN PREFLIGHT (OPTIONS)")
    print("=" * 50)
    
    url = "http://localhost:8000/api/password-reset/request_reset/"
    
    # Headers para preflight
    headers = {
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type,authorization"
    }
    
    try:
        print(f"📡 Enviando petición OPTIONS a: {url}")
        
        response = requests.options(url, headers=headers)
        
        print(f"\n📊 RESPUESTA PREFLIGHT:")
        print(f"   Status Code: {response.status_code}")
        
        # Verificar headers de CORS en preflight
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin', 'N/A'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods', 'N/A'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers', 'N/A'),
            'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials', 'N/A'),
            'Access-Control-Max-Age': response.headers.get('Access-Control-Max-Age', 'N/A'),
        }
        
        print(f"\n🔒 HEADERS DE CORS EN PREFLIGHT:")
        for header, value in cors_headers.items():
            print(f"   {header}: {value}")
        
        if response.status_code == 200:
            print("\n✅ ¡ÉXITO! Preflight está funcionando correctamente")
        else:
            print(f"\n❌ Error en preflight: Status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error en preflight: {e}")

if __name__ == '__main__':
    # Probar petición normal
    test_cors()
    
    # Probar preflight
    test_preflight()
    
    print("\n" + "=" * 50)
    print("✅ PRUEBA DE CORS COMPLETADA")


