#!/usr/bin/env python
"""
Script para verificar que Django puede leer las variables de entorno
"""

import os
from dotenv import load_dotenv

print("🔍 VERIFICANDO VARIABLES DE ENTORNO")
print("=" * 50)

# Cargar variables de .env
load_dotenv()

# Verificar variables críticas
variables = [
    'EMAIL_HOST',
    'EMAIL_PORT', 
    'EMAIL_USE_TLS',
    'EMAIL_HOST_USER',
    'EMAIL_HOST_PASSWORD',
    'DEFAULT_FROM_EMAIL',
    'SECRET_KEY'
]

print("📧 Variables de Email:")
for var in variables:
    value = os.getenv(var)
    if var == 'EMAIL_HOST_PASSWORD':
        # Ocultar contraseña por seguridad
        if value:
            print(f"  {var}: {'*' * len(value)} (longitud: {len(value)})")
        else:
            print(f"  {var}: ❌ NO CONFIGURADA")
    else:
        print(f"  {var}: {value}")

print("\n🔐 Verificando configuración:")
if os.getenv('EMAIL_HOST_PASSWORD') and os.getenv('EMAIL_HOST_PASSWORD') != 'TU_CONTRASEÑA_DE_APLICACION_AQUI':
    print("  ✅ EMAIL_HOST_PASSWORD configurada")
else:
    print("  ❌ EMAIL_HOST_PASSWORD NO configurada correctamente")
    print("  💡 Debes reemplazar 'TU_CONTRASEÑA_DE_APLICACION_AQUI' con tu contraseña real")

if os.getenv('EMAIL_HOST_USER') == 'dmejiac@unemi.edu.ec':
    print("  ✅ EMAIL_HOST_USER correcto")
else:
    print("  ❌ EMAIL_HOST_USER incorrecto")
