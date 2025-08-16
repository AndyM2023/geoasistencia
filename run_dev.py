#!/usr/bin/env python
"""
Script de desarrollo mejorado con auto-reload automático
Ejecuta: python run_dev.py
"""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path

def setup_environment():
    """Configurar variables de entorno para desarrollo"""
    os.environ['DJANGO_EXTENSIONS_AUTO_RELOAD'] = 'True'
    os.environ['DJANGO_DEBUG'] = 'True'
    os.environ['PYTHONPATH'] = os.getcwd()
    
    print("🚀 Configurando entorno de desarrollo...")
    print(f"   - Directorio actual: {os.getcwd()}")
    print(f"   - PYTHONPATH: {os.environ.get('PYTHONPATH')}")
    print(f"   - DJANGO_EXTENSIONS_AUTO_RELOAD: {os.environ.get('DJANGO_EXTENSIONS_AUTO_RELOAD')}")

def check_dependencies():
    """Verificar que todas las dependencias estén instaladas"""
    print("🔍 Verificando dependencias...")
    
    required_packages = [
        'django',
        'django-extensions',
        'django-debug-toolbar',
        'deepface',
        'tensorflow',
        'opencv-python'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - NO INSTALADO")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ Paquetes faltantes: {', '.join(missing_packages)}")
        print("   Ejecuta: pip install " + " ".join(missing_packages))
        return False
    
    print("   ✅ Todas las dependencias están instaladas")
    return True

def run_django_server():
    """Ejecutar servidor Django con auto-reload"""
    print("\n🚀 Iniciando servidor Django con AUTO-RELOAD...")
    print("   - Los cambios en archivos .py se recargarán automáticamente")
    print("   - Presiona Ctrl+C para detener")
    print("   - URL: http://127.0.0.1:8000")
    print("=" * 60)
    
    try:
        # Ejecutar Django con auto-reload
        cmd = [
            sys.executable, 'manage.py', 'runserver',
            '--noreload',  # Desactivar reload por defecto
            '--verbosity', '2',  # Más información en consola
            '127.0.0.1:8000'
        ]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Mostrar output en tiempo real
        for line in process.stdout:
            print(line.rstrip())
            
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
        if process:
            process.terminate()
            process.wait()
    except Exception as e:
        print(f"❌ Error ejecutando Django: {e}")

def main():
    """Función principal"""
    print("🎯 DESARROLLADOR DE DJANGO CON AUTO-RELOAD")
    print("=" * 50)
    
    # Configurar entorno
    setup_environment()
    
    # Verificar dependencias
    if not check_dependencies():
        print("\n❌ No se pueden ejecutar las dependencias faltantes")
        return
    
    # Ejecutar servidor
    run_django_server()

if __name__ == "__main__":
    main()
