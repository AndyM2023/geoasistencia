#!/usr/bin/env python
"""
Script simple para probar la API de recuperación de contraseña
"""

import requests
import json

def test_password_reset_api():
    """Probar la API de recuperación de contraseña"""
    print("🧪 PROBANDO API DE RECUPERACIÓN DE CONTRASEÑA")
    print("=" * 50)
    
    # URL del endpoint
    url = "http://localhost:8000/api/password-reset/request_reset/"
    
    # Datos de prueba
    data = {
        "email": "admin@geoasistencia.com"
    }
    
    # Headers
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"📡 Enviando petición POST a: {url}")
        print(f"📧 Datos: {data}")
        
        # Hacer la petición
        response = requests.post(url, json=data, headers=headers)
        
        print(f"\n📊 RESPUESTA:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"   Datos: {json.dumps(response_data, indent=2)}")
        except:
            print(f"   Texto: {response.text}")
        
        if response.status_code == 200:
            print("\n✅ ¡ÉXITO! La API está funcionando correctamente")
        else:
            print(f"\n❌ Error: Status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión: No se puede conectar al servidor")
        print("   Asegúrate de que Django esté ejecutándose en localhost:8000")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == '__main__':
    test_password_reset_api()


