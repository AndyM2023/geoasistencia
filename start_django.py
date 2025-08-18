#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para iniciar Django fácilmente.
"""

import os
import sys
import subprocess
import time

def check_django_ready():
    """Verifica si Django está listo."""
    try:
        import requests
        response = requests.get("http://127.0.0.1:8000", timeout=2)
        return True
    except:
        return False

def main():
    print("🚀 INICIANDO DJANGO...")
    print("=" * 50)
    
    # Verificar que estemos en el directorio correcto
    if not os.path.exists("manage.py"):
        print("❌ Error: No se encontró manage.py")
        print("   - Asegúrate de estar en el directorio raíz del proyecto")
        return
    
    # Verificar que Django esté instalado
    try:
        import django
        print(f"✅ Django {django.get_version()} encontrado")
    except ImportError:
        print("❌ Error: Django no está instalado")
        print("   - Ejecuta: pip install -r requirements.txt")
        return
    
    # Verificar que el entorno virtual esté activado
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Advertencia: No parece que estés usando un entorno virtual")
        print("   - Se recomienda usar un entorno virtual")
    
    print("\n📋 Verificando configuración...")
    
    # Verificar archivos críticos
    critical_files = [
        "geoproject/settings.py",
        "geoproject/urls.py", 
        "core/views.py",
        "core/urls.py"
    ]
    
    for file_path in critical_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - NO ENCONTRADO")
            return
    
    print("\n🔧 Iniciando servidor Django...")
    print("   - Puerto: 8000")
    print("   - URL: http://127.0.0.1:8000")
    print("   - Endpoint de cambio de contraseña: http://127.0.0.1:8000/app/auth/change-password/")
    print("\n💡 Presiona Ctrl+C para detener el servidor")
    print("=" * 50)
    
    try:
        # Iniciar Django
        subprocess.run([
            sys.executable, "manage.py", "runserver", "127.0.0.1:8000"
        ], check=True)
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Servidor detenido por el usuario")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error iniciando Django: {e}")
        print("   - Verifica que no haya errores de sintaxis")
        print("   - Revisa la consola para más detalles")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")

if __name__ == "__main__":
    main()
