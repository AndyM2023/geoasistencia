#!/usr/bin/env python
"""
Script completo para probar el sistema de recuperación de contraseña
"""

import os
import django
import requests
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

from core.models import User, PasswordResetToken
from core.services.password_reset_service import PasswordResetService

def test_backend_models():
    """Probar que los modelos estén funcionando"""
    print("🔍 Probando modelos del backend...")
    
    try:
        # Verificar que el modelo PasswordResetToken esté disponible
        token_count = PasswordResetToken.objects.count()
        print(f"✅ Modelo PasswordResetToken funcionando. Tokens existentes: {token_count}")
        
        # Verificar usuarios administradores
        admin_count = User.objects.filter(role='admin', is_active=True).count()
        print(f"✅ Usuarios administradores encontrados: {admin_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en modelos: {e}")
        return False

def test_api_endpoints():
    """Probar que los endpoints de la API estén funcionando"""
    print("\n🌐 Probando endpoints de la API...")
    
    base_url = "http://localhost:8000/api"
    
    # Probar endpoint de validación de token
    try:
        response = requests.get(f"{base_url}/password-reset/validate_token/?token=test")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Endpoint validate_token funcionando: {data}")
        else:
            print(f"⚠️  Endpoint validate_token respondió con status {response.status_code}")
    except Exception as e:
        print(f"❌ Error en endpoint validate_token: {e}")
    
    # Probar endpoint de solicitud de reset
    try:
        test_data = {"email": "admin@geoasistencia.com"}
        response = requests.post(f"{base_url}/password-reset/request_reset/", json=test_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Endpoint request_reset funcionando: {data}")
        else:
            print(f"⚠️  Endpoint request_reset respondió con status {response.status_code}")
            if response.status_code == 500:
                print(f"   Error del servidor: {response.text}")
    except Exception as e:
        print(f"❌ Error en endpoint request_reset: {e}")
    
    return True

def test_password_reset_service():
    """Probar el servicio de recuperación de contraseña"""
    print("\n🔧 Probando servicio de recuperación de contraseña...")
    
    try:
        # Obtener un usuario administrador
        admin_user = User.objects.filter(role='admin', is_active=True).first()
        if not admin_user:
            print("❌ No se encontró usuario administrador para la prueba")
            return False
        
        print(f"✅ Usuario de prueba: {admin_user.username} ({admin_user.email})")
        
        # Crear token de reset
        token = PasswordResetService.create_reset_token(admin_user)
        print(f"✅ Token creado: {token.token[:20]}...")
        print(f"   Expira: {token.expires_at}")
        print(f"   Válido: {token.is_valid}")
        
        # Validar token
        is_valid = PasswordResetService.validate_token(token.token)
        print(f"✅ Validación del token: {is_valid}")
        
        # Limpiar token de prueba
        token.delete()
        print("✅ Token de prueba eliminado")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en servicio: {e}")
        return False

def test_email_configuration():
    """Probar la configuración de email"""
    print("\n📧 Probando configuración de email...")
    
    try:
        from django.conf import settings
        
        print(f"✅ EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
        print(f"✅ EMAIL_HOST: {settings.EMAIL_HOST}")
        print(f"✅ EMAIL_PORT: {settings.EMAIL_PORT}")
        print(f"✅ EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
        print(f"✅ EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
        print(f"✅ EMAIL_HOST_PASSWORD: {'Configurado' if settings.EMAIL_HOST_PASSWORD else 'NO CONFIGURADO'}")
        
        if not settings.EMAIL_HOST_PASSWORD:
            print("⚠️  IMPORTANTE: EMAIL_HOST_PASSWORD no está configurado")
            print("   Edita el archivo .env con tus credenciales de email")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error en configuración de email: {e}")
        return False

def main():
    """Función principal"""
    print("=" * 70)
    print("🔐 PRUEBA COMPLETA DEL SISTEMA DE RECUPERACIÓN DE CONTRASEÑA")
    print("=" * 70)
    print()
    
    # Ejecutar todas las pruebas
    tests = [
        ("Modelos del Backend", test_backend_models),
        ("Endpoints de la API", test_api_endpoints),
        ("Servicio de Recuperación", test_password_reset_service),
        ("Configuración de Email", test_email_configuration),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"🧪 Ejecutando: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error ejecutando {test_name}: {e}")
            results.append((test_name, False))
        print()
    
    # Resumen de resultados
    print("=" * 70)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 70)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print()
    print(f"🎯 Resultado: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON! El sistema está funcionando correctamente.")
        print("\n📋 PRÓXIMOS PASOS:")
        print("   1. Configura tus credenciales de email en .env")
        print("   2. Prueba el frontend en http://localhost:5173")
        print("   3. Haz clic en '¿Olvidaste tu contraseña?' en la página de login")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")
    
    print("=" * 70)

if __name__ == '__main__':
    main()
