#!/usr/bin/env python
"""
Script que simula exactamente lo que hace el frontend Vue.js
"""

import requests
import json

def simulate_frontend_request():
    """Simular la petición exacta del frontend"""
    print("🧪 SIMULANDO PETICIÓN DEL FRONTEND")
    print("=" * 50)
    
    # URL exacta que usa el frontend
    url = "http://localhost:8000/api/password-reset/request_reset/"
    
    # Datos exactos que envía el frontend
    data = {
        "email": "admin@geoasistencia.com"
    }
    
    # Headers exactos que envía el frontend
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        print(f"📡 Simulando petición del frontend:")
        print(f"   URL: {url}")
        print(f"   Método: POST")
        print(f"   Datos: {json.dumps(data, indent=2)}")
        print(f"   Headers: {json.dumps(headers, indent=2)}")
        
        # Hacer la petición
        response = requests.post(url, json=data, headers=headers)
        
        print(f"\n📊 RESPUESTA DEL SERVIDOR:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"   CORS Headers: {response.headers.get('Access-Control-Allow-Origin', 'N/A')}")
        
        try:
            response_data = response.json()
            print(f"   Datos JSON: {json.dumps(response_data, indent=2)}")
        except:
            print(f"   Texto: {response.text}")
        
        if response.status_code == 200:
            print("\n✅ ¡ÉXITO! La petición del frontend funciona")
        else:
            print(f"\n❌ Error: Status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión: No se puede conectar al servidor")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == '__main__':
    simulate_frontend_request()

