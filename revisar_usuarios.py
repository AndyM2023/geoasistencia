#!/usr/bin/env python
"""
Script para revisar y limpiar usuarios duplicados
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

from core.models import User

def revisar_usuarios():
    """Revisar usuarios duplicados y limpiar la base de datos"""
    print("🔍 REVISANDO USUARIOS DUPLICADOS")
    print("=" * 50)
    
    try:
        # Buscar usuarios con email dmejiac@unemi.edu.ec
        usuarios = User.objects.filter(email='dmejiac@unemi.edu.ec')
        print(f"📧 Usuarios encontrados con email 'dmejiac@unemi.edu.ec': {usuarios.count()}")
        
        if usuarios.count() > 1:
            print("\n❌ PROBLEMA: Múltiples usuarios con el mismo email")
            print("Lista de usuarios:")
            
            for i, user in enumerate(usuarios, 1):
                print(f"  {i}. ID: {user.id}")
                print(f"     Username: {user.username}")
                print(f"     Role: {user.role}")
                print(f"     Activo: {user.is_active}")
                print(f"     Fecha creación: {user.date_joined}")
                print()
            
            # Preguntar cuál mantener
            print("¿Cuál usuario quieres mantener? (ingresa el número):")
            try:
                eleccion = int(input("Opción: ")) - 1
                if 0 <= eleccion < usuarios.count():
                    usuario_a_mantener = usuarios[eleccion]
                    usuarios_a_eliminar = [u for i, u in enumerate(usuarios) if i != eleccion]
                    
                    print(f"\n✅ Manteniendo usuario: {usuario_a_mantener.username}")
                    print(f"🗑️ Eliminando {len(usuarios_a_eliminar)} usuarios duplicados...")
                    
                    for user in usuarios_a_eliminar:
                        print(f"   - Eliminando: {user.username} (ID: {user.id})")
                        user.delete()
                    
                    print("✅ Usuarios duplicados eliminados!")
                    
                else:
                    print("❌ Opción inválida")
                    
            except ValueError:
                print("❌ Debes ingresar un número")
        else:
            print("✅ No hay usuarios duplicados")
            
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    revisar_usuarios()
