#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para el endpoint de cambio de contraseña.
Usa este script para verificar que el backend esté funcionando correctamente.
"""

import requests
import json
import sys
import os

# Configuración
BASE_URL = "http://127.0.0.1:8000"
ENDPOINT = "/app/auth/change-password/"
FULL_URL = BASE_URL + ENDPOINT

def test_password_change(token, current_password, new_password):
    """
    Prueba el endpoint de cambio de contraseña.
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "current_password": current_password,
        "new_password": new_password
    }
    
    print(f"🔐 Probando cambio de contraseña...")
    print(f"📤 URL: {FULL_URL}")
    print(f"🔑 Token: {token[:20]}..." if token else "❌ Sin token")
    print(f"📝 Datos: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(FULL_URL, json=data, headers=headers, timeout=10)
        
        print(f"\n📊 RESPUESTA:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Status Text: {response.reason}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.text:
            try:
                response_data = response.json()
                print(f"   Data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            except json.JSONDecodeError:
                print(f"   Raw Response: {response.text}")
        else:
            print("   Data: (vacío)")
        
        # Análisis de la respuesta
        if response.status_code == 200:
            print("\n✅ ÉXITO: Contraseña cambiada correctamente")
            return True
        elif response.status_code == 400:
            print("\n⚠️ ERROR 400: Datos inválidos")
            if response_data.get('current_password'):
                print("   - La contraseña actual es incorrecta")
            if response_data.get('new_password'):
                print("   - La nueva contraseña no cumple los requisitos")
            return False
        elif response.status_code == 401:
            print("\n❌ ERROR 401: No autorizado")
            print("   - Verifica que el token sea válido")
            return False
        elif response.status_code == 404:
            print("\n❌ ERROR 404: Endpoint no encontrado")
            print("   - Verifica que el backend esté implementado")
            print("   - Verifica que la URL sea correcta")
            return False
        else:
            print(f"\n❌ ERROR {response.status_code}: Respuesta inesperada")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"\n❌ ERROR DE CONEXIÓN:")
        print("   - No se puede conectar al servidor")
        print("   - Verifica que Django esté corriendo en http://127.0.0.1:8000")
        return False
    except requests.exceptions.Timeout:
        print(f"\n❌ ERROR DE TIMEOUT:")
        print("   - La petición tardó demasiado")
        return False
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {str(e)}")
        return False

def test_login(username, password):
    """
    Prueba el login para obtener un token válido.
    """
    login_url = BASE_URL + "/app/auth/login/"
    
    data = {
        "username": username,
        "password": password
    }
    
    print(f"🔑 Probando login para obtener token...")
    print(f"📤 URL: {login_url}")
    print(f"👤 Usuario: {username}")
    
    try:
        response = requests.post(login_url, json=data, timeout=10)
        
        if response.status_code == 200:
            response_data = response.json()
            token = response_data.get('token') or response_data.get('access')
            if token:
                print(f"✅ Login exitoso - Token obtenido: {token[:20]}...")
                return token
            else:
                print("❌ Login exitoso pero no se recibió token")
                print(f"   Respuesta completa: {response_data}")
                return None
        else:
            print(f"❌ Login falló - Status: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error en login: {str(e)}")
        return None

def test_endpoint_availability():
    """
    Prueba si el endpoint está disponible.
    """
    print(f"🔍 Verificando disponibilidad del endpoint...")
    print(f"📤 URL: {FULL_URL}")
    
    try:
        # Probar con GET (debería dar 405 Method Not Allowed, no 404)
        response = requests.get(FULL_URL, timeout=5)
        
        if response.status_code == 405:
            print("✅ Endpoint encontrado (Method Not Allowed es correcto para GET)")
            return True
        elif response.status_code == 404:
            print("❌ Endpoint no encontrado (404)")
            return False
        else:
            print(f"⚠️ Respuesta inesperada: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor Django")
        return False
    except Exception as e:
        print(f"❌ Error verificando endpoint: {str(e)}")
        return False

def main():
    """
    Función principal del script.
    """
    print("=" * 60)
    print("🔐 SCRIPT DE PRUEBA - CAMBIO DE CONTRASEÑA")
    print("=" * 60)
    
    # Verificar que el servidor esté corriendo
    try:
        response = requests.get(BASE_URL, timeout=5)
        print(f"✅ Servidor Django accesible en {BASE_URL}")
    except:
        print(f"❌ No se puede conectar al servidor Django en {BASE_URL}")
        print("   - Asegúrate de que Django esté corriendo")
        print("   - Verifica que esté en el puerto 8000")
        return
    
    # Verificar disponibilidad del endpoint
    if not test_endpoint_availability():
        print("\n❌ El endpoint no está disponible.")
        print("   - Verifica que hayas implementado la vista ChangePasswordView")
        print("   - Verifica que hayas añadido la URL en core/urls.py")
        print("   - Reinicia Django después de los cambios")
        return
    
    print(f"\n{'='*60}")
    
    # Solicitar credenciales
    print("\n📝 INGRESA LAS CREDENCIALES:")
    username = input("👤 Usuario: ").strip()
    current_password = input("🔑 Contraseña actual: ").strip()
    new_password = input("🆕 Nueva contraseña: ").strip()
    
    if not username or not current_password or not new_password:
        print("❌ Todos los campos son requeridos")
        return
    
    # Validar nueva contraseña
    if len(new_password) < 8:
        print("❌ La nueva contraseña debe tener al menos 8 caracteres")
        return
    
    if current_password == new_password:
        print("❌ La nueva contraseña debe ser diferente a la actual")
        return
    
    print(f"\n{'='*60}")
    
    # Probar login para obtener token
    token = test_login(username, current_password)
    
    if not token:
        print("\n❌ No se pudo obtener token. No se puede probar el cambio de contraseña.")
        return
    
    print(f"\n{'='*60}")
    
    # Probar cambio de contraseña
    success = test_password_change(token, current_password, new_password)
    
    print(f"\n{'='*60}")
    
    if success:
        print("🎉 PRUEBA EXITOSA:")
        print("   - El backend está funcionando correctamente")
        print("   - El endpoint de cambio de contraseña está implementado")
        print("   - La contraseña se cambió en la base de datos")
        print("\n💡 Ahora puedes probar desde el frontend")
    else:
        print("💥 PRUEBA FALLIDA:")
        print("   - Revisa los errores mostrados arriba")
        print("   - Verifica la implementación del backend")
        print("   - Consulta los logs de Django")
    
    print(f"{'='*60}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Script interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        print("   - Verifica que todas las dependencias estén instaladas")
        print("   - Asegúrate de que requests esté instalado: pip install requests")
