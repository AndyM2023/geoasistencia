#!/usr/bin/env python
"""
Script para probar la migración del campo has_admin_access
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

from django.db import connection

def test_migration():
    """Probar si la migración se aplicó correctamente"""
    print("🔍 VERIFICANDO ESTADO DE LA MIGRACIÓN")
    print("=" * 50)
    
    try:
        # Verificar si la columna existe
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA table_info(core_employee)")
            columns = cursor.fetchall()
            
            print("📋 COLUMNAS EN LA TABLA core_employee:")
            has_admin_access_exists = False
            
            for column in columns:
                column_name = column[1]
                column_type = column[2]
                print(f"   - {column_name}: {column_type}")
                
                if column_name == 'has_admin_access':
                    has_admin_access_exists = True
            
            print(f"\n✅ Campo 'has_admin_access' existe: {has_admin_access_exists}")
            
            if has_admin_access_exists:
                print("🎉 ¡MIGRACIÓN APLICADA EXITOSAMENTE!")
                print("🔧 Ahora puedes ejecutar el script de configuración")
            else:
                print("❌ La migración no se ha aplicado aún")
                print("💡 Ejecuta: python manage.py migrate")
                
    except Exception as e:
        print(f"❌ Error verificando la base de datos: {e}")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    test_migration()
